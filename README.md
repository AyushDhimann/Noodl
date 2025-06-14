# 🍜 Noodl: AI-Powered Learning with Web3 Credentials

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![Flutter](https://img.shields.io/badge/Flutter-Stable-blue?style=for-the-badge&logo=flutter)](https://flutter.dev/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-AI-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)
[![Web3.py](https://img.shields.io/badge/Web3.py-6.x-orange?style=for-the-badge)](https://web3py.readthedocs.io/)
[![Supabase](https://img.shields.io/badge/Supabase-2.x-darkgreen?style=for-the-badge&logo=supabase)](https://supabase.com/)
[![WalletConnect](https://img.shields.io/badge/WalletConnect-v2-blueviolet?style=for-the-badge&logo=walletconnect)](https://walletconnect.com/)

**Noodl is a next-generation, AI-driven educational platform that gamifies your journey through knowledge. Securely log in using your Web3 wallet, embark on dynamically generated learning paths on any topic imaginable, and earn unique NFT certificates as immutable proof of your achievements.**

Our mission is to make learning more engaging, accessible, and verifiable by combining the power of cutting-edge AI with the decentralized trust of blockchain technology.

---

## ✨ Key Features

Noodl offers a rich set of features across its frontend and backend systems:

### 🤖 AI-Powered Content Engine (Backend)
- **Dynamic Course Creation**: Transforms user queries (e.g., "learn quantum physics") into engaging, SEO-friendly course titles (e.g., `⚛️ Unveiling the Quantum Realm: A Beginner's Guide`) and compelling descriptions.
- **Adaptive Curriculum Design**: AI analyzes topic complexity to generate a syllabus with an appropriate number of lessons, ensuring comprehensive coverage.
- **Rich, Interleaved Content**: Each lesson features a mix of detailed, Markdown-formatted slides and interactive multiple-choice quizzes to reinforce learning and assess understanding.
- **"I'm Feeling Lucky" Topic Generation**: A dedicated endpoint allows the AI to suggest novel and interesting learning topics for spontaneous discovery.
- **State-of-the-Art Hybrid Search**: Utilizes Google's `text-embedding-004` for semantic search combined with traditional keyword search for highly relevant path discovery.
- **Configurable AI Models**: Leverages specific Google Gemini models for text generation (`GEMINI_MODEL_TEXT`), embeddings (`GEMINI_MODEL_EMBEDDING`), and unique certificate image generation (`GEMINI_MODEL_VISION`).
- **Reliable AI Interaction**: Implements robust retry mechanisms for AI API calls to handle transient issues and ensure content generation reliability.
- **AI-Generated Certificate Emblems**: Dynamically creates unique, symbolic pixel art emblems for NFT certificates based on the learning path's title.

### 🔗 Web3 & Blockchain Integration (Backend & Frontend)
- **Secure Web3 Login**:
    - **MetaMask via WalletConnect v2**: Seamless and secure login on Android (14 or lower) and iOS.
    - **Manual Wallet Address Login**: Provides an alternative for platforms where WebView interactions might be restricted (e.g., Android 15+).
- **Immutable Proof-of-Creation**: A unique hash of every learning path's content is registered on the Ethereum (Sepolia Testnet) blockchain, providing a tamper-proof record of the curriculum.
- **On-Chain NFT Certificates**: Upon successful path completion, users are awarded unique NFT certificates (ERC721) minted directly to their wallet, serving as permanent, verifiable proof of achievement.
- **Idempotent Smart Contracts**: Path Registry and NFT Certificate contracts are designed for robust "upsert" behavior, enhancing resilience against desynchronization.

### 📱 Frontend & User Experience (Flutter App)
- **Gamified Learning**: Earn NFT trophies as credentials, making learning rewarding.
- **Session Persistence**: User wallet sessions are persisted using `SharedPreferences` for a smooth return experience.
- **Custom Theming & Rich UI**: Features custom fonts, animated elements, gradients, and SVG branding for an engaging and modern user interface with dark mode support.
- **Interactive Learning Interface**: Users navigate through slides and quizzes, with progress tracked and displayed.
- **Dashboard**: View enrolled paths, created paths, overall progress, and search for new learning adventures.

### 🚀 Robust Backend Architecture
- **Asynchronous Task Handling**: Long-running processes like AI course generation are handled in background threads, providing immediate API responses while users can poll for status updates.
- **Persistent Task Logging**: Generation progress is logged to a Supabase database, allowing status retrieval even across server restarts.
- **Atomic & Resilient Operations**: Designed for graceful recovery and rollback, including cleanup of partially created database entries if generation fails.
- **Modular & Secure API**: Organized into logical Flask blueprints for users, paths, progress, NFTs, and search.

---

## 📸 Demo & Screenshots

*The Noodl mobile app provides an intuitive and visually appealing interface for learners.*

| | | | |
|---|---|---|---|
| ![IMG_9733](https://github.com/user-attachments/assets/72793115-3fa5-4130-a108-cd7fc29738c1) | ![IMG_9734](https://github.com/user-attachments/assets/dafffa0d-ec68-493b-af08-69d6624aaddb) | ![IMG_9735](https://github.com/user-attachments/assets/de820a41-38ac-440f-9c40-9afc6c68f6ea) | ![IMG_9736](https://github.com/user-attachments/assets/98135719-1088-4bf4-af15-063df8644a28) |
| ![IMG_9737](https://github.com/user-attachments/assets/69bac1cd-65bb-46ad-a061-5eafc809eaca) | ![IMG_9738](https://github.com/user-attachments/assets/c8ffc3ff-e134-41a1-ba23-edf2589f7ecc) | ![IMG_9739](https://github.com/user-attachments/assets/895ea187-fcc4-4240-9460-1f6835e74890) | ![IMG_9740](https://github.com/user-attachments/assets/4e642a88-0c9e-453e-bc2a-d9d89d8de0f7) |



A **Live Demo UI** for the backend (using Gradio) is also available to showcase path generation and API interactions directly.

---

## 🛠️ Tech Stack

**Frontend (Mobile App):**
- **Flutter** (Stable Channel)
- **Provider** (State Management)
- **WalletConnect v2 (web3modal_flutter)** & **MetaMask SDK**
- **SharedPreferences** (Session Persistence)
- Custom Theming (Gradients, Fonts, Dark Mode)

**Backend (API & Services):**
- **Python 3.11+**
- **Flask** (Web Framework)
- **Google Gemini API** (AI Content Generation, Embeddings, Vision)
- **Supabase** (PostgreSQL Database, Vector Storage, Auth Helpers)
- **Web3.py** (Ethereum Blockchain Interaction)
- **IPFS & Pinata** (Decentralized Storage for NFT Assets)
- **Solidity** (Smart Contracts: ERC721 for NFTs, Path Registry)
- **Gradio** (Live Demo UI for Backend)

---

## 🏛️ System Architecture

The application follows a client-server model with distinct frontend and backend components, interacting with AI services, a database, and the blockchain.

```
+---------------------+     +------------------+      +------------------+
| Flutter Mobile App  |---->|   Flask Server   |<---->|  Google Gemini   |
| (Frontend: src/fe)  |     | (Backend: src/be)|      |       API        |
+---------------------+     +-------+----------+      +------------------+
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
*(Simplified: `src/fe` for frontend, `src/be` for backend for diagram clarity)*

---

## 🚀 Getting Started

Follow these steps to set up and run the Noodl platform locally.

### 1. Prerequisites
- **Flutter SDK** (Stable Channel): [Installation Guide](https://flutter.dev/docs/get-started/install)
- **Python 3.11+**: [Downloads](https://www.python.org/downloads/)
- **pip** & `venv` (usually comes with Python)
- **Supabase Account**: For the database. [Sign Up](https://supabase.com/)
- **Google AI Studio Account**: For a Gemini API Key. [Get API Key](https://ai.google.dev/)
- **Infura Account** (or other Sepolia RPC provider): For Ethereum node access. [Sign Up](https://infura.io/)
- **MetaMask Wallet**: With Sepolia test ETH. [Download](https://metamask.io/)
- **Pinata Account**: For IPFS hosting of NFT assets. [Sign Up](https://www.pinata.cloud/)
- **Node.js & npm** (Optional, if you need to run JavaScript maintenance scripts like `MERGER.js`)

### 2. Clone the Repository
```bash
git clone https://github.com/AyushDhimann/Noodl.git
cd noodl
```

### 3. Backend Setup
Navigate to the backend directory (assuming `src/backend/`):
```bash
cd src/backend 
```

1.  **Create and activate a Python virtual environment:**
    ```bash
    # On Windows
    python -m venv .venv
    .venv\Scripts\activate

    # On macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```
2.  **Install backend dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment Variables:**
    *   Copy `.env.example` to a new file named `.env` in the `src/backend/` directory.
    *   Fill in all required values:
        *   `GEMINI_API_KEY`
        *   `SUPABASE_URL` (e.g., `https://hffmreieoqtcukvyesqc.supabase.co`)
        *   `SUPABASE_SERVICE_KEY` (anon or service_role key)
        *   `ETHEREUM_NODE_URL` (your Infura Sepolia RPC URL)
        *   `BACKEND_WALLET_PRIVATE_KEY` & `BACKEND_WALLET_ADDRESS` (from your MetaMask for Sepolia)
        *   `PINATA_API_KEY`, `PINATA_API_SECRET`, `PINATA_GATEWAY_URL`
4.  **Setup Supabase Database:**
    *   In your Supabase project: **Database** > **Extensions** > Enable `vector`.
    *   Go to **SQL Editor** > **New Query**. Paste the entire content of `src/backend/database/schema.sql` and run it.
5.  **Deploy Smart Contracts (Sepolia Testnet):**
    *   Use [Remix IDE](https://remix.ethereum.org/).
    *   Compile `LearningPathRegistry.sol` and `NoodlCertificate.sol` (from `src/backend/contracts/`) with compiler `0.8.20` (or as per pragma).
    *   Connect MetaMask to Remix (Sepolia network).
    *   Deploy `LearningPathRegistry.sol`.
    *   Deploy `NoodlCertificate.sol`, providing your `BACKEND_WALLET_ADDRESS` (from `.env`) as the `initialOwner`.
    *   Update `PATH_REGISTRY_CONTRACT_ADDRESS` and `NFT_CONTRACT_ADDRESS` in your `.env` file with the deployed addresses.
    *   Copy the ABIs from Remix and save them as `LearningPathRegistry.json` and `NoodlCertificate.json` in `src/backend/contracts/`, replacing placeholders if necessary.
6.  **Create Certificates Directory:**
    In the `src/backend/` directory:
    ```bash
    mkdir certificates
    ```

### 4. Frontend Setup
Navigate to the frontend directory (assuming `src/frontend/`):
```bash
cd ../frontend # If you were in src/backend
# Or from project root: cd src/frontend
```

1.  **Install Flutter dependencies:**
    ```bash
    flutter pub get
    ```

---

## 🏃‍♂️ Running the Application

1.  **Start the Backend Server:**
    *   Ensure your Python virtual environment for the backend is activated.
    *   In the `src/backend/` directory:
        ```bash
        python main.py
        ```
    *   The Flask API will run on `http://localhost:5000`.
    *   The Gradio Live Demo UI for the backend will run on `http://localhost:9999` (or your configured `LIVE_DEMO_PORT`).

2.  **Run the Frontend Flutter App:**
    *   Ensure you have an emulator running or a device connected.
    *   In the `src/frontend/` directory:
        ```bash
        flutter run
        ```

---

## 🧪 API Documentation
For detailed information on all backend API endpoints, request/response formats, and examples, please refer to the `API.md` file located in the `src/backend/` directory.

---

## 🔄 Restart Guide (After a Long Break or for a Clean Slate)

If you're returning to the project or want a fresh start:

1.  **Clean Backend Caches:**
    *   In `src/backend/`, delete and recreate the `certificates` folder:
        ```bash
        rm -rf certificates # macOS/Linux
        # rmdir /s /q certificates # Windows
        mkdir certificates
        ```
2.  **Reset Supabase Database (Optional, for full data reset):**
    *   Execute `DELETE FROM table_name;` for all tables in your Supabase SQL Editor (see README in `src/backend/` for table list) or drop tables.
    *   Re-run the `src/backend/database/schema.sql` script.
3.  **Redeploy Smart Contracts (Recommended for full on-chain reset):**
    *   Follow **Backend Setup: Step 5** again.
    *   **Update `.env`** with new contract addresses.
4.  **Verify Environment Variables:** Ensure all API keys and URLs in `src/backend/.env` are current.
5.  **Rebuild Virtual Environments (Optional):** If dependencies are problematic, delete `.venv` (backend) and run `flutter clean` (frontend), then reinstall dependencies.
6.  **Start applications** as described in "Running the Application."

---

## ⚠️ Important Notes
*   **Android 15+ MetaMask Issue**: Due to platform changes, MetaMask's WebView connection might be blocked on Android 15 and newer. Users on these versions should use the **manual wallet address login** option in the Flutter app.
*   **Backend API URL in Frontend**: Ensure the `BACKEND_URL` constant in the Flutter app (e.g., in `lib/services/api_service.dart` or similar) points to your running backend, typically `http://localhost:5000` for local development.

---

This project was developed with passion for learning and innovation. We hope you enjoy exploring Noodl! 


### Made with ❤️ by [Ayush Dhimann](https://github.com/AyushDhimann) and [Parth Kalia](https://github.com/TheParthK)
