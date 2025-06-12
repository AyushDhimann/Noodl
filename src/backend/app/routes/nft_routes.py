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

    metadata_url = f"{request.host_url.rstrip('/')}/nft/metadata/{path_id}"

    try:
        minted_token_id = blockchain_service.mint_nft_on_chain(user_wallet, path_id, metadata_url)
        if minted_token_id is not None:
            # NEW: Mark path as complete in DB after successful mint
            try:
                supabase_service.set_path_completed(user_wallet, path_id)
                logger.info(f"DB: Marked path {path_id} as complete for {user_wallet}.")
            except Exception as db_e:
                # Log the error but don't fail the entire request, as the mint was successful
                logger.error(f"DB: Failed to mark path {path_id} as complete for {user_wallet} after minting. Error: {db_e}")

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


@bp.route('/nft/metadata/<int:path_id>', methods=['GET'])
def get_nft_metadata_route(path_id):
    path_res = supabase_service.get_path_by_id(path_id)
    if not path_res or not path_res.data:
        return jsonify({"error": "Path not found"}), 404

    path_data = path_res.data
    metadata = {
        "name": f"Noodl Certificate: {path_data['title']}",
        "description": f"Proves completion of the '{path_data['title']}' learning path on Noodl.",
        "image": f"{request.host_url.rstrip('/')}/nft/image/{path_id}",
        "attributes": [{"trait_type": "Platform", "value": "Noodl"}]
    }
    return jsonify(metadata)


@bp.route('/nft/image/<int:path_id>', methods=['GET'])
def get_nft_image_route(path_id):
    """
    Serves the NFT image. Checks for a local copy first,
    and generates a new one if it doesn't exist.
    """
    cert_dir = os.path.abspath("certificates")
    file_path = os.path.join(cert_dir, f"path_{path_id}.png")

    if not os.path.exists(file_path):
        logger.info(f"IMAGE: Certificate for path {path_id} not found locally. Generating...")
        path_res = supabase_service.get_path_by_id(path_id)
        if not path_res or not path_res.data:
            return "Path not found", 404

        generated_path = ai_service.generate_pixel_cert(path_res.data['title'], path_id)
        if not generated_path:
            return "Failed to generate NFT image.", 500

    try:
        return send_file(file_path, mimetype='image/png')
    except FileNotFoundError:
        logger.error(f"IMAGE: File not found at {file_path} after attempting to serve.")
        return "Image file not found on server.", 404