import json
import hashlib
import uuid
import threading
from flask import Blueprint, request, jsonify
from app import logger
from app.services import ai_service, supabase_service, blockchain_service
from app.config import config

bp = Blueprint('path_routes', __name__, url_prefix='/paths')


def update_progress(task_id, status, data=None):
    """Updates the progress log for a given task in the database."""
    log_entry = {"status": status}
    if data:
        log_entry["data"] = data
    supabase_service.update_task_log(task_id, log_entry)
    logger.info(f"TASK [{task_id}]: {status}")


def generation_worker(task_id, new_title, creator_wallet, country=None):
    """The actual long-running task that generates the path sequentially."""
    new_path_id = None
    try:
        update_progress(task_id, "✅ Designing your curriculum...")
        curriculum_titles = ai_service.generate_curriculum(new_title, country)
        total_levels = len(curriculum_titles)
        update_progress(task_id, f"Curriculum designed with {total_levels} lessons.")

        update_progress(task_id, "✍️ Writing a course description...")
        description = ai_service.generate_path_description(new_title)
        update_progress(task_id, "Description generated.")

        update_progress(task_id, "📝 Saving path outline...")
        path_res = supabase_service.create_learning_path(
            new_title, description, creator_wallet, total_levels,
            ai_service.get_embedding(new_title) if config.FEATURE_FLAG_ENABLE_DUPLICATE_CHECK else None
        )
        new_path_id = path_res.data[0]['id']

        update_progress(task_id, f"🧠 Generating content for {total_levels} lessons...")
        all_content_for_hash = []
        for i, level_title in enumerate(curriculum_titles):
            level_number = i + 1
            update_progress(task_id, f"  - Lesson {level_number}: '{level_title}'")
            level_res = supabase_service.create_level(new_path_id, level_number, level_title)
            new_level_id = level_res.data[0]['id']

            interleaved_items = ai_service.generate_interleaved_level_content(new_title, level_title)
            all_content_for_hash.append({"level": level_title, "items": interleaved_items})

            items_to_insert = [
                {"level_id": new_level_id, "item_index": j, "item_type": item['type'], "content": item['content']} for
                j, item in enumerate(interleaved_items)]
            supabase_service.create_content_items(items_to_insert)

        update_progress(task_id, "✅ All lesson content has been generated and saved.")

        if config.FEATURE_FLAG_ENABLE_BLOCKCHAIN_REGISTRATION:
            update_progress(task_id, "🔗 Registering path on the blockchain...")
            full_content_string = json.dumps(all_content_for_hash, sort_keys=True)
            content_hash = "0x" + hashlib.sha256(full_content_string.encode()).hexdigest()
            receipt = blockchain_service.register_path_on_chain(new_path_id, content_hash, task_id, update_progress)
            supabase_service.update_path_hash(new_path_id, content_hash)

            tx_hash = receipt.transactionHash.hex()
            explorer_url = f"{config.BLOCK_EXPLORER_URL.rstrip('/')}/tx/0x{tx_hash}" if config.BLOCK_EXPLORER_URL else None

            update_progress(task_id, f"Path {new_path_id} registered on-chain.",
                            {'txHash': tx_hash, 'explorer_url': explorer_url})

        final_data = {"path_id": new_path_id}
        if config.FEATURE_FLAG_ENABLE_BLOCKCHAIN_REGISTRATION and 'explorer_url' in locals() and explorer_url:
            final_data['explorer_url'] = explorer_url
        update_progress(task_id, "🎉 SUCCESS: Path generation complete!", final_data)

    except Exception as e:
        logger.error(f"TASK [{task_id}] FAILED: {e}", exc_info=True)
        update_progress(task_id, f"❌ ERROR: Path generation failed. Please check server logs for details.")
        if new_path_id:
            logger.warning(
                f"TASK [{task_id}]: An error occurred. Cleaning up partially generated path ID: {new_path_id}")
            update_progress(task_id, f"🧹 An error occurred. Cleaning up incomplete path...")
            try:
                supabase_service.delete_path_by_id(new_path_id)
                logger.info(f"TASK [{task_id}]: Cleanup successful for path ID: {new_path_id}")
                update_progress(task_id, f"Cleanup complete.")
            except Exception as cleanup_e:
                logger.error(f"TASK [{task_id}]: CRITICAL! Cleanup FAILED for path ID {new_path_id}: {cleanup_e}")
                update_progress(task_id, f"CRITICAL! Path cleanup failed. Please notify an admin.")


@bp.route('/generate', methods=['POST'])
def generate_new_path_route():
    req_data = request.get_json()
    topic = req_data.get('topic')
    creator_wallet = req_data.get('creator_wallet')

    if not topic or not creator_wallet:
        return jsonify({"error": "topic and creator_wallet are required"}), 400

    try:
        # Get user's country for context
        user_res = supabase_service.get_user_by_wallet_full(creator_wallet)
        country = user_res.data.get('country') if user_res.data else None

        logger.info(f"AI REPHRASE: Improving topic '{topic}'")
        new_title = ai_service.rephrase_topic_with_emoji(topic)
        logger.info(f"AI REPHRASE: New title is '{new_title}'")

        if config.FEATURE_FLAG_ENABLE_DUPLICATE_CHECK:
            logger.info(f"DUPE CHECK: Checking for topics similar to '{new_title}'")
            topic_embedding = ai_service.get_embedding(new_title)
            similar_paths_res = supabase_service.find_similar_paths(
                embedding=topic_embedding,
                threshold=config.SIMILARITY_THRESHOLD,
                count=1
            )
            if similar_paths_res.data:
                logger.warning(f"DUPE CHECK: Found similar path for '{new_title}'.")
                return jsonify({
                    "error": "A very similar learning path already exists.",
                    "similar_path": similar_paths_res.data[0]
                }), 409

        task_id = str(uuid.uuid4())
        supabase_service.create_task_log(task_id)

        thread = threading.Thread(target=generation_worker, args=(task_id, new_title, creator_wallet, country))
        thread.start()

        return jsonify({"message": "Path generation started.", "task_id": task_id}), 202

    except Exception as e:
        logger.error(f"GENERATE ROUTE: Failed during pre-generation step: {e}", exc_info=True)
        return jsonify({"error": "Failed to start generation process. Check server logs."}), 500


@bp.route('/generate/status/<task_id>', methods=['GET'])
def get_generation_status(task_id):
    try:
        log_res = supabase_service.get_task_log(task_id)
        if not log_res.data:
            return jsonify({"error": "Task not found."}), 404
        return jsonify({"progress": log_res.data.get('logs', [])})
    except Exception as e:
        logger.error(f"STATUS ROUTE: Failed for task {task_id}: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve task status."}), 500


@bp.route('', methods=['GET'])
def get_all_paths_route():
    logger.info("ROUTE: /paths GET")
    try:
        paths = supabase_service.get_all_paths()
        return jsonify(paths.data)
    except Exception as e:
        logger.error(f"ROUTE: /paths GET failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch paths."}), 500


@bp.route('/<int:path_id>', methods=['GET'])
def get_path_details_route(path_id):
    logger.info(f"ROUTE: /paths/<id> GET for path {path_id}")
    try:
        path_details_res = supabase_service.get_full_path_details(path_id)
        if not path_details_res.data:
            return jsonify({"error": "Path not found"}), 404

        path_data = path_details_res.data

        # Calculate total slides and questions
        total_slides = 0
        total_questions = 0
        if 'levels' in path_data and path_data['levels']:
            for level in path_data['levels']:
                if 'content_items' in level and level['content_items']:
                    for item in level['content_items']:
                        if item['item_type'] == 'slide':
                            total_slides += 1
                        elif item['item_type'] == 'quiz':
                            total_questions += 1

        # Add counts to the response
        path_data['total_slides'] = total_slides
        path_data['total_questions'] = total_questions

        return jsonify(path_data)
    except Exception as e:
        logger.error(f"ROUTE: /paths/<id> GET failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch path details."}), 500


@bp.route('/<int:path_id>', methods=['DELETE'])
def delete_path_route(path_id):
    user_wallet = request.get_json().get('user_wallet')
    if not user_wallet:
        return jsonify({"error": "user_wallet is required in the request body"}), 400

    try:
        path_res = supabase_service.get_path_by_id(path_id)
        if not path_res.data:
            return jsonify({"error": "Path not found"}), 404

        if path_res.data['creator_wallet'].lower() != user_wallet.lower():
            return jsonify({"error": "Forbidden. You are not the creator of this path."}), 403

        supabase_service.delete_path_by_id(path_id)
        return jsonify({"message": f"Path {path_id} deleted successfully."}), 200

    except Exception as e:
        logger.error(f"ROUTE: /paths/DELETE failed for path {path_id}: {e}", exc_info=True)
        return jsonify({"error": "Failed to delete path."}), 500


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