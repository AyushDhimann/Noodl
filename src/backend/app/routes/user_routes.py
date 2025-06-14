from flask import Blueprint, request, jsonify
from app import logger
from app.services import user_service # Import the new service

bp = Blueprint('user_routes', __name__, url_prefix='/users')


@bp.route('', methods=['POST'])
def create_user_route():
    data = request.get_json()
    wallet_address = data.get('wallet_address')
    logger.info(f"ROUTE: /users POST for wallet: {wallet_address}")
    if not wallet_address:
        return jsonify({"error": "wallet_address is required"}), 400

    try:
        # Use the new service function with the checkpoint logic
        user_res = user_service.upsert_user_with_checkpoint(
            wallet_address,
            data.get('name'),
            data.get('country')
        )
        logger.info(f"ROUTE: User data upserted for wallet: {wallet_address}")
        return jsonify(user_res.data), 201
    except Exception as e:
        logger.error(f"ROUTE: /users POST failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to create or update user."}), 500


@bp.route('/<wallet_address>', methods=['GET'])
def get_user_route(wallet_address):
    logger.info(f"ROUTE: /users GET for wallet: {wallet_address}")
    try:
        # Use the full user data fetch for consistency
        user_res = user_service.supabase_service.get_user_by_wallet_full(wallet_address)
        if not user_res or not user_res.data:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user_res.data)
    except Exception as e:
        logger.error(f"ROUTE: /users GET failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve user."}), 500


@bp.route('/<wallet_address>/paths', methods=['GET'])
def get_user_enrolled_paths_route(wallet_address):
    """
    Gets all learning paths a user is enrolled in (i.e., has started).
    Includes a flag indicating if the user has completed each path.
    """
    logger.info(f"ROUTE: /users/<wallet>/paths GET for wallet: {wallet_address}")
    try:
        # 1. Get user_id from wallet_address
        user_res = user_service.supabase_service.get_user_by_wallet(wallet_address)
        if not user_res or not user_res.data:
            return jsonify([])  # User not found, so no enrolled paths

        user_id = user_res.data['id']

        # 2. Get enrolled paths using the new service function
        paths_res = user_service.supabase_service.get_enrolled_paths_by_user(user_id)
        if not paths_res.data:
            return jsonify([])

        # 3. The result is nested, e.g., [{'learning_paths': {...}}, ...]. Un-nest it.
        # Also filter out any potential nulls if a path was deleted but progress remains.
        paths = [item['learning_paths'] for item in paths_res.data if item.get('learning_paths')]
        if not paths:
            return jsonify([])

        # 4. Get completion status for these paths for the same user
        path_ids = [p['id'] for p in paths]
        completion_status = user_service.supabase_service.get_user_progress_for_paths(wallet_address, path_ids)

        # 5. Add the is_complete flag to each path
        for path in paths:
            path['is_complete'] = completion_status.get(path['id'], False)

        return jsonify(paths)
    except Exception as e:
        logger.error(f"ROUTE: /users/<wallet>/paths GET failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve user-enrolled paths."}), 500


@bp.route('/<wallet_address>/paths/count', methods=['GET'])
def get_user_created_paths_count_route(wallet_address):
    logger.info(f"ROUTE: /users/<wallet>/paths/count GET for wallet: {wallet_address}")
    try:
        count = user_service.supabase_service.get_path_count_by_creator(wallet_address)
        return jsonify({
            "creator_wallet": wallet_address,
            "path_count": count
        })
    except Exception as e:
        logger.error(f"ROUTE: /users/<wallet>/paths/count GET failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve user-created path count."}), 500