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
- **State-of-the-Art Hybrid Search**: Combines the `text-embedding-004` model for semantic search with traditional keyword search to deliver highly relevant and accurate results.
- **Configurable AI Models**: Leverages specific Gemini models for text (`GEMINI_MODEL_TEXT`), embeddings (`GEMINI_MODEL_EMBEDDING`), and vision/image generation (`GEMINI_MODEL_VISION`).
- **Reliable AI Interaction**: Implements a robust retry mechanism for API calls to handle transient network issues and ensure content generation completes successfully.
- **AI-Generated Certificate Images**: Dynamically creates unique pixel art emblems for NFT certificates based on the learning path's title.

### 🔗 Web3 & Blockchain Integration
- **Immutable Proof-of-Creation**: A unique hash of every learning path's content is registered on the Ethereum blockchain, providing a tamper-proof, verifiable record of the curriculum at the time of creation.
- **On-Chain NFT Certificates**: Upon successful completion of a path, users are awarded a unique, programmatically-generated pixel-art certificate, minted directly to their wallet. This serves as a permanent, transferable proof of achievement.
- **Idempotent Smart Contracts**: Both the Path Registry and NFT Certificate contracts are designed to be idempotent, allowing for "upsert" behavior. This makes the development workflow incredibly robust against database/blockchain desynchronization.

### 🚀 Robust Backend Architecture
- **Asynchronous Task Handling**: Long-running processes like AI content generation are handled in background threads, providing an immediate response to the user and allowing them to poll for status updates.
- **Persistent Task Logging**: Generation progress is logged to a database, ensuring that status updates can be retrieved even if the server restarts.
- **Atomic & Resilient Operations**: The system is designed to be atomic and resilient. If any part of the multi-step generation process fails, it aims to gracefully recover or roll back changes, including cleaning up partially created database entries.
- **Secure & Modular Routes**: The API is organized into logical, secure blueprints (Users, Paths, Progress, NFTs, Search) for clarity and maintainability.

### 💻 Developer Experience
- **Live Demo UI**: A user-facing, interactive Gradio application that simulates the real user experience for learning and path creation.
- **Extensive Configuration**: Application behavior can be easily modified via environment variables, including feature flags to toggle major functionalities like blockchain registration or duplicate checking.
- **Detailed Documentation**: This README and the `API.md` provide a complete guide to setup, architecture, and every available API endpoint.

---

## 🏛️ System Architecture

The application is designed with a clean separation of concerns, ensuring scalability and ease of maintenance.

```
+------------------+      +------------------+      +------------------+
|   Frontend / UI  |----->|   Flask Server   |<---->|  Google Gemini   |
| (Gradio LiveDemo)|      |  (main.py, app)  |      |       API        |
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
- An [Infura](https://infura.io/) account for an Ethereum RPC URL (or any other Sepolia RPC provider).
- [MetaMask](https://metamask.io/) wallet with Sepolia test ETH.
- [Pinata](https://www.pinata.cloud/) account for IPFS hosting of NFT images and metadata.

### 2. Initial Setup
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repo-name NoodlBackend
    cd NoodlBackend 
    ```
    (Adjust the path if your backend is in a subdirectory like `src/backend/`)
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
Create a `.env` file in the root of your backend project by copying `.env.example`. Fill in all required values.
**Crucial**: Ensure your `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in the `.env` file match the *actual* Supabase project you are using (e.g., `https://hffmreieoqtcukvyesqc.supabase.co` from your logs, not a placeholder).

### 4. Database Setup
1.  In your Supabase project dashboard, navigate to **Database** > **Extensions**.
2.  Search for and enable `vector` (for pgvector).
3.  Go to the **SQL Editor**, paste the entire content of `database/schema.sql`, and run the query. This script is idempotent and can be run multiple times safely.

### 5. Smart Contract Deployment
1.  Open the [Remix IDE](https://remix.ethereum.org/).
2.  Create and paste the content of the `.sol` files from the `contracts/` directory (`LearningPathRegistry.sol` and `NoodlCertificate.sol`).
3.  Compile both contracts using a `0.8.20` (or compatible, as specified in pragma) compiler version.
4.  Connect your MetaMask wallet to Remix (ensure it's on the Sepolia test network).
5.  Deploy `LearningPathRegistry.sol`.
6.  Deploy `NoodlCertificate.sol`, providing your `BACKEND_WALLET_ADDRESS` (from your `.env`) as the `initialOwner` argument in the Remix deployment interface.
7.  Copy the deployed contract addresses and paste them into the `PATH_REGISTRY_CONTRACT_ADDRESS` and `NFT_CONTRACT_ADDRESS` fields in your `.env` file.
8.  From the "Solidity Compiler" tab in Remix (after successful compilation), find the "ABI" button for each contract. Copy the ABI (it's a JSON array) and save them as `LearningPathRegistry.json` and `NoodlCertificate.json` respectively, inside the `contracts/` directory of your project, replacing the existing placeholder files if necessary.

### 6. Certificates Directory
Ensure a directory named `certificates` exists in the root of your backend project (e.g., alongside `main.py`). This is where temporary certificate images will be stored before being uploaded to IPFS.
```bash
mkdir certificates
```

---

## 🏃‍♂️ Running the Application

The application can be run with a single command, which intelligently starts services based on your `.env` file.

```bash
python main.py
```
- The **Flask API server** will be available at `http://localhost:5000` (if `RUN_API_SERVER=true`).
- The **Gradio Live Demo UI** will be available at `http://localhost:9999` (or your `LIVE_DEMO_PORT` if `RUN_LIVE_DEMO=true`).

---

## 🧪 API Endpoints
For a detailed list of all available API endpoints, including request/response formats and examples, refer to the `API.md` file in this directory. It provides comprehensive documentation on how to interact with the backend services.

---

## 🔄 Restart Guide (After a Long Break or for a Clean Slate)

If you're returning to the project after a while, or if you want to ensure a completely fresh start (especially regarding on-chain data and local caches), follow these steps:

1.  **Clean Local Caches:**
    *   **Delete `certificates` folder:** This folder stores locally generated NFT images before they are uploaded to IPFS. Deleting it ensures fresh images are generated if needed.
        ```bash
        # In your project's root directory (where main.py is)
        rm -rf certificates  # macOS/Linux
        # rmdir /s /q certificates # Windows
        ```
    *   Recreate the folder:
        ```bash
        mkdir certificates
        ```
2.  **Reset Supabase Database (Optional, for a full data reset):**
    *   The most thorough way is to drop all tables and re-run the `database/schema.sql` script.
    *   Alternatively, you can delete all rows from the tables:
        ```sql
        DELETE FROM user_nfts;
        DELETE FROM level_progress;
        DELETE FROM user_progress;
        DELETE FROM content_items;
        DELETE FROM levels;
        DELETE FROM learning_paths;
        DELETE FROM users;
        DELETE FROM task_progress_logs;
        ```
    *   Then, re-run the `database/schema.sql` script from your Supabase SQL Editor to ensure all functions and tables are correctly set up.
3.  **Redeploy Smart Contracts (Recommended for a full on-chain reset):**
    *   Follow the steps in **Section 5. Smart Contract Deployment** again. This will give you new contract addresses.
    *   **Crucially, update your `.env` file** with the new `PATH_REGISTRY_CONTRACT_ADDRESS` and `NFT_CONTRACT_ADDRESS`.
    *   This is important because the old contracts will still exist on the blockchain with their old state. Redeploying gives you a clean slate.
4.  **Update Environment Variables:**
    *   Ensure all keys in your `.env` file (`GEMINI_API_KEY`, `SUPABASE_SERVICE_KEY`, `PINATA_API_KEY`, etc.) are still valid and active.
5.  **Rebuild Virtual Environment (Optional, if Python dependencies seem problematic):**
    ```bash
    # Deactivate if active
    # deactivate 
    rm -rf .venv # macOS/Linux
    # rmdir /s /q .venv # Windows
    python -m venv .venv
    # Activate: .venv\Scripts\activate (Windows) or source .venv/bin/activate (macOS/Linux)
    pip install -r requirements.txt
    ```
6.  **Start the Application:**
    ```bash
    python main.py
    ```

By following these steps, you can ensure a clean environment, which is especially helpful if you've made significant changes or if the application state (database, blockchain) has become inconsistent during development.
