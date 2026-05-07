# SQL migrations

Apply in order on the gg_new database.

**Connection:** `host=65.108.141.27 port=5433 dbname=gg_new user=ai_agent sslmode=disable`

| File | Creates | Purpose |
|------|---------|---------|
| `001_agent_memory.sql`   | `ai.agent_memory`   | Conversation memory (Director + sub-agents) |
| `002_action_queue.sql`   | `ai.action_queue`   | Approval queue with SLA timer |
| `003_hourly_pulse.sql`   | `ai.hourly_pulse`   | Per-agent heartbeat with status + metrics |
| `004_agent_settings.sql` | `ai.agent_settings` | System prompts, model, budget per agent (+ 11 seed rows) |
| `005_cost_log.sql`       | `ai.cost_log`       | Daily Anthropic API spend for ROI tracking |

**Apply:**
```bash
psql "host=65.108.141.27 port=5433 dbname=gg_new user=ai_agent password=$DB_PASS sslmode=disable" \
  -f sql/001_agent_memory.sql \
  -f sql/002_action_queue.sql \
  -f sql/003_hourly_pulse.sql \
  -f sql/004_agent_settings.sql \
  -f sql/005_cost_log.sql
```

**Status:** ✅ all 5 applied to production on 7 May 2026.

## Schema isolation

All AI tables live in the `ai` schema, fully separated from `public`:
- `ai_agent` user has full DDL/DML rights only inside `ai.*`
- `ai_agent` has SELECT-only on `public.*` (orders, products, users, etc.)
- Production data cannot be touched by AI workflows by design
