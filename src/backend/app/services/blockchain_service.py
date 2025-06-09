import json
from web3 import Web3
from app import w3, account, logger
from app.config import config

# Load ABIs from JSON files
with open('contracts/NoodlCertificate.json', 'r') as f:
    NFT_ABI = json.load(f)

with open('contracts/LearningPathRegistry.json', 'r') as f:
    PATH_REGISTRY_ABI = json.load(f)

# Initialize Contracts
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


def mint_nft_on_chain(user_wallet, path_id, metadata_url):
    receipt = send_tx_and_get_receipt(
        nft_contract.functions.safeMint(Web3.to_checksum_address(user_wallet), path_id, metadata_url)
    )
    transfer_event = nft_contract.events.Transfer().process_receipt(receipt)
    if transfer_event:
        return transfer_event[0]['args']['tokenId']

    logger.warning("Could not find Transfer event in transaction logs.")
    return None