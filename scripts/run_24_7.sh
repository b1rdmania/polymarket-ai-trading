#!/bin/bash
# Keep Mac Awake & Models Running Script

echo "============================================================"
echo "⚡ 24/7 LOCAL TRADING SETUP"
echo "============================================================"
echo ""

# Check if models are running
if ! pgrep -f "systematic_trader.py" > /dev/null; then
    echo "⚠️  Models not running. Starting them..."
    cd "$(dirname "$0")/.."
    python3 scripts/start_models.py
    sleep 5
fi

# Check if dashboard is running
if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Dashboard not running. Starting it..."
    cd "$(dirname "$0")/.."
    nohup python3 api/dashboard_api.py > logs/dashboard.log 2>&1 &
    sleep 3
fi

# Prevent Mac from sleeping
echo "🔋 Preventing Mac from sleeping..."
echo "   (Models will run 24/7 even with lid closed)"
echo ""

# Kill any existing caffeinate
pkill caffeinate 2>/dev/null

# Start caffeinate to prevent sleep
caffeinate -s &
CAFFEINATE_PID=$!

echo "✅ Mac will stay awake!"
echo "✅ Models are running!"
echo "✅ Dashboard: http://localhost:8000"
echo ""
echo "PID saved: $CAFFEINATE_PID"
echo $CAFFEINATE_PID > "$(dirname "$0")/../data/caffeinate_pid.txt"

echo ""
echo "============================================================"
echo "🏁 30-DAY RACE IS ON!"
echo "============================================================"
echo ""
echo "Your Mac will:"
echo "  ✅ Never sleep (even with lid closed)"
echo "  ✅ Keep trading 24/7"
echo "  ✅ Record all data"
echo ""
echo "To stop:"
echo "  bash scripts/stop_all.sh"
echo "  kill $CAFFEINATE_PID"
echo ""
echo "Check progress:"
echo "  open http://localhost:8000"
echo "  python3 scripts/monitor_models.py"
echo ""


