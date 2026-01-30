#!/bin/bash
# Start trading system - single model + API
# Includes process monitoring to restart if crashed

set -e

echo "=================================================="
echo "  Polymarket AI Trading System"
echo "=================================================="

# Create necessary directories
mkdir -p /app/data /app/logs

# Start the trading model
echo "Starting trader..."
python3 /app/agents/systematic_trader.py \
    --mode paper \
    --config /app/config/trader.yaml \
    --model trader \
    >> /app/logs/trader.log 2>&1 &

TRADER_PID=$!
echo $TRADER_PID > /app/data/trader.pid
echo "Trader started with PID $TRADER_PID"

sleep 2

# Write marker file
echo "$(date)" > /app/data/model_pids.txt
echo "trader=$TRADER_PID" >> /app/data/model_pids.txt

echo ""
echo "Starting Dashboard API..."
echo "=================================================="

# Start dashboard API in background
python3 /app/api/dashboard_api.py &
API_PID=$!
echo "Dashboard API started with PID $API_PID"

# Monitor loop - check every 60 seconds
while true; do
    sleep 60
    
    # Check if API is still running
    if ! kill -0 "$API_PID" 2>/dev/null; then
        echo "[$(date)] Dashboard API crashed, restarting..."
        python3 /app/api/dashboard_api.py &
        API_PID=$!
    fi
    
    # Check if trader is still running
    if ! kill -0 "$TRADER_PID" 2>/dev/null; then
        echo "[$(date)] Trader crashed, restarting..."
        python3 /app/agents/systematic_trader.py \
            --mode paper \
            --config /app/config/trader.yaml \
            --model trader \
            >> /app/logs/trader.log 2>&1 &
        TRADER_PID=$!
        echo $TRADER_PID > /app/data/trader.pid
    fi
    
    # Update marker file
    echo "$(date)" > /app/data/model_pids.txt
    echo "trader=$TRADER_PID" >> /app/data/model_pids.txt
done
