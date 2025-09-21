# Deployment Script
#!/bin/bash

set -e

echo "🚀 Starting deployment of Agentic AI Tool..."

# Check if required files exist
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.template to .env and configure your API keys"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed!"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed!"
    exit 1
fi

# Load environment variables
source .env

# Validate required API keys
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$SERPER_API_KEY" ]; then
    echo "❌ Error: SERPER_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$WEATHER_API_KEY" ]; then
    echo "❌ Error: WEATHER_API_KEY not set in .env file"
    exit 1
fi

echo "✅ Environment validation passed"

# Create logs directory
mkdir -p logs

# Build and start the application
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting application..."
docker-compose up -d

# Wait for application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Check if application is running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Application started successfully!"
    echo "🌐 Access the application at: http://localhost:8501"
    echo "📊 Health check: http://localhost:8501/_stcore/health"
else
    echo "❌ Application failed to start!"
    echo "📋 Checking logs..."
    docker-compose logs
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop application: docker-compose down"
echo "  - Restart: docker-compose restart"
echo "  - Update: docker-compose pull && docker-compose up -d"