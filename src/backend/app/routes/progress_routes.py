from flask import Blueprint, request, jsonify
from app import logger
from app.services import supabase_service

bp = Blueprint('progress_routes', __name__, url_prefix='/progress')

@bp.route('/level', methods=['POST'])
def upsert_level_progress_route():
    """
    Receives progress for a specific level. If the user has not started this path,
    it creates a new progress record before saving the level score.
    It also automatically checks if the entire path is now complete.
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

@bp.route('/path/<int:path_id>/<wallet_address>/completed', methods=['GET'])
def get_path_completion_route(path_id, wallet_address):
    """Checks if a user has completed a specific learning path."""
    try:
        is_completed = supabase_service.get_path_completion_status(wallet_address, path_id)
        return jsonify({"is_complete": is_completed})
    except Exception as e:
        logger.error(f"ROUTE: /progress/path/completed failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to get path completion status."}), 500

@bp.route('/level/<int:path_id>/<int:level_index>/<wallet_address>/completed', methods=['GET'])
def get_level_completion_route(path_id, level_index, wallet_address):
    """Checks if a user has completed a specific level of a path."""
    try:
        is_completed = supabase_service.get_level_completion_status(wallet_address, path_id, level_index)
        return jsonify({"is_complete": is_completed})
    except Exception as e:
        logger.error(f"ROUTE: /progress/level/completed failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to get level completion status."}), 500

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
