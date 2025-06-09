# 🍜 Noodl Backend
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![Web3.py](https://img.shields.io/badge/Web3.py-6.x-orange?style=for-the-badge)](https://web3py.readthedocs.io/)
[![Supabase](https://img.shields.io/badge/Supabase-2.x-darkgreen?style=for-the-badge&logo=supabase)](https://supabase.com/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-AI-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)

The complete backend for **Noodl**, a next-generation, AI-powered educational platform with Web3 integration. This project provides a robust API for creating dynamic learning paths, tracking user progress, and issuing on-chain NFT certificates.

## ✨ Features

- **AI-Powered Content Generation:**
    - **Title Enhancement:** Automatically rephrases user topics into engaging, course-like titles and prepends a relevant emoji.
    - **Dynamic Curriculum:** Generates a full, multi-level curriculum for any given topic using Google Gemini.
    - **Interleaved Learning:** Creates a rich learning experience with a mix of detailed markdown-based slides and interactive quizzes.
- **Robust & Reliable Generation:**
    - **Persistent Asynchronous Progress:** Uses a database-backed queue, so the status of long-running generation tasks can be checked even after a server restart.
    - **API Retry Mechanism:** Automatically retries failed AI API calls to handle transient network issues.
    - **Atomic Operations:** Ensures that if path generation fails midway, any incomplete data is automatically cleaned up from the database.
- **Duplicate Path Detection:** Uses vector embeddings on the AI-enhanced title to check for and prevent the creation of highly similar learning paths *before* generation begins.
- **Web3 Integration:**
    - **Immutable Proof:** Registers a hash of each learning path's content on the Ethereum blockchain for tamper-proof verification.
    - **NFT Certificates:** Mints unique, on-chain SVG-based NFT certificates to users upon path completion.
- **Path & Progress Management:**
    - **Live Progress Tracking:** Logs a user's real-time location within a learning path as they navigate through content.
    - **Secure Deletion:** Provides an endpoint for a path's original creator to delete their content.
- **Comprehensive Testing UI:** Includes a standalone Gradio interface with a modern aesthetic for testing all API endpoints and simulating the user learning experience.

---

## 🏛️ Architecture

The project follows a clean, modular architecture to separate concerns:

```
backend/
├── app/                  # Core Flask application package
│   ├── __init__.py       # Initializes the Flask app and services
│   ├── config.py         # Manages all environment variables and feature flags
│   ├── services/         # Business logic layer
│   │   ├── ai_service.py
│   │   ├── blockchain_service.py
│   │   └── supabase_service.py
│   └── routes/           # API endpoint definitions (Blueprints)
│       ├── path_routes.py
│       ├── user_routes.py
│       ├── progress_routes.py
│       └── nft_routes.py
│
├── contracts/            # Solidity smart contracts and their ABIs
│
├── database/             # SQL schema for the database
│
├── ui/                   # Standalone Gradio testing UI
│   └── testing_ui.py
│
├── main.py               # Main entry point to run the application
├── requirements.txt
└── .env
```

---

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### 1. Prerequisites

Ensure you have the following installed:
- [Python 3.11+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/) for package management
- A virtual environment tool like `venv` (recommended)

You will also need accounts and API keys from:
- **MetaMask:** A wallet with Sepolia test ETH.
- **Infura:** An RPC URL for the Sepolia testnet.
- **Google AI Studio:** A Gemini API Key.
- **Supabase:** A project URL and `service_role` key.

### 2. Initial Setup

**Clone the repository:**
```bash
git clone https://github.com/AyushDhimann/DuoLingo
cd DuoLingo/src/backend/
```

**Create and activate a virtual environment:**
```bash
# On Windows
python -m venv .venv
.venv\Scripts\activate

# On macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the `backend` directory by copying `.env.example` or creating a new one. Fill in all the required values with your keys and addresses.

```env
# .env
FLASK_APP=main.py
FLASK_DEBUG=True

# --- APIs and Services ---
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
SUPABASE_URL="YOUR_SUPABASE_PROJECT_URL"
SUPABASE_SERVICE_KEY="YOUR_SUPABASE_SERVICE_KEY"
# ... (fill in all other variables) ...

# --- Smart Contracts ---
BLOCK_EXPLORER_URL="https://sepolia.etherscan.io"

# --- FEATURE FLAGS ---
RUN_API_SERVER="true"
RUN_TESTING_UI="true"
FEATURE_FLAG_ENABLE_BLOCKCHAIN_REGISTRATION="true"
FEATURE_FLAG_ENABLE_NFT_MINTING="true"
FEATURE_FLAG_ENABLE_DUPLICATE_CHECK="true"
```

### 4. Smart Contract Deployment

1.  Open the [Remix IDE](https://remix.ethereum.org/).
2.  Create and paste the content of the `.sol` files from the `contracts/` directory.
3.  Compile both contracts using a `0.8.20` (or compatible) compiler version.
4.  Connect your MetaMask wallet (on Sepolia network).
5.  Deploy `LearningPathRegistry.sol`.
6.  Deploy `NoodlCertificate.sol`, making sure to **provide your wallet address** as the `initialOwner` argument in the Remix deploy panel.
7.  Copy the deployed contract addresses into your `.env` file.
8.  From the "Solidity Compiler" tab in Remix, copy the ABI for each contract and save them as `LearningPathRegistry.json` and `NoodlCertificate.json` inside the `contracts/` directory.

### 5. Database Setup

1.  In your Supabase project dashboard, navigate to **Database** > **Extensions**.
2.  Search for `vector` and enable it.
3.  Go to the **SQL Editor**, paste the entire content of `database/schema.sql`, and run the query. This script now includes the `task_progress_logs` table and a trigger function to enable persistent status tracking.

---

## 🏃‍♂️ Running the Application

This project uses a central entry point to manage the API server and the testing UI.

**To run the application:**
(Ensure `RUN_API_SERVER` and `RUN_TESTING_UI` are set to `true` in your `.env` file)

```bash
python main.py
```

This will:
- Start the Flask API server in a background thread on `http://localhost:5000`.
- Start the Gradio Testing UI in the main thread on `http://localhost:7000`.

### Using the Testing UI

Navigate to `http://localhost:7000` in your browser. The redesigned UI is organized into tabs that allow you to test every feature of the backend:
- **Generate:** Create new learning paths with real-time, persistent progress updates.
- **Learn:** Simulate a user's journey through a lesson, with live progress tracking.
- **Data & Users:** Create, manage, and view user profiles and their created paths. Includes a "Danger Zone" for deleting paths.
- **Mint NFT:** Award a certificate of completion.

---

## 🔌 API Endpoints

The backend exposes the following RESTful API endpoints:

#### User Routes (`/users`)
- `POST /users`: Create or update a user.
  - **Body Example**: `{"wallet_address": "0x...", "name": "Alice", "country": "USA"}`
- `GET /users/<wallet_address>`: Fetch a user's profile.
- `GET /users/<wallet_address>/paths`: Fetch all learning paths created by a specific user.
- `GET /users/<wallet_address>/paths/count`: Get the number of paths created by a user.

#### Path Routes (`/paths`)
- `GET /paths`: Get a list of all available learning paths.
- `POST /paths/generate`: **(Async)** Starts a background task to generate a new path. Returns a `task_id`.
  - **Body Example**: `{"topic": "Quantum Computing", "creator_wallet": "0x..."}`
- `GET /paths/generate/status/<task_id>`: **(Persistent)** Poll this endpoint to get progress updates for a generation task. Status survives server restarts.
- `GET /paths/<id>/levels/<num>`: Get the interleaved content for a specific level.
- `DELETE /paths/<path_id>`: Deletes a learning path. The request must be made by the original creator.
  - **Body Example**: `{"user_wallet": "0x..."}`

#### Progress Routes
- `POST /progress/start`: Start a learning path for a user or get existing progress.
  - **Body Example**: `{"user_wallet": "0x...", "path_id": 1}`
- `POST /progress/update`: Log a quiz attempt and update user progress.
  - **Body Example**: `{"progress_id": 1, "content_item_id": 123, "user_answer_index": 2}`
- `POST /progress/location`: Update the user's current location (item index) within a path.
  - **Body Example**: `{"progress_id": 1, "item_index": 5}`
- `GET /scores/<wallet_address>`: Get all scores for a specific user.

#### NFT Routes
- `POST /paths/<id>/complete`: Mint an NFT certificate for a completed path.
  - **Body Example**: `{"user_wallet": "0x..."}`
- `GET /nft/metadata/<id>`: Get the JSON metadata for a specific NFT.
- `GET /nft/image/<id>`: Get the SVG image for a specific NFT.
