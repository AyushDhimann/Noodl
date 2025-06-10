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
- **Reliable AI Interaction**: Implements a robust retry mechanism for API calls to handle transient network issues and ensure content generation completes successfully.

### 🔗 Web3 & Blockchain Integration
- **Immutable Proof-of-Creation**: A unique hash of every learning path's content is registered on the Ethereum blockchain, providing a tamper-proof, verifiable record of the curriculum at the time of creation.
- **On-Chain NFT Certificates**: Upon successful completion of a path, users are awarded a unique, AI-generated SVG-based NFT certificate, minted directly to their wallet. This serves as a permanent, transferable proof of achievement.

### 🚀 Robust Backend Architecture
- **Asynchronous Task Handling**: Long-running processes like AI content generation are handled in background threads, providing an immediate response to the user and allowing them to poll for status updates.
- **Persistent Task Logging**: Generation progress is logged to a database, ensuring that status updates can be retrieved even if the server restarts.
- **Atomic Operations & Cleanup**: The system is designed to be atomic. If any part of the multi-step generation process fails, all partially created data (database records, etc.) is automatically rolled back, preventing orphaned data.
- **Secure & Modular Routes**: The API is organized into logical, secure blueprints (Users, Paths, Progress, NFTs) for clarity and maintainability.

### 💻 Developer Experience
- **Comprehensive Testing UI**: Comes with a pre-built, aesthetic Gradio UI that provides a full suite of tools to test every single API endpoint without needing a separate frontend application.
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
                  +---------------+---------------+
                  |                               |
        +---------v---------+           +---------v---------+
        |  Routes (API)     |           |  Services Layer   |
        | (user, path, etc.)|           | (Business Logic)  |
        +---------+---------+           +---------+---------+
                  |                               |
                  |         +---------------------+
                  |         |
        +---------v---------v-+
        |   Database (Supabase) |
        | - Users, Paths, Logs  |
        | - Vector Similarity   |
        +-----------------------+

        +-----------------------+
        | Blockchain (Ethereum) |
        | - Smart Contracts     |
        | - Path Registry, NFTs |
        +-----------------------+
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

# --- Web3 ---
BACKEND_WALLET_PRIVATE_KEY="YOUR_BACKEND_WALLET_PRIVATE_KEY" # Do not include '0x' prefix
BACKEND_WALLET_ADDRESS="YOUR_BACKEND_WALLET_ADDRESS"

# --- Smart Contracts ---
PATH_REGISTRY_CONTRACT_ADDRESS="DEPLOYED_REGISTRY_CONTRACT_ADDRESS"
NFT_CONTRACT_ADDRESS="DEPLOYED_NFT_CONTRACT_ADDRESS"

# --- Feature Flags ---
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
8.  From the "Solidity Compiler" tab in Remix, copy the ABI for each contract and save them as `LearningPathRegistry.json` and `NoodlCertificate.json` inside the `contracts/` directory.

---

## 🏃‍♂️ Running the Application

The application can be run with a single command, which starts both the API server and the testing UI.

```bash
python main.py
```
- The Flask API server will be available at `http://localhost:5000`.
- The Gradio Testing UI will be available at `http://localhost:7000`.

---

## 🔌 API Endpoint Documentation

### User Routes
- **Create or Update a User**  
  **Endpoint**: `POST /users`  
  **Description**: Creates a new user record or updates an existing one based on the provided wallet address. This is an "upsert" operation.
  - **Request Body**:
    ```json
    {
      "wallet_address": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
      "name": "Alice",
      "country": "USA"
    }
    ```
  - **Success Response (201)**: Returns the created or updated user object.
  - **Error Response (400)**: If `wallet_address` is missing.

- **Get User Profile**  
  **Endpoint**: `GET /users/<wallet_address>`  
  **Description**: Retrieves the profile information for a single user.
  - **URL Parameters**:
    - `wallet_address` (string): The user's public wallet address.
  - **Success Response (200)**: Returns the user object.
  - **Error Response (404)**: If no user is found with the given address.

- **Get User-Created Paths**  
  **Endpoint**: `GET /users/<wallet_address>/paths`  
  **Description**: Retrieves a list of all learning paths created by a specific user.
  - **URL Parameters**:
    - `wallet_address` (string): The creator's public wallet address.
  - **Success Response (200)**: Returns an array of learning path objects.

- **Get User-Created Path Count**  
  **Endpoint**: `GET /users/<wallet_address>/paths/count`  
  **Description**: Retrieves the total number of learning paths created by a specific user.
  - **URL Parameters**:
    - `wallet_address` (string): The creator's public wallet address.
  - **Success Response (200)**:
    ```json
    {
      "creator_wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
      "path_count": 5
    }
    ```

### Path Routes
- **Generate a New Learning Path**  
  **Endpoint**: `POST /paths/generate`  
  **Description**: **(Asynchronous)** Kicks off a background task to generate a complete learning path. It performs several steps: rephrases the topic, generates a description, checks for duplicates, generates a curriculum, and then generates content for each lesson.
  - **Request Body**:
    ```json
    {
      "topic": "The history of the internet",
      "creator_wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"
    }
    ```
  - **Success Response (202)**: Indicates the task has been accepted for processing.
    ```json
    {
      "message": "Path generation started.",
      "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    }
    ```
  - **Error Response (400)**: If `topic` or `creator_wallet` are missing.
  - **Error Response (409)**: If a path with a highly similar title already exists (and the feature flag is enabled).

- **Get Generation Status**  
  **Endpoint**: `GET /paths/generate/status/<task_id>`  
  **Description**: **(Persistent)** Poll this endpoint to get real-time progress updates for a generation task. The logs are stored in the database and survive server restarts.
  - **URL Parameters**:
    - `task_id` (string): The UUID returned from the `/generate` endpoint.
  - **Success Response (200)**:
    ```json
    {
      "progress": [
        { "status": "✅ Designing your curriculum..." },
        { "status": "Curriculum designed with 8 lessons." },
        { "status": "🎉 SUCCESS: Path generation complete!", "data": { "path_id": 12 } }
      ]
    }
    ```
  - **Error Response (404)**: If the `task_id` is not found.

- **Get All Public Paths**  
  **Endpoint**: `GET /paths`  
  **Description**: Retrieves a list of all created learning paths.
  - **Success Response (200)**: Returns an array of learning path objects.

- **Get Full Path Details**  
  **Endpoint**: `GET /paths/<path_id>`  
  **Description**: Retrieves a complete, nested JSON object for a single learning path, including its title, description, and all of its levels with their associated content items.
  - **URL Parameters**:
    - `path_id` (integer): The unique ID of the learning path.
  - **Success Response (200)**: Returns the full path object.
  - **Error Response (404)**: If the path is not found.

- **Delete a Learning Path**  
  **Endpoint**: `DELETE /paths/<path_id>`  
  **Description**: Deletes a learning path and all of its associated levels and content. This action is protected; only the original creator of the path can delete it.
  - **URL Parameters**:
    - `path_id` (integer): The ID of the path to delete.
  - **Request Body**:
    ```json
    {
      "user_wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"
    }
    ```
  - **Success Response (200)**: Confirms successful deletion.
  - **Error Response (403)**: If the `user_wallet` does not match the path's creator.
  - **Error Response (404)**: If the path is not found.

### Progress & Scoring Routes
- **Start or Get Progress on a Path**  
  **Endpoint**: `POST /progress/start`  
  **Description**: Initiates a learning session for a user on a specific path. If progress already exists, it returns the existing record; otherwise, it creates a new one.
  - **Request Body**:
    ```json
    {
      "user_wallet": "0x...",
      "path_id": 1
    }
    ```
  - **Success Response (200 or 201)**: Returns the user progress object.

- **Update User's Current Location**  
  **Endpoint**: `POST /progress/location`  
  **Description**: A "fire-and-forget" endpoint to log the user's current position (e.g., which slide they are viewing) in a lesson.
  - **Request Body**:
    ```json
    {
      "progress_id": 1,
      "item_index": 3
    }
    ```
  - **Success Response (200)**: Confirms the location was updated.

- **Log a Quiz Attempt**  
  **Endpoint**: `POST /progress/update`  
  **Description**: Logs a user's answer to a quiz question and updates their progress.
  - **Request Body**:
    ```json
    {
      "progress_id": 1,
      "content_item_id": 45,
      "user_answer_index": 2
    }
    ```
  - **Success Response (200)**: Returns whether the answer was correct.

- **Get User Scores**  
  **Endpoint**: `GET /scores/<wallet_address>`  
  **Description**: Retrieves a summary of scores for a user across all paths they have attempted.
  - **URL Parameters**:
    - `wallet_address` (string): The user's public wallet address.
  - **Success Response (200)**: Returns an array of score summary objects.

### NFT Routes
- **Complete a Path & Mint NFT**  
  **Endpoint**: `POST /paths/<path_id>/complete`  
  **Description**: Initiates the minting of an NFT certificate for a user who has completed a path.
  - **URL Parameters**:
    - `path_id` (integer): The ID of the completed path.
  - **Request Body**:
    ```json
    {
      "user_wallet": "0x..."
    }
    ```
  - **Success Response (200)**: Returns the transaction details and token ID.

- **Get NFT Metadata**  
  **Endpoint**: `GET /nft/metadata/<path_id>`  
  **Description**: Returns the ERC721 standard JSON metadata for a specific NFT, which points to the image and describes its attributes.
  - **URL Parameters**:
    - `path_id` (integer): The ID of the path corresponding to the NFT.

- **Get NFT Image**  
  **Endpoint**: `GET /nft/image/<path_id>`  
  **Description**: Returns the AI-generated SVG image for the NFT.
  - **URL Parameters**:
    - `path_id` (integer): The ID of the path corresponding to the NFT.