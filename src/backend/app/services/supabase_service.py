from app import supabase_client, logger
from datetime import datetime, timezone
from . import ai_service


# --- User Functions ---
def get_user_by_wallet(wallet_address):
    return supabase_client.table('users').select('id').eq('wallet_address', wallet_address.lower()).maybe_single().execute()


def get_user_by_wallet_full(wallet_address):
    """Fetches the full user object, not just the ID."""
    return supabase_client.table('users').select('*').eq('wallet_address', wallet_address.lower()).maybe_single().execute()


def upsert_user(wallet_address, name, country):
    return supabase_client.table('users').upsert({
        'wallet_address': wallet_address.lower(), 'name': name, 'country': country
    }, on_conflict='wallet_address').execute()


def get_paths_by_creator(wallet_address):
    return supabase_client.table('learning_paths').select("id, title, short_description, total_levels, created_at").eq(
        'creator_wallet', wallet_address.lower()).order('created_at', desc=True).execute()


def get_enrolled_paths_by_user(user_id):
    """Fetches all paths a user has started (i.e., has a progress record for)."""
    logger.info(f"DB: Fetching all enrolled paths for user_id: {user_id}")
    # The join syntax is `foreign_table(columns)`.
    # The select on user_progress will return a list of objects, each containing a learning_paths object.
    return supabase_client.table('user_progress').select(
        'learning_paths(id, title, short_description, total_levels, created_at)'
    ).eq('user_id', user_id).order(
        'created_at', foreign_table='learning_paths', desc=True
    ).execute()


def get_path_count_by_creator(wallet_address):
    """Efficiently gets the count of paths created by a user."""
    response = supabase_client.table('learning_paths').select('id', count='exact').eq('creator_wallet',
                                                                                       wallet_address.lower()).execute()
    return response.count


# --- Path & Content Functions ---
def get_all_paths():
    return supabase_client.table('learning_paths').select("id, title, short_description, total_levels").execute()


def get_path_by_id(path_id):
    return supabase_client.table('learning_paths').select(
        "title, short_description, long_description, creator_wallet").eq('id',
                                                                         path_id).maybe_single().execute()


def get_full_path_details(path_id):
    """
    Fetches a single path and all its related levels and content items in one query.
    """
    return supabase_client.table('learning_paths').select(
        '*, levels(*, content_items(*))'
    ).eq('id', path_id).order(
        'level_number', foreign_table='levels'
    ).order(
        'item_index', foreign_table='levels.content_items'
    ).maybe_single().execute()


def get_full_path_details_for_user(path_id, user_wallet):
    """
    Fetches full path details and enriches it with user-specific completion and minting status.
    """
    # 1. Get the generic path details
    path_res = get_full_path_details(path_id)
    if not path_res or not path_res.data:
        return None
    path_data = path_res.data

    # 2. Get user ID
    user_res = get_user_by_wallet(user_wallet)
    user_id = user_res.data['id'] if user_res and user_res.data else None

    # 3. Get user-specific completion data for all levels in this path
    if user_id:
        progress_res = supabase_client.rpc('get_level_completion_for_path', {
            'p_user_id': user_id,
            'p_path_id': path_id
        }).execute()
        level_completion_map = {item['level_number']: item['is_complete'] for item in
                                progress_res.data} if progress_res.data else {}
    else:
        level_completion_map = {}

    # 4. Inject the 'is_complete' flag into each level
    if 'levels' in path_data and path_data['levels']:
        for level in path_data['levels']:
            level_num = level.get('level_number')
            level['is_complete'] = level_completion_map.get(level_num, False)

    # 5. Add overall path completion and NFT minted status
    path_data['is_complete'] = get_path_completion_status(user_wallet, path_id)
    if user_id:
        nft_res = supabase_client.table('user_nfts').select('id', count='exact').eq('user_id', user_id).eq('path_id', path_id).execute()
        path_data['is_minted'] = nft_res.count > 0
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
    """Deletes a path and its cascaded content. Use with care."""
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
    """Calls the match_similar_paths RPC in Supabase."""
    logger.info(f"DB: Finding similar paths with threshold {threshold}")
    return supabase_client.rpc('match_similar_paths', {
        'query_embedding': embedding,
        'match_threshold': threshold,
        'match_count': count
    }).execute()


def hybrid_search_paths(query_text):
    """
    Performs a hybrid search using both semantic vector search and keyword text search.
    """
    logger.info(f"DB: Hybrid search for query: '{query_text}'")

    # 1. Semantic Search (Vector Search)
    query_embedding = ai_service.get_embedding(query_text)
    semantic_res = supabase_client.rpc('search_paths_semantic', {
        'query_embedding': query_embedding,
        'match_threshold': 0.6,
        'match_count': 10
    }).execute()

    # 2. Keyword Search (Full-Text Search via RPC)
    search_term = f"%{query_text}%"
    keyword_res = supabase_client.rpc('search_paths_keyword', {
        'search_term': search_term,
        'match_count': 10
    }).execute()

    # 3. Format and Interleave Results
    semantic_results = []
    if semantic_res.data:
        for item in semantic_res.data:
            semantic_results.append({
                "id": item['id'],
                "match_type": "semantic",
                "result_in": "title",
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

    # Interleave results: Keyword, Semantic, Keyword, Semantic...
    final_results = []
    seen_ids = set()
    len_k = len(keyword_results)
    len_s = len(semantic_results)
    max_len = max(len_k, len_s)

    for i in range(max_len):
        # Add keyword result if available and not seen
        if i < len_k and keyword_results[i]['id'] not in seen_ids:
            final_results.append(keyword_results[i])
            seen_ids.add(keyword_results[i]['id'])

        # Add semantic result if available and not seen
        if i < len_s and semantic_results[i]['id'] not in seen_ids:
            final_results.append(semantic_results[i])
            seen_ids.add(semantic_results[i]['id'])

    return final_results


# --- Task Progress Log Functions ---
def create_task_log(task_id):
    """Creates a new entry for a task in the logs table."""
    return supabase_client.table('task_progress_logs').insert({
        'task_id': task_id,
        'logs': []
    }).execute()


def update_task_log(task_id, new_log_entry):
    """Appends a new log entry to a task's log array in the database."""
    return supabase_client.rpc('append_to_log', {
        'task_uuid': task_id,
        'new_log': new_log_entry
    }).execute()


def get_task_log(task_id):
    """Retrieves the logs for a specific task."""
    return supabase_client.table('task_progress_logs').select('logs').eq('task_id', task_id).single().execute()


# --- Progress & Scoring Functions ---
def _create_progress_record(user_id, path_id):
    """
    Internal function to create a new user_progress record.
    This is called automatically when a user submits their first level progress for a path.
    """
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
    """
    Handles starting a path if it doesn't exist, updating the score for a specific level,
    and automatically marking the entire path as complete if all levels are done.
    """
    # 1. Get User ID
    user_res = get_user_by_wallet(user_wallet)
    if not user_res or not user_res.data:
        raise ValueError(f"User not found for wallet {user_wallet}")
    user_id = user_res.data['id']

    # 2. Get or Create Progress Record
    progress_res = supabase_client.table('user_progress').select('id').eq('user_id', user_id).eq('path_id',
                                                                                                   path_id).maybe_single().execute()

    if progress_res and progress_res.data:
        progress_id = progress_res.data['id']
    else:
        logger.info(f"No progress found for user {user_id} on path {path_id}. Creating new progress record.")
        new_progress = _create_progress_record(user_id, path_id)
        progress_id = new_progress['id']

    # 3. Upsert Level Score and mark as complete
    logger.info(
        f"DB: Upserting level progress for progress_id {progress_id}, level {level_index} with score {correct_answers}/{total_questions} and marking as complete.")
    supabase_client.table('level_progress').upsert({
        'progress_id': progress_id,
        'level_number': level_index,
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'is_complete': True
    }, on_conflict='progress_id, level_number').execute()

    # 4. Check if this completes the whole path
    logger.info(f"DB: Checking if path is now complete for progress_id {progress_id}")
    supabase_client.rpc('check_and_complete_path', {'p_progress_id': progress_id}).execute()


def get_level_score(user_wallet, path_id, level_index):
    """
    Retrieves the score for a specific level of a path for a user.
    """
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

    logger.info(f"DB: Querying level_progress for progress_id {progress_id} and level_number {level_index}.")
    score_res = supabase_client.table('level_progress').select('correct_answers, total_questions').eq('progress_id',
                                                                                                        progress_id).eq(
        'level_number', level_index).maybe_single().execute()

    return score_res.data if score_res else None


def get_user_scores(user_id):
    """
    Aggregates scores for a user across all their learning paths they have started.
    """
    # FIX: Query starts from user_progress to include all started paths, even those
    # without quiz scores yet.
    res = supabase_client.table('user_progress').select(
        'path_id, learning_paths(title), level_progress(correct_answers, total_questions)'
    ).eq('user_id', user_id).execute()

    if not res.data:
        return []

    path_scores = {}
    # The structure of res.data will be a list of user_progress records.
    for progress_record in res.data:
        path_id = progress_record.get('path_id')
        if not path_id:
            continue

        path_info = progress_record.get('learning_paths') or {}
        path_title = path_info.get('title', f'Deleted Path ({path_id})')

        # Initialize the dict for this path
        if path_id not in path_scores:
            path_scores[path_id] = {
                "path_id": path_id,
                "path_title": path_title,
                "correct_answers": 0,
                "total_questions_answered": 0
            }

        # Aggregate scores from nested level_progress records for this path
        level_progress_list = progress_record.get('level_progress', [])
        for level_score in level_progress_list:
            path_scores[path_id]["correct_answers"] += level_score.get('correct_answers', 0)
            path_scores[path_id]["total_questions_answered"] += level_score.get('total_questions', 0)

    # The rest of the function for calculating percentage is the same.
    final_scores = []
    for path_id, scores in path_scores.items():
        total = scores['total_questions_answered']
        correct = scores['correct_answers']
        score_percent = (correct / total * 100) if total > 0 else 0
        scores['score_percent'] = round(score_percent, 2)
        final_scores.append(scores)

    return final_scores


def set_path_completed(user_wallet, path_id):
    """Sets a user's progress for a path to complete."""
    logger.info(f"DB: Marking path {path_id} as complete for wallet {user_wallet}")
    user_res = get_user_by_wallet(user_wallet)
    if not user_res or not user_res.data:
        raise ValueError(f"User not found for wallet {user_wallet}")
    user_id = user_res.data['id']

    progress_res = supabase_client.table('user_progress').select('id').eq('user_id', user_id).eq('path_id',
                                                                                                   path_id).maybe_single().execute()
    if not progress_res or not progress_res.data:
        logger.warning(
            f"DB: No progress record found for user {user_id} on path {path_id}. Creating one to mark as complete.")
        _create_progress_record(user_id, path_id)

    return supabase_client.table('user_progress').update({
        'is_complete': True,
        'completed_at': datetime.now(timezone.utc).isoformat()
    }).eq('user_id', user_id).eq('path_id', path_id).execute()


def get_user_progress_for_paths(user_wallet, path_ids: list):
    """Fetches completion status for a list of paths for a specific user."""
    logger.info(f"DB: Getting progress for {len(path_ids)} paths for wallet {user_wallet}")
    user_res = get_user_by_wallet(user_wallet)
    if not user_res or not user_res.data:
        return {}
    user_id = user_res.data['id']

    progress_res = supabase_client.table('user_progress').select('path_id, is_complete').eq('user_id', user_id).in_(
        'path_id', path_ids).execute()

    if not progress_res.data:
        return {}

    return {item['path_id']: item['is_complete'] for item in progress_res.data}


def get_path_completion_status(user_wallet, path_id):
    """Fetches completion status for a single path for a specific user."""
    logger.info(f"DB: Getting completion status for path {path_id} for wallet {user_wallet}")
    user_res = get_user_by_wallet(user_wallet)
    if not user_res or not user_res.data:
        return False
    user_id = user_res.data['id']

    progress_res = supabase_client.table('user_progress').select('is_complete').eq('user_id', user_id).eq('path_id',
                                                                                                          path_id).maybe_single().execute()

    if progress_res and progress_res.data:
        return progress_res.data.get('is_complete', False)

    return False


def get_level_completion_status(user_wallet, path_id, level_index):
    """Checks if a specific level is marked as complete for a user."""
    logger.info(f"DB: Getting level completion for wallet {user_wallet}, path {path_id}, level {level_index}.")
    user_res = get_user_by_wallet(user_wallet)
    if not user_res or not user_res.data:
        return False  # User not found, so not complete
    user_id = user_res.data['id']

    res = supabase_client.rpc('get_single_level_completion', {
        'p_user_id': user_id,
        'p_path_id': path_id,
        'p_level_number': level_index
    }).execute()

    return res.data


# --- NFT Functions ---
def save_user_nft(user_wallet, path_id, token_id, contract_address, metadata_url, image_gateway_url):
    """Saves a record of a minted NFT for a user."""
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
    """Retrieves all NFTs owned by a specific user."""
    logger.info(f"DB: Fetching all NFTs for wallet {wallet_address}")
    user_res = get_user_by_wallet_full(wallet_address)
    if not user_res or not user_res.data:
        return []
    user_id = user_res.data['id']

    response = supabase_client.table('user_nfts').select(
        'path_id, token_id, nft_contract_address, metadata_url, image_gateway_url, minted_at, learning_paths(title)'
    ).eq('user_id', user_id).order('minted_at', desc=True).execute()

    return response.data if response.data else []


def get_user_and_path_for_nft(user_wallet, path_id):
    """A helper function to get user and path info needed for NFT generation."""
    user_res = get_user_by_wallet_full(user_wallet)
    path_res = get_path_by_id(path_id)

    if not user_res or not user_res.data or not path_res or not path_res.data:
        return None

    return {
        "user_name": user_res.data.get('name'),
        "path_title": path_res.data.get('title')
    }