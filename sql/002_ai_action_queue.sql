-- 002_ai_action_queue.sql
-- Queue of agent-proposed actions awaiting CEO approve / auto-approved by whitelist
-- Apply on gg_new database

CREATE TABLE IF NOT EXISTS ai_action_queue (
  id                  SERIAL PRIMARY KEY,
  agent_name          VARCHAR(50) NOT NULL,
  action_type         VARCHAR(50) NOT NULL,
  payload             JSONB       NOT NULL,
  preview             TEXT,
  status              VARCHAR(20) NOT NULL DEFAULT 'pending'
                      CHECK (status IN ('pending','approved','rejected','auto','done','expired')),
  approval_required   BOOLEAN     NOT NULL DEFAULT TRUE,
  ceo_comment         TEXT,
  sla_deadline        TIMESTAMPTZ,
  why_now             TEXT,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  resolved_at         TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_aaq_status_created
  ON ai_action_queue (status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_aaq_pending_sla
  ON ai_action_queue (sla_deadline)
  WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_aaq_agent_status
  ON ai_action_queue (agent_name, status, created_at DESC);

COMMENT ON TABLE ai_action_queue IS
  'Action proposals from agents. Whitelist actions auto-approve; others wait for CEO. SLA timer triggers escalation.';
