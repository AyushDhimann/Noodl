from app import supabase_client, logger
from datetime import datetime, timezone
from . import ai_service
import time
from functools import wraps
import httpx


def supabase_retry(retries=3, delay=2):
    """A decorator to retry Supabase operations on transient network errors."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except httpx.ReadError as e:
                    logger.warning(f"DB: Network error on attempt {attempt + 1}/{retries} for {func.__name__}: {e}")
                    if attempt + 1 == retries:
                        logger.error(f"DB: All retry attempts failed for {func.__name__}.")
                        raise
                    time.sleep(delay * (attempt + 1))  # Exponential backoff

        return wrapper

    return decorator


# --- User Functions ---
@supabase_retry()
def get_user_by_wallet(wallet_address):
    return supabase_client.table('users').select('id').eq('wallet_address', wallet_address).maybe_single().execute()


@supabase_retry()
def get_user_by_wallet_full(wallet_address):
    """Fetches the full user object, not just the ID."""
    return supabase_client.table('users').select('*').eq('wallet_address', wallet_address).maybe_single().execute()


@supabase_retry()
def upsert_user(wallet_address, name, country):
    return supabase_client.table('users').upsert({
        'wallet_address': wallet_address, 'name': name, 'country': country
    }, on_conflict='wallet_address').execute()


@supabase_retry()
def get_paths_by_creator(wallet_address):
    return supabase_client.table('learning_paths').select("id, title, short_description, total_levels, created_at").eq(
        'creator_wallet', wallet_address).order('created_at', desc=True).execute()


@supabase_retry()
def get_path_count_by_creator(wallet_address):
    """Efficiently gets the count of paths created by a user."""
    response = supabase_client.table('learning_paths').select('id', count='exact').eq('creator_wallet',
                                                                                      wallet_address).execute()
    return response.count


# --- Path & Content Functions ---
@supabase_retry()
def get_all_paths():
    return supabase_client.table('learning_paths').select("id, title, short_description, total_levels").execute()


@supabase_retry()
def get_path_by_id(path_id):
    return supabase_client.table('learning_paths').select(
        "title, short_description, long_description, creator_wallet").eq('id',
                                                                         path_id).maybe_single().execute()


@supabase_retry()
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


@supabase_retry()
def create_learning_path(title, short_description, long_description, creator_wallet, total_levels, intent_type,
                         embedding):
    return supabase_client.table('learning_paths').insert({
        "title": title, "short_description": short_description, "long_description": long_description,
        "creator_wallet": creator_wallet, "total_levels": total_levels, "intent_type": intent_type,
        "title_embedding": embedding
    }).execute()


@supabase_retry()
def delete_path_by_id(path_id):
    """Deletes a path and its cascaded content. Use with care."""
    logger.warning(f"DB: Deleting path with ID: {path_id} and all its content.")
    return supabase_client.table('learning_paths').delete().eq('id', path_id).execute()


@supabase_retry()
def update_path_hash(path_id, content_hash):
    return supabase_client.table('learning_paths').update({'content_hash': content_hash}).eq('id', path_id).execute()


@supabase_retry()
def create_level(path_id, level_number, level_title):
    """
    Creates a new level for a path. This is now idempotent.
    If a level with the same path_id and level_number already exists, it does nothing.
    """
    return supabase_client.table('levels').upsert({
        "path_id": path_id, "level_number": level_number, "level_title": level_title
    }, on_conflict='path_id,level_number', ignore_duplicates=True).execute()


@supabase_retry()
def get_level(path_id, level_num):
    return supabase_client.table('levels').select('id, level_title').eq('path_id', path_id).eq('level_number',
                                                                                               level_num).single().execute()


@supabase_retry()
def create_content_items(items_to_insert):
    """
    Creates new content items for a level. This is now idempotent.
    If an item with the same level_id and item_index already exists, it does nothing.
    """
    return supabase_client.table('content_items').upsert(
        items_to_insert,
        on_conflict='level_id,item_index',
        ignore_duplicates=True
    ).execute()


@supabase_retry()
def get_content_items_for_level(level_id):
    return supabase_client.table('content_items').select('id, item_index, item_type, content').eq('level_id',
                                                                                                  level_id).order(
        'item_index').execute()


@supabase_retry()
def find_similar_paths(embedding, threshold, count):
    """Calls the match_similar_paths RPC in Supabase."""
    logger.info(f"DB: Finding similar paths with threshold {threshold}")
    return supabase_client.rpc('match_similar_paths', {
        'query_embedding': embedding,
        'match_threshold': threshold,
        'match_count': count
    }).execute()


@supabase_retry()
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
@supabase_retry()
def create_task_log(task_id):
    """Creates a new entry for a task in the logs table."""
    return supabase_client.table('task_progress_logs').insert({
        'task_id': task_id,
        'logs': []
    }).execute()


@supabase_retry()
def update_task_log(task_id, new_log_entry):
    """Appends a new log entry to a task's log array in the database."""
    return supabase_client.rpc('append_to_log', {
        'task_uuid': task_id,
        'new_log': new_log_entry
    }).execute()


@supabase_retry()
def get_task_log(task_id):
    """Retrieves the logs for a specific task."""
    return supabase_client.table('task_progress_logs').select('logs').eq('task_id', task_id).single().execute()


# --- Progress & Scoring Functions ---
@supabase_retry()
def get_progress(user_id, path_id):
    return supabase_client.table('user_progress').select('*, levels(level_number)').eq('user_id', user_id).eq('path_id',
                                                                                                              path_id).maybe_single().execute()


@supabase_retry()
def create_progress(user_id, path_id):
    first_level_res = supabase_client.table('levels').select('id').eq('path_id', path_id).eq('level_number',
                                                                                             1).single().execute()
    if not first_level_res.data:
        raise ValueError(f"Path ID {path_id} has no level 1.")

    insert_res = supabase_client.table('user_progress').insert({
        'user_id': user_id, 'path_id': path_id, 'current_level_id': first_level_res.data['id'],
        'current_item_index': -1, 'status': 'in_progress', 'started_at': datetime.now(timezone.utc).isoformat()
    }).execute()

    # The insert operation returns a list with the new record.
    new_progress_id = insert_res.data[0]['id']

    # Fetch the newly created progress record along with the level number.
    return supabase_client.table('user_progress').select('*, levels(level_number)').eq('id',
                                                                                       new_progress_id).single().execute()


@supabase_retry()
def get_quiz_item(item_id):
    return supabase_client.table('content_items').select('content, item_index').eq('id', item_id).single().execute()


@supabase_retry()
def log_quiz_attempt(progress_id, item_id, answer_index, is_correct):
    return supabase_client.table('quiz_attempts').insert({
        'progress_id': progress_id, 'content_item_id': item_id,
        'user_answer_index': answer_index, 'is_correct': is_correct
    }).execute()


@supabase_retry()
def update_user_progress_item(progress_id, item_index):
    return supabase_client.table('user_progress').update({'current_item_index': item_index}).eq('id',
                                                                                                progress_id).execute()


@supabase_retry()
def get_user_scores(user_id):
    progress_records = supabase_client.table('user_progress').select('id, path_id, status, learning_paths(title)').eq(
        'user_id', user_id).execute()
    scores = []
    for record in progress_records.data:
        attempts = supabase_client.table('quiz_attempts').select('is_correct', count='exact').eq('progress_id',
                                                                                                 record['id']).execute()
        total_attempts = attempts.count
        correct_attempts = supabase_client.table('quiz_attempts').select('is_correct', count='exact').eq('progress_id',
                                                                                                         record[
                                                                                                             'id']).eq(
            'is_correct', True).execute().count
        score = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
        scores.append({
            "path_id": record['path_id'], "path_title": record['learning_paths']['title'],
            "status": record['status'], "score_percent": round(score, 2),
            "correct_answers": correct_attempts, "total_questions_answered": total_attempts
        })
    return scores