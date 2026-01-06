#!/bin/bash
# Docker Management Script

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

case "$1" in
    start)
        echo "🐳 Starting Docker containers..."
        docker-compose up -d --build
        echo ""
        echo "✅ All containers started!"
        echo "📊 Dashboard: http://localhost:8000"
        docker-compose ps
        ;;
    
    stop)
        echo "🛑 Stopping Docker containers..."
        docker-compose down
        echo "✅ All containers stopped"
        ;;
    
    restart)
        echo "♻️  Restarting Docker containers..."
        docker-compose restart
        echo "✅ All containers restarted"
        docker-compose ps
        ;;
    
    logs)
        if [ -z "$2" ]; then
            echo "📋 Showing logs for all containers..."
            docker-compose logs -f
        else
            echo "📋 Showing logs for $2..."
            docker-compose logs -f "$2"
        fi
        ;;
    
    status)
        echo "📊 Container Status:"
        docker-compose ps
        echo ""
        echo "💻 Resource Usage:"
        docker stats --no-stream
        ;;
    
    clean)
        echo "🧹 Cleaning up..."
        docker-compose down -v
        docker system prune -f
        echo "✅ Cleanup complete"
        ;;
    
    rebuild)
        echo "🔨 Rebuilding containers..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        echo "✅ Rebuild complete"
        docker-compose ps
        ;;
    
    *)
        echo "🐳 Docker Management Script"
        echo ""
        echo "Usage: $0 {start|stop|restart|logs|status|clean|rebuild}"
        echo ""
        echo "Commands:"
        echo "  start    - Build and start all containers"
        echo "  stop     - Stop all containers"
        echo "  restart  - Restart all containers"
        echo "  logs     - View logs (add container name for specific)"
        echo "  status   - Show container status and resources"
        echo "  clean    - Stop and remove all containers/volumes"
        echo "  rebuild  - Rebuild containers from scratch"
        echo ""
        echo "Examples:"
        echo "  $0 start"
        echo "  $0 logs conservative"
        echo "  $0 status"
        ;;
esac


