import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Manages all configuration for the application, loaded from environment variables.
    """
    # Feature Flags
    RUN_API_SERVER = os.getenv("RUN_API_SERVER", "true").lower() == "true"
    RUN_TESTING_UI = os.getenv("RUN_TESTING_UI", "true").lower() == "true"
    FEATURE_FLAG_ENABLE_BLOCKCHAIN_REGISTRATION = os.getenv("FEATURE_FLAG_ENABLE_BLOCKCHAIN_REGISTRATION",
                                                            "true").lower() == "true"
    FEATURE_FLAG_ENABLE_NFT_MINTING = os.getenv("FEATURE_FLAG_ENABLE_NFT_MINTING", "true").lower() == "true"

    # API Keys and URLs
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    ETHEREUM_NODE_URL = os.getenv("ETHEREUM_NODE_URL")

    # Gemini Models
    GEMINI_MODEL_TEXT = os.getenv("GEMINI_MODEL_TEXT", "gemini-1.5-flash-latest")

    # Web3
    BACKEND_WALLET_PRIVATE_KEY = os.getenv("BACKEND_WALLET_PRIVATE_KEY")
    BACKEND_WALLET_ADDRESS = os.getenv("BACKEND_WALLET_ADDRESS")

    # Smart Contracts
    PATH_REGISTRY_CONTRACT_ADDRESS = os.getenv("PATH_REGISTRY_CONTRACT_ADDRESS")
    NFT_CONTRACT_ADDRESS = os.getenv("NFT_CONTRACT_ADDRESS")

    # App Logic
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.85))

    # Flask
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "a_very_secret_noodl_key_for_dev")


# A single, importable instance of the configuration
config = Config()