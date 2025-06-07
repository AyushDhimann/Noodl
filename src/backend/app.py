import os
import json
import hashlib
import base64
from io import BytesIO
from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
# from web3.middleware import geth_poa_middleware
import google.generativeai as genai
from supabase import create_client, Client
from PIL import Image, ImageDraw, ImageFont

# --- Initial Setup ---
load_dotenv()
app = Flask(__name__)

# --- Feature Flags & Config ---
def is_feature_enabled(flag_name):
    return os.getenv(flag_name, "false").lower() == "true"

# --- Service Connections ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
text_model = genai.GenerativeModel(os.getenv("GEMINI_MODEL_TEXT"))
vision_model = genai.GenerativeModel(os.getenv("GEMINI_MODEL_VISION"))
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
w3 = Web3(Web3.HTTPProvider(os.getenv("ETHEREUM_NODE_URL")))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
if not w3.is_connected():
    raise ConnectionError("Failed to connect to Ethereum node")

# --- Web3 Account and Contract ABIs ---
# NOTE: In a production app, load these large ABIs from separate JSON files.
PATH_REGISTRY_ABI = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"pathId","type":"uint256"},{"indexed":false,"internalType":"bytes32","name":"contentHash","type":"bytes32"}],"name":"PathRegistered","type":"event"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"pathContentHashes","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_pathId","type":"uint256"},{"internalType":"bytes32","name":"_contentHash","type":"bytes32"}],"name":"registerPath","outputs":[],"stateMutability":"nonpayable","type":"function"}]')
NFT_ABI = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"approved","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"operator","type":"address"},{"indexed":false,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"hasMinted","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"pathId","type":"uint256"},{"internalType":"string","name":"uri","type":"string"}],"name":"safeMint","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]')

account = w3.eth.account.from_key(os.getenv("BACKEND_WALLET_PRIVATE_KEY"))
w3.eth.default_account = account.address
path_registry_contract = w3.eth.contract(address=Web3.to_checksum_address(os.getenv("PATH_REGISTRY_CONTRACT_ADDRESS")), abi=PATH_REGISTRY_ABI)
nft_contract = w3.eth.contract(address=Web3.to_checksum_address(os.getenv("NFT_CONTRACT_ADDRESS")), abi=NFT_ABI)

# --- Helper Functions ---
def get_embedding(text):
    result = genai.embed_content(model="models/embedding-001", content=text)
    return result['embedding']

def generate_curriculum(topic):
    prompt = f"""You are an expert curriculum designer. For the topic "{topic}", create a learning path syllabus. The output MUST be a single, valid JSON object with one key: "levels". "levels" should be an array of strings, where each string is a concise title for a learning level. The number of levels should be appropriate for the topic's complexity, from a minimum of 3 to a maximum of 10. Do not include any text outside of the JSON object."""
    response = text_model.generate_content(prompt)
    cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(cleaned_response)['levels']

def generate_level_content(topic, level_title, level_num, total_levels):
    prompt = f"""You are an expert educator. The main topic is "{topic}". This lesson is for the level titled: "{level_title}" (Level {level_num} of {total_levels}). Generate the learning material. The output MUST be a single, valid JSON object with two keys: "slides" and "quiz". "slides": An array of 3 to 5 objects, each with a "title" and "content". "quiz": An array of 3 multiple-choice question objects, each with "question", "options" (4 strings), and "correctAnswerIndex" (integer 0-3). Ensure content is concise. Do not include any text outside of the JSON object."""
    response = text_model.generate_content(prompt)
    cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(cleaned_response)

def generate_nft_image(title):
    prompt = f"""Create a goofy, abstract, and vibrant digital art image representing the concept of learning about "{title}". Think colorful noodle-like brain synapses, lightbulbs, and quirky characters. It should be fun, modern, and suitable for a Gen-Z audience. The style should be minimalist but eye-catching."""
    try:
        image_response = vision_model.generate_content([prompt])
        image_data = image_response.parts[0].inline_data.data
        return base64.b64decode(image_data)
    except Exception as e:
        app.logger.error(f"Failed to generate NFT image, using fallback: {e}")
        img = Image.new('RGB', (512, 512), color = (73, 109, 137))
        d = ImageDraw.Draw(img)
        d.text((50,230), f"Noodl Certificate:\n{title}", fill=(255,255,255))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

def send_tx(contract_function):
    tx = contract_function.build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 1000000,
        'maxFeePerGas': w3.to_wei('250', 'gwei'),
        'maxPriorityFeePerGas': w3.to_wei('3', 'gwei'),
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=account.key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return tx_hash

# --- API Endpoints ---
@app.route('/paths/generate', methods=['POST'])
def generate_new_path():
    req_data = request.get_json()
    topic = req_data.get('topic')
    creator_wallet = req_data.get('creator_wallet')
    if not topic or not creator_wallet:
        return jsonify({"error": "Topic and creator_wallet are required"}), 400

    if is_feature_enabled("FEATURE_FLAG_ENABLE_DUPLICATE_CHECK"):
        topic_embedding = get_embedding(topic)
        threshold = float(os.getenv("SIMILARITY_THRESHOLD", 0.85))
        similar_paths = supabase.rpc('match_similar_paths', {'query_embedding': topic_embedding, 'match_threshold': threshold, 'match_count': 1}).execute()
        if similar_paths.data:
            return jsonify({"error": "A similar topic already exists.", "similar_path": similar_paths.data[0]}), 409

    try:
        curriculum_titles = generate_curriculum(topic)
        all_levels_content = []
        for i, level_title in enumerate(curriculum_titles):
            content = generate_level_content(topic, level_title, i + 1, len(curriculum_titles))
            all_levels_content.append({"level_number": i + 1, "level_title": level_title, "content": content})
    except Exception as e:
        return jsonify({"error": f"AI content generation failed: {e}"}), 500

    try:
        path_res = supabase.table('learning_paths').insert({
            "title": topic, "description": f"A user-generated learning path about {topic}.",
            "creator_wallet": creator_wallet,
            "title_embedding": get_embedding(topic) if is_feature_enabled("FEATURE_FLAG_ENABLE_DUPLICATE_CHECK") else None
        }).execute()
        new_path_id = path_res.data[0]['id']
        for level_data in all_levels_content: level_data['path_id'] = new_path_id
        supabase.table('levels').insert(all_levels_content).execute()
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500

    if is_feature_enabled("FEATURE_FLAG_ENABLE_BLOCKCHAIN_REGISTRATION"):
        full_content_string = json.dumps(all_levels_content, sort_keys=True)
        content_hash = "0x" + hashlib.sha256(full_content_string.encode()).hexdigest()
        try:
            tx_hash = send_tx(path_registry_contract.functions.registerPath(new_path_id, content_hash))
            supabase.table('learning_paths').update({'content_hash': content_hash}).eq('id', new_path_id).execute()
            app.logger.info(f"Path {new_path_id} registered on-chain. Tx: {tx_hash.hex()}")
        except Exception as e:
            app.logger.error(f"Blockchain registration failed for path {new_path_id}: {e}")

    return jsonify({"message": "Path created successfully", "path_id": new_path_id}), 201

@app.route('/paths/<int:path_id>/complete', methods=['POST'])
def complete_path_and_mint_nft(path_id):
    if not is_feature_enabled("FEATURE_FLAG_ENABLE_NFT_MINTING"):
        return jsonify({"message": "NFT minting is currently disabled."})
    user_wallet = request.get_json().get('user_wallet')
    if not user_wallet: return jsonify({"error": "user_wallet is required"}), 400
    metadata_url = f"{request.host_url.rstrip('/')}/nft/metadata/{path_id}"
    try:
        tx_hash = send_tx(nft_contract.functions.safeMint(Web3.to_checksum_address(user_wallet), path_id, metadata_url))
        return jsonify({"message": "NFT minted successfully!", "transaction_hash": tx_hash.hex()})
    except Exception as e:
        return jsonify({"error": "NFT minting failed. Certificate may already exist for this user."}), 500

@app.route('/nft/metadata/<int:path_id>', methods=['GET'])
def get_nft_metadata(path_id):
    path_data = supabase.table('learning_paths').select("title, description").eq('id', path_id).single().execute()
    if not path_data.data: return jsonify({"error": "Path not found"}), 404
    metadata = {
        "name": f"Noodl Certificate: {path_data.data['title']}",
        "description": f"Proves completion of the '{path_data.data['title']}' learning path on Noodl.",
        "image": f"{request.host_url.rstrip('/')}/nft/image/{path_id}",
        "attributes": [{"trait_type": "Platform", "value": "Noodl"}]
    }
    return jsonify(metadata)

@app.route('/nft/image/<int:path_id>', methods=['GET'])
def get_nft_image(path_id):
    path_data = supabase.table('learning_paths').select("title").eq('id', path_id).single().execute()
    if not path_data.data: return "Path not found", 404
    image_bytes = generate_nft_image(path_data.data['title'])
    return send_file(BytesIO(image_bytes), mimetype='image/png')

@app.route('/paths', methods=['GET'])
def get_all_paths():
    data = supabase.table('learning_paths').select("id, title, description").execute()
    return jsonify(data.data)

@app.route('/paths/<int:path_id>/levels/<int:level_num>', methods=['GET'])
def get_level_content(path_id, level_num):
    data = supabase.table('levels').select("content").eq('path_id', path_id).eq('level_number', level_num).single().execute()
    if not data.data: return jsonify({"error": "Level not found"}), 404
    return jsonify(data.data['content'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)