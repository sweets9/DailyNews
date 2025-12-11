#!/bin/bash
#
# DailyNews Production Setup Script
# Run this script on your Ubuntu production server to set up the DailyNews deployment
#
# Usage: ./setup-dailynews-production.sh [DEPLOY_PATH]
#   DEPLOY_PATH: Where to deploy the repository (default: /opt/DailyNews)
#

# Don't exit on error - make it resilient
set +e

DEPLOY_PATH="${1:-/opt/DailyNews}"
REPO_URL="https://git.sweet6.net/Sweet6/DailyNews"
SERVICE_USER="${SERVICE_USER:-dailynews}"

echo "=========================================="
echo "DailyNews Production Setup"
echo "=========================================="
echo "Deploy path: $DEPLOY_PATH"
echo "Repository: $REPO_URL"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Update system
echo "[1/9] Updating system packages..."
if ! command -v git &> /dev/null || ! command -v python3 &> /dev/null || ! command -v curl &> /dev/null; then
    apt-get update
    apt-get install -y curl git python3 python3-pip cron
    echo "System packages installed/updated"
else
    echo "Required packages already installed (git, python3, curl)"
fi

# Install Node.js 22
echo "[2/8] Installing Node.js 22..."
if ! command -v node &> /dev/null || [ "$(node -v | cut -d'v' -f2 | cut -d'.' -f1)" -lt 20 ]; then
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
    apt-get install -y nodejs
else
    echo "Node.js $(node -v) already installed"
fi

# Install gemini-cli globally
echo "[3/9] Installing gemini-cli..."
if ! npm list -g @google/gemini-cli &>/dev/null; then
    npm install -g @google/gemini-cli
    echo "gemini-cli installed"
else
    echo "gemini-cli already installed, updating..."
    npm install -g @google/gemini-cli
fi

# Create service user
echo "[4/8] Creating service user..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/bash -m -d /home/$SERVICE_USER $SERVICE_USER
    echo "Created user: $SERVICE_USER"
else
    echo "User $SERVICE_USER already exists"
fi

# Create deploy directory
echo "[5/8] Setting up deployment directory..."
mkdir -p "$DEPLOY_PATH"
chown $SERVICE_USER:$SERVICE_USER "$DEPLOY_PATH"

# Clone repository (as service user)
echo "[6/9] Cloning/updating repository..."
if [ -d "$DEPLOY_PATH/.git" ]; then
    echo "Repository already exists, updating..."
    cd "$DEPLOY_PATH"
    sudo -u $SERVICE_USER git fetch origin || true
    sudo -u $SERVICE_USER git reset --hard origin/main || true
    cd - > /dev/null
else
    echo "Cloning repository..."
    sudo -u $SERVICE_USER git clone "$REPO_URL" "$DEPLOY_PATH"
fi

# Configure git for service user (needed for pushing)
echo "Configuring git for service user..."
sudo -u $SERVICE_USER git -C "$DEPLOY_PATH" config user.name "DailyNews Bot" || true
sudo -u $SERVICE_USER git -C "$DEPLOY_PATH" config user.email "dailynews@$(hostname)" || true

# Create .env file from example
echo "Setting up .env file for credentials..."
if [ -f "$DEPLOY_PATH/.env.example" ]; then
    if [ ! -f "$DEPLOY_PATH/.env" ]; then
        sudo -u $SERVICE_USER cp "$DEPLOY_PATH/.env.example" "$DEPLOY_PATH/.env"
        chmod 600 "$DEPLOY_PATH/.env"
        echo "Created .env file from .env.example"
        echo ""
        echo "IMPORTANT: Edit .env file and add your credentials:"
        echo "  sudo -u $SERVICE_USER nano $DEPLOY_PATH/.env"
        echo ""
        echo "Required values:"
        echo "  - GITEA_USERNAME: Your Gitea username"
        echo "  - GITEA_PASSWORD: Your Gitea password or token"
        echo "  - GITHUB_TOKEN: Your GitHub Personal Access Token"
        echo "    (Create at: https://github.com/settings/tokens)"
        echo ""
    else
        echo ".env file already exists, skipping creation"
    fi
else
    echo "Warning: .env.example not found. Create .env manually with credentials."
fi

# Make script executable
chmod +x "$DEPLOY_PATH/fetch_cyber_news.py" 2>/dev/null || true

# Remove any existing systemd service/timer files (migrating to crontab)
echo "[7/9] Removing old systemd services/timers (if any) and setting up crontab..."
if [ -f /etc/systemd/system/dailynews.service ]; then
    echo "Removing systemd service file..."
    systemctl stop dailynews.service 2>/dev/null || true
    systemctl disable dailynews.service 2>/dev/null || true
    rm -f /etc/systemd/system/dailynews.service
fi

if [ -f /etc/systemd/system/dailynews-7am.timer ]; then
    echo "Removing systemd 7am timer..."
    systemctl stop dailynews-7am.timer 2>/dev/null || true
    systemctl disable dailynews-7am.timer 2>/dev/null || true
    rm -f /etc/systemd/system/dailynews-7am.timer
fi

if [ -f /etc/systemd/system/dailynews-10am.timer ]; then
    echo "Removing systemd 10am timer..."
    systemctl stop dailynews-10am.timer 2>/dev/null || true
    systemctl disable dailynews-10am.timer 2>/dev/null || true
    rm -f /etc/systemd/system/dailynews-10am.timer
fi

# Reload systemd if any files were removed
if [ -f /etc/systemd/system/dailynews.service ] || [ -f /etc/systemd/system/dailynews-7am.timer ] || [ -f /etc/systemd/system/dailynews-10am.timer ]; then
    systemctl daemon-reload 2>/dev/null || true
fi

# Setup crontab for scheduled runs

# Ensure cron is installed
if ! command -v crontab &> /dev/null; then
    apt-get install -y cron
fi

# Create temporary crontab file
CRON_TEMP=$(mktemp)
sudo -u $SERVICE_USER crontab -l > "$CRON_TEMP" 2>/dev/null || true

# Remove existing DailyNews entries if they exist
sed -i '/DailyNews/d' "$CRON_TEMP" 2>/dev/null || true
sed -i '/fetch_cyber_news.py/d' "$CRON_TEMP" 2>/dev/null || true

# Add new crontab entries
cat >> "$CRON_TEMP" << EOF

# DailyNews - Run at 7:00 AM daily
0 7 * * * /usr/bin/python3 $DEPLOY_PATH/fetch_cyber_news.py >> $DEPLOY_PATH/cron.log 2>&1

# DailyNews - Run at 10:00 AM daily
0 10 * * * /usr/bin/python3 $DEPLOY_PATH/fetch_cyber_news.py >> $DEPLOY_PATH/cron.log 2>&1
EOF

# Install the crontab
sudo -u $SERVICE_USER crontab "$CRON_TEMP"
rm -f "$CRON_TEMP"

# Verify crontab was installed
if sudo -u $SERVICE_USER crontab -l | grep -q "fetch_cyber_news.py"; then
    echo "Crontab entries added successfully"
    echo "Current crontab for $SERVICE_USER:"
    sudo -u $SERVICE_USER crontab -l | grep -A 2 "DailyNews" || true
else
    echo "Warning: Failed to verify crontab installation"
fi

# Ensure cron service is running
systemctl enable cron 2>/dev/null || systemctl enable crond 2>/dev/null || true
systemctl start cron 2>/dev/null || systemctl start crond 2>/dev/null || true

# Create SSH key for CI/CD (if needed)
echo "[8/9] Setting up SSH for CI/CD..."
SSH_DIR="/home/$SERVICE_USER/.ssh"
mkdir -p "$SSH_DIR"
chmod 700 "$SSH_DIR"

if [ ! -f "$SSH_DIR/id_rsa" ]; then
    echo "Generating SSH key for CI/CD deployment..."
    sudo -u $SERVICE_USER ssh-keygen -t rsa -b 4096 -f "$SSH_DIR/id_rsa" -N "" -C "dailynews-deploy"
    echo ""
    echo "=========================================="
    echo "IMPORTANT: Add this public key to your CI/CD secrets:"
    echo "=========================================="
    cat "$SSH_DIR/id_rsa.pub"
    echo ""
    echo "Add this as PROD_SSH_KEY secret in GitHub Actions"
    echo "=========================================="
fi

# Set up git config for service user
sudo -u $SERVICE_USER git -C "$DEPLOY_PATH" config user.name "DailyNews Bot" || true
sudo -u $SERVICE_USER git -C "$DEPLOY_PATH" config user.email "dailynews@$(hostname)" || true

# Create newsitems directory
echo "[9/9] Creating newsitems directory..."
mkdir -p "$DEPLOY_PATH/newsitems"
chown $SERVICE_USER:$SERVICE_USER "$DEPLOY_PATH/newsitems" 2>/dev/null || true

# Create log file for cron output
touch "$DEPLOY_PATH/cron.log"
chown $SERVICE_USER:$SERVICE_USER "$DEPLOY_PATH/cron.log" 2>/dev/null || true
chmod 644 "$DEPLOY_PATH/cron.log" 2>/dev/null || true

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure git credentials for pushing to Gitea (see above)"
echo ""
echo "2. Configure credentials in .env file:"
echo "   sudo -u $SERVICE_USER nano $DEPLOY_PATH/.env"
echo "   - Add GITEA_USERNAME and GITEA_PASSWORD"
echo "   - Add GITHUB_TOKEN (create at https://github.com/settings/tokens)"
echo "   - See GIT_REMOTES_SETUP.md for details"
echo ""
echo "3. Check crontab status:"
echo "   sudo -u $SERVICE_USER crontab -l"
echo "   systemctl status cron"
echo ""
echo "4. View cron logs:"
echo "   tail -f $DEPLOY_PATH/cron.log"
echo ""
echo "5. Test the script manually:"
echo "   sudo -u $SERVICE_USER python3 $DEPLOY_PATH/fetch_cyber_news.py"
echo ""

