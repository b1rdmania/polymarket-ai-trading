# Deployment Guide

## Prerequisites

- Python 3.9+
- Docker (optional, for containerized deployment)
- 2GB RAM minimum
- Stable internet connection

## Local Deployment

### 1. Install Dependencies

```bash
cd toolkit/execution-engine
pip install -e .

cd ../mean-reversion
pip install -e .

cd ../volatility-alerts
pip install -e .

cd ../polymarket-data
pip install -e .
```

### 2. Configure

Edit `config/trading.yaml`:
- Set `mode: paper` for testing
- Adjust risk limits
- Set `dry_run: true` initially

### 3. Run

```bash
python agents/systematic_trader.py --config config/trading.yaml
```

## Docker Deployment

### Build and Run

```bash
./scripts/deploy-docker.sh
```

### View Logs

```bash
docker logs -f systematic-trader
```

### Stop

```bash
docker stop systematic-trader
```

## Systemd Service (Linux)

### 1. Install

```bash
sudo cp scripts/systematic-trader.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### 2. Configure

Create user and directories:

```bash
sudo useradd -r -s /bin/false trader
sudo mkdir -p /opt/aztec-auction-analysis
sudo chown trader:trader /opt/aztec-auction-analysis
```

Copy application:

```bash
sudo cp -r . /opt/aztec-auction-analysis/
```

### 3. Start

```bash
sudo systemctl enable systematic-trader
sudo systemctl start systematic-trader
```

### 4. Monitor

```bash
sudo systemctl status systematic-trader
sudo journalctl -u systematic-trader -f
```

## Cloud Deployment

### DigitalOcean Droplet

1. Create droplet (Ubuntu 22.04, $10/mo)
2. SSH and clone repo
3. Install dependencies
4. Set up systemd service
5. Start trading

### AWS EC2

1. Launch t3.micro instance
2. Configure security group (outbound only)
3. Install application
4. Use systemd for management

## Monitoring

### Dashboard

Access at: `http://localhost:8000/dashboard/trading/`

### Logs

- Application: `logs/trading.log`
- Trades: `logs/trades/`
- Paper trades: `logs/paper/`

### Database

Query performance:

```bash
sqlite3 data/trades.db "SELECT * FROM performance"
```

## Emergency Stop

```bash
python scripts/emergency_stop.py
```

This will:
- Close all positions
- Cancel pending orders
- Create shutdown flag
- Stop trading loop

## Backup

Important files to backup:
- `data/trades.db`
- `logs/`
- `config/trading.yaml`

## Security

- Never commit `.env` files
- Store private keys in environment variables
- Use read-only API keys when possible
- Enable 2FA on exchanges
- Regular security audits


