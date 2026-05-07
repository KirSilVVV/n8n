-- 003_hourly_pulse.sql
-- Hourly heartbeat of each agent
-- Schema: ai

CREATE TABLE IF NOT EXISTS ai.hourly_pulse (
  id          SERIAL PRIMARY KEY,
  agent_name  VARCHAR(50) NOT NULL,
  pulse_at    TIMESTAMPTZ NOT NULL,
  status      VARCHAR(20) NOT NULL
              CHECK (status IN ('running','idle','blocked','error','degraded')),
  summary     TEXT,
  metrics     JSONB,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hp_agent_pulse
  ON ai.hourly_pulse (agent_name, pulse_at DESC);

CREATE INDEX IF NOT EXISTS idx_hp_status_pulse
  ON ai.hourly_pulse (status, pulse_at DESC)
  WHERE status IN ('blocked','error','degraded');

COMMENT ON TABLE ai.hourly_pulse IS
  'Heartbeat of each agent. Director reads latest row per agent_name to compose CEO Brief.';
