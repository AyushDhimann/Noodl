from flask import Blueprint, request, jsonify
from app import logger
from app.services import supabase_service

bp = Blueprint('progress_routes', __name__, url_prefix='/progress')


@bp.route('/start', methods=['POST'])
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
        if new_progress_res and new_progress_res.data:
            return jsonify(new_progress_res.data[0]), 201

        return jsonify({"error": "Could not create or retrieve progress."}), 500

    except Exception as e:
        logger.error(f"ROUTE: /progress/start failed: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred while starting progress."}), 500


@bp.route('/update', methods=['POST'])
def update_progress_route():
    data = request.get_json()
    progress_id = data.get('progress_id')
    content_item_id = data.get('content_item_id')
    user_answer_index = data.get('user_answer_index')
    user_wallet = data.get('user_wallet') # FIX: Get user_wallet for verification

    if not all([progress_id, content_item_id, user_answer_index is not None, user_wallet]):
        return jsonify({"error": "progress_id, content_item_id, user_answer_index, and user_wallet are required"}), 400

    try:
        # FIX: Add ownership verification
        user_res = supabase_service.get_user_by_wallet(user_wallet)
        if not user_res or not user_res.data:
            return jsonify({"error": "User not found"}), 404
        user_id = user_res.data['id']

        if not supabase_service.verify_progress_ownership(progress_id, user_id):
            return jsonify({"error": "Forbidden. You do not own this progress record."}), 403

        # Proceed with update after verification
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


@bp.route('/location', methods=['POST'])
def update_location_route():
    data = request.get_json()
    progress_id = data.get('progress_id')
    item_index = data.get('item_index')
    user_wallet = data.get('user_wallet') # FIX: Get user_wallet for verification

    if not all([progress_id, item_index is not None, user_wallet]):
        return jsonify({"error": "progress_id, item_index, and user_wallet are required"}), 400

    try:
        # FIX: Add ownership verification
        user_res = supabase_service.get_user_by_wallet(user_wallet)
        if not user_res or not user_res.data:
            return jsonify({"error": "User not found"}), 404
        user_id = user_res.data['id']

        if not supabase_service.verify_progress_ownership(progress_id, user_id):
            return jsonify({"error": "Forbidden. You do not own this progress record."}), 403

        # Proceed with update after verification
        supabase_service.update_user_progress_item(progress_id, item_index)
        return jsonify({"message": "Location updated successfully"})
    except Exception as e:
        logger.error(f"ROUTE: /progress/location failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to update location."}), 500


@bp.route('/<wallet_address>', methods=['GET'])
def get_all_user_progress_route(wallet_address):
    logger.info(f"ROUTE: /progress/<wallet> GET for wallet: {wallet_address}")
    try:
        # 1. Get user ID from wallet address
        user_res = supabase_service.get_user_by_wallet(wallet_address)
        if not user_res or not user_res.data:
            return jsonify({"error": "User not found"}), 404
        user_id = user_res.data['id']

        # 2. Get all progress records for the user
        progress_records_res = supabase_service.get_all_user_progress(user_id)
        if not progress_records_res.data:
            return jsonify([])  # Return empty list if no progress found

        progress_records = progress_records_res.data
        progress_ids = [p['id'] for p in progress_records]

        # 3. Get all quiz attempts for these progress records in one go
        attempts_res = supabase_service.get_quiz_attempts_for_progress_ids(progress_ids)
        attempts_data = attempts_res.data if attempts_res.data else []

        # 4. Process attempts to calculate scores
        scores = {}  # {progress_id: {'correct': x, 'total': y}}
        for attempt in attempts_data:
            pid = attempt['progress_id']
            if pid not in scores:
                scores[pid] = {'correct': 0, 'total': 0}
            scores[pid]['total'] += 1
            if attempt['is_correct']:
                scores[pid]['correct'] += 1

        # 5. Combine data into a final response
        detailed_progress = []
        for p in progress_records:
            progress_id = p['id']
            score_info = scores.get(progress_id, {'correct': 0, 'total': 0})
            score_percent = (score_info['correct'] / score_info['total'] * 100) if score_info['total'] > 0 else 0

            # Handle cases where joins might be null
            path_info = p.get('learning_paths') or {}
            level_info = p.get('levels') or {}

            detailed_progress.append({
                "progress_id": progress_id,
                "path_id": p['path_id'],
                "path_title": path_info.get('title', 'N/A'),
                "status": p['status'],
                "current_level_number": level_info.get('level_number', 'N/A'),
                "current_level_title": level_info.get('level_title', 'N/A'),
                "current_item_index": p['current_item_index'],
                "total_levels": path_info.get('total_levels', 'N/A'),
                "score_percent": round(score_percent, 2),
                "correct_answers": score_info['correct'],
                "total_questions_answered": score_info['total']
            })

        return jsonify(detailed_progress)

    except Exception as e:
        logger.error(f"ROUTE: /progress/<wallet> GET failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve user progress."}), 500
