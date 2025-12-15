#!/bin/bash

# HRMS Deployment Script
# Pulls latest code, rebuilds, and deploys fresh containers

set -e  # Exit on any error

echo "========================================"
echo "  HRMS Deployment Script"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
echo ""

# Configuration
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$REPO_DIR/deployment.log"
BACKUP_DIR="$REPO_DIR/backups"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to handle errors
error_exit() {
    log "ERROR: $1"
    echo ""
    echo "❌ Deployment failed. Check $LOG_FILE for details."
    exit 1
}

log "Starting deployment process..."

# Step 1: Check if Git is initialized
echo "[1/7] Checking Git repository..."
if [ ! -d ".git" ]; then
    log "WARNING: Not a Git repository. Skipping git pull."
    echo "⚠️  This is not a Git repository. Code will not be updated."
    echo "   To enable auto-updates, initialize Git and set remote:"
    echo "   git init"
    echo "   git remote add origin <your-repo-url>"
else
    log "Git repository detected"
    
    # Check for uncommitted changes
    if [[ -n $(git status -s) ]]; then
        log "WARNING: Uncommitted changes detected"
        echo "⚠️  You have uncommitted changes:"
        git status -s
        echo ""
        read -p "Do you want to stash changes and continue? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git stash || error_exit "Failed to stash changes"
            log "Changes stashed"
        else
            error_exit "Deployment cancelled by user"
        fi
    fi
    
    # Pull latest code
    log "Pulling latest code from repository..."
    git pull || error_exit "Failed to pull latest code"
    log "✓ Latest code pulled successfully"
fi
echo ""

# Step 2: Backup database (optional but recommended)
echo "[2/7] Creating database backup..."
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/hrmsdb_backup_$(date +%Y%m%d_%H%M%S).sql"

if docker-compose ps | grep -q "hrms-database.*Up"; then
    log "Creating database backup..."
    docker-compose exec -T db pg_dump -U postgres hrmsdb > "$BACKUP_FILE" 2>/dev/null || {
        log "WARNING: Database backup failed or database is empty"
        rm -f "$BACKUP_FILE"
    }
    
    if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
        log "✓ Database backup created: $BACKUP_FILE"
        
        # Keep only last 5 backups
        ls -t "$BACKUP_DIR"/hrmsdb_backup_*.sql | tail -n +6 | xargs -r rm
        log "Old backups cleaned (keeping last 5)"
    else
        log "No backup created (database might be empty)"
    fi
else
    log "Database container not running, skipping backup"
fi
echo ""

# Step 3: Stop and remove old containers
echo "[3/7] Stopping existing containers..."
log "Stopping all containers..."
docker-compose down || log "WARNING: Some containers may not have stopped cleanly"
log "✓ All containers stopped"
echo ""

# Step 4: Remove old images (optional - saves disk space)
echo "[4/7] Cleaning up old images..."
log "Removing old images..."
docker-compose down --rmi local 2>/dev/null || log "No local images to remove"

# Clean up dangling images
DANGLING=$(docker images -f "dangling=true" -q)
if [ -n "$DANGLING" ]; then
    docker rmi $DANGLING 2>/dev/null || log "WARNING: Some dangling images could not be removed"
    log "✓ Dangling images cleaned"
else
    log "No dangling images to clean"
fi
echo ""

# Step 5: Build fresh images
echo "[5/7] Building fresh Docker images..."
log "Building new images (this may take a few minutes)..."
docker-compose build --no-cache || error_exit "Failed to build Docker images"
log "✓ Docker images built successfully"
echo ""

# Step 6: Start new containers
echo "[6/7] Starting new containers..."
log "Starting all services..."
docker-compose up -d || error_exit "Failed to start containers"
log "✓ All containers started"
echo ""

# Step 7: Verify deployment
echo "[7/7] Verifying deployment..."
log "Waiting for services to be ready..."
sleep 5

# Check if all containers are running
RUNNING=$(docker-compose ps --services --filter "status=running" | wc -l)
TOTAL=$(docker-compose ps --services | wc -l)

if [ "$RUNNING" -eq "$TOTAL" ]; then
    log "✓ All $TOTAL services are running"
else
    log "WARNING: Only $RUNNING out of $TOTAL services are running"
    echo "⚠️  Some services may not be running properly"
    docker-compose ps
fi

# Test health endpoint
echo ""
echo "Testing application health..."
sleep 10  # Give services time to initialize

if curl -f -s http://localhost/health > /dev/null 2>&1; then
    log "✓ Application health check passed"
    echo "✅ Application is healthy"
else
    log "WARNING: Health check failed"
    echo "⚠️  Health check failed - application may still be starting"
fi

echo ""
echo "========================================"
echo "  Deployment Summary"
echo "========================================"
docker-compose ps
echo ""

log "Deployment completed successfully"
echo "✅ Deployment completed!"
echo ""
echo "Access your application:"
echo "  Frontend: http://localhost (or your EC2 IP/domain)"
echo "  API Docs: http://localhost/docs"
echo "  Health:   http://localhost/health"
echo ""
echo "View logs:"
echo "  docker-compose logs -f"
echo ""
echo "Deployment log saved to: $LOG_FILE"

# Optional: Send notification (uncomment and configure if needed)
# curl -X POST -H 'Content-type: application/json' \
#   --data '{"text":"HRMS deployment completed successfully"}' \
#   YOUR_SLACK_WEBHOOK_URL
