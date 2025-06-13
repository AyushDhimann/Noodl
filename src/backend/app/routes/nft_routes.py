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

    try:
        # --- Step 1: Mint the NFT to get a Token ID ---
        minted_token_id = blockchain_service.mint_nft_on_chain(user_wallet, path_id)
        if minted_token_id is None:
            return jsonify({"error": "Minting failed, did not receive a Token ID."}), 500

        logger.info(f"NFT: Mint successful for user {user_wallet}, path {path_id}. Token ID: {minted_token_id}")

        # --- Step 2: Save the record to our database ---
        try:
            supabase_service.save_user_nft(user_wallet, path_id, minted_token_id, config.NFT_CONTRACT_ADDRESS)
            logger.info(f"DB: Saved NFT record for wallet {user_wallet}, path {path_id}, token {minted_token_id}")
            # Mark path as complete in DB after a successful mint and DB save
            supabase_service.set_path_completed(user_wallet, path_id)
            logger.info(f"DB: Marked path {path_id} as complete for {user_wallet}.")
        except Exception as db_e:
            logger.error(f"DB: CRITICAL! Failed to save NFT record after minting. Error: {db_e}")
            # Don't fail the whole request, but log this critical issue. The URI won't be set.
            return jsonify({"error": "Minting succeeded but failed to save record to DB."}), 500

        # --- Step 3: Set the Token URI on the contract ---
        metadata_url = f"{request.host_url.rstrip('/')}/nft/metadata/{minted_token_id}"
        set_uri_receipt = blockchain_service.set_token_uri_on_chain(minted_token_id, metadata_url)
        if not set_uri_receipt:
            logger.error(f"NFT: Failed to set Token URI for {minted_token_id} in second transaction.")
            # The NFT is minted but its metadata is not pointing to our server.
            # This is a critical but non-fatal error for the user.
            return jsonify({"error": "Minting succeeded but failed to set metadata URL."}), 500

        return jsonify({
            "message": "NFT minted and metadata set successfully!",
            "token_id": minted_token_id,
            "nft_contract_address": config.NFT_CONTRACT_ADDRESS
        })

    except Exception as e:
        error_message = str(e)
        if 'Certificate already minted' in error_message:
            detail = "Certificate already minted for this user/path."
        elif 'insufficient funds' in error_message:
            detail = "The server's wallet has insufficient funds to pay for gas."
        else:
            detail = "An unknown blockchain error occurred."
        logger.error(f"NFT: Minting process failed. Detail: {detail} | Original Error: {e}")
        return jsonify({"error": "NFT minting failed.", "detail": detail}), 500


@bp.route('/nft/metadata/<int:token_id>', methods=['GET'])
def get_nft_metadata_route(token_id):
    nft_details = supabase_service.get_nft_details_by_token_id(token_id)
    if not nft_details:
        return jsonify({"error": "NFT with this token ID not found in our records"}), 404

    user_name = nft_details.get('user_name', nft_details.get('user_wallet'))
    path_title = nft_details.get('path_title', 'Unknown Path')
    contract_address = nft_details.get('nft_contract_address', 'Unknown Contract')

    # FIX: Add the block explorer URL to the metadata response
    block_explorer_url = f"{config.BLOCK_EXPLORER_URL.rstrip('/')}/nft/{contract_address}/{token_id}"

    metadata = {
        "name": f"KODO Certificate: {path_title}",
        "description": f"This certificate proves that {user_name} successfully completed the '{path_title}' learning path on KODO.",
        "image": f"{request.host_url.rstrip('/')}/nft/image/{token_id}",
        "block_explorer_url": block_explorer_url,
        "attributes": [
            {"trait_type": "Platform", "value": "KODO"},
            {"trait_type": "Recipient", "value": user_name},
            {"trait_type": "Token ID", "value": str(token_id)},
            {"trait_type": "Contract Address", "value": contract_address}
        ]
    }
    return jsonify(metadata)


@bp.route('/nft/image/<int:token_id>', methods=['GET'])
def get_nft_image_route(token_id):
    """
    Serves a user-specific NFT image, looked up by token_id. Generates a new one if it doesn't exist.
    """
    nft_details = supabase_service.get_nft_details_by_token_id(token_id)
    if not nft_details:
        return "NFT not found", 404

    path_id = nft_details['path_id']
    user_wallet = nft_details['user_wallet']
    user_name = nft_details.get('user_name', user_wallet)
    path_title = nft_details.get('path_title', 'Unknown Path')

    cert_dir = os.path.abspath("certificates")
    safe_wallet = user_wallet.replace('0x', '')[:10]
    file_path = os.path.join(cert_dir, f"cert_{path_id}_{safe_wallet}.png")

    if not os.path.exists(file_path):
        logger.info(
            f"IMAGE: Certificate for token {token_id} (path {path_id}, user {user_wallet}) not found. Generating...")
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