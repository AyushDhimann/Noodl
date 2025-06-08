from flask import Blueprint, request, jsonify
from app import logger
from app.services import supabase_service

bp = Blueprint('user_routes', __name__, url_prefix='/users')


@bp.route('', methods=['POST'])
def create_user_route():
    data = request.get_json()
    wallet_address = data.get('wallet_address')
    logger.info(f"ROUTE: /users POST for wallet: {wallet_address}")
    if not wallet_address:
        return jsonify({"error": "wallet_address is required"}), 400

    try:
        user_res = supabase_service.upsert_user(wallet_address, data.get('name'), data.get('country'))
        logger.info(f"ROUTE: User data upserted for wallet: {wallet_address}")
        return jsonify(user_res.data[0]), 201
    except Exception as e:
        logger.error(f"ROUTE: /users POST failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to create or update user."}), 500


@bp.route('/<wallet_address>', methods=['GET'])
def get_user_route(wallet_address):
    logger.info(f"ROUTE: /users GET for wallet: {wallet_address}")
    try:
        user_res = supabase_service.get_user_by_wallet(wallet_address)
        if not user_res or not user_res.data:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user_res.data)
    except Exception as e:
        logger.error(f"ROUTE: /users GET failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve user."}), 500