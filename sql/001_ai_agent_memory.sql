-- 001_ai_agent_memory.sql
-- Conversation memory for AI agents (Director + sub-agents)
-- Apply on gg_new database

CREATE TABLE IF NOT EXISTS ai_agent_memory (
  id          SERIAL PRIMARY KEY,
  session_id  VARCHAR(100) NOT NULL,
  agent_name  VARCHAR(50)  NOT NULL,
  role        VARCHAR(20)  NOT NULL CHECK (role IN ('user','assistant','tool','system')),
  content     TEXT         NOT NULL,
  metadata    JSONB,
  created_at  TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_aam_session_created
  ON ai_agent_memory (session_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_aam_agent_created
  ON ai_agent_memory (agent_name, created_at DESC);

COMMENT ON TABLE ai_agent_memory IS
  'Short-term conversation memory of AI agents. Trim entries older than 30 days via scheduled job.';
