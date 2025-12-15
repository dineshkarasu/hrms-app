#!/bin/bash

# HRMS Docker Stop Script
# Run this script to stop the HRMS application

echo "========================================"
echo "  Stopping HRMS Application"
echo "========================================"
echo ""

echo "Stopping all services..."
docker-compose down

if [ $? -eq 0 ]; then
    echo "✓ All services stopped successfully"
else
    echo "✗ Failed to stop services"
    exit 1
fi

echo ""
echo "To start again, run: ./start.sh"
