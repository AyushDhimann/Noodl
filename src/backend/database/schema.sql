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
    current_level_id BIGINT REFERENCES levels(id),
    current_item_index INT,
    status TEXT DEFAULT 'not_started',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    UNIQUE(user_id, path_id)
);

-- 6. QUIZ ATTEMPT HISTORY & SCORES
CREATE TABLE quiz_attempts (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    progress_id BIGINT REFERENCES user_progress(id) ON DELETE CASCADE,
    content_item_id BIGINT REFERENCES content_items(id) ON DELETE CASCADE,
    user_answer_index INT,
    is_correct BOOLEAN,
    attempted_at TIMESTAMPTZ DEFAULT now()
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

-- Trigger to update the timestamp on row update
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON task_progress_logs
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