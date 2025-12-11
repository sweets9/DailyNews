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

# Configure git credential helper to store credentials
echo "Configuring git credential storage..."
sudo -u $SERVICE_USER git config --global credential.helper store || true

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

# Configure git remotes with credentials from .env (if available)
echo "Configuring git remotes with credentials..."
if [ -f "$DEPLOY_PATH/.env" ]; then
    # Read .env file and extract credentials
    GITEA_USERNAME=""
    GITEA_PASSWORD=""
    GITHUB_USERNAME=""
    GITHUB_TOKEN=""
    
    while IFS='=' read -r key value || [ -n "$key" ]; do
        # Skip comments and empty lines
        [[ "$key" =~ ^#.*$ ]] && continue
        [[ -z "$key" ]] && continue
        
        # Remove quotes from value if present
        value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
        
        case "$key" in
            GITEA_USERNAME)
                GITEA_USERNAME="$value"
                ;;
            GITEA_PASSWORD)
                GITEA_PASSWORD="$value"
                ;;
            GITHUB_USERNAME)
                GITHUB_USERNAME="$value"
                ;;
            GITHUB_TOKEN)
                GITHUB_TOKEN="$value"
                ;;
        esac
    done < "$DEPLOY_PATH/.env"
    
    # Configure origin (Gitea) remote with credentials
    if [ -n "$GITEA_USERNAME" ] && [ -n "$GITEA_PASSWORD" ]; then
        GITEA_URL_WITH_AUTH="https://${GITEA_USERNAME}:${GITEA_PASSWORD}@git.sweet6.net/Sweet6/DailyNews"
        sudo -u $SERVICE_USER git -C "$DEPLOY_PATH" remote set-url origin "$GITEA_URL_WITH_AUTH" 2>/dev/null || \
        sudo -u $SERVICE_USER git -C "$DEPLOY_PATH" remote add origin "$GITEA_URL_WITH_AUTH" 2>/dev/null || true
        echo "✓ Configured Gitea remote with credentials (passwordless git pull enabled)"
    else
        echo "⚠ Gitea credentials not found in .env, remote may prompt for credentials"
    fi
    
    # Configure github remote with credentials (if configured)
    if [ -n "$GITHUB_TOKEN" ]; then
        GITHUB_USER="${GITHUB_USERNAME:-sweets9}"
        GITHUB_URL_WITH_AUTH="https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/sweets9/DailyNews.git"
        sudo -u $SERVICE_USER git -C "$DEPLOY_PATH" remote set-url github "$GITHUB_URL_WITH_AUTH" 2>/dev/null || \
        sudo -u $SERVICE_USER git -C "$DEPLOY_PATH" remote add github "$GITHUB_URL_WITH_AUTH" 2>/dev/null || true
        echo "✓ Configured GitHub remote with credentials"
    else
        echo "⚠ GitHub token not found in .env, GitHub remote not configured"
    fi
    
    # Test git fetch to verify credentials work
    echo "Testing git credentials..."
    cd "$DEPLOY_PATH"
    GIT_TEST_OUTPUT=$(sudo -u $SERVICE_USER git fetch origin 2>&1)
    GIT_TEST_EXIT=$?
    
    if [ $GIT_TEST_EXIT -eq 0 ]; then
        echo "✓ Git credentials verified - passwordless git pull is working"
    else
        echo "⚠ Git fetch test failed (exit code: $GIT_TEST_EXIT)"
        echo "   Output: $GIT_TEST_OUTPUT"
        echo "   This might be normal if credentials need to be set up first"
        echo "   After configuring .env, credentials will be used automatically"
    fi
    cd - > /dev/null
else
    echo "⚠ .env file not found, cannot configure git credentials automatically"
    echo "   After creating .env, run the setup script again or configure manually"
fi

# Make script executable
chmod +x "$DEPLOY_PATH/fetch_cyber_news.py" 2>/dev/null || true

# Remove any existing systemd service/timer files (migrating to crontab)
echo "[7/9] Removing old systemd services/timers (if any) and setting up crontab..."
NEED_RELOAD=false

if [ -f /etc/systemd/system/dailynews.service ]; then
    echo "Removing systemd service file..."
    systemctl stop dailynews.service 2>/dev/null || true
    systemctl disable dailynews.service 2>/dev/null || true
    rm -f /etc/systemd/system/dailynews.service
    NEED_RELOAD=true
fi

if [ -f /etc/systemd/system/dailynews-7am.timer ]; then
    echo "Removing systemd 7am timer..."
    systemctl stop dailynews-7am.timer 2>/dev/null || true
    systemctl disable dailynews-7am.timer 2>/dev/null || true
    rm -f /etc/systemd/system/dailynews-7am.timer
    NEED_RELOAD=true
fi

if [ -f /etc/systemd/system/dailynews-10am.timer ]; then
    echo "Removing systemd 10am timer..."
    systemctl stop dailynews-10am.timer 2>/dev/null || true
    systemctl disable dailynews-10am.timer 2>/dev/null || true
    rm -f /etc/systemd/system/dailynews-10am.timer
    NEED_RELOAD=true
fi

# Reload systemd if any files were removed
if [ "$NEED_RELOAD" = true ]; then
    systemctl daemon-reload 2>/dev/null || true
    echo "Systemd daemon reloaded"
fi

# Setup crontab for scheduled runs

# Ensure cron is installed
if ! command -v crontab &> /dev/null; then
    apt-get install -y cron
fi

# Create temporary crontab file in a location accessible by the service user
CRON_TEMP=$(mktemp /tmp/crontab.XXXXXX)
chmod 666 "$CRON_TEMP"  # Make it readable/writable
sudo -u $SERVICE_USER crontab -l > "$CRON_TEMP" 2>/dev/null || touch "$CRON_TEMP"

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

# Change ownership to service user and install the crontab
chown $SERVICE_USER:$SERVICE_USER "$CRON_TEMP" 2>/dev/null || true
chmod 600 "$CRON_TEMP"  # Secure permissions before installing
sudo -u $SERVICE_USER crontab "$CRON_TEMP"
rm -f "$CRON_TEMP"

# Verify crontab was installed
echo ""
echo "Verifying crontab installation..."
if sudo -u $SERVICE_USER crontab -l 2>/dev/null | grep -q "fetch_cyber_news.py"; then
    echo "✓ Crontab entries added successfully for user: $SERVICE_USER"
    echo ""
    echo "Current crontab entries for $SERVICE_USER:"
    echo "----------------------------------------"
    sudo -u $SERVICE_USER crontab -l 2>/dev/null | grep -A 2 "DailyNews" || sudo -u $SERVICE_USER crontab -l 2>/dev/null
    echo "----------------------------------------"
    echo ""
    echo "To view/edit crontab for $SERVICE_USER user:"
    echo "  View: sudo -u $SERVICE_USER crontab -l"
    echo "  Edit: sudo -u $SERVICE_USER crontab -e"
else
    echo "⚠ Warning: Failed to verify crontab installation"
    echo "Attempting to list crontab:"
    sudo -u $SERVICE_USER crontab -l 2>/dev/null || echo "No crontab found for user $SERVICE_USER"
fi

# Ensure cron service is running
systemctl enable cron 2>/dev/null || systemctl enable crond 2>/dev/null || true
systemctl start cron 2>/dev/null || systemctl start crond 2>/dev/null || true

# Create SSH key for CI/CD (if needed)
echo "[8/9] Setting up SSH for CI/CD..."
SSH_DIR="/home/$SERVICE_USER/.ssh"

# Ensure home directory exists and has correct permissions
if [ ! -d "/home/$SERVICE_USER" ]; then
    mkdir -p "/home/$SERVICE_USER"
    chown $SERVICE_USER:$SERVICE_USER "/home/$SERVICE_USER"
fi

# Create .ssh directory with correct permissions
mkdir -p "$SSH_DIR"
chown $SERVICE_USER:$SERVICE_USER "$SSH_DIR"
chmod 700 "$SSH_DIR"

if [ ! -f "$SSH_DIR/id_rsa" ]; then
    echo "Generating SSH key for CI/CD deployment..."
    # Generate key as the service user
    sudo -u $SERVICE_USER ssh-keygen -t rsa -b 4096 -f "$SSH_DIR/id_rsa" -N "" -C "dailynews-deploy" 2>&1
    
    # Verify key was created
    if [ -f "$SSH_DIR/id_rsa.pub" ]; then
        echo ""
        echo "=========================================="
        echo "IMPORTANT: Add this public key to your CI/CD secrets:"
        echo "=========================================="
        cat "$SSH_DIR/id_rsa.pub"
        echo ""
        echo "Add this as PROD_SSH_KEY secret in GitHub Actions"
        echo "=========================================="
    else
        echo "⚠ Warning: SSH key generation may have failed"
        echo "   Check permissions on $SSH_DIR"
    fi
else
    echo "SSH key already exists, skipping generation"
    if [ -f "$SSH_DIR/id_rsa.pub" ]; then
        echo "Public key:"
        cat "$SSH_DIR/id_rsa.pub"
    fi
fi

# Set up git config for service user (if not already done)
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

