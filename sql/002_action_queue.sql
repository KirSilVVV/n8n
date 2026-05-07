-- 002_action_queue.sql
-- Queue of agent-proposed actions awaiting CEO approve / auto-approved by whitelist
-- Schema: ai

CREATE TABLE IF NOT EXISTS ai.action_queue (
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

CREATE INDEX IF NOT EXISTS idx_aq_status_created
  ON ai.action_queue (status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_aq_pending_sla
  ON ai.action_queue (sla_deadline)
  WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_aq_agent_status
  ON ai.action_queue (agent_name, status, created_at DESC);

COMMENT ON TABLE ai.action_queue IS
  'Action proposals from agents. Whitelist actions auto-approve; others wait for CEO. SLA timer triggers escalation.';
