#!/bin/bash
#
# DailyNews Update Script
# Pulls latest changes from repository and re-runs setup script
#
# Usage: sudo ./update-dailynews.sh [DEPLOY_PATH]
#   DEPLOY_PATH: Where the repository is deployed (default: /opt/DailyNews)
#

set -e

DEPLOY_PATH="${1:-/opt/DailyNews}"
SERVICE_USER="${SERVICE_USER:-dailynews}"

echo "=========================================="
echo "DailyNews Update Script"
echo "=========================================="
echo "Deploy path: $DEPLOY_PATH"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Check if repository exists
if [ ! -d "$DEPLOY_PATH/.git" ]; then
    echo "Error: Repository not found at $DEPLOY_PATH"
    echo "Please run setup-dailynews-production.sh first"
    exit 1
fi

echo "[1/3] Pulling latest changes from repository..."
cd "$DEPLOY_PATH"

# Pull latest changes as the service user
sudo -u $SERVICE_USER git fetch origin
sudo -u $SERVICE_USER git reset --hard origin/main

echo "✓ Repository updated to latest version"
echo ""

echo "[2/3] Running setup script to apply any configuration changes..."
if [ -f "$DEPLOY_PATH/setup-dailynews-production.sh" ]; then
    bash "$DEPLOY_PATH/setup-dailynews-production.sh" "$DEPLOY_PATH"
    echo "✓ Setup script completed"
else
    echo "⚠ Warning: setup-dailynews-production.sh not found in repository"
    echo "   Setup script may need to be run manually"
fi

echo ""
echo "[3/3] Verifying installation..."
echo ""

# Check crontab
if sudo -u $SERVICE_USER crontab -l 2>/dev/null | grep -q "fetch_cyber_news.py"; then
    echo "✓ Crontab entries found"
else
    echo "⚠ Warning: Crontab entries not found"
fi

# Check .env file
if [ -f "$DEPLOY_PATH/.env" ]; then
    echo "✓ .env file exists"
else
    echo "⚠ Warning: .env file not found"
fi

# Check git remotes
if sudo -u $SERVICE_USER git -C "$DEPLOY_PATH" remote get-url origin >/dev/null 2>&1; then
    echo "✓ Git remotes configured"
else
    echo "⚠ Warning: Git remotes not configured"
fi

echo ""
echo "=========================================="
echo "Update completed!"
echo "=========================================="
echo ""
echo "To test the script:"
echo "  sudo -u $SERVICE_USER python3 $DEPLOY_PATH/fetch_cyber_news.py"
echo ""

