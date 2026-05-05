# Scripts

| File | Purpose |
|------|---------|
| `readme-generator.py` | Auto-generate workflows/README.md from workflow metadata |
| `archive-mover.py` | Move workflows between folders preserving git history |
| `workflow-deployer.py` | Push workflow JSON to n8n instance via API |

All scripts use env vars: `GH_TOKEN`, `N8N_API_KEY`, `N8N_HOST`.
