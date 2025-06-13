# 🔌 API Endpoint Documentation

## User Endpoints

- **Create or Update a User**  
  **Endpoint**: `POST /users`  
  **Description**: Creates a new user record or updates an existing one. This endpoint uses checkpoint logic: it will only fill in `name` or `country` if they are currently empty, preventing accidental overwrites of existing user data.
  - **Request Body**:
    ```json
    {
      "wallet_address": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
      "name": "Alice",
      "country": "USA"
    }
    ```
  - **Success Response (201)**: Returns the full user object after the operation.
  - **Error Response (400)**: If `wallet_address` is missing from the body.

- **Get User Profile**  
  **Endpoint**: `GET /users/<wallet_address>`  
  **Description**: Retrieves the complete profile information for a single user.
  - **URL Parameters**:
    - `wallet_address` (string): The user's public wallet address.
  - **Success Response (200)**: Returns the user object.
  - **Error Response (404)**: If no user is found with the given address.

- **Get User-Created Paths**  
  **Endpoint**: `GET /users/<wallet_address>/paths`  
  **Description**: Retrieves a list of all learning paths created by a specific user, ordered by most recent first. Each path object includes an `is_complete` boolean indicating if that user has completed the path.
  - **URL Parameters**:
    - `wallet_address` (string): The creator's public wallet address.
  - **Success Response (200)**: Returns an array of learning path objects, each with an `is_complete` flag.

- **Get User-Created Path Count**  
  **Endpoint**: `GET /users/<wallet_address>/paths/count`  
  **Description**: Retrieves just the total number of learning paths created by a specific user.
  - **URL Parameters**:
    - `wallet_address` (string): The creator's public wallet address.
  - **Success Response (200)**:
    ```json
    {
      "creator_wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
      "path_count": 5
    }
    ```

## Path & Content Endpoints

- **Generate a New Learning Path**  
  **Endpoint**: `POST /paths/generate`  
  **Description**: **(Asynchronous)** Kicks off a background task to generate a complete learning path. This is the main entry point for content creation.
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
  - **Error Response (409)**: If a path with a highly similar title already exists.

- **Get a Random Topic**  
  **Endpoint**: `GET /paths/random-topic`  
  **Description**: Asks the AI to generate a single, interesting topic for a learning path. Perfect for an "I'm Feeling Lucky" feature.
  - **Success Response (200)**:
    ```json
    {
      "topic": "The History of the Rosetta Stone"
    }
    ```

- **Get Generation Status**  
  **Endpoint**: `GET /paths/generate/status/<task_id>`  
  **Description**: **(Persistent)** Poll this endpoint to get progress updates for a generation task. Status survives server restarts.
  - **URL Parameters**:
    - `task_id` (string): The UUID returned from the `/generate` endpoint.
  - **Success Response (200)**: Returns an array of log objects for the task.

- **Get All Public Paths**  
  **Endpoint**: `GET /paths`  
  **Description**: Retrieves a list of all created learning paths, suitable for a public catalog.
  - **Success Response (200)**: Returns an array of learning path objects.

- **Get Full Path Details**  
  **Endpoint**: `GET /paths/<path_id>`  
  **Description**: Retrieves a complete, nested JSON object for a single learning path, including its title, description, all levels, and all content items. It also includes calculated counts of total slides and questions for the entire path.
  - **URL Parameters**:
    - `path_id` (integer): The unique ID of the learning path.
  - **Success Response (200)**: Returns the full, nested path object with metadata.
  - **Error Response (404)**: If the path is not found.

- **Get Full Path Details for a Specific User**  
  **Endpoint**: `GET /paths/<path_id>/<wallet_address>`  
  **Description**: Retrieves a complete, nested JSON object for a single learning path and enriches it with user-specific progress. It adds an `is_complete` boolean to the overall path and to **each individual level** to show what the specified user has completed.
  - **URL Parameters**:
    - `path_id` (integer): The unique ID of the learning path.
    - `wallet_address` (string): The user's public wallet address to check progress against.
  - **Success Response (200)**: Returns the full, nested path object with user-specific completion flags.
  - **Error Response (404)**: If the path is not found.

- **Get Specific Level Content**  
  **Endpoint**: `GET /paths/<path_id>/levels/<level_num>`  
  **Description**: Retrieves the content for a single level within a path, including a list of its items and counts of slides and questions for that specific level.
  - **URL Parameters**:
    - `path_id` (integer): The ID of the learning path.
    - `level_num` (integer): The number of the level to retrieve.
  - **Success Response (200)**: Returns the level object with its content items and metadata.

- **Delete a Learning Path**  
  **Endpoint**: `DELETE /paths/<path_id>`  
  **Description**: Deletes a learning path and all of its associated content. This action is protected and can only be performed by the original creator.
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

## Search Endpoints

- **Search for Paths**  
  **Endpoint**: `GET /search`  
  **Description**: Performs a hybrid search that combines semantic (vector) search on titles with keyword search across titles and descriptions.
  - **Query Parameters**:
    - `q` (string): The search query. Must be at least 2 characters long.
  - **Success Response (200)**: Returns an interleaved array of keyword and semantic matches.
    ```json
    [
      {
        "id": 12,
        "match_type": "keyword",
        "result_in": "title",
        "similarity": null,
        "title": "🐍 An Introduction to Python"
      },
      {
        "id": 23,
        "match_type": "semantic",
        "result_in": "title",
        "similarity": 0.8912,
        "title": "Learn the Basics of Coding with Python"
      }
    ]
    ```

## Progress & Scoring Endpoints

- **Upsert Level Progress**  
  **Endpoint**: `POST /progress/level`  
  **Description**: Upserts a user's progress for a specific level. If this is the first time a user is submitting progress for a path, this endpoint will automatically create the main progress record before saving the level's score. Submitting any progress for a level automatically marks that level as complete for the user.
  - **Request Body**:
    ```json
    {
      "user_wallet": "0x...",
      "path_id": 1,
      "level_index": 3,
      "correct_answers": 8,
      "total_questions": 10
    }
    ```
  - **Success Response (200)**:
    ```json
    {
      "message": "Progress updated successfully"
    }
    ```

- **Get Level Score**  
  **Endpoint**: `GET /scores/level`  
  **Description**: Retrieves the score for a single, specific level that a user has completed.
  - **Query Parameters**:
    - `user_wallet` (string): The user's public wallet address.
    - `path_id` (integer): The ID of the learning path.
    - `level_index` (integer): The 1-based index of the level.
  - **Success Response (200)**:
    ```json
    {
      "correct_answers": 8,
      "total_questions": 10
    }
    ```
  - **Success Response (200, if not started)**:
    ```json
    {
      "correct_answers": 0,
      "total_questions": 0
    }
    ```

- **Get All User Scores**  
  **Endpoint**: `GET /scores/<wallet_address>`  
  **Description**: Retrieves an aggregated summary of scores for all paths a user has made progress on. It calculates the total score by summing up the results from all completed levels within each path.
  - **URL Parameters**:
    - `wallet_address` (string): The user's public wallet address.
  - **Success Response (200)**: Returns an array of score summary objects.
    ```json
    [
      {
        "path_id": 4,
        "path_title": "📱 iPhone 11 Screen Repair: A Step-by-Step Guide",
        "correct_answers": 6,
        "total_questions_answered": 7,
        "score_percent": 85.71
      }
    ]
    ```

## NFT Endpoints

- **Complete a Path & Mint NFT**  
  **Endpoint**: `POST /paths/<path_id>/complete`  
  **Description**: Initiates the minting of a personalized NFT certificate for a user. This is a two-step blockchain process: first, the NFT is minted to generate a unique `token_id`. Second, the metadata URI (which includes the new `token_id`) is set on the contract. The endpoint also marks the path as complete and saves a record of the NFT to the database.
  - **URL Parameters**:
    - `path_id` (integer): The ID of the completed path.
  - **Request Body**:
    ```json
    {
      "user_wallet": "0x..."
    }
    ```
  - **Success Response (200)**: Returns the transaction details and token ID.

- **Get All User NFTs**  
  **Endpoint**: `GET /nfts/<wallet_address>`  
  **Description**: Retrieves a list of all NFT certificates a user has earned, including the path title and token ID.
  - **URL Parameters**:
    - `wallet_address` (string): The user's public wallet address.
  - **Success Response (200)**:
    ```json
    [
      {
        "path_id": 12,
        "token_id": 74418500,
        "nft_contract_address": "0x...",
        "minted_at": "2023-10-27T10:00:00Z",
        "learning_paths": {
          "title": "⚛️ Understand the Basics of Quantum Mechanics."
        }
      }
    ]
    ```

- **Get NFT Metadata**  
  **Endpoint**: `GET /nft/metadata/<token_id>`  
  **Description**: Returns the ERC721 standard JSON metadata for a personalized NFT. This now includes a direct `block_explorer_url` for easy verification.
  - **URL Parameters**:
    - `token_id` (integer): The unique ID of the NFT.
  - **Success Response (200)**:
    ```json
    {
        "name": "KODO Certificate: The History of the Internet",
        "description": "This certificate proves that Alice successfully completed the 'The History of the Internet' learning path on KODO.",
        "image": "http://localhost:5000/nft/image/74418500",
        "block_explorer_url": "https://sepolia.etherscan.io/nft/0x.../74418500",
        "attributes": [
            {"trait_type": "Platform", "value": "KODO"},
            {"trait_type": "Recipient", "value": "Alice"},
            {"trait_type": "Token ID", "value": "74418500"},
            {"trait_type": "Contract Address", "value": "0x..."}
        ]
    }
    ```

- **Get NFT Image**  
  **Endpoint**: `GET /nft/image/<token_id>`  
  **Description**: Returns the programmatically generated, personalized certificate image for the NFT, including the user's name.
  - **URL Parameters**:
    - `token_id` (integer): The unique ID of the NFT.

---

## Complete Endpoint List

`POST /users` 

`GET /users/<wallet_address>`

`GET /users/<wallet_address>/paths` 

`GET /users/<wallet_address>/paths/count`  

`POST /paths/generate`

`GET /paths/random-topic`

`GET /paths/generate/status/<task_id>`

`GET /paths`

`GET /paths/<path_id>`

`GET /paths/<path_id>/<wallet_address>`

`DELETE /paths/<path_id>`

`GET /paths/<path_id>/levels/<level_num>`

`GET /search`

`POST /progress/level`

`GET /scores/level`

`GET /scores/<wallet_address>`

`POST /paths/<path_id>/complete`

`GET /nfts/<wallet_address>`

`GET /nft/metadata/<token_id>`

`GET /nft/image/<token_id>`