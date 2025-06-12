from flask import Blueprint, request, jsonify
from app import logger
from app.services import supabase_service

bp = Blueprint('progress_routes', __name__)


# This route is for submitting data, so it correctly only accepts POST requests.
# It expects a JSON body with a 'Content-Type: application/json' header.
# Manually sending data as URL parameters will result in a 415 Unsupported Media Type error.
# Accessing this URL with a GET request (e.g., in a browser) will result in a 405 Method Not Allowed error.
@bp.route('/progress/level', methods=['POST'])
def upsert_level_progress_route():
    """
    Receives progress for a specific level. If the user has not started this path,
    it creates a new progress record before saving the level score.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    user_wallet = data.get('user_wallet')
    path_id = data.get('path_id')
    level_index = data.get('level_index')
    correct_answers = data.get('correct_answers')
    total_questions = data.get('total_questions')

    if not all([user_wallet, path_id is not None, level_index is not None, correct_answers is not None, total_questions is not None]):
        return jsonify({"error": "user_wallet, path_id, level_index, correct_answers, and total_questions are required"}), 400

    try:
        path_id_int = int(path_id)
        level_index_int = int(level_index)
        correct_answers_int = int(correct_answers)
        total_questions_int = int(total_questions)

        supabase_service.upsert_level_progress(user_wallet, path_id_int, level_index_int, correct_answers_int, total_questions_int)
        return jsonify({"message": "Progress updated successfully"}), 200
    except (ValueError, TypeError):
        return jsonify({"error": "path_id, level_index, correct_answers, and total_questions must be valid integers"}), 400
    except Exception as e:
        logger.error(f"ROUTE: /progress/level failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to update level progress."}), 500


@bp.route('/scores/level', methods=['GET'])
def get_level_score_route():
    """
    Gets the score for a specific level of a path for a user.
    """
    user_wallet = request.args.get('user_wallet')
    path_id = request.args.get('path_id', type=int)
    level_index = request.args.get('level_index', type=int)

    if not all([user_wallet, path_id is not None, level_index is not None]):
        return jsonify({"error": "user_wallet, path_id, and level_index are required query parameters"}), 400

    try:
        score_data = supabase_service.get_level_score(user_wallet, path_id, level_index)
        if score_data:
            return jsonify(score_data), 200
        else:
            return jsonify({"correct_answers": 0, "total_questions": 0}), 200
    except ValueError as ve:
        logger.error(f"ROUTE: /scores/level ValueError: {ve}")
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        logger.error(f"ROUTE: /scores/level failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve level score."}), 500


@bp.route('/scores/<wallet_address>', methods=['GET'])
def get_user_scores_route(wallet_address):
    """
    Gets the aggregated scores for all paths a user has started.
    """
    try:
        user_res = supabase_service.get_user_by_wallet(wallet_address)
        if not user_res or not user_res.data:
            return jsonify({"error": "User not found"}), 404

        scores = supabase_service.get_user_scores(user_res.data['id'])
        return jsonify(scores)
    except Exception as e:
        logger.error(f"ROUTE: /scores/<wallet> failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch scores."}), 500