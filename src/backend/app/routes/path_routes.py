import json
import hashlib
from flask import Blueprint, request, jsonify
from app import logger, socketio
from app.services import ai_service, supabase_service, blockchain_service
from app.config import config

bp = Blueprint('path_routes', __name__, url_prefix='/paths')


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


@bp.route('/generate', methods=['POST'])
def generate_new_path_route():
    req_data = request.get_json()
    topic = req_data.get('topic')
    creator_wallet = req_data.get('creator_wallet')
    sid = req_data.get('sid')

    def emit_status(status, data=None):
        if sid:
            socketio.emit('status_update', {'status': status, 'data': data}, room=sid, namespace='/pathProgress')
            socketio.sleep(0.01)

    emit_status(f"Received generation request for topic: '{topic}'")

    try:
        emit_status("Step 1: Generating curriculum...")
        curriculum_titles = ai_service.generate_curriculum(topic)
        total_levels = len(curriculum_titles)
        emit_status(f"Curriculum generated with {total_levels} levels.")

        emit_status("Step 2: Saving path metadata to Supabase...")
        path_res = supabase_service.create_learning_path(
            topic, f"A user-generated learning path about {topic}.",
            creator_wallet, total_levels,
            ai_service.get_embedding(topic) if config.SIMILARITY_THRESHOLD > 0 else None
        )
        new_path_id = path_res.data[0]['id']

        emit_status(f"Step 3: Generating and saving content for {total_levels} levels...")
        all_content_for_hash = []
        for i, level_title in enumerate(curriculum_titles):
            level_number = i + 1
            emit_status(f"  - Generating content for level {level_number}: '{level_title}'...")
            level_res = supabase_service.create_level(new_path_id, level_number, level_title)
            new_level_id = level_res.data[0]['id']

            interleaved_items = ai_service.generate_interleaved_level_content(topic, level_title)
            all_content_for_hash.append({"level": level_title, "items": interleaved_items})

            items_to_insert = [
                {"level_id": new_level_id, "item_index": j, "item_type": item['type'], "content": item['content']} for
                j, item in enumerate(interleaved_items)]
            supabase_service.create_content_items(items_to_insert)
            emit_status(f"  - Saved {len(items_to_insert)} content items for level {level_number}.")

    except Exception as e:
        emit_status(f"ERROR: Path generation failed: {e}")
        logger.error(f"ROUTE: /paths/generate failed during AI/DB phase: {e}", exc_info=True)
        return jsonify({"error": f"Path generation failed: {e}"}), 500

    if config.RUN_API_SERVER:  # A stand-in for a real feature flag
        emit_status("Step 4: Registering content hash on the blockchain...")
        full_content_string = json.dumps(all_content_for_hash, sort_keys=True)
        content_hash = "0x" + hashlib.sha256(full_content_string.encode()).hexdigest()
        try:
            receipt = blockchain_service.register_path_on_chain(new_path_id, content_hash, sid)
            supabase_service.update_path_hash(new_path_id, content_hash)
            emit_status(f"Path {new_path_id} registered on-chain.", {'txHash': receipt.transactionHash.hex()})
        except Exception as e:
            emit_status(f"ERROR: Blockchain registration failed: {e}")

    emit_status("SUCCESS: Path generation complete!")
    return jsonify({"message": "Path created successfully", "path_id": new_path_id}), 201