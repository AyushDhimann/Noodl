from flask import Blueprint, request, jsonify
from app import logger
from app.services import supabase_service

bp = Blueprint('progress_routes', __name__)


@bp.route('/progress/start', methods=['POST'])
def start_or_get_progress_route():
    try:
        data = request.get_json()
        user_wallet = data.get('user_wallet')
        path_id = data.get('path_id')
        logger.info(f"ROUTE: /progress/start for user {user_wallet} on path {path_id}.")
        if not user_wallet or not path_id:
            return jsonify({"error": "user_wallet and path_id are required"}), 400

        user_res = supabase_service.get_user_by_wallet(user_wallet)
        if not user_res or not user_res.data:
            return jsonify({"error": "User not found. Please create the user first."}), 404
        user_id = user_res.data['id']

        progress_res = supabase_service.get_progress(user_id, path_id)

        if progress_res and progress_res.data:
            return jsonify(progress_res.data)

        new_progress_res = supabase_service.create_progress(user_id, path_id)

        # FIX: The 'create_progress' service function returns a single dictionary, not a list.
        # Accessing its 'data' attribute directly is correct.
        if new_progress_res and new_progress_res.data:
            return jsonify(new_progress_res.data), 201

        # Fallback error
        return jsonify({"error": "Could not create or retrieve progress."}), 500

    except Exception as e:
        logger.error(f"ROUTE: /progress/start failed: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred while starting progress."}), 500


@bp.route('/progress/update', methods=['POST'])
def update_progress_route():
    data = request.get_json()
    progress_id = data.get('progress_id')
    content_item_id = data.get('content_item_id')
    user_answer_index = data.get('user_answer_index')

    try:
        quiz_item = supabase_service.get_quiz_item(content_item_id)
        correct_answer_index = quiz_item.data['content']['correctAnswerIndex']
        is_correct = int(user_answer_index) == int(correct_answer_index)

        supabase_service.log_quiz_attempt(progress_id, content_item_id, user_answer_index, is_correct)
        supabase_service.update_user_progress_item(progress_id, quiz_item.data['item_index'])

        return jsonify({"message": "Progress updated", "is_correct": is_correct})
    except Exception as e:
        logger.error(f"ROUTE: /progress/update failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to update progress."}), 500


@bp.route('/scores/<wallet_address>', methods=['GET'])
def get_user_scores_route(wallet_address):
    try:
        user_res = supabase_service.get_user_by_wallet(wallet_address)
        if not user_res or not user_res.data:
            return jsonify({"error": "User not found"}), 404

        scores = supabase_service.get_user_scores(user_res.data['id'])
        return jsonify(scores)
    except Exception as e:
        logger.error(f"ROUTE: /scores failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch scores."}), 500


@bp.route('/progress/location', methods=['POST'])
def update_location_route():
    data = request.get_json()
    progress_id = data.get('progress_id')
    item_index = data.get('item_index')

    if progress_id is None or item_index is None:
        return jsonify({"error": "progress_id and item_index are required"}), 400

    try:
        supabase_service.update_user_progress_item(progress_id, item_index)
        return jsonify({"message": "Location updated successfully"})
    except Exception as e:
        logger.error(f"ROUTE: /progress/location failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to update location."}), 500