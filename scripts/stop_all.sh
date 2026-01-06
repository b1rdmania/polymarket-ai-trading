#!/bin/bash
# Stop All Services Script

echo "============================================================"
echo "🛑 STOPPING ALL SERVICES"
echo "============================================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Stop trading models
echo "Stopping trading models..."
python3 scripts/stop_models.py

# Stop dashboard
if [ -f data/dashboard_pid.txt ]; then
    DASHBOARD_PID=$(cat data/dashboard_pid.txt)
    echo ""
    echo "Stopping dashboard (PID: $DASHBOARD_PID)..."
    
    if ps -p $DASHBOARD_PID > /dev/null; then
        kill $DASHBOARD_PID
        echo "✅ Dashboard stopped"
    else
        echo "⚠️  Dashboard not running"
    fi
    
    rm data/dashboard_pid.txt
else
    echo ""
    echo "⚠️  No dashboard PID file found"
    
    # Try to find and kill by port
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
        echo "Found dashboard on port 8000, stopping..."
        kill $(lsof -t -i:8000) 2>/dev/null
        echo "✅ Dashboard stopped"
    fi
fi

echo ""
echo "============================================================"
echo "✅ ALL SERVICES STOPPED"
echo "============================================================"
echo ""


