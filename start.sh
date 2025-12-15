#!/bin/bash

# HRMS Docker Setup Script
# Run this script to set up and start the HRMS application

echo "========================================"
echo "  HRMS Application Docker Setup"
echo "========================================"
echo ""

# Check if Docker is running
echo "[1/6] Checking Docker..."
if ! docker version &> /dev/null; then
    echo "✗ Docker is not running. Please start Docker and try again."
    exit 1
fi
echo "✓ Docker is running"
echo ""

# Check if .env file exists
echo "[2/6] Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "⚠ .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file. You can edit it to customize settings."
else
    echo "✓ .env file exists"
fi
echo ""

# Check if ports are available
echo "[3/6] Checking port availability..."
ports_in_use=""

for port in 80 8000 5432; do
    if netstat -tuln 2>/dev/null | grep -q ":$port " || ss -tuln 2>/dev/null | grep -q ":$port "; then
        ports_in_use="$ports_in_use $port"
    fi
done

if [ -n "$ports_in_use" ]; then
    echo "⚠ Warning: The following ports are in use:$ports_in_use"
    echo "  The application may fail to start. Consider stopping services using these ports."
else
    echo "✓ All required ports (80, 8000, 5432) are available"
fi
echo ""

# Stop existing containers
echo "[4/6] Stopping existing containers..."
docker-compose down &> /dev/null
echo "✓ Stopped existing containers"
echo ""

# Build and start services
echo "[5/6] Building and starting services..."
echo "This may take a few minutes on first run..."
docker-compose up -d --build

if [ $? -eq 0 ]; then
    echo "✓ Services started successfully"
else
    echo "✗ Failed to start services"
    exit 1
fi
echo ""

# Wait for services to be healthy
echo "[6/6] Waiting for services to be ready..."
sleep 10

# Check service health
max_attempts=30
attempt=0
healthy=false

while [ $attempt -lt $max_attempts ] && [ "$healthy" = false ]; do
    if curl -f -s http://localhost/health > /dev/null 2>&1; then
        healthy=true
    else
        attempt=$((attempt + 1))
        sleep 2
        echo -n "."
    fi
done

echo ""

if [ "$healthy" = true ]; then
    echo "✓ All services are healthy and ready!"
else
    echo "⚠ Services started but health check timed out. Check logs with: docker-compose logs"
fi

echo ""
echo "========================================"
echo "  Application is ready!"
echo "========================================"
echo ""
echo "Access the application at:"
echo "  • Frontend:        http://localhost"
echo "  • API Docs:        http://localhost/docs"
echo "  • Health Check:    http://localhost/health"
echo ""
echo "Useful commands:"
echo "  • View logs:       docker-compose logs -f"
echo "  • Seed data:       docker-compose exec api python seed_data.py"
echo "  • Stop services:   docker-compose down"
echo "  • Restart:         docker-compose restart"
echo ""
echo "Setup complete! 🎉"
