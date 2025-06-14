import logging
from flask import Flask
from supabase import create_client, Client
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import google.generativeai as genai
from app.config import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(config)

supabase_client: Client = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
logger.info("Supabase client initialized.")

genai.configure(api_key=config.GEMINI_API_KEY)

generation_config = genai.types.GenerationConfig(temperature=config.GENERATION_TEMPERATURE)

text_model = genai.GenerativeModel(
    config.GEMINI_MODEL_TEXT,
    generation_config=generation_config
)
logger.info("Gemini AI text model initialized.")

w3 = Web3(Web3.HTTPProvider(config.ETHEREUM_NODE_URL))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
if w3.is_connected():
    logger.info(f"Web3 client connected to chain ID: {w3.eth.chain_id}")
    account = w3.eth.account.from_key(config.BACKEND_WALLET_PRIVATE_KEY)
    w3.eth.default_account = account.address
    logger.info(f"Web3 default account set to: {account.address}")
else:
    logger.error("CRITICAL: Failed to connect to Ethereum node.")
    account = None

from app.routes import user_routes, path_routes, progress_routes, nft_routes, search_routes

app.register_blueprint(user_routes.bp)
app.register_blueprint(path_routes.bp)
app.register_blueprint(progress_routes.bp)
app.register_blueprint(nft_routes.bp)
app.register_blueprint(search_routes.bp)
