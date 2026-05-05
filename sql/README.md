# SQL migrations

Apply in order on the gg_new database (PG 65.108.141.27:5433).

| File | Purpose |
|------|---------|
| `001_ai_agent_memory.sql` | Conversation memory of AI agents (Director + sub-agents) |
| `002_ai_action_queue.sql` | Queue of actions awaiting CEO approve / auto-approved by whitelist |
| `003_ai_hourly_pulse.sql` | Heartbeat of each agent every hour with status + summary |
| `004_ai_agent_settings.sql` | System prompts, model choice, whitelist actions per agent |
| `005_ai_cost_log.sql` | Daily Anthropic API spend per agent for ROI tracking |

Apply with:
```bash
psql -h 65.108.141.27 -p 5433 -U n8n_writer -d gg_new -f sql/001_ai_agent_memory.sql
```
