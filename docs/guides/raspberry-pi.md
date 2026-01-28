# 🥧 Raspberry Pi Complete Guide

## 💰 Shopping List (~$100-120)

### Core Kit
1. **Raspberry Pi 5 (8GB RAM)** - $80
   - Where: Amazon, CanaKit, Adafruit
   - Why 8GB: Running 3 models + other apps
   
2. **Official 27W USB-C Power Supply** - $12
   - Must be official Pi 5 power supply
   - 27W required (don't use phone charger!)

3. **128GB MicroSD Card (Class 10/U3)** - $15
   - Samsung EVO Plus or SanDisk Extreme
   - 128GB gives room for other projects
   
4. **Case with Active Cooling** - $15
   - Argon ONE V3 (best) - $25
   - Or Geekworm with dual fans - $15
   - Cooling is IMPORTANT for 24/7 operation

5. **Ethernet Cable (Cat6)** - $5
   - More reliable than WiFi for trading

**Total: ~$127** (can save $10 with cheaper case)

### Optional but Recommended
- **Heatsink Kit** - $8 (if case has no fan)
- **32GB USB Drive** - $10 (for backups)
- **Mini HDMI Cable** - $8 (for initial setup)

---

## 🚀 What You Can Run on the Pi

### 🤖 Your Trading System (Primary)
```
3 Polymarket models + Dashboard
Resources: ~2GB RAM, 10GB storage
Uptime: 24/7
```

### 🏠 Home Server Stuff

#### 1. **Pi-hole** (Ad Blocker for Entire Network)
- Blocks ads on ALL devices
- Faster browsing
- Privacy protection
```bash
curl -sSL https://install.pi-hole.net | bash
```

#### 2. **Home Assistant** (Smart Home Hub)
- Control lights, thermostats, cameras
- Automation rules
- No cloud needed
```bash
docker run -d --name homeassistant homeassistant/home-assistant
```

#### 3. **Plex/Jellyfin** (Media Server)
- Stream movies/TV to any device
- Your own Netflix
- Pi 5 can handle 1080p transcoding
```bash
docker run -d --name plex plexinc/pms-docker
```

#### 4. **NextCloud** (Personal Cloud Storage)
- Your own Dropbox/Google Drive
- File sync across devices
- Calendar, contacts, notes
```bash
docker run -d --name nextcloud nextcloud
```

#### 5. **Wireguard VPN** (Secure Remote Access)
- Access home network from anywhere
- Secure browsing on public WiFi
- Connect to your Pi remotely
```bash
docker run -d --name wireguard linuxserver/wireguard
```

#### 6. **Monitoring Stack**
- Grafana + Prometheus
- Monitor your trading performance
- System health dashboards
```bash
docker-compose up -d  # Pre-built stack
```

#### 7. **Git Server** (Gitea)
- Private GitHub
- Code backup
- Lightweight
```bash
docker run -d --name gitea gitea/gitea
```

#### 8. **Network Storage (NAS)**
- Samba/NFS file sharing
- Time Machine backups
- Shared folder for all devices

---

## 🎯 Recommended Pi Setup

### For Your Use Case

**Priority 1: Trading System** (Always Running)
- 3 Polymarket models
- Dashboard
- Auto-restart on crash
- Resources: 2GB RAM

**Priority 2: Useful Stuff**
- **Pi-hole** (ad blocking) - 512MB RAM
- **Wireguard VPN** (remote access) - 256MB RAM  
- **Monitoring** (Grafana) - 512MB RAM

**Total Used: ~3.2GB / 8GB** = Plenty of room!

---

## 📦 Pi 5 8GB Specs

- **CPU**: 2.4GHz quad-core ARM Cortex-A76
- **RAM**: 8GB LPDDR4X
- **Storage**: MicroSD (we'll use 128GB)
- **Network**: Gigabit Ethernet + WiFi 6
- **USB**: 2x USB 3.0, 2x USB 2.0
- **Power**: 5V 5A (27W max)
- **Cooling**: Needs active cooling for 24/7

**Performance**: ~3x faster than Pi 4!

---

## 🔧 Initial Setup (When Pi Arrives)

### Day 1: Basic Setup (30 min)

1. **Flash OS**
```bash
# On your Mac
# Download Raspberry Pi Imager
brew install raspberry-pi-imager

# Flash Raspberry Pi OS (64-bit)
# Enable SSH before flashing!
```

2. **Boot Pi**
- Insert SD card
- Connect ethernet
- Connect power
- Wait 2 min for boot

3. **SSH In**
```bash
# Find Pi on network
ping raspberrypi.local

# Connect
ssh pi@raspberrypi.local
# Default password: raspberry
```

4. **Update Everything**
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

### Day 1: Docker Setup (15 min)

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker pi

# Install Docker Compose
sudo apt install docker-compose -y

# Test
docker --version
docker-compose --version
```

### Day 1: Deploy Trading System (5 min)

```bash
# Clone your repo
git clone <your-repo-url>
cd aztec-auction-analysis

# Start everything
docker-compose up -d

# Check
docker-compose ps
```

**Done!** Dashboard at: `http://raspberrypi.local:8000`

---

## 📊 Resource Planning

### RAM Usage
```
Trading Models:     2.0 GB
Dashboard:          0.3 GB
Pi-hole:            0.5 GB
Wireguard:          0.2 GB
System/Buffer:      1.0 GB
---
Total:             4.0 GB / 8 GB (50% usage)
```

**Remaining 4GB** for other projects!

### Storage Usage
```
OS:                 8 GB
Trading System:    10 GB
Docker Images:      5 GB
Logs (30 days):     2 GB
Other Apps:        20 GB
Free Space:        83 GB
---
Total:            45 GB / 128 GB
```

---

## 🌡️ Cooling Matters!

### Without Cooling
- Pi throttles at 80°C
- Performance drops
- Crashes possible
- Shorter lifespan

### With Good Cooling
- Stays ~50-60°C
- Full performance 24/7
- Reliable for years
- Silent operation

**Best cases**:
1. **Argon ONE V3** ($25) - Best cooling + power button
2. **Geekworm** ($15) - Great cooling, budget
3. **Flirc** ($20) - Passive (aluminum), silent

---

## 💡 Cool Pi Projects (After Trading Setup)

### 1. **Security Camera System**
- Motion detection
- 24/7 recording
- Remote viewing
- Face recognition

### 2. **Crypto Node**
- Run Bitcoin/Ethereum node
- Support decentralization
- Learn blockchain tech

### 3. **Retro Gaming Station**
- RetroPie
- Thousands of games
- 4K output

### 4. **Network Monitor**
- Track internet speed
- Uptime monitoring
- Alert on outages

### 5. **Personal Assistant**
- Voice control (Mycroft)
- Task automation
- Calendar integration

### 6. **Weather Station**
- Add sensors
- Log data
- Beautiful dashboards

### 7. **Pi Cluster** (if you get more Pis)
- Kubernetes cluster
- Learn cloud tech
- Overkill but cool

---

## 🎯 Why Pi 5 Over Pi 4?

| Feature | Pi 4 8GB | Pi 5 8GB |
|---------|----------|----------|
| **CPU Speed** | 1.8 GHz | 2.4 GHz |
| **Performance** | Good | 3x faster |
| **RAM Speed** | LPDDR4 | LPDDR4X (faster) |
| **USB** | USB 3.0 x2 | USB 3.0 x2 |
| **Network** | 1 Gbps | 1 Gbps |
| **PCIe** | No | Yes! (NVMe possible) |
| **Power** | 15W | 27W |
| **Price** | $75 | $80 |

**Verdict**: Pi 5 for $5 more is worth it!

---

## 📱 Remote Access Setup

Once your Pi is running, access from anywhere:

### Option 1: Wireguard VPN (Secure)
```bash
# Install on Pi
docker run -d --name wireguard linuxserver/wireguard

# Connect from phone/laptop
# Access dashboard: http://raspberrypi.local:8000
```

### Option 2: Tailscale (Easier)
```bash
# Install on Pi
curl -fsSL https://tailscale.com/install.sh | sh

# Access from anywhere
# No port forwarding needed!
```

### Option 3: Cloudflare Tunnel (Public)
```bash
# Make dashboard public
cloudflared tunnel --url localhost:8000

# Get public URL
# Share with friends!
```

---

## 🛒 Where to Buy

### Amazon
- Fast shipping
- Easy returns
- Slightly more expensive

### CanaKit
- Complete kits
- Quality parts
- Good support
- www.canakit.com

### Adafruit
- Official distributor
- Great quality
- Educational focus
- www.adafruit.com

### Direct (Raspberry Pi)
- Cheapest
- Longer shipping
- www.raspberrypi.com

---

## 🎯 Your Week 1 Plan

### Today (No Pi Yet)
- ✅ Docker on your Mac (we're doing this now!)
- Run trading for the week
- Learn Docker basics

### When Pi Arrives
1. **Day 1**: Setup + Deploy trading (1 hour)
2. **Day 2**: Add Pi-hole (30 min)
3. **Day 3**: Add monitoring (30 min)
4. **Day 4**: Add VPN for remote access (30 min)
5. **Day 5-7**: Explore other projects!

### Week 2+
- Trading runs 24/7 automatically
- Add more cool stuff
- Low power usage (~5W)
- Silent operation
- Never think about it

---

## 💰 Cost Breakdown

### Initial
- Pi 5 kit: $127
- Electricity (30 days): ~$2
- **Total first month**: $129

### Monthly After
- Electricity: ~$2/month
- No subscription fees
- Runs forever

### vs Cloud Server
- DigitalOcean: $6/month = $72/year
- Pi: $127 one-time + $24/year = $151 year 1, $24/year after

**Pi pays for itself in year 2!**

---

## 🎉 Bottom Line

**Pi 5 8GB** is perfect for:
- ✅ Your trading bots (always on)
- ✅ 5-10 other projects simultaneously
- ✅ Learning server/Docker/Linux
- ✅ Home automation
- ✅ Ad blocking for whole network

**For $127 you get**:
- Powerful little computer
- Runs 24/7 for $2/month
- Can do 10+ things at once
- Learn tons of skills
- Fun projects forever

**Order next week, running by next weekend!** 🚀

---

## 📦 Exact Shopping Cart (Copy/Paste)

**Amazon:**
1. CanaKit Raspberry Pi 5 Starter Kit (8GB) - $127
   - Includes: Pi, power supply, case, SD card, cables
   - One order, everything you need!

OR build your own:

1. Raspberry Pi 5 (8GB) - $80
2. Official 27W Power Supply - $12  
3. Samsung EVO Plus 128GB MicroSD - $15
4. Geekworm Armor Case with Fans - $15
5. Cat6 Ethernet Cable 6ft - $5

**Total: $127** (same either way!)

---

**Want me to find the exact Amazon links?** 📦


