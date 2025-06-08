import json
from web3 import Web3
from app import w3, account, socketio, logger
from app.config import config

# --- FIX: Load the ABI array directly from the JSON files ---
with open('contracts/NoodlCertificate.json', 'r') as f:
    NFT_ABI = json.load(f)

with open('contracts/LearningPathRegistry.json', 'r') as f:
    PATH_REGISTRY_ABI = json.load(f)
# --- END OF FIX ---

# Initialize Contracts
path_registry_contract = w3.eth.contract(address=Web3.to_checksum_address(config.PATH_REGISTRY_CONTRACT_ADDRESS),
                                         abi=PATH_REGISTRY_ABI)
nft_contract = w3.eth.contract(address=Web3.to_checksum_address(config.NFT_CONTRACT_ADDRESS), abi=NFT_ABI)
logger.info("Blockchain service and contracts initialized.")


def send_tx_and_get_receipt(contract_function, sid=None):
    """Sends a transaction and emits progress updates over WebSocket."""

    def emit_status(status, data=None):
        if sid:
            # Use the correct namespace when emitting
            socketio.emit('status_update', {'status': status, 'data': data}, room=sid, namespace='/pathProgress')
            socketio.sleep(0.01)

    try:
        emit_status(f"TX PREP: Building transaction for function: {contract_function.fn_name}")
        tx_params = {
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'maxFeePerGas': w3.to_wei('20', 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei('1.5', 'gwei'),
        }
        gas_estimate = contract_function.estimate_gas({'from': account.address})
        tx_params['gas'] = int(gas_estimate * 1.2)
        emit_status(f"TX PREP: Gas estimated at {gas_estimate}. Using {tx_params['gas']} with buffer.")

        transaction = contract_function.build_transaction(tx_params)
        emit_status("TX PREP: Signing transaction...")
        signed_tx = w3.eth.account.sign_transaction(transaction, private_key=account.key)

        emit_status("TX SEND: Sending raw transaction...")
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        emit_status(f"TX SEND: Transaction sent. Hash: {tx_hash.hex()}", {'txHash': tx_hash.hex()})

        emit_status("TX WAIT: Waiting for transaction receipt...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        status_msg = 'Success' if tx_receipt.status == 1 else 'Failed'
        emit_status(f"TX WAIT: Transaction receipt received. Status: {status_msg}")
        return tx_receipt
    except Exception as e:
        logger.error(f"TX FAILED: {e}")
        emit_status(f"TX FAILED: {str(e)}")
        raise e


def register_path_on_chain(path_id, content_hash, sid=None):
    return send_tx_and_get_receipt(
        path_registry_contract.functions.registerPath(path_id, content_hash), sid
    )


def mint_nft_on_chain(user_wallet, path_id, metadata_url, sid=None):
    receipt = send_tx_and_get_receipt(
        nft_contract.functions.safeMint(Web3.to_checksum_address(user_wallet), path_id, metadata_url), sid
    )

    # Use the correct contract object to process the receipt
    transfer_event = nft_contract.events.Transfer().process_receipt(receipt)
    if transfer_event:
        return transfer_event[0]['args']['tokenId']

    logger.warning("Could not find Transfer event in transaction logs.")
    return None