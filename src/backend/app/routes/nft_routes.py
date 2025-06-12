from flask import Blueprint, request, jsonify, send_file
from app import logger
from app.services import supabase_service, blockchain_service, ai_service
from app.config import config
import os

bp = Blueprint('nft_routes', __name__)


@bp.route('/paths/<int:path_id>/complete', methods=['POST'])
def complete_path_and_mint_nft_route(path_id):
    if not config.FEATURE_FLAG_ENABLE_NFT_MINTING:
        return jsonify({"message": "NFT minting is currently disabled."})

    user_wallet = request.get_json().get('user_wallet')
    if not user_wallet:
        return jsonify({"error": "user_wallet is required"}), 400

    # The metadata URL is now user-specific to generate a personalized NFT
    metadata_url = f"{request.host_url.rstrip('/')}/nft/metadata/{path_id}/{user_wallet}"

    try:
        minted_token_id = blockchain_service.mint_nft_on_chain(user_wallet, path_id, metadata_url)
        if minted_token_id is not None:
            # Mark path as complete in DB
            supabase_service.set_path_completed(user_wallet, path_id)
            logger.info(f"DB: Marked path {path_id} as complete for {user_wallet}.")

            # Save the minted NFT record to the database
            try:
                supabase_service.save_user_nft(user_wallet, path_id, minted_token_id, config.NFT_CONTRACT_ADDRESS)
                logger.info(f"DB: Saved NFT record for wallet {user_wallet}, path {path_id}, token {minted_token_id}")
            except Exception as db_e:
                logger.error(f"DB: CRITICAL! Failed to save NFT record after minting. Error: {db_e}")
                # Don't fail the request, but log this critical issue.

            return jsonify({
                "message": "NFT minted successfully!",
                "token_id": minted_token_id,
                "nft_contract_address": config.NFT_CONTRACT_ADDRESS
            })
        else:
            return jsonify({"error": "Mint succeeded but failed to parse Token ID."}), 500
    except Exception as e:
        error_message = str(e)
        if 'Certificate already minted' in error_message:
            detail = "Certificate already minted for this user/path."
        elif 'insufficient funds' in error_message:
            detail = "The server's wallet has insufficient funds to pay for gas."
        else:
            detail = "An unknown blockchain error occurred."
        logger.error(f"NFT: Minting failed. Detail: {detail} | Original Error: {e}")
        return jsonify({"error": "NFT minting failed.", "detail": detail}), 500


@bp.route('/nft/metadata/<int:path_id>/<user_wallet>', methods=['GET'])
def get_nft_metadata_route(path_id, user_wallet):
    path_res = supabase_service.get_path_by_id(path_id)
    if not path_res or not path_res.data:
        return jsonify({"error": "Path not found"}), 404

    user_res = supabase_service.get_user_by_wallet_full(user_wallet)
    if not user_res or not user_res.data:
        return jsonify({"error": "User not found"}), 404

    path_data = path_res.data
    user_data = user_res.data
    user_name = user_data.get('name', user_wallet)

    metadata = {
        "name": f"KODO Certificate: {path_data['title']}",
        "description": f"This certificate proves that {user_name} successfully completed the '{path_data['title']}' learning path on KODO.",
        "image": f"{request.host_url.rstrip('/')}/nft/image/{path_id}/{user_wallet}",
        "attributes": [
            {"trait_type": "Platform", "value": "KODO"},
            {"trait_type": "Recipient", "value": user_name}
        ]
    }
    return jsonify(metadata)

@bp.route('/nft/image/<int:path_id>/<user_wallet>', methods=['GET'])
def get_nft_image_route(path_id, user_wallet):
    """
    Serves a user-specific NFT image. Generates a new one if it doesn't exist.
    """
    cert_dir = os.path.abspath("certificates")
    # Sanitize wallet address for filename
    safe_wallet = user_wallet.replace('0x', '')[:10]
    file_path = os.path.join(cert_dir, f"cert_{path_id}_{safe_wallet}.png")

    if not os.path.exists(file_path):
        logger.info(f"IMAGE: Certificate for path {path_id} and user {user_wallet} not found. Generating...")
        path_res = supabase_service.get_path_by_id(path_id)
        user_res = supabase_service.get_user_by_wallet_full(user_wallet)

        if not path_res or not path_res.data:
            return "Path not found", 404
        if not user_res or not user_res.data:
            return "User not found", 404

        path_title = path_res.data['title']
        user_name = user_res.data.get('name', user_wallet)

        generated_path = ai_service.generate_certificate_image(path_title, user_name, file_path)
        if not generated_path:
            return "Failed to generate NFT image.", 500

    try:
        return send_file(file_path, mimetype='image/png')
    except FileNotFoundError:
        logger.error(f"IMAGE: File not found at {file_path} after attempting to serve.")
        return "Image file not found on server.", 404


@bp.route('/nfts/<wallet_address>', methods=['GET'])
def get_user_nfts_route(wallet_address):
    """Retrieves all NFTs owned by a user."""
    try:
        nfts = supabase_service.get_nfts_by_user(wallet_address)
        return jsonify(nfts)
    except Exception as e:
        logger.error(f"ROUTE: /nfts/<wallet> failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch user NFTs."}), 500