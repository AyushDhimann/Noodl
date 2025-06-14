from flask import Blueprint, request, jsonify
from app import logger
from app.services import supabase_service, blockchain_service, ai_service, ipfs_service
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
        # --- Pre-check: Ensure the path is actually complete ---
        is_complete = supabase_service.get_path_completion_status(user_wallet, path_id)
        if not is_complete:
            return jsonify({"error": "Path is not yet complete. Cannot mint NFT."}), 400

        # --- Step 1: Generate the certificate image locally ---
        nft_details = supabase_service.get_user_and_path_for_nft(user_wallet, path_id)
        if not nft_details:
            return jsonify({"error": "Could not find user or path details."}), 404

        user_name = nft_details.get('user_name', user_wallet)
        path_title = nft_details.get('path_title', 'Unknown Path')

        cert_dir = os.path.abspath("certificates")
        safe_wallet = user_wallet.replace('0x', '')[:10]
        image_file_path = os.path.join(cert_dir, f"cert_{path_id}_{safe_wallet}.png")

        if not os.path.exists(image_file_path):
            logger.info(f"IMAGE: Certificate for path {path_id} not found. Generating...")
            generated_path = ai_service.generate_certificate_image(path_title, user_name, image_file_path)
            if not generated_path:
                return jsonify({"error": "Failed to generate NFT image."}), 500

        # --- Step 2: Upload the image to IPFS ---
        image_cid = ipfs_service.upload_to_ipfs(file_path=image_file_path)
        if not image_cid:
            return jsonify({"error": "Failed to upload certificate image to IPFS."}), 500

        image_ipfs_url = f"ipfs://{image_cid}"
        image_gateway_url = f"{config.PINATA_GATEWAY_URL}/{image_cid}"

        # --- Step 3: Create and upload the metadata JSON to IPFS ---
        metadata = {
            "name": f"KODO Certificate: {path_title}",
            "description": f"This certificate proves that {user_name} successfully completed the '{path_title}' learning path on KODO.",
            "image": image_gateway_url,  # Use the full gateway URL in the metadata
            "attributes": [
                {"trait_type": "Platform", "value": "KODO"},
                {"trait_type": "Recipient", "value": user_name}
            ]
        }
        metadata_name = f"metadata_{path_id}_{safe_wallet}.json"
        metadata_cid = ipfs_service.upload_to_ipfs(json_data=metadata, name=metadata_name)
        if not metadata_cid:
            return jsonify({"error": "Failed to upload metadata to IPFS."}), 500

        metadata_ipfs_url = f"ipfs://{metadata_cid}"

        # --- Step 4: Mint the NFT to get a Token ID ---
        minted_token_id = blockchain_service.mint_nft_on_chain(user_wallet, path_id)
        if minted_token_id is None:
            return jsonify({"error": "Minting failed, did not receive a Token ID."}), 500

        logger.info(f"NFT: Mint successful for user {user_wallet}, path {path_id}. Token ID: {minted_token_id}")

        # --- Step 5: Save the record to our database ---
        try:
            supabase_service.save_user_nft(
                user_wallet, path_id, minted_token_id, config.NFT_CONTRACT_ADDRESS,
                metadata_ipfs_url, image_gateway_url
            )
            logger.info(f"DB: Saved NFT record for wallet {user_wallet}, path {path_id}, token {minted_token_id}")
        except Exception as db_e:
            logger.error(f"DB: CRITICAL! Failed to save NFT record after minting. Error: {db_e}")
            return jsonify({"error": "Minting succeeded but failed to save record to DB."}), 500

        # --- Step 6: Set the Token URI on the contract ---
        set_uri_receipt = blockchain_service.set_token_uri_on_chain(minted_token_id, metadata_ipfs_url)
        if not set_uri_receipt:
            logger.error(f"NFT: Failed to set Token URI for {minted_token_id} in second transaction.")
            return jsonify({"error": "Minting succeeded but failed to set metadata URL."}), 500

        tx_hash = set_uri_receipt.transactionHash.hex()
        explorer_url = f"{config.BLOCK_EXPLORER_URL.rstrip('/')}/tx/{tx_hash}" if config.BLOCK_EXPLORER_URL else None

        nft_gateway_url = f"{config.PINATA_GATEWAY_URL}/{metadata_cid}"

        return jsonify({
            "message": "NFT minted and metadata set successfully!",
            "token_id": minted_token_id,
            "nft_contract_address": config.NFT_CONTRACT_ADDRESS,
            "metadata_url": metadata_ipfs_url,
            "image_gateway_url": image_gateway_url,
            "explorer_url": explorer_url,
            "nft_gateway_url": nft_gateway_url
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


@bp.route('/nfts/<wallet_address>', methods=['GET'])
def get_user_nfts_route(wallet_address):
    """Retrieves all NFTs owned by a user."""
    try:
        nfts = supabase_service.get_nfts_by_user(wallet_address)
        return jsonify(nfts)
    except Exception as e:
        logger.error(f"ROUTE: /nfts/<wallet> failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch user NFTs."}), 500