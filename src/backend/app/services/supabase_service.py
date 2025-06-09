from app import supabase_client, logger
from datetime import datetime, timezone


# --- User Functions ---
def get_user_by_wallet(wallet_address):
    return supabase_client.table('users').select('id').eq('wallet_address', wallet_address).maybe_single().execute()


def upsert_user(wallet_address, name, country):
    return supabase_client.table('users').upsert({
        'wallet_address': wallet_address, 'name': name, 'country': country
    }, on_conflict='wallet_address').execute()


def get_paths_by_creator(wallet_address):
    return supabase_client.table('learning_paths').select("id, title, description, total_levels, created_at").eq(
        'creator_wallet', wallet_address).order('created_at', desc=True).execute()


def get_path_count_by_creator(wallet_address):
    """Efficiently gets the count of paths created by a user."""
    response = supabase_client.table('learning_paths').select('id', count='exact').eq('creator_wallet', wallet_address).execute()
    return response.count


# --- Path & Content Functions ---
def get_all_paths():
    return supabase_client.table('learning_paths').select("id, title, description, total_levels").execute()


def get_path_by_id(path_id):
    return supabase_client.table('learning_paths').select("title, description, creator_wallet").eq('id',
                                                                                   path_id).maybe_single().execute()


def create_learning_path(title, description, creator_wallet, total_levels, embedding):
    return supabase_client.table('learning_paths').insert({
        "title": title, "description": description, "creator_wallet": creator_wallet,
        "total_levels": total_levels, "title_embedding": embedding
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


# --- Task Progress Log Functions (NEW) ---
def create_task_log(task_id):
    """Creates a new entry for a task in the logs table."""
    return supabase_client.table('task_progress_logs').insert({
        'task_id': task_id,
        'logs': []
    }).execute()


def update_task_log(task_id, new_log_entry):
    """Appends a new log entry to a task's log array in the database."""
    # This uses the 'rpc' method to call a custom PostgreSQL function
    # that appends to the JSONB array. This is more robust than fetching and updating.
    return supabase_client.rpc('append_to_log', {
        'task_uuid': task_id,
        'new_log': new_log_entry
    }).execute()


def get_task_log(task_id):
    """Retrieves the logs for a specific task."""
    return supabase_client.table('task_progress_logs').select('logs').eq('task_id', task_id).single().execute()


# --- Progress & Scoring Functions ---
def get_progress(user_id, path_id):
    return supabase_client.table('user_progress').select('*, levels(level_number)').eq('user_id', user_id).eq('path_id',
                                                                                                              path_id).maybe_single().execute()


def create_progress(user_id, path_id):
    first_level_res = supabase_client.table('levels').select('id').eq('path_id', path_id).eq('level_number',
                                                                                             1).single().execute()
    if not first_level_res.data:
        raise ValueError(f"Path ID {path_id} has no level 1.")

    insert_res = supabase_client.table('user_progress').insert({
        'user_id': user_id, 'path_id': path_id, 'current_level_id': first_level_res.data['id'],
        'current_item_index': -1, 'status': 'in_progress', 'started_at': datetime.now(timezone.utc).isoformat()
    }).execute()

    new_progress_id = insert_res.data[0]['id']
    return supabase_client.table('user_progress').select('*, levels(level_number)').eq('id',
                                                                                       new_progress_id).single().execute()


def get_quiz_item(item_id):
    return supabase_client.table('content_items').select('content, item_index').eq('id', item_id).single().execute()


def log_quiz_attempt(progress_id, item_id, answer_index, is_correct):
    return supabase_client.table('quiz_attempts').insert({
        'progress_id': progress_id, 'content_item_id': item_id,
        'user_answer_index': answer_index, 'is_correct': is_correct
    }).execute()


def update_user_progress_item(progress_id, item_index):
    return supabase_client.table('user_progress').update({'current_item_index': item_index}).eq('id',
                                                                                                progress_id).execute()


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