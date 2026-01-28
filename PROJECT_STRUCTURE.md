# Project Structure

Clean, organized structure for the Polymarket AI Trading System.

```
polymarket-ai-trading/
├── README.md                 # Main project documentation
├── render.yaml              # Render deployment config
├── docker-compose.yml       # Local Docker setup
├── Dockerfile              # Container definition
├── .env.example            # Environment variable template
│
├── agents/                 # Trading agents
│   └── systematic_trader.py
│
├── api/                    # Backend API
│   └── dashboard_api.py    # FastAPI server
│
├── config/                 # Trading model configurations
│   ├── active_conservative.yaml
│   ├── active_moderate.yaml
│   ├── active_aggressive.yaml
│   └── models.yaml
│
├── scripts/                # Utility scripts
│   ├── start_all.sh       # Render startup script
│   └── init_databases.py  # Database initialization
│
├── toolkit/                # Reusable modules
│   ├── execution-engine/  # Order execution
│   ├── mean-reversion/    # Statistical arbitrage
│   ├── polymarket-data/   # Market data fetching
│   ├── volatility-alerts/ # Price movement detection
│   └── whale-tracker/     # Large position monitoring
│
├── research/               # Academic research & papers
│   ├── berg-rietz-2018-longshots-overconfidence.md
│   ├── munger-25-biases.md
│   └── papers/            # PDF research papers
│
├── tests/                  # Test suite
│   └── integration/       # Integration tests
│
├── vercel-frontend/        # Web dashboard
│   ├── public/
│   │   ├── index.html     # Main dashboard
│   │   ├── signals.html   # Live signals
│   │   ├── quality.html   # Market quality
│   │   ├── ai-insights.html
│   │   └── resolution.html
│   └── vercel.json        # Vercel config
│
└── docs/                   # Documentation
    ├── README.md          # Documentation index
    ├── deployment/        # Deployment guides
    │   ├── render-quickstart.md
    │   ├── render-complete.md
    │   ├── docker.md
    │   └── vercel.md
    ├── guides/            # User guides
    │   ├── getting-started.md
    │   ├── paper-trading.md
    │   ├── backtesting.md
    │   └── raspberry-pi.md
    └── archive/           # Historical docs
        └── [old summaries & notes]
```

## Runtime Directories (gitignored)

These are created at runtime and not tracked in git:

```
├── data/                   # SQLite databases
│   ├── trades_conservative.db
│   ├── trades_moderate.db
│   └── trades_aggressive.db
│
├── logs/                   # Application logs
│   ├── conservative.log
│   ├── moderate.log
│   └── aggressive.log
│
└── dashboard/             # Old dashboard (deprecated)
```

## Key Files

### Configuration

- **`.env`** - Environment variables (API keys, secrets) - **NEVER COMMIT**
- **`render.yaml`** - Render deployment config (auto-detected)
- **`docker-compose.yml`** - Local multi-container setup
- **`Dockerfile`** - Container image definition

### Entry Points

- **`api/dashboard_api.py`** - Main API server (FastAPI)
- **`agents/systematic_trader.py`** - Trading agent entry point
- **`scripts/start_all.sh`** - Render startup (runs all services)

### Frontend

- **`vercel-frontend/public/index.html`** - Main dashboard
- Dashboard pages are static HTML with vanilla JS
- Deployed to Vercel, consumes FastAPI backend

## Clean Commands

```bash
# Remove runtime data
rm -rf data/ logs/ dashboard/

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Remove node modules
rm -rf vercel-frontend/node_modules

# Full clean (Docker)
docker compose down -v
```

## Development Workflow

1. **Local development**: `docker compose up -d`
2. **View logs**: `docker compose logs -f`
3. **Run tests**: `pytest tests/`
4. **Deploy to Render**: Push to `master` (auto-deploys)
5. **Update frontend**: Push to `master` (Vercel auto-deploys)

---

**Keep it clean!** Only commit source code and documentation, never runtime data or secrets.
