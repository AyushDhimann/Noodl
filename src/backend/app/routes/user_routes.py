from flask import Blueprint, request, jsonify
from app import logger
from app.services import user_service, supabase_service

bp = Blueprint('user_routes', __name__, url_prefix='/users')


@bp.route('', methods=['POST'])
def create_user_route():
    data = request.get_json()
    wallet_address = data.get('wallet_address')
    logger.info(f"ROUTE: /users POST for wallet: {wallet_address}")
    if not wallet_address:
        return jsonify({"error": "wallet_address is required"}), 400

    try:
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
        user_res = supabase_service.get_user_by_wallet_full(wallet_address)
        if not user_res or not user_res.data:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user_res.data)
    except Exception as e:
        logger.error(f"ROUTE: /users GET failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve user."}), 500


@bp.route('/<wallet_address>/paths', methods=['GET'])
def get_user_associated_paths_route(wallet_address):
    """
    Gets all learning paths associated with a user:
    those they created AND those they are enrolled in (have started).
    Ordered by most recent activity (creation or enrollment start).
    """
    logger.info(f"ROUTE: /users/<wallet>/paths (ASSOCIATED) GET for wallet: {wallet_address}")
    try:
        # The RPC function get_user_associated_paths takes wallet address directly
        paths_res = supabase_service.get_user_associated_paths_rpc(wallet_address)

        if paths_res.data is None:  # Check if data is None (e.g. RPC error or no user)
            logger.warning(f"No associated paths found or RPC error for wallet {wallet_address}.")
            return jsonify([])

        # The RPC directly returns the list of paths
        return jsonify(paths_res.data)

    except Exception as e:
        logger.error(f"ROUTE: /users/<wallet>/paths (ASSOCIATED) GET failed: {e}", exc_info=True)
        # Check if the error is from PostgREST and try to return its message
        if hasattr(e, 'message') and isinstance(e.message, dict):
            return jsonify({"error": "Failed to retrieve user-associated paths.", "details": e.message}), 500
        return jsonify({"error": "Failed to retrieve user-associated paths."}), 500


@bp.route('/<wallet_address>/paths/count', methods=['GET'])
def get_user_created_paths_count_route(wallet_address):
    logger.info(f"ROUTE: /users/<wallet>/paths/count GET for wallet: {wallet_address}")
    try:
        count = supabase_service.get_path_count_by_creator(wallet_address)
        return jsonify({
            "creator_wallet": wallet_address,
            "path_count": count
        })
    except Exception as e:
        logger.error(f"ROUTE: /users/<wallet>/paths/count GET failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve user-created path count."}), 500