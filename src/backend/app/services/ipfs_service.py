import requests
import json
import os
from app import logger
from app.config import config

PINATA_BASE_URL = "https://api.pinata.cloud/"
PINATA_PIN_FILE_URL = f"{PINATA_BASE_URL}pinning/pinFileToIPFS"
PINATA_PIN_JSON_URL = f"{PINATA_BASE_URL}pinning/pinJSONToIPFS"

def upload_to_ipfs(file_path=None, json_data=None, name=None):
    """
    Uploads a file or a JSON object to IPFS via Pinata.
    Returns the IPFS hash (CID).
    'name' parameter is used to set a filename for the upload on Pinata.
    """
    if not config.PINATA_API_KEY or not config.PINATA_API_SECRET:
        logger.error("IPFS Error: Pinata API Key or Secret is not configured.")
        raise ValueError("Pinata API credentials are not set in the environment.")

    headers = {
        "pinata_api_key": config.PINATA_API_KEY,
        "pinata_secret_api_key": config.PINATA_API_SECRET
    }

    try:
        if file_path:
            logger.info(f"IPFS: Uploading file '{file_path}' to Pinata.")
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                response = requests.post(PINATA_PIN_FILE_URL, headers=headers, files=files, timeout=60)
        elif json_data:
            logger.info(f"IPFS: Uploading JSON data to Pinata with name '{name}'.")
            payload = {"pinataContent": json_data}
            if name:
                payload['pinataMetadata'] = {'name': name}
            response = requests.post(PINATA_PIN_JSON_URL, headers=headers, json=payload, timeout=60)
        else:
            raise ValueError("Either file_path or json_data must be provided.")

        response.raise_for_status()
        result = response.json()
        ipfs_hash = result.get("IpfsHash")
        logger.info(f"IPFS: Successfully uploaded. CID: {ipfs_hash}")
        return ipfs_hash

    except requests.exceptions.RequestException as e:
        logger.error(f"IPFS: Request failed: {e.response.text if e.response else str(e)}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"IPFS: An unexpected error occurred during upload: {e}", exc_info=True)
        return None