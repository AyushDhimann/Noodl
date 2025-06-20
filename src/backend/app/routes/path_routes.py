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


def generation_worker(task_id, original_topic, new_title, creator_wallet, country=None):
    """The actual long-running task that generates the path sequentially."""
    new_path_id = None
    try:

        update_progress(task_id, "🤔 Analyzing your request...")
        intent = ai_service.classify_topic_intent(original_topic)
        update_progress(task_id, f"Request analyzed. Intent: **{intent.upper()}**")

        update_progress(task_id, "✅ Designing your curriculum...")
        if intent == 'learn':
            curriculum_titles = ai_service.generate_learn_curriculum(new_title, country)
        else:
            curriculum_titles = ai_service.generate_help_curriculum(new_title)
        total_levels = len(curriculum_titles)
        update_progress(task_id, f"Curriculum designed with {total_levels} lessons.")

        update_progress(task_id, "✍️ Writing a course description...")
        description_data = ai_service.generate_path_description(new_title)
        update_progress(task_id, "Description generated.")

        update_progress(task_id, "📝 Saving path outline...")
        path_res = supabase_service.create_learning_path(
            title=new_title,
            short_description=description_data.get('short_description'),
            long_description=description_data.get('long_description'),
            creator_wallet=creator_wallet,
            total_levels=total_levels,
            intent_type=intent,
            embedding=ai_service.get_embedding(new_title) if config.FEATURE_FLAG_ENABLE_DUPLICATE_CHECK else None
        )

        if path_res and path_res.data and len(path_res.data) > 0 and 'id' in path_res.data[0]:
            new_path_id = path_res.data[0]['id']
            logger.info(f"TASK [{task_id}]: Path outline saved. New path ID: {new_path_id}")
        else:
            logger.error(f"TASK [{task_id}]: Failed to create learning path or retrieve its ID. Response: {path_res}")
            raise Exception("Failed to create learning path in database or retrieve its ID.")

        update_progress(task_id, f"🧠 Generating content for {total_levels} lessons...")
        all_content_for_hash = []
        for i, level_title in enumerate(curriculum_titles):
            try:
                level_number = i + 1
                is_final_level = (level_number == total_levels)
                update_progress(task_id, f"  - Lesson {level_number}: '{level_title}'")

                level_res = supabase_service.create_level(new_path_id, level_number, level_title)

                if level_res and level_res.data and len(level_res.data) > 0 and 'id' in level_res.data[0]:
                    new_level_id = level_res.data[0]['id']
                else:
                    logger.warning(
                        f"TASK [{task_id}]: Failed to create level {level_number} or retrieve its ID. Response: {level_res}. Attempting to fetch if it already exists.")
                    # This case might occur if the insert succeeded but didn't return data, or if there was a race/retry.
                    # Let's try to fetch it. If it doesn't exist, then it's a hard failure for this level.
                    existing_level_res = supabase_service.get_level(new_path_id, level_number)
                    if existing_level_res and existing_level_res.data and 'id' in existing_level_res.data:
                        new_level_id = existing_level_res.data['id']
                        logger.info(
                            f"TASK [{task_id}]: Fetched existing level ID {new_level_id} for level {level_number}.")
                    else:
                        raise Exception(
                            f"Could not create or find level {level_number} for path {new_path_id} after initial create attempt. Create response: {level_res}, Get response: {existing_level_res}")

                if intent == 'learn':
                    interleaved_items = ai_service.generate_learn_level_content(new_title, level_title, is_final_level)
                else:
                    interleaved_items = ai_service.generate_help_level_content(new_title, level_title, is_final_level)

                all_content_for_hash.append({"level": level_title, "items": interleaved_items})

                items_to_insert = [
                    {"level_id": new_level_id, "item_index": j, "item_type": item['type'], "content": item['content']}
                    for
                    j, item in enumerate(interleaved_items)]
                supabase_service.create_content_items(items_to_insert)
            except Exception as level_e:
                error_msg = f"  - ❌ Failed to generate content for level {i + 1} ('{level_title}'). Error: {level_e}"
                logger.error(f"TASK [{task_id}]: {error_msg}", exc_info=True)
                update_progress(task_id, error_msg)

                continue

        update_progress(task_id, "✅ All lesson content has been generated and saved.")

        if config.FEATURE_FLAG_ENABLE_BLOCKCHAIN_REGISTRATION:
            update_progress(task_id, "🔗 Registering path on the blockchain...")
            full_content_string = json.dumps(all_content_for_hash, sort_keys=True)
            content_hash = "0x" + hashlib.sha256(full_content_string.encode()).hexdigest()
            receipt = blockchain_service.register_path_on_chain(new_path_id, content_hash, task_id, update_progress)
            supabase_service.update_path_hash(new_path_id, content_hash)

            tx_hash = receipt.transactionHash.hex()
            explorer_url = f"{config.BLOCK_EXPLORER_URL.rstrip('/')}/tx/{tx_hash}" if config.BLOCK_EXPLORER_URL else None

            update_progress(task_id, f"Path {new_path_id} registered on-chain.",
                            {'txHash': tx_hash, 'explorer_url': explorer_url})

        final_data = {"path_id": new_path_id}
        if config.FEATURE_FLAG_ENABLE_BLOCKCHAIN_REGISTRATION and 'explorer_url' in locals() and explorer_url:
            final_data['explorer_url'] = explorer_url
        update_progress(task_id, "🎉 SUCCESS: Path generation complete!", final_data)

    except Exception as e:
        logger.error(f"TASK [{task_id}] FAILED: {e}", exc_info=True)
        error_detail = str(e)
        if "insufficient funds" in error_detail:
            user_message = "❌ ERROR: The server's wallet has insufficient funds to pay for the transaction."
        elif "execution reverted" in error_detail:
            user_message = f"❌ ERROR: A blockchain error occurred. This can happen if the contract state is out of sync. Details: {error_detail}"
        else:
            user_message = "❌ ERROR: Path generation failed. Please check server logs for details."

        update_progress(task_id, user_message)

        if new_path_id:
            logger.warning(
                f"TASK [{task_id}]: An error occurred during path generation. Attempting to cleanup partially generated path ID: {new_path_id}")
            update_progress(task_id, f"🧹 An error occurred. Cleaning up incomplete path ID: {new_path_id}...")
            try:
                logger.info(f"TASK [{task_id}]: Calling supabase_service.delete_path_by_id({new_path_id}) for cleanup.")
                delete_response = supabase_service.delete_path_by_id(new_path_id)
                logger.info(f"TASK [{task_id}]: Response from delete_path_by_id: {delete_response}")

                if delete_response and hasattr(delete_response, 'error') and delete_response.error:
                    logger.error(
                        f"TASK [{task_id}]: Cleanup FAILED for path ID {new_path_id}. Supabase delete error: {delete_response.error}")
                    update_progress(task_id,
                                    f"CRITICAL! Path cleanup failed for ID {new_path_id} (Supabase error). Please notify an admin.")
                elif delete_response and hasattr(delete_response, 'data') and not delete_response.data:
                    logger.warning(
                        f"TASK [{task_id}]: Cleanup for path ID {new_path_id} reported no data deleted. It might have already been deleted or never fully created.")
                    update_progress(task_id, f"Cleanup for path ID {new_path_id} reported no data deleted.")
                else:
                    logger.info(f"TASK [{task_id}]: Cleanup successful for path ID: {new_path_id}.")
                    update_progress(task_id, f"Cleanup complete for path ID: {new_path_id}.")
            except Exception as cleanup_e:
                logger.error(
                    f"TASK [{task_id}]: CRITICAL! Exception during cleanup attempt for path ID {new_path_id}: {cleanup_e}",
                    exc_info=True)
                update_progress(task_id,
                                f"CRITICAL! Path cleanup failed for ID {new_path_id} (Exception). Please notify an admin.")
        else:
            logger.info(
                f"TASK [{task_id}]: Path generation failed before path ID was assigned. No DB cleanup needed for learning_paths table.")


@bp.route('/generate', methods=['POST'])
def generate_new_path_route():
    req_data = request.get_json()
    topic = req_data.get('topic')
    creator_wallet = req_data.get('creator_wallet')

    if not topic or not creator_wallet:
        return jsonify({"error": "topic and creator_wallet are required"}), 400

    try:
        user_res = supabase_service.get_user_by_wallet_full(creator_wallet)
        country = user_res.data.get('country') if user_res and user_res.data else None

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
                similar_path = similar_paths_res.data[0]
                logger.warning(
                    f"DUPE CHECK: Found a similar path (ID: {similar_path['id']}, Title: '{similar_path['title']}') for new topic '{new_title}'. Halting generation.")
                return jsonify({
                    "error": f"A very similar learning path already exists.",
                    "similar_path": similar_path
                }), 409

        task_id = str(uuid.uuid4())
        supabase_service.create_task_log(task_id)

        thread = threading.Thread(target=generation_worker, args=(task_id, topic, new_title, creator_wallet, country))
        thread.start()

        return jsonify({"message": "Path generation started.", "task_id": task_id}), 202

    except Exception as e:
        logger.error(f"GENERATE ROUTE: Failed during pre-generation step: {e}", exc_info=True)
        return jsonify({"error": "Failed to start generation process. Check server logs."}), 500


@bp.route('/random-topic', methods=['GET'])
def get_random_topic_route():
    try:
        topic = ai_service.generate_random_topic()
        return jsonify({"topic": topic})
    except Exception as e:
        logger.error(f"RANDOM TOPIC ROUTE: Failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to generate a random topic."}), 500


@bp.route('/generate/status/<task_id>', methods=['GET'])
def get_generation_status(task_id):
    try:
        log_res = supabase_service.get_task_log(task_id)
        if not log_res or not log_res.data:
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
        if not path_details_res or not path_details_res.data:
            return jsonify({"error": "Path not found"}), 404

        path_data = path_details_res.data

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

        path_data['total_slides'] = total_slides
        path_data['total_questions'] = total_questions

        return jsonify(path_data)
    except Exception as e:
        logger.error(f"ROUTE: /paths/<id> GET failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch path details."}), 500


@bp.route('/<int:path_id>/<wallet_address>', methods=['GET'])
def get_path_details_for_user_route(path_id, wallet_address):
    """
    Gets full path details and enriches each level with the user-specific completion status.
    """
    logger.info(f"ROUTE: /paths/<id>/<wallet> GET for path {path_id} and user {wallet_address}")
    try:
        path_data = supabase_service.get_full_path_details_for_user(path_id, wallet_address)

        if not path_data:
            return jsonify({"error": "Path not found"}), 404

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

        path_data['total_slides'] = total_slides
        path_data['total_questions'] = total_questions

        return jsonify(path_data)
    except Exception as e:
        logger.error(f"ROUTE: /paths/<id>/<wallet> GET failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch path details for user."}), 500


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
        level_res = supabase_service.get_level(path_id, level_num)
        if not level_res.data:
            return jsonify({"error": "Level not found"}), 404

        items_res = supabase_service.get_content_items_for_level(level_res.data['id'])
        items = items_res.data

        level_slides = 0
        level_questions = 0
        for item in items:
            if item.get('item_type') == 'slide':
                level_slides += 1
            elif item.get('item_type') == 'quiz':
                level_questions += 1

        return jsonify({
            "level_title": level_res.data['level_title'],
            "total_slides_in_level": level_slides,
            "total_questions_in_level": level_questions,
            "items": items
        })
    except Exception as e:
        logger.error(f"ROUTE: /paths/.../levels GET failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch level content."}), 500