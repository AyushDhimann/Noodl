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
        existing_nft_db = supabase_service.get_nft_by_user_and_path(user_wallet, path_id)
        if existing_nft_db:
            logger.warning(f"NFT: DB check blocked re-mint for user {user_wallet}, path {path_id}.")
            return jsonify({
                "error": "Certificate has already been minted.",
                "detail": "Our database shows that an NFT certificate has already been awarded for this path.",
                "nft_data": existing_nft_db
            }), 409

        is_already_minted_on_chain = blockchain_service.check_if_nft_already_minted(user_wallet, path_id)
        if is_already_minted_on_chain:
            logger.warning(f"NFT: Blockchain check blocked re-mint for user {user_wallet}, path {path_id}.")
            return jsonify({
                "error": "Certificate has already been minted.",
                "detail": "The blockchain confirms that an NFT certificate has already been awarded for this path.",
            }), 409

        is_complete = supabase_service.get_path_completion_status(user_wallet, path_id)
        if not is_complete:
            return jsonify({"error": "Path is not yet complete. Cannot mint NFT."}), 400

        nft_details = supabase_service.get_user_and_path_for_nft(user_wallet, path_id)
        if not nft_details:
            return jsonify({"error": "Could not find user or path details."}), 404

        user_name = nft_details.get('user_name', user_wallet)
        path_title = nft_details.get('path_title', 'Unknown Path')

        cert_dir = os.path.abspath("certificates")
        safe_wallet = user_wallet.replace('0x', '')[:10]
        image_file_name = f"cert_{path_id}_{safe_wallet}.png"
        image_file_path = os.path.join(cert_dir, image_file_name)
        logger.info(f"IMAGE: Target certificate image path: {image_file_path}")

        if not os.path.exists(image_file_path):
            logger.info(f"IMAGE: Certificate file '{image_file_path}' not found. Generating new image...")
            generated_path = ai_service.generate_certificate_image(path_title, user_name, image_file_path)
            if not generated_path:
                logger.error(
                    f"IMAGE: ai_service.generate_certificate_image failed to produce an image at {image_file_path}")
                return jsonify({"error": "Failed to generate NFT image."}), 500
            logger.info(f"IMAGE: New certificate image generated and saved to '{generated_path}'")
        else:
            logger.info(f"IMAGE: Certificate file '{image_file_path}' already exists. Using existing image.")

        if not os.path.exists(image_file_path):
            logger.error(
                f"IMAGE: CRITICAL! Image file '{image_file_path}' still does not exist after generation/check. Cannot proceed with IPFS upload.")
            return jsonify({"error": "Failed to obtain certificate image for IPFS upload."}), 500

        logger.info(f"IMAGE: Attempting to upload '{image_file_path}' to IPFS.")
        image_cid = ipfs_service.upload_to_ipfs(file_path=image_file_path)
        if not image_cid:
            logger.error(f"IPFS: Failed to upload certificate image '{image_file_path}' to IPFS.")
            return jsonify({"error": "Failed to upload certificate image to IPFS."}), 500
        logger.info(f"IPFS: Image '{image_file_path}' uploaded. CID: {image_cid}")

        image_gateway_url = f"{config.PINATA_GATEWAY_URL}/{image_cid}"

        metadata = {
            "name": f"KODO Certificate: {path_title}",
            "description": f"This certificate proves that {user_name} successfully completed the '{path_title}' learning path on KODO.",
            "image": image_gateway_url,
            "attributes": [
                {"trait_type": "Platform", "value": "KODO"},
                {"trait_type": "Recipient", "value": user_name}
            ]
        }
        metadata_name = f"metadata_{path_id}_{safe_wallet}.json"
        logger.info(f"IPFS: Attempting to upload metadata JSON object '{metadata_name}'.")
        metadata_cid = ipfs_service.upload_to_ipfs(json_data=metadata, name=metadata_name)
        if not metadata_cid:
            logger.error(f"IPFS: Failed to upload metadata JSON '{metadata_name}' to IPFS.")
            return jsonify({"error": "Failed to upload metadata to IPFS."}), 500
        logger.info(f"IPFS: Metadata JSON '{metadata_name}' uploaded. CID: {metadata_cid}")

        metadata_ipfs_url = f"ipfs://{metadata_cid}"

        minted_token_id = blockchain_service.mint_nft_on_chain(user_wallet, path_id)
        if minted_token_id is None:
            return jsonify({"error": "Minting failed, did not receive a Token ID."}), 500

        logger.info(f"NFT: Mint successful for user {user_wallet}, path {path_id}. Token ID: {minted_token_id}")

        try:
            supabase_service.save_user_nft(
                user_wallet, path_id, minted_token_id, config.NFT_CONTRACT_ADDRESS,
                metadata_ipfs_url, image_gateway_url
            )
            logger.info(f"DB: Saved NFT record for wallet {user_wallet}, path {path_id}, token {minted_token_id}")
        except Exception as db_e:
            logger.error(f"DB: CRITICAL! Failed to save NFT record after minting. Error: {db_e}")
            # Consider how to handle this: the NFT is minted but not recorded.
            # For now, returning an error indicating this state.
            return jsonify({"error": "Minting succeeded but failed to save record to DB. Please contact support.",
                            "details": str(db_e)}), 500

        set_uri_receipt = blockchain_service.set_token_uri_on_chain(minted_token_id, metadata_ipfs_url)
        if not set_uri_receipt:
            logger.error(f"NFT: Failed to set Token URI for {minted_token_id} in second transaction.")
            # NFT is minted and saved in DB, but URI is not set on chain. This is also a partial failure.
            return jsonify(
                {"error": "Minting succeeded and DB record saved, but failed to set metadata URL on blockchain."}), 500

        tx_hash = set_uri_receipt.transactionHash.hex()
        explorer_url = f"{config.BLOCK_EXPLORER_URL.rstrip('/')}/tx/{tx_hash}" if config.BLOCK_EXPLORER_URL else None

        nft_gateway_url = f"{config.PINATA_GATEWAY_URL}/{metadata_cid}"  # Gateway for the metadata JSON

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
        elif 'already known' in error_message:
            detail = "Blockchain transaction for minting failed (likely a nonce issue or duplicate transaction). Please try again in a moment."
        else:
            detail = "An unknown blockchain error occurred during the minting process."
        logger.error(f"NFT: Minting process failed. Detail: {detail} | Original Error: {e}", exc_info=True)
        return jsonify({"error": "NFT minting failed.", "detail": detail}), 500


@bp.route('/nfts/<wallet_address>', methods=['GET'])
def get_user_nfts_route(wallet_address):
    try:
        nfts = supabase_service.get_nfts_by_user(wallet_address)
        return jsonify(nfts)
    except Exception as e:
        logger.error(f"ROUTE: /nfts/<wallet> failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch user NFTs."}), 500