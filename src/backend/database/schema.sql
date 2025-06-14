-- 1. USERS TABLE
CREATE TABLE users (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    wallet_address TEXT NOT NULL UNIQUE,
    name TEXT,
    country TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. LEARNING PATHS TABLE
CREATE TABLE learning_paths (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    title TEXT NOT NULL,
    short_description TEXT,
    long_description TEXT,
    creator_wallet TEXT,
    content_hash TEXT,
    total_levels INT,
    intent_type TEXT, -- To store 'learn' or 'help'
    title_embedding vector(768),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. LEVELS TABLE
CREATE TABLE levels (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    path_id BIGINT REFERENCES learning_paths(id) ON DELETE CASCADE,
    level_number INT NOT NULL,
    level_title TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(path_id, level_number)
);

-- 4. CONTENT ITEMS TABLE
CREATE TABLE content_items (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    level_id BIGINT REFERENCES levels(id) ON DELETE CASCADE,
    item_index INT NOT NULL,
    item_type TEXT NOT NULL,
    content JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(level_id, item_index)
);

-- 5. USER PROGRESS TRACKER
CREATE TABLE user_progress (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    path_id BIGINT REFERENCES learning_paths(id) ON DELETE CASCADE,
    is_complete BOOLEAN NOT NULL DEFAULT false,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    UNIQUE(user_id, path_id)
);

-- 6. LEVEL PROGRESS & SCORES (REPLACES quiz_attempts)
CREATE TABLE level_progress (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    progress_id BIGINT REFERENCES user_progress(id) ON DELETE CASCADE,
    level_number INT NOT NULL,
    correct_answers INT,
    total_questions INT,
    is_complete BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(progress_id, level_number)
);

-- 7. FUNCTION FOR SIMILARITY SEARCH (for duplicate check)
CREATE OR REPLACE FUNCTION match_similar_paths(
  query_embedding vector(768),
  match_threshold float,
  match_count int
)
RETURNS TABLE (id bigint, title text, short_description text, similarity float)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT lp.id, lp.title, lp.short_description, 1 - (lp.title_embedding <=> query_embedding) AS similarity
  FROM learning_paths lp
  WHERE 1 - (lp.title_embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;

-- 8. TASK PROGRESS LOGS TABLE
CREATE TABLE task_progress_logs (
    task_id UUID PRIMARY KEY,
    logs JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Function to update the updated_at timestamp automatically
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update the timestamp on task_progress_logs
CREATE TRIGGER set_timestamp_task_logs
BEFORE UPDATE ON task_progress_logs
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

-- Trigger for the new level_progress table
CREATE TRIGGER set_timestamp_level_progress
BEFORE UPDATE ON level_progress
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();


-- 9. FUNCTION TO APPEND LOGS
CREATE OR REPLACE FUNCTION append_to_log(task_uuid UUID, new_log JSONB)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE task_progress_logs
  SET logs = logs || new_log
  WHERE task_id = task_uuid;
END;
$$;

-- 10. FUNCTION FOR SEMANTIC SEARCH (UPDATED)
CREATE OR REPLACE FUNCTION search_paths_semantic(
  match_count int,
  match_threshold float,
  query_embedding vector(768)
)
RETURNS TABLE (id bigint, title text, similarity float)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    lp.id,
    lp.title,
    1 - (lp.title_embedding <=> query_embedding) AS similarity
  FROM learning_paths lp
  WHERE 1 - (lp.title_embedding <=> query_embedding) > match_threshold
  ORDER BY lp.title_embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- 11. FUNCTION FOR KEYWORD SEARCH (NEW)
CREATE OR REPLACE FUNCTION search_paths_keyword(
  search_term text,
  match_count int
)
RETURNS TABLE (id bigint, title text, result_in text)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    lp.id,
    lp.title,
    CASE
        WHEN lp.title ILIKE search_term THEN 'title'
        WHEN lp.short_description ILIKE search_term THEN 'short_description'
        WHEN lp.long_description ILIKE search_term THEN 'long_description'
        ELSE 'unknown'
    END AS result_in
  FROM learning_paths lp
  WHERE
    lp.title ILIKE search_term OR
    lp.short_description ILIKE search_term OR
    lp.long_description ILIKE search_term
  LIMIT match_count;
END;
$$;


-- 12. PERFORMANCE INDEXES (IMPORTANT!)
-- Run these commands once in your Supabase SQL Editor to enable fast search.

-- Enable the pg_trgm extension for fast text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create indexes for fast case-insensitive text search on relevant columns
CREATE INDEX IF NOT EXISTS trgm_idx_paths_title ON learning_paths USING gin (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS trgm_idx_paths_short_desc ON learning_paths USING gin (short_description gin_trgm_ops);
CREATE INDEX IF NOT EXISTS trgm_idx_paths_long_desc ON learning_paths USING gin (long_description gin_trgm_ops);

-- Ensure you have a vector index for fast semantic search.
-- This is an example using IVFFlat, which is good for performance/accuracy balance.
-- You can adjust `lists` based on the number of rows you expect.
-- CREATE INDEX ON learning_paths USING ivfflat (title_embedding vector_cosine_ops) WITH (lists = 100);


-- 13. FUNCTION TO GET LEVEL COMPLETION STATUS FOR A USER AND PATH (UPDATED)
CREATE OR REPLACE FUNCTION get_level_completion_for_path(p_user_id bigint, p_path_id bigint)
RETURNS TABLE(level_number int, is_complete boolean)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    lp.level_number,
    lp.is_complete
  FROM level_progress lp
  JOIN user_progress up ON lp.progress_id = up.id
  WHERE
    up.user_id = p_user_id AND
    up.path_id = p_path_id;
END;
$$;

-- 14. USER NFTS TABLE (UPDATED)
CREATE TABLE user_nfts (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    path_id BIGINT NOT NULL REFERENCES learning_paths(id) ON DELETE CASCADE,
    token_id BIGINT NOT NULL,
    nft_contract_address TEXT NOT NULL,
    metadata_url TEXT, -- To store the IPFS URL
    image_gateway_url TEXT,
    minted_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, path_id),
    UNIQUE(token_id)
);

-- Index for fast lookup of user's NFTs
CREATE INDEX IF NOT EXISTS idx_user_nfts_user_id ON user_nfts(user_id);

-- 15. FUNCTION TO AUTOMATICALLY COMPLETE A PATH (NEW)
CREATE OR REPLACE FUNCTION check_and_complete_path(p_progress_id bigint)
RETURNS void AS $$
DECLARE
    v_path_id bigint;
    v_user_id bigint;
    total_levels_in_path int;
    completed_levels_for_user int;
BEGIN
    -- Get user_id and path_id from the progress record
    SELECT user_id, path_id INTO v_user_id, v_path_id
    FROM user_progress
    WHERE id = p_progress_id;

    -- Get the total number of levels for this path
    SELECT total_levels INTO total_levels_in_path
    FROM learning_paths
    WHERE id = v_path_id;

    -- Count how many levels the user has completed for this path
    SELECT count(*) INTO completed_levels_for_user
    FROM level_progress
    WHERE progress_id = p_progress_id AND is_complete = true;

    -- If the counts match, the path is complete
    IF total_levels_in_path > 0 AND completed_levels_for_user >= total_levels_in_path THEN
        UPDATE user_progress
        SET
            is_complete = true,
            completed_at = now()
        WHERE id = p_progress_id AND is_complete = false; -- Only update if not already complete
    END IF;
END;
$$ LANGUAGE plpgsql;


-- 16. FUNCTION TO GET A SINGLE LEVEL'S COMPLETION STATUS (NEW)
CREATE OR REPLACE FUNCTION get_single_level_completion(p_user_id bigint, p_path_id bigint, p_level_number int)
RETURNS boolean AS $$
DECLARE
    v_is_complete boolean;
BEGIN
    SELECT lp.is_complete INTO v_is_complete
    FROM level_progress lp
    JOIN user_progress up ON lp.progress_id = up.id
    WHERE up.user_id = p_user_id
      AND up.path_id = p_path_id
      AND lp.level_number = p_level_number;

    RETURN COALESCE(v_is_complete, false);
END;
$$ LANGUAGE plpgsql;

-- 17. FUNCTION TO GET ALL USER ASSOCIATED PATHS (ENROLLED OR CREATED)
CREATE OR REPLACE FUNCTION get_user_associated_paths(p_wallet_address TEXT)
RETURNS TABLE (
    id bigint, -- This will be the learning_paths.id
    title text,
    short_description text,
    total_levels int,
    created_at timestamptz, -- This will be learning_paths.created_at
    is_complete boolean,
    completed_levels bigint
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_id bigint;
BEGIN
    SELECT u.id INTO v_user_id FROM users u WHERE u.wallet_address = LOWER(p_wallet_address);

    RETURN QUERY
    WITH enrolled_paths_cte AS (
        SELECT
            lp_enrolled.id AS path_id,
            lp_enrolled.title AS path_title,
            lp_enrolled.short_description AS path_short_description,
            lp_enrolled.total_levels AS path_total_levels,
            lp_enrolled.created_at AS path_created_at,
            up.is_complete AS progress_is_complete,
            COALESCE(progress_agg.completed_count, 0) AS progress_completed_levels,
            up.started_at AS effective_date
        FROM
            user_progress up
        JOIN
            learning_paths lp_enrolled ON up.path_id = lp_enrolled.id
        LEFT JOIN (
            SELECT
                lp_sub.progress_id,
                COUNT(*) AS completed_count
            FROM
                level_progress lp_sub
            WHERE
                lp_sub.is_complete = true
            GROUP BY
                lp_sub.progress_id
        ) AS progress_agg ON up.id = progress_agg.progress_id
        WHERE
            up.user_id = v_user_id
    ),
    created_paths_cte AS (
        SELECT
            lp_created.id AS path_id,
            lp_created.title AS path_title,
            lp_created.short_description AS path_short_description,
            lp_created.total_levels AS path_total_levels,
            lp_created.created_at AS path_created_at,
            FALSE AS progress_is_complete, -- Default for created but not started
            0 AS progress_completed_levels, -- Default for created but not started
            lp_created.created_at AS effective_date
        FROM
            learning_paths lp_created
        WHERE
            lp_created.creator_wallet = LOWER(p_wallet_address)
            AND NOT EXISTS (SELECT 1 FROM enrolled_paths_cte ep WHERE ep.path_id = lp_created.id)
    )
    SELECT
        cte.path_id,
        cte.path_title,
        cte.path_short_description,
        cte.path_total_levels,
        cte.path_created_at,
        cte.progress_is_complete,
        cte.progress_completed_levels
    FROM (
        SELECT path_id, path_title, path_short_description, path_total_levels, path_created_at, progress_is_complete, progress_completed_levels, effective_date FROM enrolled_paths_cte
        UNION ALL
        SELECT path_id, path_title, path_short_description, path_total_levels, path_created_at, progress_is_complete, progress_completed_levels, effective_date FROM created_paths_cte
    ) AS cte
    ORDER BY
        cte.effective_date DESC;
END;
$$;

-- Remove old RPC function if it exists and is no longer needed
DROP FUNCTION IF EXISTS get_user_enrolled_paths_with_progress(bigint);