# 🌐 Vercel + Tunnel Deployment Guide

## What This Does

**Frontend**: Deployed to Vercel (global CDN, fast everywhere)  
**Backend**: Runs locally (Docker on Mac/Pi), exposed via Cloudflare Tunnel

**Result**: Access dashboard from anywhere in the world! 🌍

---

## 🚀 One-Command Deploy

```bash
bash scripts/deploy_vercel.sh
```

This will:
1. ✅ Install Cloudflare Tunnel
2. ✅ Expose your local API  
3. ✅ Deploy frontend to Vercel
4. ✅ Connect them together

---

## 📋 Manual Steps (If Needed)

### Step 1: Install Tools

```bash
# Cloudflare Tunnel
brew install cloudflare/cloudflare/cloudflared

# Vercel CLI
npm install -g vercel
```

### Step 2: Start Tunnel

```bash
# Expose local API
cloudflared tunnel --url http://localhost:8000
```

You'll get a URL like: `https://random-name.trycloudflare.com`

### Step 3: Deploy to Vercel

```bash
cd vercel-frontend

# Login (first time only)
vercel login

# Deploy
vercel --prod
```

You'll get a URL like: `https://your-dashboard.vercel.app`

### Step 4: Connect Them

The frontend automatically connects to the tunnel URL!

---

## 🎯 What You Get

### Frontend (Vercel)
- ✅ Fast global CDN
- ✅ HTTPS automatically
- ✅ Custom domain possible
- ✅ Free hosting
- ✅ Instant deploys

### Backend (Local + Tunnel)
- ✅ Runs on your Mac/Pi
- ✅ Access to local databases
- ✅ Secure tunnel
- ✅ No data leaves your machine
- ✅ Free tunnel

---

## 🔒 Security

**Good**:
- Data stays on your machine
- Tunnel is encrypted
- Only API is exposed (not your whole network)

**Be Aware**:
- Tunnel URL is public (anyone with URL can access)
- For production: Add authentication

---

## 💰 Cost

**Everything is FREE**:
- Vercel: Free tier (perfect for this)
- Cloudflare Tunnel: Free
- Total: $0/month

---

## 🎮 Managing It

### View Tunnel URL
```bash
# Tunnel creates a random URL each time
# Check tunnel.log for the current URL
cat tunnel.log | grep trycloudflare
```

### Stop Tunnel
```bash
# Get PID
cat data/tunnel_pid.txt

# Stop it
kill $(cat data/tunnel_pid.txt)
```

### Update Frontend
```bash
cd vercel-frontend
vercel --prod
```

### View Logs
```bash
# Tunnel logs
tail -f tunnel.log

# Docker logs (backend)
docker compose logs -f
```

---

## 🌟 Advanced: Permanent Tunnel URL

**Free random URL** (changes on restart):
```bash
cloudflared tunnel --url http://localhost:8000
```

**Permanent URL** (need Cloudflare account):
```bash
# Create tunnel
cloudflared tunnel create trading-dashboard

# Get permanent URL
cloudflared tunnel route dns trading-dashboard dashboard.yourdomain.com

# Run it
cloudflared tunnel run trading-dashboard
```

---

## 🎯 Access From Anywhere

Once deployed:

**From phone** 📱:
- Visit your Vercel URL
- See live dashboard
- Check performance

**From work** 💼:
- Monitor trades
- View P&L
- Real-time updates

**Show friends** 👥:
- Share Vercel URL
- They see your live dashboard
- Impress everyone

---

## 🔥 Pro Tips

### 1. Keep Tunnel Running
```bash
# Run in background
nohup cloudflared tunnel --url http://localhost:8000 > tunnel.log 2>&1 &
```

### 2. Auto-Restart Tunnel
```bash
# Create a systemd service (Linux/Pi)
# Or launchd (Mac)
# Restarts tunnel if it dies
```

### 3. Custom Domain
```bash
# On Vercel dashboard:
# Settings > Domains > Add
# Point your domain to Vercel
```

### 4. Add Auth (For Live Money)
```bash
# Add to vercel-frontend/index.html
# Simple password protection
# Or use Vercel's built-in auth
```

---

## 🎨 How It Works

```
Your Phone 📱
    ↓
Vercel CDN 🌐 (HTML/JS/CSS)
    ↓
Cloudflare Tunnel 🚇
    ↓
Your Mac/Pi 💻 (Docker containers)
    ↓
SQLite Databases 💾 (trade data)
```

**Fast**: Static files from Vercel CDN  
**Secure**: Data never leaves your machine  
**Simple**: No port forwarding needed

---

## 🚀 Deploy Now!

```bash
bash scripts/deploy_vercel.sh
```

**3 minutes later**: Dashboard accessible from anywhere! 🌍

---

## 📞 Troubleshooting

### Tunnel won't start
```bash
# Check if port 8000 is accessible
curl http://localhost:8000/api/health

# Try manual tunnel
cloudflared tunnel --url http://localhost:8000
```

### Vercel deploy fails
```bash
# Login first
vercel login

# Try again
cd vercel-frontend
vercel --prod
```

### Frontend can't connect to API
```bash
# Check tunnel URL is correct
cat vercel-frontend/public/_env.js

# Should show: window.DASHBOARD_API_URL = 'https://...'
```

---

**Ready to go live?** 🚀


