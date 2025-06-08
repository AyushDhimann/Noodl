import os
import json
import hashlib
from io import BytesIO
import logging
from flask import Flask, request, jsonify, send_file, Response
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from supabase import create_client, Client
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import base64
from datetime import datetime, timezone

# --- Initial Setup & Logging ---
load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app.logger.setLevel(logging.INFO)


# --- Feature Flags & Config ---
def is_feature_enabled(flag_name):
    return os.getenv(flag_name, "false").lower() == "true"


# --- Service Connections ---
app.logger.info("Initializing service connections...")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
text_model = genai.GenerativeModel(os.getenv("GEMINI_MODEL_TEXT"))
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
w3 = Web3(Web3.HTTPProvider(os.getenv("ETHEREUM_NODE_URL")))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

if not w3.is_connected():
    app.logger.error("CRITICAL: Failed to connect to Ethereum node.")
    raise ConnectionError("Failed to connect to Ethereum node")
else:
    app.logger.info(f"Successfully connected to Ethereum node. Chain ID: {w3.eth.chain_id}")

# --- Web3 Account and Contract ABIs ---
PATH_REGISTRY_ABI = json.loads(
    '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"pathId","type":"uint256"},{"indexed":false,"internalType":"bytes32","name":"contentHash","type":"bytes32"}],"name":"PathRegistered","type":"event"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"pathContentHashes","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_pathId","type":"uint256"},{"internalType":"bytes32","name":"_contentHash","type":"bytes32"}],"name":"registerPath","outputs":[],"stateMutability":"nonpayable","type":"function"}]')
NFT_ABI = json.loads(
    '[{"inputs":[{"name":"initialOwner","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"approved","type":"address"},{"indexed":true,"name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"operator","type":"address"},{"indexed":false,"name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"previousOwner","type":"address"},{"indexed":true,"name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":true,"name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"name":"to","type":"address"},{"name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"name":"tokenId","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getCurrentTokenId","outputs":[{"type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getTotalSupply","outputs":[{"type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"name":"user","type":"address"},{"name":"pathId","type":"uint256"}],"name":"hasUserMinted","outputs":[{"type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"name":"owner","type":"address"},{"name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"to","type":"address"},{"name":"pathId","type":"uint256"},{"name":"uri","type":"string"}],"name":"safeMint","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"tokenId","type":"uint256"},{"name":"data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"operator","type":"address"},{"name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]')

account = w3.eth.account.from_key(os.getenv("BACKEND_WALLET_PRIVATE_KEY"))
w3.eth.default_account = account.address
path_registry_contract = w3.eth.contract(address=Web3.to_checksum_address(os.getenv("PATH_REGISTRY_CONTRACT_ADDRESS")),
                                         abi=PATH_REGISTRY_ABI)
nft_contract = w3.eth.contract(address=Web3.to_checksum_address(os.getenv("NFT_CONTRACT_ADDRESS")), abi=NFT_ABI)
app.logger.info(f"Web3 account {account.address} and contracts initialized.")


# --- AI Helper Functions ---
def get_embedding(text):
    result = genai.embed_content(model="models/embedding-001", content=text)
    return result['embedding']


def generate_curriculum(topic):
    prompt = f"""You are an expert curriculum designer for a learning app. For the topic "{topic}", create a syllabus. The output MUST be a single, valid JSON object with one key: "levels". "levels" should be an array of strings, where each string is a concise title for a learning level. The number of levels should be appropriate for the topic's complexity (3-10 levels). Do not include any text outside of the JSON object."""
    response = text_model.generate_content(prompt)
    cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(cleaned_response)['levels']


def generate_interleaved_level_content(topic, level_title):
    prompt = f"""
    You are an expert educator creating a lesson for a learning app. The main topic is "{topic}", and this specific lesson is titled "{level_title}".
    Your task is to create an interleaved learning experience with slides and quizzes.
    The output MUST be a single, valid JSON object with one key: "items".
    "items" must be an array of objects. Each object must have a "type" ('slide' or 'quiz') and a "content" field.

    1.  For a 'slide' item:
        - The "content" field should be a string containing rich markdown.
        - Use markdown for formatting: `### Subheadings`, `**bold**`, `* item 1`, `* item 2`.
        - The content should be detailed and informative, providing real value. A slide can be multiple paragraphs long.
        - Structure the lesson logically: start with an introduction, explain concepts with a few slides, then add a quiz to check understanding. Repeat this pattern 2-3 times, ending with a final quiz. A typical level should have 5-8 items in total.

    2.  For a 'quiz' item:
        - The "content" field should be a JSON object with four keys: "question" (string), "options" (array of 4 strings), "correctAnswerIndex" (integer 0-3), and "explanation" (string).
        - The "explanation" should be a "Do you know? 🤓" fun fact or a clear explanation of why the correct answer is right. It should also be formatted with markdown.

    Generate the complete, interleaved lesson for "{level_title}". Do not include any text outside of the main JSON object.
    """
    response = text_model.generate_content(prompt)
    cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(cleaned_response)['items']


def generate_nft_svg(title):
    prompt = f"""Create a simple, abstract, and colorful SVG image representing learning about "{title}". The SVG must be 512x512 pixels. Use a dark background like #1a1a1a. Generate 3-5 random, colorful, overlapping geometric shapes (circles, rectangles). Use vibrant colors like #FF6B6B, #4ECDC4, #45B7D1. Add the text "Noodl Certificate" and "{title}" on separate lines with a light color like #FFFFFF. The output must be ONLY the SVG code, starting with <svg> and ending with </svg>. Do not add any other text or markdown."""
    try:
        response = text_model.generate_content(prompt)
        svg_code = response.text.strip().replace("```svg", "").replace("```", "")
        if not svg_code.startswith('<svg'):
            raise ValueError("AI did not return valid SVG")
        return svg_code
    except Exception as e:
        app.logger.error(f"Failed to generate NFT SVG, creating fallback image: {e}")
        img = Image.new('RGB', (512, 512), color='#1a1a1a')
        d = ImageDraw.Draw(img)
        try:
            title_font = ImageFont.truetype("DejaVuSans.ttf", 32)
            subtitle_font = ImageFont.truetype("DejaVuSans.ttf", 24)
        except IOError:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        d.text((256, 220), "Noodl Certificate", font=title_font, fill="#FFFFFF", anchor="ms")
        d.text((256, 260), title, font=subtitle_font, fill="#DDDDDD", anchor="ms")
        d.rectangle([(20, 20), (512 - 20, 512 - 20)], outline="#4ECDC4", width=5)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        png_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f'<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg"><image href="data:image/png;base64,{png_b64}" height="512" width="512"/></svg>'


# --- Blockchain Helper ---
def send_tx_and_get_receipt(contract_function):
    try:
        app.logger.info(f"TX PREP: Building transaction for function: {contract_function.fn_name}")
        tx_params = {
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'maxFeePerGas': w3.to_wei('20', 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei('1.5', 'gwei'),
        }
        gas_estimate = contract_function.estimate_gas({'from': account.address})
        tx_params['gas'] = int(gas_estimate * 1.2)
        app.logger.info(f"TX PREP: Gas estimated at {gas_estimate}. Using {tx_params['gas']} with buffer.")

        transaction = contract_function.build_transaction(tx_params)
        app.logger.info("TX PREP: Signing transaction...")
        signed_tx = w3.eth.account.sign_transaction(transaction, private_key=account.key)

        app.logger.info("TX SEND: Sending raw transaction...")
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        app.logger.info(f"TX SEND: Transaction sent. Hash: {tx_hash.hex()}")

        app.logger.info("TX WAIT: Waiting for transaction receipt...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        app.logger.info(
            f"TX WAIT: Transaction receipt received. Status: {'Success' if tx_receipt.status == 1 else 'Failed'}")
        return tx_receipt
    except Exception as e:
        app.logger.error(f"TX FAILED: {e}")
        raise e


# --- User Endpoints ---
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    wallet_address = data.get('wallet_address')
    app.logger.info(f"USER: Received request to create/update user for wallet: {wallet_address}")
    if not wallet_address:
        return jsonify({"error": "wallet_address is required"}), 400

    user_data = supabase.table('users').upsert({
        'wallet_address': wallet_address,
        'name': data.get('name'),
        'country': data.get('country')
    }, on_conflict='wallet_address').execute()
    app.logger.info(f"USER: User data upserted successfully for wallet: {wallet_address}")
    return jsonify(user_data.data[0]), 201


@app.route('/users/<wallet_address>', methods=['GET'])
def get_user(wallet_address):
    app.logger.info(f"USER: Received request to get user data for wallet: {wallet_address}")
    user_data = supabase.table('users').select('*').eq('wallet_address', wallet_address).single().execute()
    if not user_data.data:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_data.data)


# --- Learning Path Endpoints ---
@app.route('/paths', methods=['GET'])
def get_all_paths():
    app.logger.info("PATH: Received request to get all learning paths.")
    data = supabase.table('learning_paths').select("id, title, description, total_levels").execute()
    return jsonify(data.data)


@app.route('/paths/generate', methods=['POST'])
def generate_new_path():
    req_data = request.get_json()
    topic = req_data.get('topic')
    creator_wallet = req_data.get('creator_wallet')
    app.logger.info(f"PATH: Received /generate request for topic: '{topic}'")
    if not topic or not creator_wallet:
        return jsonify({"error": "Topic and creator_wallet are required"}), 400

    if is_feature_enabled("FEATURE_FLAG_ENABLE_DUPLICATE_CHECK"):
        # ... (Duplicate check logic) ...
        pass

    try:
        app.logger.info("PATH-GEN: Step 1: Generating curriculum...")
        curriculum_titles = generate_curriculum(topic)
        total_levels = len(curriculum_titles)
        app.logger.info(f"PATH-GEN: Curriculum generated with {total_levels} levels.")

        app.logger.info("PATH-GEN: Step 2: Saving path metadata to Supabase...")
        path_res = supabase.table('learning_paths').insert({
            "title": topic, "description": f"A user-generated learning path about {topic}.",
            "creator_wallet": creator_wallet, "total_levels": total_levels,
            "title_embedding": get_embedding(topic) if is_feature_enabled(
                "FEATURE_FLAG_ENABLE_DUPLICATE_CHECK") else None
        }).execute()
        new_path_id = path_res.data[0]['id']

        app.logger.info(f"PATH-GEN: Step 3: Generating and saving content for {total_levels} levels...")
        all_content_for_hash = []
        for i, level_title in enumerate(curriculum_titles):
            level_number = i + 1
            level_res = supabase.table('levels').insert(
                {"path_id": new_path_id, "level_number": level_number, "level_title": level_title}).execute()
            new_level_id = level_res.data[0]['id']

            interleaved_items = generate_interleaved_level_content(topic, level_title)
            all_content_for_hash.append({"level": level_title, "items": interleaved_items})

            items_to_insert = [
                {"level_id": new_level_id, "item_index": j, "item_type": item['type'], "content": item['content']} for
                j, item in enumerate(interleaved_items)]
            supabase.table('content_items').insert(items_to_insert).execute()
            app.logger.info(f"  - Saved {len(items_to_insert)} content items for level {level_number}.")

    except Exception as e:
        app.logger.error(f"PATH-GEN: Path generation failed: {e}", exc_info=True)
        return jsonify({"error": f"Path generation failed: {e}"}), 500

    if is_feature_enabled("FEATURE_FLAG_ENABLE_BLOCKCHAIN_REGISTRATION"):
        full_content_string = json.dumps(all_content_for_hash, sort_keys=True)
        content_hash = "0x" + hashlib.sha256(full_content_string.encode()).hexdigest()
        try:
            receipt = send_tx_and_get_receipt(path_registry_contract.functions.registerPath(new_path_id, content_hash))
            supabase.table('learning_paths').update({'content_hash': content_hash}).eq('id', new_path_id).execute()
            app.logger.info(f"PATH-GEN: Path {new_path_id} registered on-chain. Tx: {receipt.transactionHash.hex()}")
        except Exception as e:
            app.logger.error(f"PATH-GEN: Blockchain registration failed for path {new_path_id}: {e}")

    return jsonify({"message": "Path created successfully", "path_id": new_path_id}), 201


@app.route('/paths/<int:path_id>/levels/<int:level_num>', methods=['GET'])
def get_level_content(path_id, level_num):
    app.logger.info(f"CONTENT: Request for path {path_id}, level {level_num}.")
    level_data = supabase.table('levels').select('id, level_title').eq('path_id', path_id).eq('level_number',
                                                                                              level_num).single().execute()
    if not level_data.data:
        return jsonify({"error": "Level not found"}), 404

    level_id = level_data.data['id']
    items_data = supabase.table('content_items').select('id, item_index, item_type, content').eq('level_id',
                                                                                                 level_id).order(
        'item_index').execute()

    return jsonify({"level_title": level_data.data['level_title'], "items": items_data.data})


# --- Progress & Scoring Endpoints ---
@app.route('/progress/start', methods=['POST'])
def start_or_get_progress():
    try:
        data = request.get_json()
        user_wallet = data.get('user_wallet')
        path_id = data.get('path_id')
        app.logger.info(f"PROGRESS: Start/get request for user {user_wallet} on path {path_id}.")
        if not user_wallet or not path_id:
            return jsonify({"error": "user_wallet and path_id are required"}), 400

        user_res = supabase.table('users').select('id').eq('wallet_address', user_wallet).maybe_single().execute()
        if not user_res or not user_res.data:
            app.logger.error(f"PROGRESS: User not found for wallet {user_wallet}")
            return jsonify({"error": "User not found. Please create the user first."}), 404
        user_id = user_res.data['id']

        progress_res = supabase.table('user_progress').select('*, levels(level_number)').eq('user_id', user_id).eq(
            'path_id', path_id).maybe_single().execute()
        if progress_res and progress_res.data:
            app.logger.info(f"PROGRESS: Found existing progress record.")
            return jsonify(progress_res.data)

        app.logger.info(f"PROGRESS: No existing progress. Starting new record.")
        first_level_res = supabase.table('levels').select('id').eq('path_id', path_id).eq('level_number',
                                                                                          1).single().execute()

        if not first_level_res.data:
            app.logger.error(f"PROGRESS: Cannot start. Path ID {path_id} or its first level does not exist.")
            return jsonify({"error": f"Learning path with ID {path_id} not found or is incomplete."}), 404

        # FIX: Separate the insert and select operations
        # Step 1: Insert the new data
        insert_res = supabase.table('user_progress').insert({
            'user_id': user_id, 'path_id': path_id, 'current_level_id': first_level_res.data['id'],
            'current_item_index': -1, 'status': 'in_progress', 'started_at': datetime.now(timezone.utc).isoformat()
        }).execute()

        new_progress_id = insert_res.data[0]['id']

        # Step 2: Select the newly created record with its relationships
        new_progress_data = supabase.table('user_progress').select('*, levels(level_number)').eq('id',
                                                                                                 new_progress_id).single().execute()

        return jsonify(new_progress_data.data), 201
    except Exception as e:
        app.logger.error(f"PROGRESS: An unexpected error occurred in /progress/start: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred while starting progress.", "details": str(e)}), 500


@app.route('/progress/update', methods=['POST'])
def update_progress():
    data = request.get_json()
    progress_id = data.get('progress_id')
    content_item_id = data.get('content_item_id')
    user_answer_index = data.get('user_answer_index')
    app.logger.info(
        f"PROGRESS: Update request for progress_id {progress_id} on item {content_item_id} with answer {user_answer_index}")

    quiz_item = supabase.table('content_items').select('content, item_index').eq('id',
                                                                                 content_item_id).single().execute()
    correct_answer_index = quiz_item.data['content']['correctAnswerIndex']
    is_correct = int(user_answer_index) == int(correct_answer_index)

    supabase.table('quiz_attempts').insert({
        'progress_id': progress_id, 'content_item_id': content_item_id,
        'user_answer_index': user_answer_index, 'is_correct': is_correct
    }).execute()
    app.logger.info(f"PROGRESS: Logged quiz attempt. Correct: {is_correct}")

    supabase.table('user_progress').update({'current_item_index': quiz_item.data['item_index']}).eq('id',
                                                                                                    progress_id).execute()

    return jsonify({"message": "Progress updated", "is_correct": is_correct})


@app.route('/scores/<wallet_address>', methods=['GET'])
def get_user_scores(wallet_address):
    app.logger.info(f"SCORES: Request for wallet {wallet_address}")
    user = supabase.table('users').select('id').eq('wallet_address', wallet_address).single().execute()
    if not user.data: return jsonify({"error": "User not found"}), 404
    user_id = user.data['id']

    progress_records = supabase.table('user_progress').select('id, path_id, status, learning_paths(title)').eq(
        'user_id', user_id).execute()

    scores = []
    for record in progress_records.data:
        attempts = supabase.table('quiz_attempts').select('is_correct', count='exact').eq('progress_id',
                                                                                          record['id']).execute()
        total_attempts = attempts.count
        correct_attempts = supabase.table('quiz_attempts').select('is_correct', count='exact').eq('progress_id',
                                                                                                  record['id']).eq(
            'is_correct', True).execute().count
        score = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
        scores.append({
            "path_id": record['path_id'], "path_title": record['learning_paths']['title'],
            "status": record['status'], "score_percent": round(score, 2),
            "correct_answers": correct_attempts, "total_questions_answered": total_attempts
        })
    return jsonify(scores)


# --- NFT Endpoints ---
@app.route('/paths/<int:path_id>/complete', methods=['POST'])
def complete_path_and_mint_nft(path_id):
    app.logger.info(f"NFT: Received /complete request for path ID: {path_id}")
    if not is_feature_enabled("FEATURE_FLAG_ENABLE_NFT_MINTING"):
        return jsonify({"message": "NFT minting is currently disabled."})
    user_wallet = request.get_json().get('user_wallet')
    if not user_wallet: return jsonify({"error": "user_wallet is required"}), 400

    app.logger.info(f"NFT: Attempting to mint for user {user_wallet}")
    metadata_url = f"{request.host_url.rstrip('/')}/nft/metadata/{path_id}"
    app.logger.info(f"NFT: Using metadata URL: {metadata_url}")

    try:
        receipt = send_tx_and_get_receipt(
            nft_contract.functions.safeMint(Web3.to_checksum_address(user_wallet), path_id, metadata_url))

        transfer_event = nft_contract.events.Transfer().process_receipt(receipt)
        if transfer_event:
            minted_token_id = transfer_event[0]['args']['tokenId']
            app.logger.info(f"NFT: Successfully minted! Token ID: {minted_token_id}")
            return jsonify({
                "message": "NFT minted successfully!", "transaction_hash": receipt.transactionHash.hex(),
                "token_id": minted_token_id, "nft_contract_address": os.getenv("NFT_CONTRACT_ADDRESS")
            })
        else:
            app.logger.error("NFT: Mint transaction succeeded, but could not find Transfer event in logs.")
            return jsonify({"error": "Mint succeeded but failed to parse Token ID."}), 500

    except Exception as e:
        error_message = str(e)
        if 'Certificate already minted' in error_message:
            detail = "Certificate already minted for this user/path."
        elif 'insufficient funds' in error_message:
            detail = "The server's wallet has insufficient funds to pay for gas."
        else:
            detail = "An unknown blockchain error occurred."
        app.logger.error(f"NFT: Minting failed. Detail: {detail}")
        return jsonify({"error": "NFT minting failed.", "detail": detail}), 500


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
    svg_data = generate_nft_svg(path_data.data['title'])
    return Response(svg_data, mimetype='image/svg+xml')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)