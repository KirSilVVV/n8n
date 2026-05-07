-- 001_agent_memory.sql
-- Conversation memory for AI agents (Director + sub-agents)
-- Schema: ai (isolated from public)

CREATE TABLE IF NOT EXISTS ai.agent_memory (
  id          SERIAL PRIMARY KEY,
  session_id  VARCHAR(100) NOT NULL,
  agent_name  VARCHAR(50)  NOT NULL,
  role        VARCHAR(20)  NOT NULL CHECK (role IN ('user','assistant','tool','system')),
  content     TEXT         NOT NULL,
  metadata    JSONB,
  created_at  TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_am_session_created
  ON ai.agent_memory (session_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_am_agent_created
  ON ai.agent_memory (agent_name, created_at DESC);

COMMENT ON TABLE ai.agent_memory IS
  'Short-term conversation memory of AI agents. Trim entries older than 30 days via scheduled job.';
