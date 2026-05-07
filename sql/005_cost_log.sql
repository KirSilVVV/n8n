-- 005_cost_log.sql
-- Daily Anthropic API spend per agent (ROI tracking)
-- Schema: ai

CREATE TABLE IF NOT EXISTS ai.cost_log (
  id              SERIAL PRIMARY KEY,
  log_date        DATE         NOT NULL,
  agent_name      VARCHAR(50)  NOT NULL,
  model           VARCHAR(100) NOT NULL,
  tokens_input    BIGINT       DEFAULT 0,
  tokens_output   BIGINT       DEFAULT 0,
  cost_usd        NUMERIC(10,4) DEFAULT 0,
  requests        INTEGER       DEFAULT 0,
  created_at      TIMESTAMPTZ   DEFAULT NOW(),
  UNIQUE (log_date, agent_name, model)
);

CREATE INDEX IF NOT EXISTS idx_cl_date
  ON ai.cost_log (log_date DESC);

CREATE INDEX IF NOT EXISTS idx_cl_agent_date
  ON ai.cost_log (agent_name, log_date DESC);

COMMENT ON TABLE ai.cost_log IS
  'Daily API spend per agent. Cost Watcher updates this; Director computes ROI vs revenue.';
