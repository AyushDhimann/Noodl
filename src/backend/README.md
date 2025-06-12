# 🍜 Noodl Backend: AI-Powered Learning with Web3 Integration

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![Web3.py](https://img.shields.io/badge/Web3.py-6.x-orange?style=for-the-badge)](https://web3py.readthedocs.io/)
[![Supabase](https://img.shields.io/badge/Supabase-2.x-darkgreen?style=for-the-badge&logo=supabase)](https://supabase.com/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-AI-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)

Welcome to the Noodl backend, a powerful and robust engine for a next-generation, AI-driven educational platform. This project provides a complete server-side solution, from dynamic, on-the-fly course creation to immutable, on-chain proof of completion via NFTs.

The core philosophy is to leverage cutting-edge AI to create high-quality, structured learning paths for any topic imaginable, and to use Web3 technology to bring verifiable ownership and achievement to the learning process.

---

## ✨ Key Features

### 🤖 AI-Powered Content Engine
- **Dynamic Title & Description Generation**: Automatically transforms a simple user query (e.g., "learn python") into an engaging, SEO-friendly course title (`🐍 Python Programming: From Zero to Hero`) and a compelling description.
- **Adaptive Curriculum Design**: The AI analyzes the complexity of the topic to generate a syllabus with an appropriate number of lessons—fewer for simple topics, more for complex ones.
- **Rich, Interleaved Content**: Each lesson is a rich mix of detailed, markdown-formatted slides and interactive multiple-choice quizzes to reinforce learning.
- **Creative Generation**: Utilizes a configurable temperature setting for the Gemini model to foster more creative and engaging content.
- **"I'm Feeling Lucky" Topic Generation**: A dedicated endpoint can ask the AI to invent a novel, interesting topic, powering spontaneous discovery.
- **State-of-the-Art Hybrid Search**: Combines the latest `text-embedding-004` model for semantic search with traditional keyword search to deliver highly relevant and accurate results.
- **Reliable AI Interaction**: Implements a robust retry mechanism for API calls to handle transient network issues and ensure content generation completes successfully.

### 🔗 Web3 & Blockchain Integration
- **Immutable Proof-of-Creation**: A unique hash of every learning path's content is registered on the Ethereum blockchain, providing a tamper-proof, verifiable record of the curriculum at the time of creation.
- **On-Chain NFT Certificates**: Upon successful completion of a path, users are awarded a unique, programmatically-generated pixel-art certificate, minted directly to their wallet. This serves as a permanent, transferable proof of achievement.
- **Idempotent Smart Contracts**: Both the Path Registry and NFT Certificate contracts are designed to be idempotent, allowing for "upsert" behavior. This makes the development workflow incredibly robust against database/blockchain desynchronization.

### 🚀 Robust Backend Architecture
- **Asynchronous Task Handling**: Long-running processes like AI content generation are handled in background threads, providing an immediate response to the user and allowing them to poll for status updates.
- **Persistent Task Logging**: Generation progress is logged to a database, ensuring that status updates can be retrieved even if the server restarts.
- **Atomic & Resilient Operations**: The system is designed to be atomic and resilient. If any part of the multi-step generation process fails (e.g., due to a network error), it can gracefully recover or roll back changes, preventing orphaned data and duplicate record errors.
- **Secure & Modular Routes**: The API is organized into logical, secure blueprints (Users, Paths, Progress, NFTs, Search) for clarity and maintainability.

### 💻 Developer Experience
- **Multiple UIs for Development**:
    - **Live Demo UI**: A user-facing, interactive Gradio application that simulates the real user experience.
    - **Testing UI**: A comprehensive Gradio UI that provides a full suite of tools to test every single API endpoint individually.
- **Extensive Configuration**: Application behavior can be easily modified via environment variables, including feature flags to toggle major functionalities like blockchain registration or duplicate checking.
- **Detailed Documentation**: This README provides a complete guide to setup, architecture, and every available API endpoint.

---

## 🏛️ System Architecture

The application is designed with a clean separation of concerns, ensuring scalability and ease of maintenance.

```
+------------------+      +------------------+      +------------------+
|   Frontend / UI  |----->|   Flask Server   |<---->|  Google Gemini   |
| (e.g., Gradio)   |      |  (main.py, app)  |      |       API        |
+------------------+      +-------+----------+      +------------------+
                                  |
                  +---------------+---------------------+
                  |                                     |
        +---------v---------+                 +---------v---------+
        |  Routes (API)     |                 |  Services Layer   |
        | (user, path, etc.)|                 | (Business Logic)  |
        +---------+---------+                 +----+----------+---+
                  |                              |              |
                  |         +--------------------+              |
                  |         |                                   |
        +---------v---------v-+                     +-----------v-----------+
        |   Database (Supabase) |                     | Blockchain (Ethereum) |
        | - Users, Paths, Logs  |                     | - Smart Contracts     |
        | - Vector Similarity   |                     | - Path Registry, NFTs |
        +-----------------------+                     +-----------------------+
```

---

## 🚀 Getting Started

Follow these steps to get the Noodl backend up and running on your local machine.

### 1. Prerequisites
- [Python 3.11+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/) & `venv`
- A [Supabase](https://supabase.com/) account for the database.
- A [Google AI Studio](https://ai.google.dev/) account for a Gemini API Key.
- An [Infura](https://infura.io/) account for an Ethereum RPC URL.
- [MetaMask](https://metamask.io/) wallet with Sepolia test ETH.

### 2. Initial Setup
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/AyushDhimann/DuoLingo
    cd DuoLingo/src/backend/
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    # On Windows
    python -m venv .venv
    .venv\Scripts\activate

    # On macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Environment Configuration
Create a `.env` file by copying `.env.example`. Fill in all required values.

```env
# .env
FLASK_APP=main.py
FLASK_DEBUG=True

# --- APIs and Services ---
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
SUPABASE_URL="YOUR_SUPABASE_PROJECT_URL"
SUPABASE_SERVICE_KEY="YOUR_SUPABASE_SERVICE_ROLE_KEY"
ETHEREUM_NODE_URL="YOUR_INFURA_SEPOLIA_RPC_URL"
BLOCK_EXPLORER_URL="https://sepolia.etherscan.io"

# --- Gemini Configuration ---
GEMINI_MODEL_TEXT="gemini-1.5-flash-latest"
GEMINI_MODEL_EMBEDDING="models/text-embedding-004"
GENERATION_TEMPERATURE=1.5

# --- Web3 ---
BACKEND_WALLET_PRIVATE_KEY="YOUR_BACKEND_WALLET_PRIVATE_KEY" # Do not include '0x' prefix
BACKEND_WALLET_ADDRESS="YOUR_BACKEND_WALLET_ADDRESS"

# --- Smart Contracts ---
PATH_REGISTRY_CONTRACT_ADDRESS="DEPLOYED_REGISTRY_CONTRACT_ADDRESS"
NFT_CONTRACT_ADDRESS="DEPLOYED_NFT_CONTRACT_ADDRESS"

# --- Feature Flags & App Behavior ---
RUN_API_SERVER="true"
RUN_TESTING_UI="false"
RUN_LIVE_DEMO="true"
LIVE_DEMO_PORT=9999
FEATURE_FLAG_ENABLE_BLOCKCHAIN_REGISTRATION="true"
FEATURE_FLAG_ENABLE_NFT_MINTING="true"
FEATURE_FLAG_ENABLE_DUPLICATE_CHECK="true"
```

### 4. Database Setup
1.  In your Supabase project dashboard, navigate to **Database** > **Extensions**.
2.  Search for and enable `vector`.
3.  Go to the **SQL Editor**, paste the entire content of `database/schema.sql`, and run the query. This script is idempotent and can be run multiple times safely.

### 5. Smart Contract Deployment
1.  Open the [Remix IDE](https://remix.ethereum.org/).
2.  Create and paste the content of the `.sol` files from the `contracts/` directory.
3.  Compile both contracts using a `0.8.20` (or compatible) compiler version.
4.  Connect your MetaMask wallet (on Sepolia network).
5.  Deploy `LearningPathRegistry.sol`.
6.  Deploy `NoodlCertificate.sol`, providing your wallet address as the `initialOwner`.
7.  Copy the deployed contract addresses into your `.env` file.
    > **Note**: Both contracts are designed to be idempotent. The `LearningPathRegistry` allows the owner to overwrite path hashes, and `NoodlCertificate` allows the owner to update a user's token URI if it already exists. This is intentional for development robustness, making the system resilient to database resets without requiring contract redeployment.
8.  From the "Solidity Compiler" tab in Remix, copy the ABI for each contract and save them as `LearningPathRegistry.json` and `NoodlCertificate.json` inside the `contracts/` directory.

---

## 🏃‍♂️ Running the Application

The application can be run with a single command, which intelligently starts services based on your `.env` file.

```bash
python main.py
```
- The **Flask API server** will be available at `http://localhost:5000`.
- The **Gradio Live Demo UI** will be available at `http://localhost:9999` (if `RUN_LIVE_DEMO=true`).
- The **Gradio Testing UI** will be available at `http://localhost:7000` (if `RUN_TESTING_UI=true`).