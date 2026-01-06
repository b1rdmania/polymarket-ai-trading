# Polymarket AI Trading Protocol

AI-assisted probability analysis with smart contract execution for Polymarket prediction markets.

**by [b1rdmania](https://github.com/b1rdmania)**

## 🎯 Overview

This is a production-ready AI trading system for Polymarket that uses:
- **Mean reversion models** trained on 40 years of prediction market research
- **Three parallel trading strategies** (Conservative, Moderate, Aggressive)
- **Paper trading mode** for risk-free testing
- **Real-time AI analysis** using OpenAI GPT-4o-mini
- **Live monitoring dashboard** hosted on Vercel

## 🚀 Features

- ✅ Live market data streaming from Polymarket
- ✅ AI-powered probability analysis
- ✅ Multi-model parallel trading (3 strategies)
- ✅ Real-time signal detection
- ✅ Market quality scoring
- ✅ Resolution tracking and accuracy metrics
- ✅ Semantic market search using embeddings
- ✅ Docker-based deployment
- ✅ 24/7 operation via Cloudflare Tunnel

## 📊 Live Dashboard

**Frontend**: https://vercel-frontend-g4o1sdx6o-boom-test-c54cde04.vercel.app  
**Backend**: https://postposted-spent-knife-given.trycloudflare.com  
**Status**: ✅ Production

The dashboard shows:
- Real-time market data streaming
- Backend connection status (green dot = connected)
- AI insights and analysis
- Market quality indicators
- Trading signals
- Resolution tracking
- Model performance comparison

## 🏗️ Architecture

```
Frontend (Vercel)
    ↓
Cloudflare Tunnel
    ↓
Docker Backend (localhost:8000)
    ↓
3 Trading Models + Dashboard API
```

### Trading Models

1. **Conservative**: Low-risk, high-confidence trades
2. **Moderate**: Balanced risk/reward
3. **Aggressive**: High-risk, high-reward opportunities

All models run in **paper trading mode** by default.

## 🛠️ Quick Start

### Prerequisites

- Docker Desktop
- OpenAI API key (for AI features)
- Cloudflare Tunnel (for public access)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/b1rdmania/polymarket-ai-trading.git
cd polymarket-ai-trading
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. **Start Docker containers**
```bash
docker compose up -d
```

4. **Start Cloudflare Tunnel** (optional, for public access)
```bash
cloudflared tunnel --url http://localhost:8000
```

5. **Deploy frontend to Vercel**
```bash
cd vercel-frontend
vercel --prod
```

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT.md)
- [Docker Guide](DOCKER_GUIDE.md)
- [Paper Trading Start](PAPER_TRADING_START.md)
- [Backtesting Guide](BACKTESTING_GUIDE.md)
- [Vercel Deployment](VERCEL_DEPLOY.md)
- [Go Live Instructions](GO_LIVE.md)

## 🔬 Research Foundation

Based on extensive prediction market research:
- Mean reversion strategies
- Behavioral biases in prediction markets
- Quantitative probability analysis
- 40+ years of academic literature

See [research/](research/) for detailed papers and findings.

## 🧰 Toolkit

The system includes several specialized modules:

- **execution-engine**: Order execution and trade management
- **mean-reversion**: Statistical arbitrage detection
- **polymarket-data**: Market data fetching and analysis
- **volatility-alerts**: Price movement detection
- **whale-tracker**: Large position monitoring

## 🎨 Frontend

Modern, responsive dashboard built with vanilla JavaScript:
- Real-time market data ticker
- AI insights and analysis
- Market quality indicators
- Trading signal detection
- Resolution tracking
- Model performance comparison

## 🐳 Docker Setup

The system runs 4 containers:
- `polymarket-dashboard`: API and web interface (port 8000)
- `polymarket-conservative`: Conservative trading model
- `polymarket-moderate`: Moderate trading model
- `polymarket-aggressive`: Aggressive trading model

## 🔐 Security

- API keys stored in `.env` (gitignored)
- Paper trading mode prevents real trades
- Cloudflare Tunnel for secure public access
- No private keys in code

## 📈 Monitoring

Access the dashboard at `http://localhost:8000` or your Cloudflare Tunnel URL to monitor:
- Live market data
- Model performance
- Trading signals
- P&L tracking
- Resolution accuracy

## 🤝 Contributing

This is a personal research project, but suggestions and feedback are welcome!

## 📄 License

MIT License - See LICENSE for details

## 🙏 Acknowledgments

Built on research from:
- Berg & Rietz (2018) - Longshots and overconfidence
- Munger's 25 cognitive biases
- Prediction market accuracy literature
- @the_smart_ape's trading insights

## 🔗 Links

- [GitHub Repository](https://github.com/b1rdmania/polymarket-ai-trading)
- [Polymarket](https://polymarket.com)
- [My GitHub](https://github.com/b1rdmania)

---

**Note**: This system is for educational and research purposes. Always trade responsibly.

