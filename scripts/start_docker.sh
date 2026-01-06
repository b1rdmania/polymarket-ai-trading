#!/bin/bash
# Run AFTER Docker Desktop is installed and running

echo "============================================================"
echo "🐳 DOCKER DEPLOYMENT"
echo "============================================================"
echo ""

# Check if Docker is running
if ! docker ps &> /dev/null; then
    echo "❌ Docker is not running!"
    echo ""
    echo "Please:"
    echo "  1. Open Docker Desktop app"
    echo "  2. Wait for whale icon in menu bar to be steady"
    echo "  3. Run this script again"
    echo ""
    exit 1
fi

echo "✅ Docker is running!"
echo ""

# Navigate to project
cd "$(dirname "$0")/.."

# Stop any local processes
echo "Stopping any local processes..."
bash scripts/stop_all.sh 2>/dev/null
pkill caffeinate 2>/dev/null

echo ""
echo "============================================================"
echo "🔨 BUILDING CONTAINERS"
echo "============================================================"
echo ""

# Build and start containers
echo "This may take 3-5 minutes on first run..."
echo ""

docker-compose up -d --build

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ SUCCESS! ALL CONTAINERS RUNNING"
    echo "============================================================"
    echo ""
    
    # Wait a moment for containers to fully start
    sleep 5
    
    # Show status
    docker-compose ps
    
    echo ""
    echo "============================================================"
    echo "📊 YOUR SYSTEM"
    echo "============================================================"
    echo ""
    echo "Dashboard:  http://localhost:8000"
    echo "API Docs:   http://localhost:8000/docs"
    echo ""
    echo "Containers:"
    echo "  🐳 polymarket-conservative  (Model 1)"
    echo "  🐳 polymarket-moderate      (Model 2)"
    echo "  🐳 polymarket-aggressive    (Model 3)"
    echo "  🐳 polymarket-dashboard     (Web UI)"
    echo ""
    echo "Commands:"
    echo "  View logs:    docker-compose logs -f moderate"
    echo "  Stop all:     docker-compose down"
    echo "  Restart:      docker-compose restart"
    echo "  Status:       docker-compose ps"
    echo ""
    echo "============================================================"
    echo "🎉 CLOSE YOUR LAPTOP - THEY'LL KEEP RUNNING!"
    echo "============================================================"
    echo ""
    echo "Docker containers will:"
    echo "  ✅ Keep running even when you close your laptop"
    echo "  ✅ Auto-restart if they crash"
    echo "  ✅ Persist all data"
    echo "  ✅ Resume on Mac restart"
    echo ""
    echo "Opening dashboard..."
    sleep 2
    open http://localhost:8000
    
else
    echo ""
    echo "❌ Something went wrong!"
    echo ""
    echo "Check Docker Desktop is running and try again."
    echo "Or run: docker-compose logs"
fi


