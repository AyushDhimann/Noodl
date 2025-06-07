# SETUP

### **Overview of the Project**

We will build the complete backend for "Noodl," a Duolingo-like educational app.

*   **Functionality:**
    1.  AI dynamically generates a full curriculum (variable number of levels) for any given topic.
    2.  AI generates slides and quizzes for each level.
    3.  AI checks for and prevents the creation of duplicate or very similar topics.
    4.  A hash of the course content is stored on the blockchain for immutable proof.
    5.  Upon completion, a user is rewarded with an NFT certificate featuring a unique, AI-generated image.
*   **Tech Stack:**
    *   **Backend:** Python with Flask
    *   **AI:** Google Gemini (for text, embeddings, and image generation)
    *   **Database:** Supabase (with pgvector for similarity search)
    *   **Blockchain:** Ethereum (Sepolia Testnet) via Web3.py
    *   **Testing UI:** Gradio

---

### **Step 1: Prerequisites & Initial Setup**

Before writing any code, you need accounts and keys from the following services:

1.  **MetaMask:** Install the [MetaMask browser extension](https://metamask.io/). Create a wallet and switch it to the **Sepolia Testnet**. Get free test ETH from a faucet like [sepoliafaucet.com](https://sepoliafaucet.com/).
2.  **Infura:** Sign up for a free [Infura](https://www.infura.io/) account. Create a new project and get your **Sepolia RPC URL**.
3.  **Google AI Studio:** Go to [Google AI Studio](https://aistudio.google.com/) and get a **Gemini API Key**.
4.  **Supabase:** Sign up for a free [Supabase](https://supabase.io/) account. Create a new project and note down your **Project URL** and your **`service_role` key** (from Project Settings > API).

---

### **Step 2: Smart Contracts (Solidity)**

We need two smart contracts. You will deploy these using the [Remix IDE](https://remix.ethereum.org/).

**Deployment Instructions:**
1.  Open Remix. Create two new files: `LearningPathRegistry.sol` and `NoodlCertificate.sol`.
2.  Paste the code below into the respective files.
3.  For `NoodlCertificate.sol`, Remix will automatically fetch the OpenZeppelin contracts.
4.  Go to the "Solidity Compiler" tab, select a compiler version like `0.8.18`, and compile both contracts.
5.  Go to the "Deploy & Run Transactions" tab.
    *   Set ENVIRONMENT to "Injected Provider - MetaMask" (ensure MetaMask is on Sepolia).
    *   Select each contract from the dropdown and click "Deploy".
    *   Confirm both transactions in MetaMask.
6.  **Crucially, copy the deployed addresses for both contracts.** You will need them for your `.env` file.
7.  Also, from the "Solidity Compiler" tab, copy the **ABI** for both contracts.

---

### **Step 3: Supabase Database Setup**

1.  In your Supabase project dashboard, go to **Database** > **Extensions**. Find `vector` and enable it.
2.  Go to the **SQL Editor** > **New query**. Paste and run the entire script below.

```sql
-- 1. Create the table for learning paths
CREATE TABLE learning_paths (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  title TEXT NOT NULL,
  description TEXT,
  creator_wallet TEXT,
  content_hash TEXT,
  is_premade BOOLEAN DEFAULT false,
  title_embedding vector(768), -- For similarity search
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Create the table for level content
CREATE TABLE levels (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  path_id BIGINT REFERENCES learning_paths(id) ON DELETE CASCADE,
  level_number INT NOT NULL,
  level_title TEXT, -- Title for the dynamic level
  content JSONB, -- Stores the slides and quiz JSON
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(path_id, level_number)
);

-- 3. Create the function for similarity search
CREATE OR REPLACE FUNCTION match_similar_paths(
  query_embedding vector(768),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id bigint,
  title text,
  description text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    lp.id,
    lp.title,
    lp.description,
    1 - (lp.title_embedding <=> query_embedding) AS similarity
  FROM
    learning_paths lp
  WHERE 1 - (lp.title_embedding <=> query_embedding) > match_threshold
  ORDER BY
    similarity DESC
  LIMIT match_count;
END;
$$;
```

---

### **Step 4: Backend Project Structure & Setup**

Create a project folder for your backend. Inside it, create the following files and folders:

```
noodl_backend/
├── templates/
│   └── index.html  (We won't use this, but Flask likes the folder)
├── app.py
├── test_ui.py
├── requirements.txt
└── .env
```


#### `.env` file
Rename `.env.example` to `.env` file and fill it with your own keys and addresses. **NEVER commit this file to Git.**

---



# **Usage**

1.  **Install Dependencies:** Open your terminal in the project folder and run:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the Backend:** In the same terminal, start the Flask server. It will run on `http://localhost:5000`.
    ```bash
    flask run
    ```
3.  **Run the UI:** Open a **new, separate terminal** in the same project folder. Start the Gradio UI.
    ```bash
    python UITesting.py
    ```
4.  **Test:** Your terminal will print a URL (like `http://127.0.0.1:7860`). Open this URL in your browser. You can now use the interface to interact with your running backend.
    *   Go to the "Generate New Path" tab, enter a topic and your MetaMask wallet address, and click generate. Watch the Flask server's console for logs.
    *   Once a path is created, go to the "View Content" tab to fetch it.
    *   Finally, go to the "Mint NFT" tab to receive your certificate. You can view it by connecting your wallet to [https://testnets.opensea.io/](https://testnets.opensea.io/).