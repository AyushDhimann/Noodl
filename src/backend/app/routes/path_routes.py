import json
import hashlib
import uuid
import threading
from flask import Blueprint, request, jsonify
from app import logger
from app.services import ai_service, supabase_service, blockchain_service
from app.config import config

bp = Blueprint('path_routes', __name__, url_prefix='/paths')

# A simple in-memory dictionary to store task progress.
# In a real production app, you might use Redis or a database table for this.
PROGRESS_LOGS = {}


def update_progress(task_id, status, data=None):
    """Updates the progress log for a given task."""
    if task_id not in PROGRESS_LOGS:
        PROGRESS_LOGS[task_id] = []

    log_entry = {"status": status}
    if data:
        log_entry["data"] = data

    PROGRESS_LOGS[task_id].append(log_entry)
    logger.info(f"TASK [{task_id}]: {status}")


def generation_worker(task_id, topic, creator_wallet):
    """The actual long-running task that generates the path."""
    try:
        update_progress(task_id, "Step 1: Generating curriculum...")
        curriculum_titles = ai_service.generate_curriculum(topic)
        total_levels = len(curriculum_titles)
        update_progress(task_id, f"Curriculum generated with {total_levels} levels.")

        update_progress(task_id, "Step 2: Saving path metadata to Supabase...")
        path_res = supabase_service.create_learning_path(
            topic, f"A user-generated learning path about {topic}.",
            creator_wallet, total_levels,
            ai_service.get_embedding(topic) if config.SIMILARITY_THRESHOLD > 0 else None
        )
        new_path_id = path_res.data[0]['id']

        update_progress(task_id, f"Step 3: Generating and saving content for {total_levels} levels...")
        all_content_for_hash = []
        for i, level_title in enumerate(curriculum_titles):
            level_number = i + 1
            update_progress(task_id, f"  - Generating content for level {level_number}: '{level_title}'...")
            level_res = supabase_service.create_level(new_path_id, level_number, level_title)
            new_level_id = level_res.data[0]['id']

            interleaved_items = ai_service.generate_interleaved_level_content(topic, level_title)
            all_content_for_hash.append({"level": level_title, "items": interleaved_items})

            items_to_insert = [
                {"level_id": new_level_id, "item_index": j, "item_type": item['type'], "content": item['content']} for
                j, item in enumerate(interleaved_items)]
            supabase_service.create_content_items(items_to_insert)
            update_progress(task_id, f"  - Saved {len(items_to_insert)} content items for level {level_number}.")

        if config.FEATURE_FLAG_ENABLE_BLOCKCHAIN_REGISTRATION:
            update_progress(task_id, "Step 4: Registering content hash on the blockchain...")
            full_content_string = json.dumps(all_content_for_hash, sort_keys=True)
            content_hash = "0x" + hashlib.sha256(full_content_string.encode()).hexdigest()
            receipt = blockchain_service.register_path_on_chain(new_path_id, content_hash, task_id, update_progress)
            supabase_service.update_path_hash(new_path_id, content_hash)
            update_progress(task_id, f"Path {new_path_id} registered on-chain.",
                            {'txHash': receipt.transactionHash.hex()})

        update_progress(task_id, "SUCCESS: Path generation complete!", {"path_id": new_path_id})

    except Exception as e:
        logger.error(f"TASK [{task_id}] FAILED: {e}", exc_info=True)
        update_progress(task_id, f"ERROR: Path generation failed: {e}")


@bp.route('/generate', methods=['POST'])
def generate_new_path_route():
    req_data = request.get_json()
    topic = req_data.get('topic')
    creator_wallet = req_data.get('creator_wallet')

    task_id = str(uuid.uuid4())
    PROGRESS_LOGS[task_id] = []

    thread = threading.Thread(target=generation_worker, args=(task_id, topic, creator_wallet))
    thread.start()

    return jsonify({"message": "Path generation started.", "task_id": task_id}), 202


@bp.route('/generate/status/<task_id>', methods=['GET'])
def get_generation_status(task_id):
    progress = PROGRESS_LOGS.get(task_id)
    if progress is None:
        return jsonify({"error": "Task not found."}), 404

    return jsonify({"progress": progress})


@bp.route('', methods=['GET'])
def get_all_paths_route():
    logger.info("ROUTE: /paths GET")
    try:
        paths = supabase_service.get_all_paths()
        return jsonify(paths.data)
    except Exception as e:
        logger.error(f"ROUTE: /paths GET failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch paths."}), 500


@bp.route('/<int:path_id>/levels/<int:level_num>', methods=['GET'])
def get_level_content_route(path_id, level_num):
    logger.info(f"ROUTE: /paths/.../levels GET for path {path_id}, level {level_num}")
    try:
        level = supabase_service.get_level(path_id, level_num)
        if not level.data:
            return jsonify({"error": "Level not found"}), 404

        items = supabase_service.get_content_items_for_level(level.data['id'])
        return jsonify({"level_title": level.data['level_title'], "items": items.data})
    except Exception as e:
        logger.error(f"ROUTE: /paths/.../levels GET failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch level content."}), 500