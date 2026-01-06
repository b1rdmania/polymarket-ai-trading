#!/bin/bash
# Docker Installation Check and Setup for macOS

echo "============================================================"
echo "🐳 DOCKER SETUP"
echo "============================================================"
echo ""

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
    docker --version
    
    # Check if Docker daemon is running
    if docker ps &> /dev/null; then
        echo "✅ Docker daemon is running"
    else
        echo "⚠️  Docker is installed but not running"
        echo ""
        echo "Please start Docker Desktop:"
        echo "  1. Open Docker Desktop app"
        echo "  2. Wait for it to start (whale icon in menu bar)"
        echo "  3. Run this script again"
        exit 1
    fi
else
    echo "❌ Docker is not installed"
    echo ""
    echo "📥 Installing Docker..."
    echo ""
    echo "On macOS, we need Docker Desktop:"
    echo ""
    echo "Option 1: Homebrew (Recommended)"
    echo "  brew install --cask docker"
    echo ""
    echo "Option 2: Manual Download"
    echo "  Visit: https://www.docker.com/products/docker-desktop"
    echo ""
    
    # Try homebrew install
    if command -v brew &> /dev/null; then
        echo "🍺 Homebrew detected!"
        read -p "Install Docker Desktop via Homebrew? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            brew install --cask docker
            echo ""
            echo "✅ Docker Desktop installed!"
            echo ""
            echo "⚠️  NEXT STEPS:"
            echo "  1. Open Docker Desktop from Applications"
            echo "  2. Complete the setup wizard"
            echo "  3. Wait for Docker to start (whale icon in menu bar)"
            echo "  4. Run: bash scripts/docker.sh start"
            exit 0
        fi
    fi
    
    echo ""
    echo "Please install Docker Desktop manually:"
    echo "  https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check docker-compose
if command -v docker-compose &> /dev/null; then
    echo "✅ docker-compose is installed"
    docker-compose --version
elif docker compose version &> /dev/null; then
    echo "✅ docker compose (v2) is installed"
    docker compose version
    
    # Create alias for docker-compose
    echo ""
    echo "💡 Creating docker-compose alias..."
    echo 'alias docker-compose="docker compose"' >> ~/.zshrc
    echo "✅ Alias created (restart terminal or source ~/.zshrc)"
else
    echo "❌ docker-compose not found"
    echo "Installing via pip..."
    pip3 install --user docker-compose
fi

echo ""
echo "============================================================"
echo "✅ DOCKER IS READY!"
echo "============================================================"
echo ""
echo "Next step: Start containers"
echo "  bash scripts/docker.sh start"
echo ""


