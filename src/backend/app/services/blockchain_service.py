import json
from web3 import Web3
from app import w3, account, logger
from app.config import config

with open('contracts/NoodlCertificate.json', 'r') as f:
    NFT_ABI = json.load(f)

with open('contracts/LearningPathRegistry.json', 'r') as f:
    PATH_REGISTRY_ABI = json.load(f)

path_registry_contract = w3.eth.contract(address=Web3.to_checksum_address(config.PATH_REGISTRY_CONTRACT_ADDRESS),
                                         abi=PATH_REGISTRY_ABI)
nft_contract = w3.eth.contract(address=Web3.to_checksum_address(config.NFT_CONTRACT_ADDRESS), abi=NFT_ABI)
logger.info("Blockchain service and contracts initialized.")

def send_tx_and_get_receipt(contract_function, task_id=None, progress_callback=None):
    """Sends a transaction and uses a callback for progress updates."""

    def update_status(status, data=None):
        if task_id and progress_callback:
            progress_callback(task_id, status, data)

    try:
        update_status(f"Building transaction for '{contract_function.fn_name}'...")
        tx_params = {
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'maxFeePerGas': w3.to_wei('20', 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei('1.5', 'gwei'),
        }
        gas_estimate = contract_function.estimate_gas({'from': account.address})
        tx_params['gas'] = int(gas_estimate * 1.2)
        update_status(f"Gas estimated. Preparing to send.")

        transaction = contract_function.build_transaction(tx_params)
        update_status("Signing transaction with backend wallet...")
        signed_tx = w3.eth.account.sign_transaction(transaction, private_key=account.key)

        update_status("Sending transaction to the network...")
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        update_status(f"Transaction sent. Hash: {tx_hash.hex()}", {'txHash': tx_hash.hex()})

        update_status("Waiting for confirmation from the network (this can take a moment)...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        status_msg = 'Success' if tx_receipt.status == 1 else 'Failed'
        update_status(f"Transaction confirmed on the blockchain. Status: {status_msg}")
        return tx_receipt
    except Exception as e:
        logger.error(f"TX FAILED: {e}")
        update_status(f"Blockchain transaction failed: {str(e)}")
        raise e

def register_path_on_chain(path_id, content_hash, task_id=None, progress_callback=None):
    return send_tx_and_get_receipt(
        path_registry_contract.functions.registerPath(path_id, content_hash), task_id, progress_callback
    )

def check_if_nft_already_minted(user_wallet, path_id):
    """
    Directly queries the blockchain to see if an NFT has been minted.
    This is a read-only call and does not cost gas. It's the ultimate source of truth.
    """
    logger.info(f"CHAIN CHECK: Verifying mint status for user {user_wallet}, path {path_id} on-chain.")
    try:
        has_minted = nft_contract.functions.hasUserMinted(
            Web3.to_checksum_address(user_wallet),
            path_id
        ).call()
        if has_minted:
            logger.warning(f"CHAIN CHECK: Confirmed user {user_wallet} HAS already minted for path {path_id}.")
        else:
            logger.info(f"CHAIN CHECK: Confirmed user {user_wallet} has NOT minted for path {path_id}.")
        return has_minted
    except Exception as e:
        logger.error(f"CHAIN CHECK: Failed to query hasUserMinted function: {e}", exc_info=True)
                                                          
        return False

def mint_nft_on_chain(user_wallet, path_id):
    """
    Step 1 of 2: Mints a new NFT for the user and path, returning the new token ID.
    The token URI is set in a subsequent transaction.
    """
    logger.info(f"NFT Mint (1/2): Calling safeMint for user {user_wallet}, path {path_id}")
    receipt = send_tx_and_get_receipt(
        nft_contract.functions.safeMint(Web3.to_checksum_address(user_wallet), path_id)
    )

    try:
        transfer_event = nft_contract.events.Transfer().process_receipt(receipt)
        if transfer_event:
            token_id = transfer_event[0]['args']['tokenId']
            logger.info(f"NFT Mint (1/2): Successfully parsed tokenId {token_id} from Transfer event.")
            return token_id
    except Exception as e:
        logger.error(f"Could not parse Transfer event from receipt, even though transaction succeeded. Error: {e}",
                     exc_info=True)

    logger.warning("Could not find Transfer event in transaction logs. Mint may have failed silently.")
    return None

def set_token_uri_on_chain(token_id, metadata_url):
    """
    Step 2 of 2: Sets the Token URI for a recently minted NFT.
    """
    logger.info(f"NFT Mint (2/2): Calling setTokenURI for token {token_id} with URL: {metadata_url}")
    receipt = send_tx_and_get_receipt(
        nft_contract.functions.setTokenURI(token_id, metadata_url)
    )
    if receipt.status == 1:
        logger.info(f"NFT Mint (2/2): Successfully set token URI for token {token_id}.")
        return receipt
    else:
        logger.error(f"NFT Mint (2/2): Failed to set token URI for token {token_id}.")
        return None
