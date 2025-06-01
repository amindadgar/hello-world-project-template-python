#!/bin/bash

# AI Agent System Startup Script
# This script helps you get the full system running quickly

set -e  # Exit on any error

echo "🚀 Starting AI Agent System..."
echo "================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp env.template .env
    echo "⚠️  Please edit .env and set your OPENAI_API_KEY before continuing!"
    echo "   You can edit it with: nano .env"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

echo "🔧 Building and starting services..."

# Stop any existing containers
docker-compose down

# Build and start all services
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service status..."

# Wait for Temporal to be ready
echo "   Checking Temporal server..."
timeout=60
while [ $timeout -gt 0 ]; do
    if curl -s http://localhost:8080 >/dev/null 2>&1; then
        echo "   ✅ Temporal Web UI is ready"
        break
    fi
    timeout=$((timeout-1))
    sleep 1
done

if [ $timeout -eq 0 ]; then
    echo "   ⚠️  Temporal Web UI not responding, but continuing..."
fi

# Wait for MongoDB to be ready
echo "   Checking MongoDB..."
timeout=30
while [ $timeout -gt 0 ]; do
    if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
        echo "   ✅ MongoDB is ready"
        break
    fi
    timeout=$((timeout-1))
    sleep 1
done

if [ $timeout -eq 0 ]; then
    echo "   ⚠️  MongoDB not responding, but continuing..."
fi

# Wait for Streamlit dashboard
echo "   Checking Streamlit dashboard..."
timeout=30
while [ $timeout -gt 0 ]; do
    if curl -s http://localhost:8501 >/dev/null 2>&1; then
        echo "   ✅ Streamlit dashboard is ready"
        break
    fi
    timeout=$((timeout-1))
    sleep 1
done

if [ $timeout -eq 0 ]; then
    echo "   ⚠️  Streamlit dashboard not responding, but continuing..."
fi

echo ""
echo "🎉 System is starting up!"
echo "================================"
echo "📊 Services:"
echo "   • Temporal Web UI:     http://localhost:8080"
echo "   • Streamlit Dashboard: http://localhost:8501 (password: admin123)"
echo "   • MongoDB Express:     http://localhost:8081 (admin/password)"
echo "   • MongoDB:             localhost:27017"
echo ""
echo "🔧 Management Commands:"
echo "   • View logs:           docker-compose logs -f"
echo "   • Stop system:         docker-compose down"
echo "   • Restart system:      docker-compose restart"
echo ""
echo "🧪 Testing:"
echo "   • Run system tests:    python scripts/test_system.py"
echo "   • Test workflow:       python run_workflow.py"
echo ""
echo "📖 For more information, see README.md"
echo ""

# Final check
if [ "$1" = "--check" ]; then
    echo "🔍 Running system health check..."
    if [ -f scripts/test_system.py ]; then
        python scripts/test_system.py
    else
        echo "⚠️  Test script not found. Please run 'python scripts/test_system.py' manually."
    fi
fi 