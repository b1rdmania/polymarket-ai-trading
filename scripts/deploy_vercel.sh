#!/bin/bash
# Deploy Dashboard to Vercel + Setup Cloudflare Tunnel

echo "============================================================"
echo "🌐 VERCEL + TUNNEL DEPLOYMENT"
echo "============================================================"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Step 1: Install Cloudflare Tunnel
echo "Step 1: Installing Cloudflare Tunnel..."
echo ""

if ! command -v cloudflared &> /dev/null; then
    echo "Installing cloudflared..."
    brew install cloudflare/cloudflare/cloudflared
    
    if [ $? -eq 0 ]; then
        echo "✅ Cloudflared installed"
    else
        echo "❌ Failed to install cloudflared"
        echo "   Try: brew install cloudflare/cloudflare/cloudflared"
        exit 1
    fi
else
    echo "✅ Cloudflared already installed"
fi

echo ""

# Step 2: Start Cloudflare Tunnel
echo "Step 2: Starting Cloudflare Tunnel..."
echo ""

echo "This will expose your API to the internet..."
cloudflared tunnel --url http://localhost:8000 > tunnel.log 2>&1 &
TUNNEL_PID=$!
echo $TUNNEL_PID > data/tunnel_pid.txt

echo "✅ Tunnel started (PID: $TUNNEL_PID)"
echo "   Waiting for tunnel URL..."
sleep 5

# Extract tunnel URL from log
TUNNEL_URL=$(grep -o 'https://.*\.trycloudflare.com' tunnel.log | head -1)

if [ -z "$TUNNEL_URL" ]; then
    echo "❌ Could not get tunnel URL"
    echo "   Check tunnel.log for details"
    cat tunnel.log
    exit 1
fi

echo ""
echo "✅ Tunnel URL: $TUNNEL_URL"
echo ""

# Step 3: Deploy to Vercel
echo "Step 3: Deploying to Vercel..."
echo ""

cd vercel-frontend

# Check if vercel is installed
if ! command -v vercel &> /dev/null; then
    echo "Installing Vercel CLI..."
    npm install -g vercel
fi

# Create a config file with the API URL
cat > public/_env.js << EOF
window.DASHBOARD_API_URL = '$TUNNEL_URL';
EOF

echo "Deploying to Vercel..."
vercel --prod

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ DEPLOYMENT COMPLETE!"
    echo "============================================================"
    echo ""
    echo "Your Dashboard:"
    echo "  Frontend: (Vercel will show URL above)"
    echo "  API Tunnel: $TUNNEL_URL"
    echo ""
    echo "The frontend on Vercel will connect to your local API"
    echo "through the Cloudflare tunnel!"
    echo ""
    echo "To stop tunnel:"
    echo "  kill $TUNNEL_PID"
    echo ""
    echo "Tunnel log: tunnel.log"
    echo ""
else
    echo "❌ Vercel deployment failed"
    echo "   You may need to run 'vercel login' first"
fi

cd "$PROJECT_ROOT"


