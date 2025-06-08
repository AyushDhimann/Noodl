# 🍜 Noodl Backend
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![Web3.py](https://img.shields.io/badge/Web3.py-6.x-orange?style=for-the-badge)](https://web3py.readthedocs.io/)
[![Socket.IO](https://img.shields.io/badge/Socket.IO-5.x-yellow?style=for-the-badge&logo=socket.io)](https://python-socketio.readthedocs.io/)
[![Supabase](https://img.shields.io/badge/Supabase-2.x-darkgreen?style=for-the-badge&logo=supabase)](https://supabase.com/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-AI-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)

The complete backend for **Noodl**, a next-generation, AI-powered educational platform with Web3 integration. This project provides a robust API for creating dynamic learning paths, tracking user progress, and issuing on-chain NFT certificates.

## ✨ Features

- **Dynamic AI Curriculum:** Automatically generates a full, multi-level curriculum for any given topic using Google Gemini.
- **Interleaved Learning:** Creates a rich learning experience with a mix of detailed markdown-based slides and interactive quizzes.
- **AI-Generated Explanations:** Quizzes include fun facts or detailed explanations for correct answers, enhancing the learning loop.
- **Web3 Integration:**
    - **Immutable Proof:** Registers a hash of each learning path's content on the Ethereum blockchain for tamper-proof verification.
    - **NFT Certificates:** Mints unique, on-chain SVG-based NFT certificates to users upon path completion.
- **Real-time Progress Updates:** Utilizes WebSockets to provide live feedback to the frontend during the long-running content generation process.
- **Scalable Architecture:** Built with a modular, service-oriented structure for easy maintenance and expansion.
- **Comprehensive Testing UI:** Includes a standalone Gradio interface for testing all API endpoints and simulating the user learning experience.

---

## 🏛️ Architecture

The project follows a clean, modular architecture to separate concerns:

```
backend/
├── app/                  # Core Flask application package
│   ├── __init__.py       # Initializes the Flask app, extensions, and services
│   ├── config.py         # Manages all environment variables and feature flags
│   ├── services/         # Business logic layer
│   │   ├── ai_service.py
│   │   ├── blockchain_service.py
│   │   └── supabase_service.py
│   └── routes/           # API endpoint definitions (Blueprints)
│       ├── path_routes.py
│       ├── user_routes.py
│       ├── progress_routes.py
│       ├── nft_routes.py
│       └── websocket_routes.py
│
├── contracts/            # Solidity smart contracts
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
git clone <your-repo-url>
cd backend
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

Rename the `.env.example` file to `.env` and fill in all the required values with your keys and addresses.

```env
# .env
FLASK_APP=main.py
FLASK_DEBUG=True

# --- APIs and Services ---
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
# ... (fill in all other variables) ...

# --- FEATURE FLAGS ---
RUN_API_SERVER="true"
RUN_TESTING_UI="true"
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
3.  Go to the **SQL Editor**, paste the entire content of `database/schema.sql`, and run the query.

---

## 🏃‍♂️ Running the Application

This project uses a central entry point to manage the API server and the testing UI.

**To run both the API and the UI:**
(Ensure `RUN_API_SERVER` and `RUN_TESTING_UI` are set to `true` in your `.env` file)

```bash
python main.py
```

This will:
- Start the Flask API server on `http://localhost:5000`.
- Start the Gradio Testing UI on `http://localhost:7000`.

**To run only the API server:**
```bash
python main.py api
```

**To run only the testing UI:**
(Assumes the API server is already running separately)
```bash
python main.py ui
```

### Using the Testing UI

Navigate to `http://localhost:7000` in your browser. The UI is organized into tabs that allow you to test every feature of the backend:
- **Interactive Learner:** Simulate a user's journey through a lesson.
- **Paths & Content:** Generate new learning paths with real-time WebSocket progress updates.
- **Users:** Create and manage user profiles.
- **Progress & Scoring:** Track user progress and fetch scores.
- **Mint NFT:** Award a certificate of completion.

---

## 🔌 API Endpoints

The backend exposes the following RESTful API endpoints:

#### User Routes (`/users`)
- `POST /users`: Create or update a user.
- `GET /users/<wallet_address>`: Fetch a user's profile.

#### Path Routes (`/paths`)
- `GET /paths`: Get a list of all available learning paths.
- `POST /paths/generate`: Generate a new learning path (long-running, uses WebSockets for progress).
- `GET /paths/<id>/levels/<num>`: Get the interleaved content for a specific level.

#### Progress Routes
- `POST /progress/start`: Start a learning path for a user or get existing progress.
- `POST /progress/update`: Log a quiz attempt and update user progress.
- `GET /scores/<wallet_address>`: Get all scores for a specific user.

#### NFT Routes
- `POST /paths/<id>/complete`: Mint an NFT certificate for a completed path.
- `GET /nft/metadata/<id>`: Get the JSON metadata for a specific NFT.
- `GET /nft/image/<id>`: Get the SVG image for a specific NFT.
