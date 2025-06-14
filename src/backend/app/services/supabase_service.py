from app import supabase_client, logger
from datetime import datetime, timezone
from . import ai_service  # Assuming ai_service.py is in the same directory


def get_user_by_wallet(wallet_address):
    return supabase_client.table('users').select('id').eq('wallet_address',
                                                          wallet_address.lower()).maybe_single().execute()


def get_user_by_wallet_full(wallet_address):
    """Fetches the full user object, not just the ID."""
    return supabase_client.table('users').select('*').eq('wallet_address',
                                                         wallet_address.lower()).maybe_single().execute()


def upsert_user(wallet_address, name, country):
    return supabase_client.table('users').upsert({
        'wallet_address': wallet_address.lower(), 'name': name, 'country': country
    }, on_conflict='wallet_address').execute()


def get_paths_by_creator(wallet_address):
    # This function returns paths created by a user, could be used for a dedicated "My Creations" view
    return supabase_client.table('learning_paths').select(
        "id, title, short_description, total_levels, created_at, intent_type").eq(
        'creator_wallet', wallet_address.lower()).order('created_at', desc=True).execute()


def get_user_associated_paths_rpc(user_wallet_address: str):
    """
    Fetches all paths associated with a user (created by them OR enrolled in)
    using the get_user_associated_paths RPC function.
    """
    logger.info(f"DB: Fetching all associated paths for wallet: {user_wallet_address} using RPC.")
    return supabase_client.rpc('get_user_associated_paths', {
        'p_user_wallet_address': user_wallet_address
    }).execute()


def get_path_count_by_creator(wallet_address):
    """Efficiently gets the count of paths created by a user."""
    response = supabase_client.table('learning_paths').select('id', count='exact').eq('creator_wallet',
                                                                                      wallet_address.lower()).execute()
    return response.count


def get_all_paths():
    return supabase_client.table('learning_paths').select(
        "id, title, short_description, total_levels, intent_type").order('created_at', desc=True).execute()


def get_path_by_id_for_delete_check(path_id):  # Renamed to avoid conflict if a more general one is needed
    return supabase_client.table('learning_paths').select("creator_wallet").eq('id', path_id).maybe_single().execute()


def get_full_path_details(path_id):
    """
    Fetches a single path and all its related levels and content items in one query.
    """
    return supabase_client.table('learning_paths').select(
        '*, levels(*, content_items(*))'
    ).eq('id', path_id).order(
        'level_number', referenced_table='levels'  # Supabase new syntax
    ).order(
        'item_index', referenced_table='levels.content_items'  # Supabase new syntax
    ).maybe_single().execute()


def get_full_path_details_for_user(path_id, user_wallet):
    """
    Fetches full path details and enriches it with user-specific completion and minting status.
    """
    path_res = get_full_path_details(path_id)
    if not path_res or not path_res.data:
        return None
    path_data = path_res.data

    user_res = get_user_by_wallet(user_wallet)
    user_id = user_res.data['id'] if user_res and user_res.data else None

    if user_id:
        progress_res = supabase_client.rpc('get_level_completion_for_path', {
            'p_user_id': user_id,
            'p_path_id': path_id
        }).execute()
        level_completion_map = {item['level_number']: item['is_complete'] for item in
                                progress_res.data} if progress_res.data else {}
    else:
        level_completion_map = {}

    if 'levels' in path_data and path_data['levels']:
        for level in path_data['levels']:
            level_num = level.get('level_number')
            level['is_complete'] = level_completion_map.get(level_num, False)

    path_data['is_complete'] = get_path_completion_status(user_wallet, path_id)
    if user_id:
        nft_res = get_nft_by_user_and_path(user_wallet, path_id)
        path_data['is_minted'] = nft_res is not None
    else:
        path_data['is_minted'] = False

    return path_data


def create_learning_path(title, short_description, long_description, creator_wallet, total_levels, intent_type,
                         embedding):
    return supabase_client.table('learning_paths').insert({
        "title": title, "short_description": short_description, "long_description": long_description,
        "creator_wallet": creator_wallet.lower(), "total_levels": total_levels, "intent_type": intent_type,
        "title_embedding": embedding
    }).execute()


def delete_path_by_id(path_id):
    logger.warning(f"DB: Deleting path with ID: {path_id} and all its content.")
    return supabase_client.table('learning_paths').delete().eq('id', path_id).execute()


def update_path_hash(path_id, content_hash):
    return supabase_client.table('learning_paths').update({'content_hash': content_hash}).eq('id', path_id).execute()


def create_level(path_id, level_number, level_title):
    return supabase_client.table('levels').insert({
        "path_id": path_id, "level_number": level_number, "level_title": level_title
    }).execute()


def get_level(path_id, level_num):
    return supabase_client.table('levels').select('id, level_title').eq('path_id', path_id).eq('level_number',
                                                                                               level_num).single().execute()


def create_content_items(items_to_insert):
    return supabase_client.table('content_items').insert(items_to_insert).execute()


def get_content_items_for_level(level_id):
    return supabase_client.table('content_items').select('id, item_index, item_type, content').eq('level_id',
                                                                                                  level_id).order(
        'item_index').execute()


def find_similar_paths(embedding, threshold, count):
    logger.info(f"DB: Finding similar paths with threshold {threshold}")
    return supabase_client.rpc('match_similar_paths', {
        'query_embedding': embedding,
        'match_threshold': threshold,
        'match_count': count
    }).execute()


def hybrid_search_paths(query_text):
    logger.info(f"DB: Hybrid search for query: '{query_text}'")
    query_embedding = ai_service.get_embedding(query_text)
    semantic_res = supabase_client.rpc('search_paths_semantic', {
        'query_embedding': query_embedding,
        'match_threshold': 0.6,
        'match_count': 10
    }).execute()

    search_term = f"%{query_text}%"  # Ensure wildcards are used for ILIKE
    keyword_res = supabase_client.rpc('search_paths_keyword', {
        'search_term': search_term,
        'match_count': 10
    }).execute()

    semantic_results = []
    if semantic_res.data:
        for item in semantic_res.data:
            semantic_results.append({
                "id": item['id'],
                "match_type": "semantic",
                "result_in": "title",  # Semantic search primarily matches on title embedding
                "similarity": round(item['similarity'], 4),
                "title": item['title']
            })

    keyword_results = []
    if keyword_res.data:
        for item in keyword_res.data:
            keyword_results.append({
                "id": item['id'],
                "match_type": "keyword",
                "result_in": item['result_in'],
                "similarity": None,
                "title": item['title']
            })

    final_results = []
    seen_ids = set()
    # Interleave results: one keyword, one semantic, etc.
    len_k = len(keyword_results)
    len_s = len(semantic_results)
    max_len = max(len_k, len_s)

    for i in range(max_len):
        if i < len_k and keyword_results[i]['id'] not in seen_ids:
            final_results.append(keyword_results[i])
            seen_ids.add(keyword_results[i]['id'])
        if i < len_s and semantic_results[i]['id'] not in seen_ids:
            final_results.append(semantic_results[i])
            seen_ids.add(semantic_results[i]['id'])

    return final_results


def create_task_log(task_id):
    return supabase_client.table('task_progress_logs').insert({
        'task_id': task_id,
        'logs': []
    }).execute()


def update_task_log(task_id, new_log_entry):
    return supabase_client.rpc('append_to_log', {
        'task_uuid': task_id,
        'new_log': new_log_entry
    }).execute()


def get_task_log(task_id):
    return supabase_client.table('task_progress_logs').select('logs').eq('task_id', task_id).single().execute()


def _create_progress_record(user_id, path_id):
    logger.info(f"DB: Creating new progress record for user {user_id} on path {path_id}.")
    insert_res = supabase_client.table('user_progress').insert({
        'user_id': user_id,
        'path_id': path_id,
        'started_at': datetime.now(timezone.utc).isoformat()
    }).execute()
    if not insert_res.data:
        raise Exception(f"Failed to create progress record for user {user_id} on path {path_id}")
    logger.info(f"DB: Successfully created progress record with ID: {insert_res.data[0]['id']}")
    return insert_res.data[0]


def upsert_level_progress(user_wallet, path_id, level_index, correct_answers, total_questions):
    user_res = get_user_by_wallet(user_wallet)
    if not user_res or not user_res.data:
        raise ValueError(f"User not found for wallet {user_wallet}")
    user_id = user_res.data['id']

    progress_res = supabase_client.table('user_progress').select('id').eq('user_id', user_id).eq('path_id',
                                                                                                 path_id).maybe_single().execute()  # Use maybe_single

    if progress_res and progress_res.data:
        progress_id = progress_res.data['id']
    else:
        logger.info(f"No progress found for user {user_id} on path {path_id}. Creating new progress record.")
        new_progress = _create_progress_record(user_id, path_id)
        progress_id = new_progress['id']

    logger.info(
        f"DB: Upserting level progress for progress_id {progress_id}, level {level_index} with score {correct_answers}/{total_questions} and marking as complete.")
    supabase_client.table('level_progress').upsert({
        'progress_id': progress_id,
        'level_number': level_index,
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'is_complete': True
    }, on_conflict='progress_id, level_number').execute()

    logger.info(f"DB: Checking if path is now complete for progress_id {progress_id}")
    supabase_client.rpc('check_and_complete_path', {'p_progress_id': progress_id}).execute()


def get_level_score(user_wallet, path_id, level_index):
    logger.info(f"DB: Getting level score for wallet {user_wallet}, path {path_id}, level {level_index}.")
    user_res = get_user_by_wallet(user_wallet)
    if not user_res or not user_res.data:
        raise ValueError(f"User not found for wallet {user_wallet}")
    user_id = user_res.data['id']

    progress_res = supabase_client.table('user_progress').select('id').eq('user_id', user_id).eq('path_id',
                                                                                                 path_id).maybe_single().execute()
    if not progress_res or not progress_res.data:
        logger.warning(f"DB: No progress record found for user {user_id} on path {path_id}.")
        return None

    progress_id = progress_res.data['id']
    score_res = supabase_client.table('level_progress').select('correct_answers, total_questions').eq('progress_id',
                                                                                                      progress_id).eq(
        'level_number', level_index).maybe_single().execute()

    return score_res.data if score_res and score_res.data else None


def get_user_scores(user_id):
    res = supabase_client.table('user_progress').select(
        'path_id, learning_paths(title), level_progress(correct_answers, total_questions)'
    ).eq('user_id', user_id).execute()

    if not res.data:
        return []
    path_scores = {}
    for progress_record in res.data:
        path_id = progress_record.get('path_id')
        if not path_id:
            continue
        path_info = progress_record.get('learning_paths') or {}
        path_title = path_info.get('title', f'Deleted Path ({path_id})')
        if path_id not in path_scores:
            path_scores[path_id] = {
                "path_id": path_id,
                "path_title": path_title,
                "correct_answers": 0,
                "total_questions_answered": 0
            }
        level_progress_list = progress_record.get('level_progress', [])
        for level_score in level_progress_list:
            path_scores[path_id]["correct_answers"] += level_score.get('correct_answers', 0)
            path_scores[path_id]["total_questions_answered"] += level_score.get('total_questions', 0)
    final_scores = []
    for path_id, scores in path_scores.items():
        total = scores['total_questions_answered']
        correct = scores['correct_answers']
        score_percent = (correct / total * 100) if total > 0 else 0
        scores['score_percent'] = round(score_percent, 2)
        final_scores.append(scores)
    return final_scores


def get_path_completion_status(user_wallet, path_id):
    logger.info(f"DB: Getting completion status for path {path_id} for wallet {user_wallet}")
    user_res = get_user_by_wallet(user_wallet)
    if not user_res or not user_res.data:
        return False
    user_id = user_res.data['id']
    try:
        progress_res = supabase_client.table('user_progress').select('is_complete').eq('user_id', user_id).eq('path_id',
                                                                                                              path_id).maybe_single().execute()  # Use maybe_single
        if progress_res and progress_res.data:
            return progress_res.data.get('is_complete', False)
    except Exception as e:
        logger.error(f"DB: Error getting path completion status for user {user_id}, path {path_id}. Error: {e}",
                     exc_info=True)
    return False


def get_level_completion_status(user_wallet, path_id, level_index):
    logger.info(f"DB: Getting level completion for wallet {user_wallet}, path {path_id}, level {level_index}.")
    user_res = get_user_by_wallet(user_wallet)
    if not user_res or not user_res.data:
        return False
    user_id = user_res.data['id']

    res = supabase_client.rpc('get_single_level_completion', {
        'p_user_id': user_id,
        'p_path_id': path_id,
        'p_level_number': level_index
    }).execute()
    return res.data if res.data is not None else False


def save_user_nft(user_wallet, path_id, token_id, contract_address, metadata_url, image_gateway_url):
    logger.info(f"DB: Saving NFT record for wallet {user_wallet}, path {path_id}, token {token_id}")
    user_res = get_user_by_wallet(user_wallet)
    if not user_res or not user_res.data:
        raise ValueError(f"User not found for wallet {user_wallet}")
    user_id = user_res.data['id']

    return supabase_client.table('user_nfts').insert({
        'user_id': user_id,
        'path_id': path_id,
        'token_id': token_id,
        'nft_contract_address': contract_address,
        'metadata_url': metadata_url,
        'image_gateway_url': image_gateway_url
    }).execute()


def get_nfts_by_user(wallet_address):
    logger.info(f"DB: Fetching all NFTs for wallet {wallet_address}")
    user_res = get_user_by_wallet_full(wallet_address)  # Use full user details
    if not user_res or not user_res.data:
        return []
    user_id = user_res.data['id']

    response = supabase_client.table('user_nfts').select(
        'path_id, token_id, nft_contract_address, metadata_url, image_gateway_url, minted_at, learning_paths(title)'
    ).eq('user_id', user_id).order('minted_at', desc=True).execute()

    return response.data if response.data else []


def get_nft_by_user_and_path(user_wallet, path_id):
    logger.info(f"DB: Checking for existing NFT for wallet {user_wallet} and path {path_id}")
    user_res = get_user_by_wallet(user_wallet)
    if not user_res or not user_res.data:
        logger.warning(f"DB: User not found for wallet {user_wallet} during NFT check.")
        return None
    user_id = user_res.data['id']
    try:
        response = supabase_client.table('user_nfts').select('id, token_id, metadata_url, image_gateway_url').eq(
            'user_id', user_id).eq(  # Added image_gateway_url
            'path_id', path_id).maybe_single().execute()  # Use maybe_single
        if response and response.data:
            logger.info(f"DB: Found existing NFT for user {user_id} and path {path_id}.")
            return response.data
        else:
            return None
    except Exception as e:
        logger.error(f"DB: Error checking for existing NFT. Assuming it doesn't exist. Error: {e}", exc_info=True)
        return None


def get_user_and_path_for_nft(user_wallet, path_id):
    user_res = get_user_by_wallet_full(user_wallet)
    # Fetch path details directly instead of get_path_by_id which has a limited select
    path_res = supabase_client.table('learning_paths').select("title").eq('id', path_id).maybe_single().execute()

    if not user_res or not user_res.data or not path_res or not path_res.data:
        return None

    return {
        "user_name": user_res.data.get('name'),
        "path_title": path_res.data.get('title')
    }