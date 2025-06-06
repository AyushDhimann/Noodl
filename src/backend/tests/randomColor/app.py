import os
import random
import json
from functools import wraps

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from web3 import Web3
# from web3.middleware import geth_poa_middleware  # For PoA chains like Sepolia
import google.generativeai as genai
from supabase import create_client, Client
from web3.middleware import ExtraDataToPOAMiddleware

# Load environment variables
load_dotenv()

# --- Initialize Flask App ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY", "a_very_secret_key_for_dev")  # For session, etc.

# --- Gemini API Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash-lite')  # Or other suitable model

# --- Supabase Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("Supabase URL or Key not found in .env file")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# --- Web3 Configuration ---
ETHEREUM_NODE_URL = os.getenv("ETHEREUM_NODE_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
BACKEND_WALLET_PRIVATE_KEY = os.getenv("BACKEND_WALLET_PRIVATE_KEY")
BACKEND_WALLET_ADDRESS = os.getenv("BACKEND_WALLET_ADDRESS")

if not all([ETHEREUM_NODE_URL, CONTRACT_ADDRESS, BACKEND_WALLET_PRIVATE_KEY, BACKEND_WALLET_ADDRESS]):
    raise ValueError("Ethereum configuration missing in .env file")

w3 = Web3(Web3.HTTPProvider(ETHEREUM_NODE_URL))
# If connecting to a PoA network like Sepolia, Goerli, Rinkeby (you might need this)
# w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
if not w3.is_connected():
    raise ConnectionError("Failed to connect to Ethereum node")

# Contract ABI (Paste the ABI you copied from Remix here)
# It's a large JSON, so often stored in a separate file and loaded.
# For simplicity, pasting a snippet. Replace with your full ABI.
CONTRACT_ABI = json.loads("""
[
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "hexCode",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "description",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "address",
				"name": "submitter",
				"type": "address"
			}
		],
		"name": "ColorAdded",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_hexCode",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_description",
				"type": "string"
			}
		],
		"name": "addColor",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "allColors",
		"outputs": [
			{
				"internalType": "string",
				"name": "hexCode",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "description",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "submitter",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_id",
				"type": "uint256"
			}
		],
		"name": "getColorById",
		"outputs": [
			{
				"internalType": "string",
				"name": "hexCode",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "description",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "submitter",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getColorCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"name": "isHexCodeStored",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "withdraw",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]
""")  # Replace with your actual full ABI

color_registry_contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=CONTRACT_ABI)

# --- Authentication ---
# Simple API Key Auth for this example. Flutter app sends this in a header.
# For production, use JWTs.
FLUTTER_API_KEY_EXPECTED = os.getenv("FLUTTER_API_KEY")


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')  # Or 'Authorization: Bearer <key>'
        if api_key and api_key == FLUTTER_API_KEY_EXPECTED:
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized. Invalid or missing API Key."}), 401

    return decorated_function


# --- Helper Functions ---
def generate_random_hex_color():
    """Generates a random hex color code."""
    return f"#{random.randint(0, 0xFFFFFF):06x}"


def get_color_description_gemini(hex_code):
    """Gets a color description from Gemini API."""
    prompt = f"Describe the color {hex_code} in one short, evocative sentence. For example, for #FF0000, you might say 'A vibrant and passionate crimson red.' or for #00FF00 'A lush and lively lime green.'"
    try:
        response = gemini_model.generate_content(prompt)
        # Ensure you handle cases where response.text might be empty or error
        if response.parts:
            # Accessing the text from the first part, assuming it's text
            description = response.parts[0].text.strip()
            # Clean up potential markdown or unwanted characters
            description = description.replace("*", "").replace("\"", "")
            return description
        elif response.text:  # Fallback if .parts is not populated as expected but .text is
            description = response.text.strip().replace("*", "").replace("\"", "")
            return description
        else:
            app.logger.error(f"Gemini API returned no usable content for {hex_code}. Response: {response}")
            return "A mysterious and undescribed color."
    except Exception as e:
        app.logger.error(f"Error calling Gemini API for {hex_code}: {e}")
        return "A color beyond description due to a temporary glitch."


# --- API Endpoints ---
@app.route('/')
def home():
    return "Color API is running!"


@app.route('/random', methods=['GET'])
@require_api_key  # Apply authentication
def get_random_color_data():
    try:
        hex_code = generate_random_hex_color()
        description = get_color_description_gemini(hex_code)

        # 1. Save to Supabase
        try:
            data, count = supabase.table('colors').insert({
                "hex_code": hex_code,
                "description": description
            }).execute()
            app.logger.info(f"Saved to Supabase: {data}")
        except Exception as e:
            app.logger.error(f"Error saving to Supabase: {e}")
            # Decide if you want to proceed if Supabase fails

        # 2. Save to Blockchain
        try:
            nonce = w3.eth.get_transaction_count(Web3.to_checksum_address(BACKEND_WALLET_ADDRESS))
            # Estimate gas if needed, or use a fixed gas limit. Be generous for testnet.
            # gas_estimate = color_registry_contract.functions.addColor(hex_code, description).estimate_gas({'from': BACKEND_WALLET_ADDRESS})

            tx_params = {
                'from': Web3.to_checksum_address(BACKEND_WALLET_ADDRESS),
                'nonce': nonce,
                'gas': 500000,  # Adjust gas limit as needed, can be higher for safety
                'gasPrice': w3.eth.gas_price  # Or set a specific gas price
            }

            # For chains like Sepolia that might be EIP-1559, you might need:
            # tx_params['maxFeePerGas'] = w3.to_wei('250', 'gwei')
            # tx_params['maxPriorityFeePerGas'] = w3.to_wei('2', 'gwei')
            # if 'gasPrice' in tx_params: del tx_params['gasPrice'] # Remove legacy gasPrice if using EIP-1559

            transaction = color_registry_contract.functions.addColor(hex_code, description).build_transaction(tx_params)

            signed_tx = w3.eth.account.sign_transaction(transaction, private_key=BACKEND_WALLET_PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            app.logger.info(f"Sent to Blockchain, TxHash: {tx_hash.hex()}")

            # Optional: Wait for transaction receipt (can be slow)
            # tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            # app.logger.info(f"Blockchain transaction confirmed: {tx_receipt}")

        except Exception as e:
            app.logger.error(f"Error saving to Blockchain: {e}")
            # Decide if you want to proceed if Blockchain fails.
            # For this app, we'll still return the color even if blockchain save fails.

        response_data = {
            "HexCode": hex_code,
            "Description": description
        }
        return jsonify(response_data), 200

    except Exception as e:
        app.logger.error(f"Error in /random endpoint: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")