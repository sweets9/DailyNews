#!/bin/bash
#
# DailyNews Production Setup Script
# Run this script on your Ubuntu production server to set up the DailyNews deployment
#
# Usage: ./setup-dailynews-production.sh [DEPLOY_PATH]
#   DEPLOY_PATH: Where to deploy the repository (default: /opt/DailyNews)
#

set -e

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
echo "[1/8] Updating system packages..."
apt-get update
apt-get install -y curl git python3 python3-pip

# Install Node.js 22
echo "[2/8] Installing Node.js 22..."
if ! command -v node &> /dev/null || [ "$(node -v | cut -d'v' -f2 | cut -d'.' -f1)" -lt 20 ]; then
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
    apt-get install -y nodejs
else
    echo "Node.js $(node -v) already installed"
fi

# Install gemini-cli globally
echo "[3/8] Installing gemini-cli..."
npm install -g @google/gemini-cli

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
echo "[6/8] Cloning repository..."
if [ -d "$DEPLOY_PATH/.git" ]; then
    echo "Repository already exists, skipping clone"
    echo "Run 'cd $DEPLOY_PATH && git pull' to update"
else
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
chmod +x "$DEPLOY_PATH/fetch_cyber_news.py"

# Create systemd service
echo "[7/8] Creating systemd service..."
cat > /etc/systemd/system/dailynews.service << EOF
[Unit]
Description=DailyNews Cyber Security News Fetcher
After=network.target

[Service]
Type=oneshot
User=$SERVICE_USER
WorkingDirectory=$DEPLOY_PATH
Environment="PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin"
ExecStart=/usr/bin/python3 $DEPLOY_PATH/fetch_cyber_news.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create systemd timer for 7am and 10am
cat > /etc/systemd/system/dailynews-7am.timer << EOF
[Unit]
Description=Run DailyNews at 7:00 AM
Requires=dailynews.service

[Timer]
OnCalendar=*-*-* 07:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

cat > /etc/systemd/system/dailynews-10am.timer << EOF
[Unit]
Description=Run DailyNews at 10:00 AM
Requires=dailynews.service

[Timer]
OnCalendar=*-*-* 10:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Reload systemd and enable timers
systemctl daemon-reload
systemctl enable dailynews-7am.timer
systemctl enable dailynews-10am.timer
systemctl start dailynews-7am.timer
systemctl start dailynews-10am.timer

# Create SSH key for CI/CD (if needed)
echo "[8/8] Setting up SSH for CI/CD..."
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
mkdir -p "$DEPLOY_PATH/newsitems"
chown $SERVICE_USER:$SERVICE_USER "$DEPLOY_PATH/newsitems"

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
echo "3. Check timer status:"
echo "   systemctl status dailynews-7am.timer"
echo "   systemctl status dailynews-10am.timer"
echo ""
echo "4. Test the script manually:"
echo "   sudo -u $SERVICE_USER python3 $DEPLOY_PATH/fetch_cyber_news.py"
echo ""

