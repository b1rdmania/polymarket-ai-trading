# 🐳 Docker Deployment Guide

## What This Does

Runs all 3 trading models + dashboard in **Docker containers**:
- ✅ Runs on any computer (Mac, Linux, Windows, Pi)
- ✅ Auto-restarts if crashes
- ✅ Isolated environments
- ✅ Easy to deploy anywhere
- ✅ Professional setup

---

## 🚀 Quick Start (3 Commands)

### 1. Stop Local Processes

```bash
bash scripts/stop_all.sh
```

### 2. Build & Start Docker

```bash
docker-compose up -d --build
```

### 3. View Dashboard

```bash
open http://localhost:8000
```

**That's it!** All 4 containers are running!

---

## 📦 What's Running

### 4 Containers

```
polymarket-conservative  (Model 1)
polymarket-moderate      (Model 2)
polymarket-aggressive    (Model 3)
polymarket-dashboard     (Web UI)
```

Each in its own isolated container, with auto-restart!

---

## 🎮 Docker Commands

### Start Everything
```bash
docker-compose up -d
```

### Stop Everything
```bash
docker-compose down
```

### View Logs
```bash
# All containers
docker-compose logs -f

# Specific model
docker-compose logs -f conservative
docker-compose logs -f moderate
docker-compose logs -f aggressive
docker-compose logs -f dashboard
```

### Check Status
```bash
docker-compose ps
```

### Restart One Model
```bash
docker-compose restart conservative
```

### Restart All
```bash
docker-compose restart
```

---

## 🔍 Monitor Performance

### Dashboard (Browser)
```bash
open http://localhost:8000
```

### Terminal Monitor (from host)
```bash
python3 scripts/monitor_models.py --loop
```

### Container Stats
```bash
# CPU/Memory usage
docker stats

# Specific container
docker stats polymarket-conservative
```

---

## 📊 Data Persistence

### Volumes (Data is Saved)

Even if you stop containers, data persists:
- `./data/` → Databases
- `./logs/` → Log files
- `./config/` → Configurations

**Safe to stop/restart anytime!**

---

## 🔧 Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs conservative

# Rebuild
docker-compose up -d --build --force-recreate
```

### Dashboard not accessible

```bash
# Check if running
docker-compose ps

# Check port
lsof -i :8000

# Restart dashboard
docker-compose restart dashboard
```

### Models not trading

```bash
# View live logs
docker-compose logs -f moderate

# Check for errors
docker-compose logs moderate | grep ERROR
```

### Reset everything

```bash
# Stop and remove containers
docker-compose down

# Remove old images
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

---

## 🌍 Deploy to Cloud (Any Provider)

### DigitalOcean ($6/month)

```bash
# 1. Create droplet (Ubuntu)
# 2. SSH in
ssh root@your-droplet-ip

# 3. Install Docker
curl -fsSL https://get.docker.com | sh

# 4. Clone repo
git clone https://github.com/yourusername/aztec-auction-analysis.git
cd aztec-auction-analysis

# 5. Start
docker-compose up -d

# 6. Access dashboard
# http://your-droplet-ip:8000
```

### AWS EC2 (Free Tier)

```bash
# Same as above, but use EC2 instance
# Ubuntu 22.04 LTS
# t2.micro (free tier)
```

### Raspberry Pi

```bash
# 1. Install Docker on Pi
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker pi

# 2. Clone repo
git clone <your-repo>
cd aztec-auction-analysis

# 3. Start
docker-compose up -d

# 4. Access on local network
# http://raspberrypi.local:8000
```

---

## 🔐 Environment Variables (Optional)

For live trading (not paper), create `.env`:

```bash
# .env
POLYGON_WALLET_PRIVATE_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

Docker Compose will automatically load it.

---

## 📈 Production Best Practices

### 1. Enable Auto-Start on Boot

```bash
# Docker will restart containers on reboot
# Already configured with: restart: unless-stopped
```

### 2. Set Up Monitoring

```bash
# Use cron to check health
crontab -e

# Add:
*/5 * * * * docker-compose -f /path/to/docker-compose.yml ps | grep -q "Up" || docker-compose -f /path/to/docker-compose.yml up -d
```

### 3. Backup Data

```bash
# Backup databases daily
crontab -e

# Add:
0 0 * * * tar -czf /backups/polymarket-$(date +\%Y\%m\%d).tar.gz /path/to/data/
```

---

## 🆚 Docker vs Local

| Feature | Local | Docker |
|---------|-------|--------|
| **Setup** | ✅ Simple | ⚠️ Requires Docker |
| **Portability** | ❌ Mac only | ✅ Any platform |
| **Isolation** | ❌ Shared env | ✅ Isolated |
| **Auto-restart** | ❌ Manual | ✅ Automatic |
| **Deploy to Cloud** | ❌ Hard | ✅ Easy |
| **Pi Compatible** | ❌ No | ✅ Yes |
| **Resource Usage** | ✅ Lower | ⚠️ Slightly higher |

---

## 🎯 Recommended Setup

### For Testing (30 days)
**Local** - Keep your Mac on
- Simpler
- Already running
- Free

### For Live Trading (Real $$$)
**Docker on Cloud** - $6/month DigitalOcean
- 24/7 uptime
- Professional
- Remote access
- Auto-restart

### For Home Setup
**Docker on Raspberry Pi** - $100 one-time
- Runs at home
- Low power
- Always on
- Cost effective

---

## 🚀 Quick Deploy to DigitalOcean

### 1-Click Setup Script

```bash
#!/bin/bash
# deploy-to-do.sh

# Install Docker
curl -fsSL https://get.docker.com | sh

# Clone repo
git clone <your-repo-url>
cd aztec-auction-analysis

# Start everything
docker-compose up -d

# Show status
docker-compose ps

echo "Dashboard: http://$(curl -s ifconfig.me):8000"
```

Run on your droplet:
```bash
bash deploy-to-do.sh
```

Done! 🎉

---

## 📞 Support

### Check everything is running
```bash
docker-compose ps
```

Should see:
```
NAME                      STATUS              PORTS
polymarket-conservative   Up (healthy)
polymarket-moderate       Up (healthy)
polymarket-aggressive     Up (healthy)
polymarket-dashboard      Up (healthy)    0.0.0.0:8000->8000/tcp
```

### Logs location
- Inside containers: `/app/logs/`
- On host: `./logs/`

---

## 🎯 Current Status

**You now have**:
- ✅ Dockerfile (build config)
- ✅ docker-compose.yml (orchestration)
- ✅ .dockerignore (optimization)
- ✅ Complete documentation

**To switch from local to Docker**:

```bash
# Stop local
bash scripts/stop_all.sh

# Start Docker
docker-compose up -d --build

# Check
docker-compose ps
```

**Dashboard stays the same**: http://localhost:8000

---

**Ready to containerize?** 🐳


