-- =============================================================================
-- MIRROR FUTURE - 100% PRODUCTION REAL SCHEMA FOR SUPABASE (ZERO MOCKS, ZERO FAKE DATA)
-- Database Architecture: PostgreSQL + pgvector (384 dimensions)
-- Strict Production DDL provided for Supabase RAG and Relational Ingestion
-- =============================================================================

-- Enable vector and crypto extensions in Supabase for RAG over real chats
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Real User Profile and Telemetry of Actual Time/Habits
CREATE TABLE IF NOT EXISTS user_real_profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    whatsapp_alias TEXT NOT NULL, -- Exact user alias as it appears in exported WhatsApp chats
    occupation_and_goals TEXT NOT NULL,
    real_calendar_busy_hours_week FLOAT DEFAULT 40.0, -- Calculated from Google Calendar / real .ics
    real_avg_sleep_hours FLOAT DEFAULT 6.5,
    real_study_thesis_hours_day FLOAT DEFAULT 2.5,
    github_username TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE user_real_profile IS 'Real User Profile and Telemetry of Real Time/Habits calculated from Calendar and GitHub.';

-- 2. Real Contacts Extracted from WhatsApp Exports
CREATE TABLE IF NOT EXISTS real_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_real_profile(id) ON DELETE CASCADE,
    contact_name TEXT NOT NULL, -- Real contact name extracted from WhatsApp archive
    relationship_type TEXT NOT NULL, -- 'FAMILY', 'WORK', 'FRIEND', 'ROMANTIC'
    total_messages_analyzed INT DEFAULT 0,
    real_median_reply_minutes FLOAT, -- Real median latency in minutes to reply
    user_initiates_pct FLOAT, -- % of times user initiates conversation vs contact
    active_hours_distribution JSONB, -- Real histogram of active hours from 00h to 23h
    real_lexical_profile JSONB, -- Most frequent words, authentic emojis, average message length, tone
    extracted_psych_summary TEXT, -- Psychological profile synthesized by Meta Llama reading real chats
    last_interaction_at TIMESTAMPTZ,
    CONSTRAINT unique_user_real_contact UNIQUE (user_id, contact_name)
);

COMMENT ON TABLE real_contacts IS 'Real Contacts Extracted from WhatsApp Exports with exact lexical profile and response latency.';

-- 3. Real Episodic Memory (Dense Vectorized WhatsApp Messages)
CREATE TABLE IF NOT EXISTS real_chat_episodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID REFERENCES real_contacts(id) ON DELETE CASCADE,
    episode_timestamp TIMESTAMPTZ NOT NULL,
    conversation_chunk TEXT NOT NULL, -- Real dialogue block (User <-> Contact)
    sentiment_score FLOAT, -- Calculated during ingestion (-1.0 to +1.0)
    embedding vector(384) -- Dense vector generated with sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
);

COMMENT ON TABLE real_chat_episodes IS 'Real Episodic Memory with 384-dimensional dense vectors for semantic search.';

-- 4. Semantic Search RPC Function across Real Chats
CREATE OR REPLACE FUNCTION match_real_episodes (
    p_contact_id UUID,
    query_embedding vector(384),
    match_count INT DEFAULT 5
) RETURNS TABLE (
    id UUID,
    episode_timestamp TIMESTAMPTZ,
    conversation_chunk TEXT,
    similarity FLOAT
) LANGUAGE plpgsql STABLE SECURITY DEFINER AS $$
BEGIN
    RETURN QUERY
    SELECT e.id,
           e.episode_timestamp,
           e.conversation_chunk,
           (1 - (e.embedding <=> query_embedding))::FLOAT AS similarity
    FROM real_chat_episodes e
    WHERE e.contact_id = p_contact_id
      AND e.embedding IS NOT NULL
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END; $$;

COMMENT ON FUNCTION match_real_episodes IS 'Semantic Search RPC Function across Real Chats using pgvector cosine distance.';

-- 5. Calibration Log: Predictions vs. Reality (Scientific Evaluation)
CREATE TABLE IF NOT EXISTS causal_predictions_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_real_profile(id),
    decision_type TEXT NOT NULL,
    decision_payload JSONB NOT NULL,
    predicted_outcomes JSONB NOT NULL,
    actual_real_world_outcome JSONB, -- Verified real-world outcome following decision
    brier_accuracy_score FLOAT, -- Mathematical accuracy score of Mirror Future prediction
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE causal_predictions_log IS 'Log of Predictions vs. Real-world Outcomes for Scientific Calibration of the Agent.';

-- =============================================================================
-- PERFORMANCE INDEXES (HNSW & B-TREE)
-- =============================================================================

-- HNSW Vector Index for sub-millisecond cosine similarity search
CREATE INDEX IF NOT EXISTS idx_real_chat_episodes_hnsw
    ON real_chat_episodes 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- B-Tree indexes for relational queries and foreign key constraints
CREATE INDEX IF NOT EXISTS idx_real_contacts_user_id ON real_contacts(user_id);
CREATE INDEX IF NOT EXISTS idx_real_contacts_name ON real_contacts(contact_name);
CREATE INDEX IF NOT EXISTS idx_real_chat_episodes_contact_id ON real_chat_episodes(contact_id);
CREATE INDEX IF NOT EXISTS idx_real_chat_episodes_timestamp ON real_chat_episodes(episode_timestamp);
CREATE INDEX IF NOT EXISTS idx_causal_predictions_user_id ON causal_predictions_log(user_id);

-- =============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES FOR SUPABASE
-- =============================================================================

ALTER TABLE user_real_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE real_contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE real_chat_episodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE causal_predictions_log ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE policyname = 'service_role_all_user_real_profile'
    ) THEN
        CREATE POLICY service_role_all_user_real_profile ON user_real_profile FOR ALL TO service_role USING (true) WITH CHECK (true);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE policyname = 'service_role_all_real_contacts'
    ) THEN
        CREATE POLICY service_role_all_real_contacts ON real_contacts FOR ALL TO service_role USING (true) WITH CHECK (true);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE policyname = 'service_role_all_real_chat_episodes'
    ) THEN
        CREATE POLICY service_role_all_real_chat_episodes ON real_chat_episodes FOR ALL TO service_role USING (true) WITH CHECK (true);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE policyname = 'service_role_all_causal_predictions_log'
    ) THEN
        CREATE POLICY service_role_all_causal_predictions_log ON causal_predictions_log FOR ALL TO service_role USING (true) WITH CHECK (true);
    END IF;
END $$;
