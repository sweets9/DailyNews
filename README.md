# Daily News

Automated daily cyber security news aggregator that fetches the latest security updates and saves them to this repository.

## How It Works

1. Script runs daily at 7:00 AM and 10:00 AM (via crontab)
2. Fetches latest cyber security news using Gemini CLI
3. Saves news items to `newsitems/` directory
4. Updates this README with links to new items
5. Commits and pushes changes:
   - **Gitea**: All files (including scripts)
   - **GitHub**: Only README.md and newsitems/ (scripts excluded for security)

## Repository Configuration

The script pushes to two remotes:
- **origin**: Gitea repository (`git.sweet6.net/Sweet6/DailyNews`)
- **github**: GitHub repository (`sweets9/DailyNews`)

### Credentials Setup

Credentials are stored in `.env` file (excluded from git sync):

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   - `GITEA_USERNAME` and `GITEA_PASSWORD`: Gitea credentials
   - `GITHUB_TOKEN`: GitHub Personal Access Token

3. The script automatically configures git remotes using credentials from `.env`

See `GIT_REMOTES_SETUP.md` for detailed setup instructions.

## Production Setup

To set up on an Ubuntu production server:

1. **Clone the repository**:
   ```bash
   git clone https://git.sweet6.net/Sweet6/DailyNews /opt/DailyNews
   ```

2. **Run the setup script**:
   ```bash
   sudo bash /opt/DailyNews/setup-dailynews-production.sh
   ```

3. **Configure credentials**:
   ```bash
   sudo -u dailynews nano /opt/DailyNews/.env
   ```

The setup script will:
- Install Node.js 22 and gemini-cli
- Create the `dailynews` service user
- Clone/update the repository
- Set up crontab entries for 7am and 10am runs
- Create the `.env` file from template
- Configure git credentials securely

**Note**: The setup script is idempotent - safe to run multiple times without breaking existing configuration.

## Updating

To update the installation with latest changes:

```bash
sudo bash /opt/DailyNews/update-dailynews.sh
```

This will:
- Pull latest changes from the repository
- Re-run the setup script to apply any configuration changes
- Verify the installation

**Note**: Always use `/opt/DailyNews` (capital D and N) as the deployment path.

## Cyber Security News
- [2025-12-23 10:01](newsitems/CyberNews-2025-12-23_10:01.md)
- [2025-12-23 07:01](newsitems/CyberNews-2025-12-23_07:01.md)
- [2025-12-21 10:02](newsitems/CyberNews-2025-12-21_10:02.md)
- [2025-12-21 07:03](newsitems/CyberNews-2025-12-21_07:03.md)
- [2025-12-20 10:00](newsitems/CyberNews-2025-12-20_10:00.md)
- [2025-12-20 07:03](newsitems/CyberNews-2025-12-20_07:03.md)
- [2025-12-19 10:01](newsitems/CyberNews-2025-12-19_10:01.md)
- [2025-12-19 07:02](newsitems/CyberNews-2025-12-19_07:02.md)
- [2025-12-18 10:00](newsitems/CyberNews-2025-12-18_10:00.md)
- [2025-12-18 07:02](newsitems/CyberNews-2025-12-18_07:02.md)
- [2025-12-17 10:03](newsitems/CyberNews-2025-12-17_10:03.md)
- [2025-12-17 07:01](newsitems/CyberNews-2025-12-17_07:01.md)
- [2025-12-16 10:01](newsitems/CyberNews-2025-12-16_10:01.md)
- [2025-12-16 07:01](newsitems/CyberNews-2025-12-16_07:01.md)
- [2025-12-15 10:01](newsitems/CyberNews-2025-12-15_10:01.md)
- [2025-12-15 07:02](newsitems/CyberNews-2025-12-15_07:02.md)
- [2025-12-14 10:02](newsitems/CyberNews-2025-12-14_10:02.md)
- [2025-12-13 10:00](newsitems/CyberNews-2025-12-13_10:00.md)
- [2025-12-13 07:01](newsitems/CyberNews-2025-12-13_07:01.md)
- [2025-12-12 10:00](newsitems/CyberNews-2025-12-12_10:00.md)
- [2025-12-12 07:01](newsitems/CyberNews-2025-12-12_07:01.md)
- [2025-12-11 15:54](newsitems/CyberNews-2025-12-11_15:54.md)

