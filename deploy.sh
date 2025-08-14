#!/bin/bash

echo "🚀 Profile Automation System - Docker Deployment"
echo "================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it first."
    exit 1
fi

echo "✅ Docker and docker-compose are ready!"

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from example..."
    if [ -f environment.example ]; then
        cp environment.example .env
        echo "📝 Please edit .env file with your actual configuration values"
        echo "   Then run this script again."
        exit 1
    else
        echo "❌ environment.example not found. Please create .env file manually."
        exit 1
    fi
fi

echo "🔧 Building and starting containers..."

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start containers
echo "🔨 Building new image..."
docker-compose build --no-cache

echo "🚀 Starting containers..."
docker-compose up -d

# Wait for containers to be ready
echo "⏳ Waiting for application to start..."
sleep 10

# Check container status
echo "📊 Container status:"
docker-compose ps

# Check if application is responding
echo "🔍 Checking application health..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Application is healthy and running!"
    echo "🌐 Your Profile Automation System is available at:"
    echo "   http://localhost"
    echo "   http://localhost/docs (API documentation)"
else
    echo "⚠️  Application might still be starting up..."
    echo "📋 Check logs with: docker-compose logs -f"
fi

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop app: docker-compose down"
echo "   Restart app: docker-compose restart"
echo "   Update app: ./deploy.sh"
echo ""
echo "🔧 For future updates, just run: ./deploy.sh"
