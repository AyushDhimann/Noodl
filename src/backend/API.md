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
- **Success (201 Created):** Returns the full user object (either newly created or existing, potentially updated).
  ```json
  {
    "id": 1,
    "wallet_address": "0xab5801a7d398351b8be11c439e05c5b3259aec9b",
    "name": "Alice",
    "country": "USA",
    "created_at": "2025-06-14T12:00:00.000000+00:00"
  }
  ```
- **Error (400 Bad Request):** If `wallet_address` is missing.
  ```json
  {
    "error": "wallet_address is required"
  }
  ```
- **Error (500 Internal Server Error):** If the database operation fails.
  ```json
  {
    "error": "Failed to create or update user."
  }
  ```

---

### Get User Profile
- **Endpoint:** `GET /users/<wallet_address>`
- **Description:** Retrieves the complete public profile for a single user, including their wallet address, name, and country.
- **URL Parameters:**
  - `wallet_address` (string, required): The user's blockchain wallet address.
- **Success (200 OK):** Returns the user object.
  ```json
  {
    "id": 1,
    "wallet_address": "0xab5801a7d398351b8be11c439e05c5b3259aec9b",
    "name": "Alice",
    "country": "USA",
    "created_at": "2025-06-14T12:00:00.000000+00:00"
  }
  ```
- **Error (404 Not Found):** If the user is not found.
  ```json
  {
    "error": "User not found"
  }
  ```
- **Error (500 Internal Server Error):** If the database query fails.
  ```json
  {
    "error": "Failed to retrieve user."
  }
  ```

---

### Get User-Associated Paths
- **Endpoint:** `GET /users/<wallet_address>/paths`
- **Description:** Retrieves a list of all learning paths a user is associated with (either enrolled in or created by them), ordered by most recent activity (start date for enrolled paths, creation date otherwise) first. Includes progress details for enrolled paths; created-only paths will show 0 completed levels and `is_complete: false`.
- **URL Parameters:**
  - `wallet_address` (string, required): The user's blockchain wallet address.
- **Success (200 OK):** Returns an array of path objects with progress details.
  ```json
  [
    {
      "id": 5, // Path ID
      "title": "🚀 Introduction to Rocket Science",
      "short_description": "Learn the basics of rockets.",
      "total_levels": 5,
      "created_at": "2025-06-14T10:00:00.000000+00:00", // Path creation timestamp
      "is_complete": false, // User's overall completion status for this path
      "completed_levels": 2 // Number of levels completed by the user in this path
    },
    {
      "id": 8, // Path ID
      "title": "🎨 My New Art Course",
      "short_description": "A course I just created.",
      "total_levels": 3,
      "created_at": "2025-06-15T09:00:00.000000+00:00",
      "is_complete": false, // Default for created, not-yet-started paths
      "completed_levels": 0 // Default for created, not-yet-started paths
    }
  ]
  ```
- **Note:** Returns an empty array `[]` if the user is not found or has no associated paths.
- **Error (500 Internal Server Error):** If the database query fails.
  ```json
  {
    "error": "Failed to retrieve user-associated paths."
  }
  ```

---

### Get User-Created Path Count
- **Endpoint:** `GET /users/<wallet_address>/paths/count`
- **Description:** Retrieves the total number of learning paths created by a specific user.
- **URL Parameters:**
  - `wallet_address` (string, required): The user's blockchain wallet address.
- **Success (200 OK):**
  ```json
  {
    "creator_wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
    "path_count": 3
  }
  ```
- **Error (500 Internal Server Error):** If the database query fails.
  ```json
  {
    "error": "Failed to retrieve user-created path count."
  }
  ```

## 📚 Path & Content Endpoints

Endpoints for generating, retrieving, and managing learning paths and their content.

---

### Generate a New Learning Path
- **Endpoint:** `POST /paths/generate`
- **Description:** (Asynchronous) Kicks off a background task to generate a complete learning path based on a topic. The user's country (if available in their profile) may be used to tailor content.
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
- **Error (400 Bad Request):** If `topic` or `creator_wallet` are missing.
  ```json
  {
    "error": "topic and creator_wallet are required"
  }
  ```
- **Error (409 Conflict):** If a path with a highly similar title already exists (and duplicate check is enabled).
  ```json
  {
    "error": "A very similar learning path already exists.",
    "similar_path": {
      "id": 12,
      "title": "🌐 A Brief History of the World Wide Web",
      "short_description": "Explore the origins of the internet.",
      "similarity": 0.92 // (Example field, actual field name from DB is 'similarity')
    }
  }
  ```
- **Error (500 Internal Server Error):** If the generation process fails to start (e.g., AI service error, database error during initial setup).
  ```json
  {
    "error": "Failed to start generation process. Check server logs."
  }
  ```

---

### Get Generation Status
- **Endpoint:** `GET /paths/generate/status/<task_id>`
- **Description:** Poll this endpoint to get progress updates for an asynchronous path generation task.
- **URL Parameters:**
  - `task_id` (string, required): The UUID of the generation task.
- **Success (200 OK):** Returns an array of log objects for the task.
  ```json
  {
    "progress": [
      {"status": "🤔 Analyzing your request..."},
      {"status": "Request analyzed. Intent: **LEARN**"},
      {"status": "✅ Designing your curriculum..."},
      {"status": "Curriculum designed with 5 lessons."},
      // ... more progress steps ...
      {"status": "🎉 SUCCESS: Path generation complete!", "data": {"path_id": 101, "explorer_url": "https://sepolia.etherscan.io/tx/0x..."}}
    ]
  }
  ```
  (If an error occurs during generation, the `status` will reflect it, e.g., "❌ ERROR: The server's wallet has insufficient funds...")
- **Error (404 Not Found):** If the `task_id` is not found.
  ```json
  {
    "error": "Task not found."
  }
  ```
- **Error (500 Internal Server Error):** If retrieving status fails.
  ```json
  {
    "error": "Failed to retrieve task status."
  }
  ```

---

### Get a Random Topic
- **Endpoint:** `GET /paths/random-topic`
- **Description:** Generates a single, interesting topic suitable for a new learning path using the AI model.
- **Success (200 OK):**
  ```json
  {
    "topic": "The History and Cultural Impact of Coffee"
  }
  ```
- **Error (500 Internal Server Error):** If topic generation fails (e.g., AI service error).
  ```json
  {
    "error": "Failed to generate a random topic."
  }
  ```

---

### Get All Public Paths
- **Endpoint:** `GET /paths`
- **Description:** Retrieves a list of all created learning paths (basic details: id, title, short_description, total_levels).
- **Success (200 OK):** Returns an array of path objects.
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
- **Error (500 Internal Server Error):** If fetching paths fails.
  ```json
  {
    "error": "Failed to fetch paths."
  }
  ```

---

### Get Full Path Details (Generic)
- **Endpoint:** `GET /paths/<path_id>`
- **Description:** Retrieves a complete, nested JSON object for a single learning path, including all levels and content items. Also includes total slide and question counts for the path.
- **URL Parameters:**
  - `path_id` (integer, required): The ID of the learning path.
- **Success (200 OK):** Returns the full, nested path object.
  ```json
  {
    "id": 1,
    "title": "🐍 An Introduction to Python",
    "short_description": "Learn Python from scratch.",
    "long_description": "This course covers all the fundamental concepts of Python programming...",
    "creator_wallet": "0x...",
    "content_hash": "0x...", // Blockchain content hash if registered
    "total_levels": 3,
    "intent_type": "learn",
    "created_at": "2025-06-14T12:00:00.123456+00:00",
    "title_embedding": null, // Or the vector if fetched explicitly
    "total_slides": 15,
    "total_questions": 6,
    "levels": [
      {
        "id": 10, // Level ID
        "path_id": 1,
        "level_number": 1,
        "level_title": "🐣 Getting Started",
        "created_at": "2025-06-14T12:01:00.123456+00:00",
        "content_items": [
          {
            "id": 100, // Content Item ID
            "level_id": 10,
            "item_index": 0,
            "item_type": "slide",
            "content": "### Welcome to Python!",
            "created_at": "2025-06-14T12:02:00.123456+00:00"
          },
          {
            "id": 101,
            "level_id": 10,
            "item_index": 1,
            "item_type": "quiz",
            "content": {
              "question": "What is Python?",
              "options": ["A snake", "A programming language", "A fruit", "A car"],
              "correctAnswerIndex": 1,
              "explanation": "Python is a versatile programming language."
            },
            "created_at": "2025-06-14T12:03:00.123456+00:00"
          }
        ]
      }
      // ... more levels
    ]
  }
  ```
- **Error (404 Not Found):** If the path is not found.
  ```json
  {
    "error": "Path not found"
  }
  ```
- **Error (500 Internal Server Error):** If fetching fails.
  ```json
  {
    "error": "Failed to fetch path details."
  }
  ```

---

### Get Full Path Details for a Specific User
- **Endpoint:** `GET /paths/<path_id>/<wallet_address>`
- **Description:** Retrieves a complete, nested JSON object for a single learning path, enriched with user-specific progress. Includes `is_complete` flags for the path and each level, an `is_minted` flag for the NFT status, and total slide/question counts.
- **URL Parameters:**
  - `path_id` (integer, required): The ID of the learning path.
  - `wallet_address` (string, required): The user's blockchain wallet address.
- **Success (200 OK):** Returns the full, nested path object with user-specific metadata.
  ```json
  {
    "id": 1,
    "title": "🐍 An Introduction to Python",
    // ... other path fields like in generic GET /paths/<path_id> ...
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
        "is_complete": true, // User's completion status for this specific level
        "content_items": [
          // ... content items as in generic GET /paths/<path_id> ...
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
- **Error (404 Not Found):** If the path is not found.
  ```json
  {
    "error": "Path not found"
  }
  ```
- **Error (500 Internal Server Error):** If fetching fails.
  ```json
  {
    "error": "Failed to fetch path details for user."
  }
  ```

---

### Get Specific Level Content
- **Endpoint:** `GET /paths/<path_id>/levels/<level_num>`
- **Description:** Retrieves the content for a single level within a path, including its items and slide/question counts for that specific level.
- **URL Parameters:**
  - `path_id` (integer, required): The ID of the learning path.
  - `level_num` (integer, required): The 1-based number of the level.
- **Success (200 OK):** Returns the level object with its content items.
  ```json
  {
    "level_title": "🐣 Getting Started",
    "total_slides_in_level": 5,
    "total_questions_in_level": 2,
    "items": [
      {"id": 100, "item_index": 0, "item_type": "slide", "content": "### Welcome!", "created_at": "..."},
      {"id": 101, "item_index": 1, "item_type": "quiz", "content": {"question": "...", "options": [], ...}, "created_at": "..."}
      // ... more items
    ]
  }
  ```
- **Error (404 Not Found):** If the path or level (by number) is not found.
  ```json
  {
    "error": "Level not found" 
  }
  ```
- **Error (500 Internal Server Error):** If fetching fails.
  ```json
  {
    "error": "Failed to fetch level content."
  }
  ```

---

### Delete a Learning Path
- **Endpoint:** `DELETE /paths/<path_id>`
- **Description:** Deletes a learning path and all its associated content (levels, items, progress records due to CASCADE). Can only be performed by the original creator of the path.
- **URL Parameters:**
  - `path_id` (integer, required): The ID of the learning path to delete.
- **Request Body:**
  ```json
  {
    "user_wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"
  }
  ```
- **Success (200 OK):** Confirms successful deletion.
  ```json
  {
    "message": "Path 1 deleted successfully."
  }
  ```
- **Error (400 Bad Request):** If `user_wallet` is missing in the body.
  ```json
  {
    "error": "user_wallet is required in the request body"
  }
  ```
- **Error (403 Forbidden):** If the `user_wallet` does not match the path's creator.
  ```json
  {
    "error": "Forbidden. You are not the creator of this path."
  }
  ```
- **Error (404 Not Found):** If the path does not exist.
  ```json
  {
    "error": "Path not found"
  }
  ```
- **Error (500 Internal Server Error):** If deletion fails for other reasons.
  ```json
  {
    "error": "Failed to delete path."
  }
  ```

## 🔍 Search Endpoints

---

### Search for Paths
- **Endpoint:** `GET /search`
- **Description:** Performs a hybrid semantic (vector-based on title embeddings) and keyword search across path titles and descriptions.
- **Query Parameters:**
  - `q` (string, required, min 2 characters): The search query.
- **Success (200 OK):** Returns an array of matching path objects, potentially from both search types, interleaved.
  ```json
  [
    {
      "id": 12,
      "match_type": "semantic", // "semantic" or "keyword"
      "title": "🐍 An Introduction to Python",
      "similarity": 0.8872, // Cosine similarity for semantic matches, null for keyword
      "result_in": "title" // For keyword: "title", "short_description", or "long_description". For semantic: "title".
    },
    {
      "id": 15,
      "match_type": "keyword",
      "title": "Advanced Python Techniques",
      "similarity": null,
      "result_in": "short_description"
    }
  ]
  ```
  (Returns an empty array `[]` if `q` is less than 2 characters or no matches are found.)
- **Error (400 Bad Request):** If `q` parameter is missing.
  ```json
  {
    "error": "Query parameter 'q' is required."
  }
  ```
- **Error (500 Internal Server Error):** If the search operation fails.
  ```json
  {
    "error": "Failed to perform search."
  }
  ```

## 📈 Progress & Scoring Endpoints

---

### Upsert Level Progress
- **Endpoint:** `POST /progress/level`
- **Description:** Creates or updates a user's progress for a specific level within a path. If it's the user's first interaction with the path, a `user_progress` record is automatically created. Automatically marks the entire path as complete in `user_progress` if all its levels are now finished (via a database trigger/RPC).
- **Request Body:**
  ```json
  {
    "user_wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
    "path_id": 1,
    "level_index": 3,        // 1-based index of the level within the path
    "correct_answers": 8,    // Number of questions answered correctly in this level attempt
    "total_questions": 10    // Total questions in this specific level
  }
  ```
- **Success (200 OK):** Confirms the update.
  ```json
  {
    "message": "Progress updated successfully"
  }
  ```
- **Error (400 Bad Request):** If required fields are missing or data types are incorrect (e.g., non-integer for counts).
  ```json
  {
    "error": "user_wallet, path_id, level_index, correct_answers, and total_questions are required" 
    // or "path_id, level_index, correct_answers, and total_questions must be valid integers"
  }
  ```
- **Error (500 Internal Server Error):** If the update fails (e.g., database error, user not found).
  ```json
  {
    "error": "Failed to update level progress."
  }
  ```

---

### Get Path Completion Status
- **Endpoint:** `GET /progress/path/<path_id>/<wallet_address>/completed`
- **Description:** Checks if a user has completed an entire learning path.
- **URL Parameters:**
  - `path_id` (integer, required): The ID of the learning path.
  - `wallet_address` (string, required): The user's blockchain wallet address.
- **Success (200 OK):**
  ```json
  {
    "is_complete": true // or false
  }
  ```
- **Error (500 Internal Server Error):** If status retrieval fails.
  ```json
  {
    "error": "Failed to get path completion status."
  }
  ```

---

### Get Level Completion Status
- **Endpoint:** `GET /progress/level/<path_id>/<level_index>/<wallet_address>/completed`
- **Description:** Checks if a user has completed a specific level (1-based index) within a path.
- **URL Parameters:**
  - `path_id` (integer, required): The ID of the learning path.
  - `level_index` (integer, required): The 1-based index of the level.
  - `wallet_address` (string, required): The user's blockchain wallet address.
- **Success (200 OK):**
  ```json
  {
    "is_complete": false // or true
  }
  ```
- **Error (500 Internal Server Error):** If status retrieval fails.
  ```json
  {
    "error": "Failed to get level completion status."
  }
  ```

---

### Get Specific Level Score
- **Endpoint:** `GET /progress/scores/level`
- **Description:** Retrieves the score (correct answers and total questions) for a specific level of a path for a user.
- **Query Parameters:**
  - `user_wallet` (string, required): The user's blockchain wallet address.
  - `path_id` (integer, required): The ID of the learning path.
  - `level_index` (integer, required): The 1-based index of the level.
- **Success (200 OK):**
  ```json
  {
    "correct_answers": 3,
    "total_questions": 5
  }
  ```
  (Returns `{"correct_answers": 0, "total_questions": 0}` if no progress for that level yet, or if the path/user combination doesn't exist for progress.)
- **Error (400 Bad Request):** If required query parameters are missing.
  ```json
  {
    "error": "user_wallet, path_id, and level_index are required query parameters"
  }
  ```
- **Error (404 Not Found):** If the user is not found (raised as ValueError in service, caught by route).
  ```json
  {
    "error": "User not found for wallet <wallet_address>"
  }
  ```
- **Error (500 Internal Server Error):** If score retrieval fails for other reasons.
  ```json
  {
    "error": "Failed to retrieve level score."
  }
  ```

---

### Get All User Scores (Aggregated)
- **Endpoint:** `GET /progress/scores/<wallet_address>`
- **Description:** Retrieves an aggregated summary of scores for all paths a user has made progress on.
- **URL Parameters:**
  - `wallet_address` (string, required): The user's blockchain wallet address.
- **Success (200 OK):** Returns an array of score summary objects.
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
  (Returns an empty array `[]` if the user has no scores or progress.)
- **Error (404 Not Found):** If the user is not found.
  ```json
  {
    "error": "User not found"
  }
  ```
- **Error (500 Internal Server Error):** If score retrieval fails.
  ```json
  {
    "error": "Failed to fetch scores."
  }
  ```

## 🖼️ NFT Endpoints

Endpoints for minting and retrieving NFT certificates. NFT minting is subject to `FEATURE_FLAG_ENABLE_NFT_MINTING`.

---

### Complete a Path & Mint NFT
- **Endpoint:** `POST /paths/<path_id>/complete`
- **Description:** Initiates the minting process for an NFT certificate. The path must be fully completed by the user before this can be called. This endpoint handles:
    1. Verifying path completion.
    2. Checking if NFT already minted (DB & Blockchain).
    3. Generating certificate image (if not cached locally).
    4. Uploading image to IPFS.
    5. Uploading metadata JSON (including image IPFS URL) to IPFS.
    6. Minting the NFT on the blockchain (first transaction).
    7. Saving NFT details to the database.
    8. Setting the token URI on the minted NFT (second transaction).
- **URL Parameters:**
  - `path_id` (integer, required): The ID of the learning path.
- **Request Body:**
  ```json
  {
    "user_wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"
  }
  ```
- **Success (200 OK):**
  ```json
  {
      "message": "NFT minted and metadata set successfully!",
      "token_id": 74418501, // Example token ID
      "nft_contract_address": "0x62fe3D8fCe99BA2C1F016d8D01a1D3033D8A895d", // From .env
      "metadata_url": "ipfs://bafkreihdwdcefgh45...", // IPFS URI for metadata JSON
      "image_gateway_url": "https://beige-elaborate-hummingbird-35.mypinata.cloud/ipfs/bafybeig...", // HTTP Gateway URL for image
      "explorer_url": "https://sepolia.etherscan.io/tx/0x...", // Transaction hash URL for setTokenURI
      "nft_gateway_url": "https://beige-elaborate-hummingbird-35.mypinata.cloud/ipfs/bafkreihdwdcefgh45..." // HTTP Gateway URL for metadata JSON
  }
  ```
- **Error (400 Bad Request):**
  - If `user_wallet` is missing: `{"error": "user_wallet is required"}`
  - If the path is not yet complete by the user: `{"error": "Path is not yet complete. Cannot mint NFT."}`
- **Error (404 Not Found):** If user or path details for NFT cannot be found.
  ```json
  {
    "error": "Could not find user or path details."
  }
  ```
- **Error (409 Conflict):**
  - If DB check shows NFT already minted: `{"error": "Certificate has already been minted.", "detail": "Our database shows...", "nft_data": { ... }}`
  - If Blockchain check shows NFT already minted: `{"error": "Certificate has already been minted.", "detail": "The blockchain confirms..."}`
- **Error (500 Internal Server Error):** If any step in the multi-stage minting process fails. The `detail` field will provide more context.
  ```json
  {
    "error": "NFT minting failed.", // Generic error
    "detail": "The server's wallet has insufficient funds to pay for gas." // Example specific detail
  }
  ```
  Other details include: "Failed to generate NFT image.", "Failed to upload certificate image to IPFS.", "Failed to upload metadata to IPFS.", "Minting failed, did not receive a Token ID.", "Minting succeeded but failed to save record to DB...", "Minting succeeded and DB record saved, but failed to set metadata URL on blockchain."

---

### Get All User NFTs
- **Endpoint:** `GET /nfts/<wallet_address>`
- **Description:** Retrieves a list of all NFT certificates a user has earned, including the path title and gateway URL for the image.
- **URL Parameters:**
  - `wallet_address` (string, required): The user's blockchain wallet address.
- **Success (200 OK):** Returns an array of NFT objects.
  ```json
  [
    {
      "path_id": 1,
      "token_id": 74418507,
      "nft_contract_address": "0x62fe3D8fCe99BA2C1F016d8D01a1D3033D8A895d",
      "metadata_url": "ipfs://QmYja38cwqgZWFCKevvPZR1Q3QMmRrE6Z2Sey3VbLViuV6",
      "image_gateway_url": "https://beige-elaborate-hummingbird-35.mypinata.cloud/ipfs/bafybeig...",
      "minted_at": "2025-06-13T13:58:49.541875+00:00",
      "learning_paths": { // Joined data from learning_paths table
        "title": "🛡️ Recognize and Conquer Gaslighting."
      }
    }
  ]
  ```
  (Returns an empty array `[]` if the user has no NFTs or the user is not found.)
- **Error (500 Internal Server Error):** If fetching NFTs fails.
  ```json
  {
    "error": "Failed to fetch user NFTs."
  }
  ```