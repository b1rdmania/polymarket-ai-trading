#!/bin/bash
# Complete Startup Script
# Starts all 3 models + dashboard in one command

echo "============================================================"
echo "🚀 POLYMARKET TRADING SYSTEM - COMPLETE STARTUP"
echo "============================================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "📁 Working directory: $PROJECT_ROOT"
echo ""

# Step 1: Start the 3 trading models
echo "============================================================"
echo "Step 1: Starting 3 Trading Models"
echo "============================================================"
echo ""

python3 scripts/start_models.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to start models"
    exit 1
fi

echo ""
echo "✅ All 3 models started successfully!"
echo ""

# Step 2: Start the dashboard API
echo "============================================================"
echo "Step 2: Starting Dashboard API"
echo "============================================================"
echo ""

# Check if dashboard is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Dashboard already running on port 8000"
    echo "   Stopping existing process..."
    kill $(lsof -t -i:8000) 2>/dev/null
    sleep 2
fi

# Start dashboard in background
echo "Starting dashboard on http://localhost:8000"
nohup python3 api/dashboard_api.py > logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!

# Wait a moment for it to start
sleep 3

# Check if it's running
if ps -p $DASHBOARD_PID > /dev/null; then
    echo "✅ Dashboard started successfully (PID: $DASHBOARD_PID)"
    echo $DASHBOARD_PID > data/dashboard_pid.txt
else
    echo "❌ Dashboard failed to start"
    echo "   Check logs/dashboard.log for errors"
    exit 1
fi

echo ""
echo "============================================================"
echo "✅ SYSTEM FULLY OPERATIONAL"
echo "============================================================"
echo ""
echo "📊 Dashboard:  http://localhost:8000"
echo "🔌 API Docs:   http://localhost:8000/docs"
echo ""
echo "Models Running:"
echo "  💎 Conservative"
echo "  ⚖️  Moderate"
echo "  🚀 Aggressive"
echo ""
echo "Logs:"
echo "  Models:    logs/conservative/  logs/moderate/  logs/aggressive/"
echo "  Dashboard: logs/dashboard.log"
echo ""
echo "Commands:"
echo "  Monitor:   python3 scripts/monitor_models.py --loop"
echo "  Stop All:  bash scripts/stop_all.sh"
echo ""
echo "============================================================"
echo "🏁 The 30-day race has begun!"
echo "============================================================"
echo ""

# Optionally open browser (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🌐 Opening dashboard in browser..."
    open http://localhost:8000
fi


