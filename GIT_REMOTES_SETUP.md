# Git Remotes Setup

Since Gitea push mirroring is not available, the script pushes directly to both Gitea and GitHub remotes.

**Credentials are stored in `.env` file which is excluded from git sync.**

## Quick Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your credentials:
   ```bash
   nano .env  # or use your preferred editor
   ```

3. The script will automatically configure git remotes using credentials from `.env`

## Detailed Setup Instructions

### 1. Create .env File

1. Copy the example file:
   ```bash
   cd /opt/DailyNews  # or your deployment path
   cp .env.example .env
   ```

2. Edit `.env` and fill in your credentials:
   ```bash
   nano .env
   ```

3. Required values:
   - `GITEA_USERNAME`: Your Gitea username
   - `GITEA_PASSWORD`: Your Gitea password or access token
   - `GITHUB_TOKEN`: Your GitHub Personal Access Token (create at https://github.com/settings/tokens)

### 2. Configure Authentication

The script automatically configures git remotes using credentials from `.env`. No manual git remote configuration needed!

#### For HTTPS (Recommended - Default)

1. **Create GitHub Personal Access Token**:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Name: "DailyNews Bot"
   - Select scope: `repo` (full control of private repositories)
   - Generate and copy the token

2. **Add token to .env file**:
   ```bash
   GITHUB_TOKEN=ghp_your_token_here
   ```

3. **The script will automatically use the token** - no manual git configuration needed!

#### For SSH (Alternative)

If you prefer SSH instead of HTTPS:

1. **Set in .env file**:
   ```bash
   GITHUB_USE_SSH=true
   GITEA_USE_SSH=true  # if also using SSH for Gitea
   ```

2. **Generate SSH key** (if not already done):
   ```bash
   ssh-keygen -t ed25519 -C "dailynews-bot" -f ~/.ssh/id_ed25519_github
   ```

3. **Add SSH key to GitHub**:
   - Copy public key: `cat ~/.ssh/id_ed25519_github.pub`
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Paste the public key and save

4. **Configure SSH for GitHub**:
   ```bash
   # Add to ~/.ssh/config
   cat >> ~/.ssh/config << EOF
   Host github.com
       HostName github.com
       User git
       IdentityFile ~/.ssh/id_ed25519_github
       IdentitiesOnly yes
   EOF
   chmod 600 ~/.ssh/config
   ```

5. **Update .env with SSH URL**:
   ```bash
   GITHUB_URL=git@github.com:sweets9/DailyNews.git
   ```

### 3. Verify Setup

The script automatically configures remotes from `.env` on each run. To verify:

1. **Check .env file exists and has credentials**:
   ```bash
   ls -la .env
   # Make sure it's readable by the service user
   ```

2. **Test the script**:
   ```bash
   python3 fetch_cyber_news.py
   ```

3. **Verify remotes are configured** (after first run):
   ```bash
   git remote -v
   ```

   You should see both remotes configured with credentials embedded in URLs (for HTTPS).

### 4. Security Notes

- **`.env` file is excluded from git** (in `.gitignore`)
- **Never commit `.env` file** - it contains sensitive credentials
- **File permissions**: Ensure `.env` is readable only by the service user:
   ```bash
   chmod 600 .env
   chown dailynews:dailynews .env
   ```

## Troubleshooting

### GitHub Authentication Errors

- **"Authentication failed"**: 
  - Verify your Personal Access Token is correct and has `repo` scope
  - For HTTPS: Use token as password, not your GitHub password
  - For SSH: Verify SSH key is added to GitHub account

- **"Permission denied"**:
  - Ensure the GitHub repository exists: https://github.com/sweets9/DailyNews
  - Verify you have push access to the repository
  - Check that the remote URL is correct

### Gitea Authentication Errors

- **"Authentication failed"**:
  - Verify Gitea credentials are configured
  - Check that the service user has push access to the repository
  - For HTTPS: Ensure credentials are stored in git credential helper

### Remote Not Found

- **"fatal: 'github' does not appear to be a git repository"**:
  - Run: `git remote add github https://github.com/sweets9/DailyNews.git`
  - Verify with: `git remote -v`

## Security Notes

- **Never commit credentials**: Store tokens/keys securely
- **Use credential helper**: For HTTPS, use git credential helper to store tokens
- **SSH keys**: Keep private keys secure (600 permissions)
- **Token scope**: Use minimum required scope (`repo` for private repos)

## Alternative: Single Remote with Post-Receive Hook

If you prefer, you can configure Gitea to push to GitHub using a post-receive hook:

1. Go to Gitea: **Settings** → **Repository** → **Git Hooks**
2. Edit `post-receive` hook:
   ```bash
   #!/bin/bash
   git push github main || echo "Failed to push to GitHub"
   ```

This way, the script only pushes to Gitea, and Gitea automatically pushes to GitHub.

