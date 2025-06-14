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
    creator_wallet TEXT, -- Stored as is, comparison should be case-insensitive
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

-- 6. LEVEL PROGRESS & SCORES
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

-- 7. FUNCTION FOR SIMILARITY SEARCH
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

-- Trigger for task_progress_logs
CREATE TRIGGER set_timestamp_task_logs
BEFORE UPDATE ON task_progress_logs
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

-- Trigger for level_progress
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

-- 10. FUNCTION FOR SEMANTIC SEARCH
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

-- 11. FUNCTION FOR KEYWORD SEARCH
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


-- 12. PERFORMANCE INDEXES
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS trgm_idx_paths_title ON learning_paths USING gin (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS trgm_idx_paths_short_desc ON learning_paths USING gin (short_description gin_trgm_ops);
CREATE INDEX IF NOT EXISTS trgm_idx_paths_long_desc ON learning_paths USING gin (long_description gin_trgm_ops);
-- CREATE INDEX ON learning_paths USING ivfflat (title_embedding vector_cosine_ops) WITH (lists = 100);


-- 13. FUNCTION TO GET LEVEL COMPLETION STATUS FOR A USER AND PATH
CREATE OR REPLACE FUNCTION get_level_completion_for_path(p_user_id bigint, p_path_id bigint)
RETURNS TABLE(level_number int, is_complete boolean)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    l_prog.level_number,
    l_prog.is_complete
  FROM level_progress l_prog
  JOIN user_progress u_prog ON l_prog.progress_id = u_prog.id
  WHERE
    u_prog.user_id = p_user_id AND
    u_prog.path_id = p_path_id;
END;
$$;

-- 14. USER NFTS TABLE
CREATE TABLE user_nfts (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    path_id BIGINT NOT NULL REFERENCES learning_paths(id) ON DELETE CASCADE,
    token_id BIGINT NOT NULL,
    nft_contract_address TEXT NOT NULL,
    metadata_url TEXT,
    image_gateway_url TEXT,
    minted_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, path_id),
    UNIQUE(token_id)
);
CREATE INDEX IF NOT EXISTS idx_user_nfts_user_id ON user_nfts(user_id);

-- 15. FUNCTION TO AUTOMATICALLY COMPLETE A PATH
CREATE OR REPLACE FUNCTION check_and_complete_path(p_progress_id bigint)
RETURNS void AS $$
DECLARE
    v_path_id bigint;
    v_user_id bigint;
    total_levels_in_path int;
    completed_levels_for_user int;
BEGIN
    SELECT user_id, path_id INTO v_user_id, v_path_id
    FROM user_progress
    WHERE id = p_progress_id;

    SELECT total_levels INTO total_levels_in_path
    FROM learning_paths
    WHERE id = v_path_id;

    SELECT count(*) INTO completed_levels_for_user
    FROM level_progress
    WHERE progress_id = p_progress_id AND is_complete = true;

    IF total_levels_in_path > 0 AND completed_levels_for_user >= total_levels_in_path THEN
        UPDATE user_progress
        SET
            is_complete = true,
            completed_at = now()
        WHERE id = p_progress_id AND is_complete = false;
    END IF;
END;
$$ LANGUAGE plpgsql;


-- 16. FUNCTION TO GET A SINGLE LEVEL'S COMPLETION STATUS
CREATE OR REPLACE FUNCTION get_single_level_completion(p_user_id bigint, p_path_id bigint, p_level_number int)
RETURNS boolean AS $$
DECLARE
    v_is_complete boolean;
BEGIN
    SELECT lp.is_complete INTO v_is_complete
    FROM level_progress lp
    JOIN user_progress uprog ON lp.progress_id = uprog.id
    WHERE uprog.user_id = p_user_id
      AND uprog.path_id = p_path_id
      AND lp.level_number = p_level_number;

    RETURN COALESCE(v_is_complete, false);
END;
$$ LANGUAGE plpgsql;

-- 17. FUNCTION TO GET USER ENROLLED PATHS (USED AS BASE FOR COMBINED FUNCTION)
-- This function is kept for potential direct use if only enrolled paths are needed.
-- The ambiguity fix is applied here too.
CREATE OR REPLACE FUNCTION get_user_enrolled_paths_with_progress(p_user_id bigint)
RETURNS TABLE (
    id bigint,
    title text,
    short_description text,
    total_levels int,
    created_at timestamptz,
    is_complete boolean,
    completed_levels bigint,
    started_at timestamptz -- Added for ordering
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    lp.id,
    lp.title,
    lp.short_description,
    lp.total_levels,
    lp.created_at,
    up.is_complete,
    COALESCE(progress_agg.completed_count, 0) AS completed_levels,
    up.started_at
  FROM
    user_progress up
  JOIN
    learning_paths lp ON up.path_id = lp.id
  LEFT JOIN (
    SELECT
      lp_sub.progress_id,
      count(*) AS completed_count
    FROM
      level_progress lp_sub
    WHERE
      lp_sub.is_complete = true
    GROUP BY
      lp_sub.progress_id
  ) AS progress_agg ON up.id = progress_agg.progress_id
  WHERE
    up.user_id = p_user_id;
END;
$$;

-- 18. NEW FUNCTION: Get all paths associated with a user (created OR enrolled)
CREATE OR REPLACE FUNCTION get_user_associated_paths(p_user_wallet_address TEXT)
RETURNS TABLE (
    path_id BIGINT,
    title TEXT,
    short_description TEXT,
    total_levels INT,
    path_created_at TIMESTAMPTZ,
    is_created_by_user BOOLEAN,
    is_enrolled BOOLEAN,
    user_progress_is_complete BOOLEAN,
    user_progress_started_at TIMESTAMPTZ,
    completed_levels BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_id BIGINT;
BEGIN
    SELECT id INTO v_user_id FROM users WHERE lower(wallet_address) = lower(p_user_wallet_address);

    RETURN QUERY
    WITH user_created_paths AS (
        SELECT
            lp.id,
            lp.title,
            lp.short_description,
            lp.total_levels,
            lp.created_at,
            TRUE AS is_created_by_user
        FROM learning_paths lp
        WHERE lower(lp.creator_wallet) = lower(p_user_wallet_address)
    ),
    user_enrolled_details AS (
        SELECT
            e_lp.id,
            up.is_complete AS enrolled_is_complete,
            up.started_at AS enrolled_started_at,
            COALESCE(progress_agg.completed_count, 0) AS enrolled_completed_levels,
            TRUE as is_enrolled_flag
        FROM
            user_progress up
        JOIN
            learning_paths e_lp ON up.path_id = e_lp.id
        LEFT JOIN (
            SELECT
              lp_sub.progress_id,
              count(*) AS completed_count
            FROM
              level_progress lp_sub
            WHERE
              lp_sub.is_complete = true
            GROUP BY
              lp_sub.progress_id
        ) AS progress_agg ON up.id = progress_agg.progress_id
        WHERE
            up.user_id = v_user_id
    )
    SELECT
        COALESCE(ucp.id, ued.id) AS path_id,
        COALESCE(ucp.title, (SELECT lp_title.title FROM learning_paths lp_title WHERE lp_title.id = ued.id)),
        COALESCE(ucp.short_description, (SELECT lp_sd.short_description FROM learning_paths lp_sd WHERE lp_sd.id = ued.id)),
        COALESCE(ucp.total_levels, (SELECT lp_tl.total_levels FROM learning_paths lp_tl WHERE lp_tl.id = ued.id)),
        COALESCE(ucp.created_at, (SELECT lp_ca.created_at FROM learning_paths lp_ca WHERE lp_ca.id = ued.id)),
        COALESCE(ucp.is_created_by_user, FALSE) AS is_created_by_user,
        COALESCE(ued.is_enrolled_flag, FALSE) AS is_enrolled,
        ued.enrolled_is_complete,
        ued.enrolled_started_at,
        ued.enrolled_completed_levels
    FROM user_created_paths ucp
    FULL OUTER JOIN user_enrolled_details ued ON ucp.id = ued.id
    ORDER BY GREATEST(ucp.created_at, ued.enrolled_started_at) DESC, path_id DESC;

END;
$$;