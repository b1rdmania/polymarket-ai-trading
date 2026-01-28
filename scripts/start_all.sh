#!/bin/bash
# Start all services in one container for Render deployment
# This allows shared SQLite database access

set -e

echo "=================================================="
echo "  Polymarket AI Trading System - Starting All Services"
echo "=================================================="

# Create necessary directories
mkdir -p /app/data /app/logs

# Start each trading model in background
echo "Starting Conservative model..."
python3 /app/agents/systematic_trader.py \
  --mode paper \
  --config /app/config/active_conservative.yaml \
  --model conservative \
  > /app/logs/conservative.log 2>&1 &

echo "Starting Moderate model..."
python3 /app/agents/systematic_trader.py \
  --mode paper \
  --config /app/config/active_moderate.yaml \
  --model moderate \
  > /app/logs/moderate.log 2>&1 &

echo "Starting Aggressive model..."
python3 /app/agents/systematic_trader.py \
  --mode paper \
  --config /app/config/active_aggressive.yaml \
  --model aggressive \
  > /app/logs/aggressive.log 2>&1 &

# Wait a bit for models to initialize
sleep 5

echo "All trading models started!"
echo ""
echo "Starting Dashboard API (foreground)..."
echo "=================================================="

# Start dashboard API in foreground (keeps container alive)
exec python3 /app/api/dashboard_api.py
