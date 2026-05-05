# n8n Workflows

**Last updated:** 2026-05-05
**n8n instance:** https://n8n-4d54.onrender.com
**Telegram chat:** `83436260`
**Telegram bot:** [@n8n_ggbot](https://t.me/n8n_ggbot)
**Postgres:** `65.108.141.27:5433` · db `gg_new`

---

## Production workflows (22 active)

### Reports & orchestration

| Workflow | n8n ID | Schedule | Purpose |
|---|---|---|---|
| `[REPORT]-GG-Daily-CEO-Brief.json` | `YVH67YNAB44TlTee` | `0 6 * * *` (09:00 МСК) | Daily CEO Brief in Telegram |
| `[BOT]-GG-Telegram-v2.json` | `lpRlcddSkLxcLVwb` | webhook | Telegram bot for notifications & commands |
| `[PULSE]-GG-Order-Watchdog.json` | `j0kAQH8eXHtMCO51` | every 15 min | Watch new orders / SHOP_FAILED |

### SEO stack

| Workflow | n8n ID | Schedule | Purpose |
|---|---|---|---|
| `WF-201_GSC_GA4_SEO_Report.json` | `1EcezAM2sWYv6WSL` | `0 5 * * *` | GSC + GA4 + Yandex Webmaster daily fetch |
| `WF-202_SEO_AI_Agent_v2.json` | — | `0 6 * * *` | Analyze SEO data, propose actions |
| `WF-204_Yandex_Recrawl.json` | `ayh2yYy0u5p3tWap` | daily 21:00 UTC | Send fresh URLs to Yandex Webmaster (910 quota) |
| `WF-205_Weekly_SEO_Audit.json` | `jzA0CgaqzrXBYUu5` | `0 7 * * 4` (Thu) | Weekly SEO delta with audit |
| `WF-206_Google_Indexing.json` | `G9xgJQOOs1hMvBF0` | manual | Google Indexing API (blocked: scope) |
| `WF-301_SEO_Content_Generator.json` | `xPhhEHGFbGHjfZN7` | nightly | Generate SEO packs (~1443 pages/night, $0.03/page) |

### Retention stack

| Workflow | n8n ID | Schedule | Purpose |
|---|---|---|---|
| `WF-R02_weekly_rfm_digest.json` | `9Qd6VR48og61qd4q` | Mon 09:00 МСК | RFM segmentation digest |
| `WF-R-CHAMPION-CHURN_daily.json` | `bVj6oMkR97M9m1G5` | daily 08:30 МСК | Whale silent ≥10 days alert (LTV ≥€500) |
| `WF-R-WINBACK-01_weekly_at_risk_scan.json` | `b3Ki8FYNjTh3pIzn` | Tue 09:30 МСК | At Risk CSV with personal WB-promo codes |
| `WF-R-WINBACK-02_post_campaign_report.json` | `XSHDd09EwLcFd9yk` | Mon 10:00 МСК | Post-campaign ROI on WB* codes |
| `WF-R-ALERT-01_problem_skus_weekly.json` | `fVocELq5ZqC4EHKQ` | Fri 10:00 МСК | Combined alert by problem SKUs |
| `WF-WINBACK-EMAIL-SENDER.json` | `CMJWU3gJG8oxsn5r` | webhook | ⚠ Awaiting SMTP credentials |
| `SQL-Safety-Check-001_weekly_new_problems.json` | `dtsNbhqyu4tRF6z7` | Thu 10:00 МСК | New SKUs with cancel ≥50% |

### Product / monitoring

| Workflow | n8n ID | Schedule | Purpose |
|---|---|---|---|
| `WF-103-Product-Agent-(SHOP_FAILED-Monitor).json` | `jBTUv16jWd1Gqjvk` | daily 07:00 UTC | SHOP_FAILED monitor + AI agent recommendations |
| `WF-MONITOR_Error_Alert.json` | `1OdOc9QTkRFve0dM` | every 2h | Alert on workflow errors + 09:00 daily summary |

### AI Manager Context

| Workflow | n8n ID | Schedule | Purpose |
|---|---|---|---|
| `[AI]-WF-014-Daily-Manager-Context-Refresh.json` | `BkvZZxZoyp9vSnrg` | daily | Refresh `ai_manager_context` table |
| `[API]-WF-015-Get-Manager-Context.json` | `h4xzLhMFoq044JIm` | webhook | Read context for agents |

### Utilities

| Workflow | n8n ID | Schedule | Purpose |
|---|---|---|---|
| `[UTIL]-Render-Keepalive.json` | `MgdXyzvYmeQWfSSt` | every 10 min | Keep Render free-tier alive |
| `[TEST]-PG-Query.json` | `GvQ1CVxAHzgUZUMq` | webhook `/pg-test-v2` | Live SQL query webhook |

---

## Planned workflows (not yet built)

These are scoped in `docs/` and will be added during May 2026 sprints.

| Workflow | Sprint | Purpose |
|---|---|---|
| `WF-200_Director_Orchestrator.json` | 1 | Main orchestrator: collect 6 sub-agents → Telegram brief |
| `WF-210_Action_Queue.json` | 1 | Webhook CRUD for `ai_action_queue` |
| `WF-203_Sales_Agent.json` | 2 | B2B pipeline + whale-touch drafts |
| `WF-220_Whale_Personal_Touch.json` | 2 | Daily top-20 scan + auto-drafts to CEO |
| `WF-211_Self_Healing.json` | 2 | 4-hour health check + autofix |
| `WF-207_Owner_Daily_Digest.json` | 3 | 21:00 МСК digest to Andrey Zokin |
| `WF-212_Cost_Watcher.json` | 3 | Daily Anthropic API spend + ROI |

See `docs/` for full system prompts and architecture.

---

## Conventions

- **Strictly linear chains**, no parallel branches.
- **No SplitInBatches for write operations** (PG UPDATE without RETURNING returns zero rows).
- **HTTP Request node with `batching:1`** for sequential processing.
- **JSON bodies**: `contentType: "json"` + `specifyBody: "json"` + `jsonBody` as `={{ {key: value} }}`.
- **Webhook responses**: wrap SQL in `SELECT json_agg(t) AS result FROM ({sql}) t` to return all rows.
- **GitHub commits**: fetch existing file SHA first before PUT.

---

## Folder structure

```
workflows/         ← active production (22 files)
archive/           ← deprecated workflows kept for history
  ceo-brief-old/   ← 3 old CEO Brief versions
  wf-201-old/      ← 3 old WF-201 versions
  seo-other/       ← WF-202 v1, wf_205_yw intermediate
  research-2026-q1/← 16 one-shot SQL queries
sql/               ← migrations: ai_action_queue, ai_hourly_pulse, etc.
scripts/           ← repo automation (readme-generator, deployer, mover)
docs/              ← architecture, prompts, operating model
```
