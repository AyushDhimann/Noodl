# 🔌 API Endpoint Documentation

This document provides a comprehensive guide to all available API endpoints.

## 👤 User Endpoints

Endpoints for managing user profiles and their created content.

---

### Create or Update a User
- **Endpoint:** `POST /users`
- **Description:** Creates a new user or updates an existing one. This endpoint uses checkpoint logic: it will only fill in `name` or `country` if they are currently empty, preventing accidental overwrites.
- **Request Body:**
  ```json
  {
    "wallet_address": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
    "name": "Alice",
    "country": "USA"
  }
  ```
- **Success (201):** Returns the full user object.
- **Error (400):** If `wallet_address` is missing.

---

### Get User Profile
- **Endpoint:** `GET /users/<wallet_address>`
- **Description:** Retrieves the complete public profile for a single user, including their wallet address, name, and country. This endpoint requires no authentication.
- **Success (200):** Returns the user object.
- **Error (404):** If the user is not found.

---

### Get User-Created Paths
- **Endpoint:** `GET /users/<wallet_address>/paths`
- **Description:** Retrieves a list of all learning paths created by a specific user, ordered by most recent first.
- **Success (200):** Returns an array of path objects.

---

### Get User-Created Path Count
- **Endpoint:** `GET /users/<wallet_address>/paths/count`
- **Description:** Retrieves the total number of learning paths created by a user.
- **Success (200):**
  ```json
  {
    "creator_wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
    "path_count": 5
  }
  ```

## 📚 Path & Content Endpoints

Endpoints for generating, retrieving, and managing learning paths and their content.

---

### Generate a New Learning Path
- **Endpoint:** `POST /paths/generate`
- **Description:** (Asynchronous) Kicks off a background task to generate a complete learning path.
- **Request Body:**
  ```json
  {
    "topic": "The history of the internet",
    "creator_wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"
  }
  ```
- **Success (202):**
  ```json
  {
    "message": "Path generation started.",
    "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
  }
  ```
- **Error (409):** If a path with a highly similar title already exists.

---

### Get Generation Status
- **Endpoint:** `GET /paths/generate/status/<task_id>`
- **Description:** Poll this endpoint to get progress updates for a generation task.
- **Success (200):** Returns an array of log objects for the task.

---

### Get a Random Topic
- **Endpoint:** `GET /paths/random-topic`
- **Description:** Generates a single, interesting topic for a learning path.
- **Success (200):**
  ```json
  {
    "topic": "The History of the Rosetta Stone"
  }
  ```

---

### Get All Public Paths
- **Endpoint:** `GET /paths`
- **Description:** Retrieves a list of all created learning paths.
- **Success (200):** Returns an array of path objects.

---

### Get Full Path Details for a Specific User
- **Endpoint:** `GET /paths/<path_id>/<wallet_address>`
- **Description:** Retrieves a complete, nested JSON object for a single learning path, enriched with user-specific progress. Includes `is_complete` flags for the path and each level, and an `is_minted` flag for the NFT status.
- **Success (200):** Returns the full, nested path object with user-specific metadata.
- **Error (404):** If the path is not found.

---

### Get Specific Level Content
- **Endpoint:** `GET /paths/<path_id>/levels/<level_num>`
- **Description:** Retrieves the content for a single level within a path.
- **Success (200):** Returns the level object with its content items.

---

### Delete a Learning Path
- **Endpoint:** `DELETE /paths/<path_id>`
- **Description:** Deletes a learning path. Can only be performed by the original creator.
- **Request Body:**
  ```json
  {
    "user_wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"
  }
  ```
- **Success (200):** Confirms successful deletion.
- **Error (403):** If the `user_wallet` does not match the creator.

## 🔍 Search Endpoints

---

### Search for Paths
- **Endpoint:** `GET /search`
- **Description:** Performs a hybrid semantic and keyword search across path titles and descriptions.
- **Query Parameters:** `q` (string, min 2 chars)
- **Success (200):** Returns an array of matches.
  ```json
  [
    {
      "id": 12,
      "match_type": "keyword",
      "title": "🐍 An Introduction to Python",
      "similarity": null
    }
  ]
  ```

## 📈 Progress & Scoring Endpoints

Endpoints for tracking and retrieving user progress and scores.

---

### Upsert Level Progress
- **Endpoint:** `POST /progress/level`
- **Description:** Creates or updates a user's progress for a level. Automatically marks the path as complete if all levels are finished.
- **Request Body:**
  ```json
  {
    "user_wallet": "0x...",
    "path_id": 1,
    "level_index": 3,
    "correct_answers": 8,
    "total_questions": 10
  }
  ```
- **Success (200):** Confirms the update.

---

### Get Path Completion Status
- **Endpoint:** `GET /progress/path/<path_id>/<wallet_address>/completed`
- **Description:** Checks if a user has completed an entire learning path.
- **Success (200):**
  ```json
  {
    "is_complete": true
  }
  ```

---

### Get Level Completion Status
- **Endpoint:** `GET /progress/level/<path_id>/<level_index>/<wallet_address>/completed`
- **Description:** Checks if a user has completed a specific level within a path.
- **Success (200):**
  ```json
  {
    "is_complete": false
  }
  ```

---

### Get All User Scores
- **Endpoint:** `GET /scores/<wallet_address>`
- **Description:** Retrieves an aggregated summary of scores for all paths a user has made progress on.
- **Success (200):** Returns an array of score summary objects.

---

## 🖼️ NFT Endpoints

Endpoints for minting and retrieving NFT certificates.

---

### Complete a Path & Mint NFT
- **Endpoint:** `POST /paths/<path_id>/complete`
- **Description:** Initiates the minting process for an NFT certificate. The path must be complete before this can be called.
- **Request Body:**
  ```json
  {
    "user_wallet": "0x..."
  }
  ```
- **Success (200):**
  ```json
  {
      "message": "NFT minted and metadata set successfully!",
      "token_id": 74418501,
      "nft_contract_address": "0x...",
      "metadata_url": "ipfs://bafkreihdwdcefgh45...",
      "explorer_url": "https://sepolia.etherscan.io/tx/0x...",
      "nft_gateway_url": "https://beige-elaborate-hummingbird-35.mypinata.cloud/ipfs/bafkreihdwdcefgh45..."
  }
  ```
- **Error (400):** If the path is not yet complete.

---

### Get All User NFTs
- **Endpoint:** `GET /nfts/<wallet_address>`
- **Description:** Retrieves a list of all NFT certificates a user has earned, with a full gateway URL for the metadata.
- **Success (200):** Returns an array of NFT objects.
  ```json
  [
    {
      "learning_paths": {
        "title": "🛡️ Recognize and Conquer Gaslighting."
      },
      "metadata_url": "https://beige-elaborate-hummingbird-35.mypinata.cloud/ipfs/QmYja38cwqgZWFCKevvPZR1Q3QMmRrE6Z2Sey3VbLViuV6",
      "minted_at": "2025-06-13T13:58:49.541875+00:00",
      "nft_contract_address": "0xEC94A5c84c850366F5E06BD6FfB9188c384d33e1",
      "path_id": 1,
      "token_id": 74418507
    }
  ]
  ```
  