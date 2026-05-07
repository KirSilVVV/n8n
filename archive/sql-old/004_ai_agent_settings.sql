-- 004_ai_agent_settings.sql
-- Mutable settings per agent: system prompt, model, whitelist actions
-- Apply on gg_new database

CREATE TABLE IF NOT EXISTS ai_agent_settings (
  agent_name          VARCHAR(50) PRIMARY KEY,
  system_prompt       TEXT,
  model               VARCHAR(100) DEFAULT 'claude-sonnet-4-5-20250929',
  temperature         NUMERIC(3,2) DEFAULT 0.30,
  max_tokens          INTEGER      DEFAULT 4000,
  is_active           BOOLEAN      DEFAULT TRUE,
  whitelist_actions   JSONB        DEFAULT '[]'::JSONB,
  budget_usd_month    NUMERIC(8,2) DEFAULT 30.00,
  schedule_cron       VARCHAR(100),
  updated_at          TIMESTAMPTZ  DEFAULT NOW()
);

-- Seed rows for the 11 known agents (prompts loaded later from docs/PROMPTS.md)
INSERT INTO ai_agent_settings (agent_name, model, budget_usd_month, schedule_cron) VALUES
  ('director',           'claude-sonnet-4-5-20250929', 15.00, '0 6,9,12,15,18 * * *'),
  ('cmo',                'claude-sonnet-4-5-20250929', 30.00, '0 7 * * *'),
  ('cpo',                'claude-sonnet-4-5-20250929', 25.00, '0 8 * * *'),
  ('sales',              'claude-sonnet-4-5-20250929', 20.00, '0 9 * * 1'),
  ('seo',                'claude-sonnet-4-5-20250929', 15.00, '0 6 * * *'),
  ('retention',          'claude-haiku-4-5-20251001',   5.00, '0 8 * * *'),
  ('cto_backlog',        'claude-sonnet-4-5-20250929', 10.00, '0 10 * * *'),
  ('whale_personal',     'claude-sonnet-4-5-20250929', 15.00, '30 9 * * *'),
  ('owner_digest',       'claude-haiku-4-5-20251001',   2.00, '0 21 * * *'),
  ('cost_watcher',       'claude-haiku-4-5-20251001',   1.00, '30 23 * * *'),
  ('self_healing',       'claude-haiku-4-5-20251001',   3.00, '0 */4 * * *')
ON CONFLICT (agent_name) DO NOTHING;

COMMENT ON TABLE ai_agent_settings IS
  'Per-agent runtime settings. Editable via panel without redeploy. Loaded by each workflow at start.';
