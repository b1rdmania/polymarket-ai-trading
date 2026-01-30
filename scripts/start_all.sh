#!/bin/bash
# Start all services in one container for Render deployment
# Includes process monitoring to restart crashed trading models

set -e

echo "=================================================="
echo "  Polymarket AI Trading System - Starting All"
echo "=================================================="

# Create necessary directories
mkdir -p /app/data /app/logs

# Function to start a trading model
start_model() {
    local model=$1
    local config=$2
    
    echo "Starting $model model..."
    python3 /app/agents/systematic_trader.py \
        --mode paper \
        --config "/app/config/$config" \
        --model "$model" \
        >> "/app/logs/$model.log" 2>&1 &
    
    echo $! > "/app/data/${model}.pid"
    echo "  $model started with PID $(cat /app/data/${model}.pid)"
}

# Function to check if a model is running
check_model() {
    local model=$1
    local pid_file="/app/data/${model}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            return 0  # Running
        fi
    fi
    return 1  # Not running
}

# Function to restart a model if crashed
ensure_running() {
    local model=$1
    local config=$2
    
    if ! check_model "$model"; then
        echo "[$(date)] $model is not running, restarting..."
        start_model "$model" "$config"
    fi
}

# Start all trading models
start_model "conservative" "active_conservative.yaml"
start_model "moderate" "active_moderate.yaml"
start_model "aggressive" "active_aggressive.yaml"

sleep 3
echo ""
echo "All trading models started!"
echo ""

# Write a marker file to indicate models are running
echo "$(date)" > /app/data/model_pids.txt
echo "conservative=$(cat /app/data/conservative.pid 2>/dev/null || echo 'N/A')" >> /app/data/model_pids.txt
echo "moderate=$(cat /app/data/moderate.pid 2>/dev/null || echo 'N/A')" >> /app/data/model_pids.txt
echo "aggressive=$(cat /app/data/aggressive.pid 2>/dev/null || echo 'N/A')" >> /app/data/model_pids.txt

echo "Starting Dashboard API with process monitor..."
echo "=================================================="

# Start dashboard API in background
python3 /app/api/dashboard_api.py &
API_PID=$!
echo "Dashboard API started with PID $API_PID"

# Monitor loop - check every 60 seconds and restart crashed models
while true; do
    sleep 60
    
    # Check if API is still running
    if ! kill -0 "$API_PID" 2>/dev/null; then
        echo "[$(date)] Dashboard API crashed, restarting..."
        python3 /app/api/dashboard_api.py &
        API_PID=$!
    fi
    
    # Restart any crashed trading models
    ensure_running "conservative" "active_conservative.yaml"
    ensure_running "moderate" "active_moderate.yaml"
    ensure_running "aggressive" "active_aggressive.yaml"
    
    # Update PID file
    echo "$(date)" > /app/data/model_pids.txt
    echo "conservative=$(cat /app/data/conservative.pid 2>/dev/null || echo 'N/A')" >> /app/data/model_pids.txt
    echo "moderate=$(cat /app/data/moderate.pid 2>/dev/null || echo 'N/A')" >> /app/data/model_pids.txt
    echo "aggressive=$(cat /app/data/aggressive.pid 2>/dev/null || echo 'N/A')" >> /app/data/model_pids.txt
done
