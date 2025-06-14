# 🔌 API Endpoint Documentation

This document provides a comprehensive guide to all available API endpoints for the Noodl backend.

## 👤 User Endpoints

Endpoints for managing user profiles and their created content.

---

### Create or Update a User
- **Endpoint:** `POST /users`
- **Description:** Creates a new user or updates an existing one. This endpoint uses checkpoint logic: it will only fill in `name` or `country` if they are currently empty for an existing user, preventing accidental overwrites of existing data. If the user does not exist, a new record is created with all provided details.
- **Request Body:**
  ```json
  {
    "wallet_address": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
    "name": "Alice",
    "country": "USA"
  }
  ```
- **Success (201):** Returns the full user object (either newly created or existing, potentially updated).
  ```json
  {
    "id": 1,
    "wallet_address": "0xab5801a7d398351b8be11c439e05c5b3259aec9b",
    "name": "Alice",
    "country": "USA",
    "created_at": "2025-06-14T12:00:00.000000+00:00"
  }
  ```
- **Error (400):** If `wallet_address` is missing.

---

### Get User Profile
- **Endpoint:** `GET /users/<wallet_address>`
- **Description:** Retrieves the complete public profile for a single user, including their wallet address, name, and country.
- **Success (200):** Returns the user object.
  ```json
  {
    "id": 1,
    "wallet_address": "0xab5801a7d398351b8be11c439e05c5b3259aec9b",
    "name": "Alice",
    "country": "USA",
    "created_at": "2025-06-14T12:00:00.000000+00:00"
  }
  ```
- **Error (404):** If the user is not found.

---

### Get User-Enrolled Paths
- **Endpoint:** `GET /users/<wallet_address>/paths`
- **Description:** Retrieves a list of all learning paths a user is enrolled in (has started progress on), ordered by most recent first. Includes progress details.
- **Success (200):** Returns an array of path objects with progress.
  ```json
  [
    {
      "id": 5,
      "title": "🚀 Introduction to Rocket Science",
      "short_description": "Learn the basics of rockets.",
      "total_levels": 5,
      "created_at": "2025-06-14T10:00:00.000000+00:00",
      "is_complete": false,
      "completed_levels": 2
    }
  ]
  ```
- **Note:** Returns an empty array `[]` if the user is not found or has no enrolled paths.

---

### Get User-Created Path Count
- **Endpoint:** `GET /users/<wallet_address>/paths/count`
- **Description:** Retrieves the total number of learning paths created by a specific user.
- **Success (200):**
  ```json
  {
    "creator_wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
    "path_count": 3
  }
  ```

## 📚 Path & Content Endpoints

Endpoints for generating, retrieving, and managing learning paths and their content.

---

### Generate a New Learning Path
- **Endpoint:** `POST /paths/generate`
- **Description:** (Asynchronous) Kicks off a background task to generate a complete learning path based on a topic.
- **Request Body:**
  ```json
  {
    "topic": "The history of the internet",
    "creator_wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"
  }
  ```
- **Success (202 Accepted):** Indicates the task has been accepted for processing.
  ```json
  {
    "message": "Path generation started.",
    "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
  }
  ```
- **Error (400):** If `topic` or `creator_wallet` are missing.
- **Error (409 Conflict):** If a path with a highly similar title already exists (and duplicate check is enabled).
  ```json
  {
    "error": "A very similar learning path already exists.",
    "similar_path": {
      "id": 12,
      "title": "🌐 A Brief History of the World Wide Web",
      "short_description": "Explore the origins of the internet.",
      "similarity": 0.92
    }
  }
  ```
- **Error (500):** If the generation process fails to start.

---

### Get Generation Status
- **Endpoint:** `GET /paths/generate/status/<task_id>`
- **Description:** Poll this endpoint to get progress updates for an asynchronous path generation task.
- **Success (200):** Returns an array of log objects for the task.
  ```json
  {
    "progress": [
      {"status": "🤔 Analyzing your request..."},
      {"status": "Request analyzed. Intent: **LEARN**"},
      {"status": "✅ Designing your curriculum..."},
      {"status": "Curriculum designed with 5 lessons."},
      {"status": "🎉 SUCCESS: Path generation complete!", "data": {"path_id": 101, "explorer_url": "https://sepolia.etherscan.io/tx/0x..."}}
    ]
  }
  ```
- **Error (404):** If the `task_id` is not found.

---

### Get a Random Topic
- **Endpoint:** `GET /paths/random-topic`
- **Description:** Generates a single, interesting topic suitable for a new learning path.
- **Success (200):**
  ```json
  {
    "topic": "The History and Cultural Impact of Coffee"
  }
  ```
- **Error (500):** If topic generation fails.

---

### Get All Public Paths
- **Endpoint:** `GET /paths`
- **Description:** Retrieves a list of all created learning paths (basic details).
- **Success (200):** Returns an array of path objects.
  ```json
  [
    {
      "id": 1,
      "title": "🐍 An Introduction to Python",
      "short_description": "Learn Python from scratch.",
      "total_levels": 7
    },
    {
      "id": 2,
      "title": "🎨 The Art of Digital Painting",
      "short_description": "Master digital art techniques.",
      "total_levels": 5
    }
  ]
  ```

---

### Get Full Path Details (Generic)
- **Endpoint:** `GET /paths/<path_id>`
- **Description:** Retrieves a complete, nested JSON object for a single learning path, including all levels and content items. Also includes total slide and question counts for the path.
- **Success (200):** Returns the full, nested path object.
  ```json
  {
    "id": 1,
    "title": "🐍 An Introduction to Python",
    "short_description": "Learn Python from scratch.",
    "long_description": "This course covers all the fundamental concepts of Python programming...",
    "creator_wallet": "0x...",
    "content_hash": "0x...",
    "total_levels": 3,
    "intent_type": "learn",
    "created_at": "2025-06-14T12:00:00Z",
    "total_slides": 15,
    "total_questions": 6,
    "levels": [
      {
        "id": 10,
        "path_id": 1,
        "level_number": 1,
        "level_title": "🐣 Getting Started",
        "content_items": [
          {"id": 100, "level_id": 10, "item_index": 0, "item_type": "slide", "content": "### Welcome!"},
          {"id": 101, "level_id": 10, "item_index": 1, "item_type": "quiz", "content": {"question": "...", "options": [], ...}}
        ]
      }
      // ... more levels
    ]
  }
  ```
- **Error (404):** If the path is not found.

---

### Get Full Path Details for a Specific User
- **Endpoint:** `GET /paths/<path_id>/<wallet_address>`
- **Description:** Retrieves a complete, nested JSON object for a single learning path, enriched with user-specific progress. Includes `is_complete` flags for the path and each level, an `is_minted` flag for the NFT status, and total slide/question counts.
- **Success (200):** Returns the full, nested path object with user-specific metadata.
  ```json
  {
    "id": 1,
    "title": "🐍 An Introduction to Python",
    // ... other path fields like above ...
    "total_slides": 15,
    "total_questions": 6,
    "is_complete": false, // User's overall completion status for this path
    "is_minted": false,   // Whether this user has minted an NFT for this path
    "levels": [
      {
        "id": 10,
        "path_id": 1,
        "level_number": 1,
        "level_title": "🐣 Getting Started",
        "is_complete": true, // User's completion status for this level
        "content_items": [
          // ... content items ...
        ]
      },
      {
        "id": 11,
        "path_id": 1,
        "level_number": 2,
        "level_title": "⚙️ Core Concepts",
        "is_complete": false,
        "content_items": [
          // ... content items ...
        ]
      }
      // ... more levels
    ]
  }
  ```
- **Error (404):** If the path is not found.

---

### Get Specific Level Content
- **Endpoint:** `GET /paths/<path_id>/levels/<level_num>`
- **Description:** Retrieves the content for a single level within a path, including its items and slide/question counts for that level.
- **Success (200):** Returns the level object with its content items.
  ```json
  {
    "level_title": "🐣 Getting Started",
    "total_slides_in_level": 5,
    "total_questions_in_level": 2,
    "items": [
      {"id": 100, "item_index": 0, "item_type": "slide", "content": "### Welcome!"},
      {"id": 101, "item_index": 1, "item_type": "quiz", "content": {"question": "...", "options": [], ...}}
      // ... more items
    ]
  }
  ```
- **Error (404):** If the path or level is not found.

---

### Delete a Learning Path
- **Endpoint:** `DELETE /paths/<path_id>`
- **Description:** Deletes a learning path. Can only be performed by the original creator of the path.
- **Request Body:**
  ```json
  {
    "user_wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"
  }
  ```
- **Success (200):** Confirms successful deletion.
  ```json
  {
    "message": "Path <path_id> deleted successfully."
  }
  ```
- **Error (400):** If `user_wallet` is missing in the body.
- **Error (403 Forbidden):** If the `user_wallet` does not match the path's creator.
- **Error (404 Not Found):** If the path does not exist.
- **Error (500):** If deletion fails for other reasons.

## 🔍 Search Endpoints

---

### Search for Paths
- **Endpoint:** `GET /search`
- **Description:** Performs a hybrid semantic and keyword search across path titles and descriptions.
- **Query Parameters:**
  - `q` (string, required, min 2 characters): The search query.
- **Success (200):** Returns an array of matching path objects.
  ```json
  [
    {
      "id": 12,
      "match_type": "semantic", // or "keyword"
      "title": "🐍 An Introduction to Python",
      "similarity": 0.8872, // null for keyword matches
      "result_in": "title" // "title", "short_description", or "long_description" for keyword
    }
  ]
  ```
- **Error (400):** If `q` parameter is missing or too short.

## 📈 Progress & Scoring Endpoints

---

### Upsert Level Progress
- **Endpoint:** `POST /progress/level`
- **Description:** Creates or updates a user's progress for a specific level within a path. If it's the user's first interaction with the path, a `user_progress` record is created. Automatically marks the entire path as complete in `user_progress` if all its levels are now finished.
- **Request Body:**
  ```json
  {
    "user_wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
    "path_id": 1,
    "level_index": 3,        // 1-based index of the level
    "correct_answers": 8,
    "total_questions": 10    // Total questions in this specific level
  }
  ```
- **Success (200):** Confirms the update.
  ```json
  {
    "message": "Progress updated successfully"
  }
  ```
- **Error (400):** If required fields are missing or data types are incorrect.
- **Error (500):** If the update fails.

---

### Get Path Completion Status
- **Endpoint:** `GET /progress/path/<path_id>/<wallet_address>/completed`
- **Description:** Checks if a user has completed an entire learning path.
- **Success (200):**
  ```json
  {
    "is_complete": true // or false
  }
  ```
- **Error (500):** If status retrieval fails.

---

### Get Level Completion Status
- **Endpoint:** `GET /progress/level/<path_id>/<level_index>/<wallet_address>/completed`
- **Description:** Checks if a user has completed a specific level within a path.
- **Success (200):**
  ```json
  {
    "is_complete": false // or true
  }
  ```
- **Error (500):** If status retrieval fails.

---

### Get Specific Level Score
- **Endpoint:** `GET /progress/scores/level`
- **Description:** Retrieves the score (correct answers and total questions) for a specific level of a path for a user.
- **Query Parameters:**
  - `user_wallet` (string, required)
  - `path_id` (integer, required)
  - `level_index` (integer, required, 1-based)
- **Success (200):**
  ```json
  {
    "correct_answers": 3,
    "total_questions": 5
  }
  ```
  (Returns `{"correct_answers": 0, "total_questions": 0}` if no progress for that level yet.)
- **Error (400):** If required query parameters are missing.
- **Error (404):** If the user is not found.
- **Error (500):** If score retrieval fails.

---

### Get All User Scores (Aggregated)
- **Endpoint:** `GET /progress/scores/<wallet_address>`
- **Description:** Retrieves an aggregated summary of scores for all paths a user has made progress on.
- **Success (200):** Returns an array of score summary objects.
  ```json
  [
    {
      "path_id": 1,
      "path_title": "🐍 An Introduction to Python",
      "correct_answers": 20,
      "total_questions_answered": 25,
      "score_percent": 80.00
    }
    // ... more paths
  ]
  ```
- **Error (404):** If the user is not found.
- **Error (500):** If score retrieval fails.

## 🖼️ NFT Endpoints

Endpoints for minting and retrieving NFT certificates.

---

### Complete a Path & Mint NFT
- **Endpoint:** `POST /paths/<path_id>/complete`
- **Description:** Initiates the minting process for an NFT certificate. The path must be fully completed by the user before this can be called. This endpoint handles image generation (if not cached), IPFS upload of image and metadata, NFT minting, and setting the token URI.
- **Request Body:**
  ```json
  {
    "user_wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"
  }
  ```
- **Success (200):**
  ```json
  {
      "message": "NFT minted and metadata set successfully!",
      "token_id": 74418501,
      "nft_contract_address": "0xEC94A5c84c850366F5E06BD6FfB9188c384d33e1",
      "metadata_url": "ipfs://bafkreihdwdcefgh45...", // IPFS URI for metadata JSON
      "image_gateway_url": "https://yourgateway.mypinata.cloud/ipfs/bafybeig...", // HTTP Gateway URL for image
      "explorer_url": "https://sepolia.etherscan.io/tx/0x...", // Transaction hash URL on block explorer
      "nft_gateway_url": "https://yourgateway.mypinata.cloud/ipfs/bafkreihdwdcefgh45..." // HTTP Gateway URL for metadata
  }
  ```
- **Error (400):** If `user_wallet` is missing, or if the path is not yet complete by the user.
- **Error (409 Conflict):** If the NFT has already been minted for this user and path (checked against DB and blockchain).
- **Error (500):** If any step in the minting process fails (image generation, IPFS upload, blockchain transaction, database save). Detailed error messages are provided.

---

### Get All User NFTs
- **Endpoint:** `GET /nfts/<wallet_address>`
- **Description:** Retrieves a list of all NFT certificates a user has earned, including the path title and gateway URL for the image.
- **Success (200):** Returns an array of NFT objects.
  ```json
  [
    {
      "path_id": 1,
      "token_id": 74418507,
      "nft_contract_address": "0xEC94A5c84c850366F5E06BD6FfB9188c384d33e1",
      "metadata_url": "ipfs://QmYja38cwqgZWFCKevvPZR1Q3QMmRrE6Z2Sey3VbLViuV6",
      "image_gateway_url": "https://yourgateway.mypinata.cloud/ipfs/bafybeig...",
      "minted_at": "2025-06-13T13:58:49.541875+00:00",
      "learning_paths": { // Joined data from learning_paths table
        "title": "🛡️ Recognize and Conquer Gaslighting."
      }
    }
  ]
  ```
- **Error (500):** If fetching NFTs fails.