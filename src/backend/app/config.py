import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Manages all configuration for the application, loaded from environment variables.
    """

    RUN_API_SERVER = os.getenv("RUN_API_SERVER", "true").lower() == "true"
    RUN_LIVE_DEMO = os.getenv("RUN_LIVE_DEMO", "true").lower() == "true"
    FEATURE_FLAG_ENABLE_BLOCKCHAIN_REGISTRATION = os.getenv("FEATURE_FLAG_ENABLE_BLOCKCHAIN_REGISTRATION",
                                                            "true").lower() == "true"
    FEATURE_FLAG_ENABLE_NFT_MINTING = os.getenv("FEATURE_FLAG_ENABLE_NFT_MINTING", "true").lower() == "true"
    FEATURE_FLAG_ENABLE_DUPLICATE_CHECK = os.getenv("FEATURE_FLAG_ENABLE_DUPLICATE_CHECK", "true").lower() == "true"

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    ETHEREUM_NODE_URL = os.getenv("ETHEREUM_NODE_URL")
    BLOCK_EXPLORER_URL = os.getenv("BLOCK_EXPLORER_URL")
    PINATA_API_KEY = os.getenv("PINATA_API_KEY")
    PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")
    PINATA_GATEWAY_URL = os.getenv("PINATA_GATEWAY_URL")

    LIVE_DEMO_PORT = int(os.getenv("LIVE_DEMO_PORT", 9999))

    GEMINI_MODEL_TEXT = os.getenv("GEMINI_MODEL_TEXT", "gemini-2.0-flash")
    GEMINI_MODEL_EMBEDDING = os.getenv("GEMINI_MODEL_EMBEDDING", "models/text-embedding-004")
    GEMINI_MODEL_VISION = os.getenv("GEMINI_MODEL_VISION", "gemini-2.0-flash-preview-image-generation")

    GENERATION_TEMPERATURE = float(os.getenv("GENERATION_TEMPERATURE", 1.5))

    BACKEND_WALLET_PRIVATE_KEY = os.getenv("BACKEND_WALLET_PRIVATE_KEY")
    BACKEND_WALLET_ADDRESS = os.getenv("BACKEND_WALLET_ADDRESS")

    PATH_REGISTRY_CONTRACT_ADDRESS = os.getenv("PATH_REGISTRY_CONTRACT_ADDRESS")
    NFT_CONTRACT_ADDRESS = os.getenv("NFT_CONTRACT_ADDRESS")

    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.85))
    MAX_CONCURRENT_LEVEL_GENERATORS = int(os.getenv("MAX_CONCURRENT_LEVEL_GENERATORS", 3))

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "b7359d34c833f6dd3f302e28b8ec2d237dd3fd5543717fd7ce9f2ecaf66ae6be")

config = Config()
