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
- [2026-02-20 10:01](newsitems/CyberNews-2026-02-20_10:01.md)
- [2026-02-20 07:01](newsitems/CyberNews-2026-02-20_07:01.md)
- [2026-02-14 10:00](newsitems/CyberNews-2026-02-14_10:00.md)
- [2026-02-14 07:01](newsitems/CyberNews-2026-02-14_07:01.md)
- [2026-02-13 10:00](newsitems/CyberNews-2026-02-13_10:00.md)
- [2026-02-13 07:01](newsitems/CyberNews-2026-02-13_07:01.md)
- [2026-02-12 10:01](newsitems/CyberNews-2026-02-12_10:01.md)
- [2026-02-12 07:01](newsitems/CyberNews-2026-02-12_07:01.md)
- [2026-02-11 10:01](newsitems/CyberNews-2026-02-11_10:01.md)
- [2026-02-11 07:02](newsitems/CyberNews-2026-02-11_07:02.md)
- [2026-02-10 10:00](newsitems/CyberNews-2026-02-10_10:00.md)
- [2026-02-10 07:00](newsitems/CyberNews-2026-02-10_07:00.md)
- [2026-02-09 07:02](newsitems/CyberNews-2026-02-09_07:02.md)
- [2026-02-08 10:02](newsitems/CyberNews-2026-02-08_10:02.md)
- [2026-02-08 07:01](newsitems/CyberNews-2026-02-08_07:01.md)
- [2026-02-07 10:01](newsitems/CyberNews-2026-02-07_10:01.md)
- [2026-02-07 07:02](newsitems/CyberNews-2026-02-07_07:02.md)
- [2026-02-06 10:01](newsitems/CyberNews-2026-02-06_10:01.md)
- [2026-02-06 07:02](newsitems/CyberNews-2026-02-06_07:02.md)
- [2026-02-05 10:01](newsitems/CyberNews-2026-02-05_10:01.md)
- [2026-02-05 07:01](newsitems/CyberNews-2026-02-05_07:01.md)
- [2026-02-04 10:02](newsitems/CyberNews-2026-02-04_10:02.md)
- [2026-02-04 07:01](newsitems/CyberNews-2026-02-04_07:01.md)
- [2026-02-03 10:01](newsitems/CyberNews-2026-02-03_10:01.md)
- [2026-02-03 07:01](newsitems/CyberNews-2026-02-03_07:01.md)
- [2026-02-02 10:01](newsitems/CyberNews-2026-02-02_10:01.md)
- [2026-02-02 07:01](newsitems/CyberNews-2026-02-02_07:01.md)
- [2026-02-01 10:01](newsitems/CyberNews-2026-02-01_10:01.md)
- [2026-02-01 07:01](newsitems/CyberNews-2026-02-01_07:01.md)
- [2026-01-31 10:01](newsitems/CyberNews-2026-01-31_10:01.md)
- [2026-01-31 07:01](newsitems/CyberNews-2026-01-31_07:01.md)
- [2026-01-30 10:01](newsitems/CyberNews-2026-01-30_10:01.md)
- [2026-01-30 07:02](newsitems/CyberNews-2026-01-30_07:02.md)
- [2026-01-29 10:04](newsitems/CyberNews-2026-01-29_10:04.md)
- [2026-01-29 07:02](newsitems/CyberNews-2026-01-29_07:02.md)
- [2026-01-28 10:01](newsitems/CyberNews-2026-01-28_10:01.md)
- [2026-01-28 07:01](newsitems/CyberNews-2026-01-28_07:01.md)
- [2026-01-27 10:01](newsitems/CyberNews-2026-01-27_10:01.md)
- [2026-01-27 07:01](newsitems/CyberNews-2026-01-27_07:01.md)
- [2026-01-26 10:00](newsitems/CyberNews-2026-01-26_10:00.md)
- [2026-01-26 07:01](newsitems/CyberNews-2026-01-26_07:01.md)
- [2026-01-25 10:03](newsitems/CyberNews-2026-01-25_10:03.md)
- [2026-01-25 07:01](newsitems/CyberNews-2026-01-25_07:01.md)
- [2026-01-24 10:02](newsitems/CyberNews-2026-01-24_10:02.md)
- [2026-01-24 07:00](newsitems/CyberNews-2026-01-24_07:00.md)
- [2026-01-23 10:02](newsitems/CyberNews-2026-01-23_10:02.md)
- [2026-01-23 07:02](newsitems/CyberNews-2026-01-23_07:02.md)
- [2026-01-22 10:01](newsitems/CyberNews-2026-01-22_10:01.md)
- [2026-01-21 10:00](newsitems/CyberNews-2026-01-21_10:00.md)
- [2026-01-21 07:03](newsitems/CyberNews-2026-01-21_07:03.md)
- [2026-01-20 07:04](newsitems/CyberNews-2026-01-20_07:04.md)
- [2026-01-19 10:00](newsitems/CyberNews-2026-01-19_10:00.md)
- [2026-01-19 07:01](newsitems/CyberNews-2026-01-19_07:01.md)
- [2026-01-18 10:01](newsitems/CyberNews-2026-01-18_10:01.md)
- [2026-01-18 07:01](newsitems/CyberNews-2026-01-18_07:01.md)
- [2026-01-17 10:01](newsitems/CyberNews-2026-01-17_10:01.md)
- [2026-01-17 07:02](newsitems/CyberNews-2026-01-17_07:02.md)
- [2026-01-16 10:01](newsitems/CyberNews-2026-01-16_10:01.md)
- [2026-01-16 07:01](newsitems/CyberNews-2026-01-16_07:01.md)
- [2026-01-15 10:03](newsitems/CyberNews-2026-01-15_10:03.md)
- [2026-01-15 07:01](newsitems/CyberNews-2026-01-15_07:01.md)
- [2026-01-14 10:01](newsitems/CyberNews-2026-01-14_10:01.md)
- [2026-01-14 07:01](newsitems/CyberNews-2026-01-14_07:01.md)
- [2026-01-13 10:00](newsitems/CyberNews-2026-01-13_10:00.md)
- [2026-01-13 07:01](newsitems/CyberNews-2026-01-13_07:01.md)
- [2026-01-12 10:01](newsitems/CyberNews-2026-01-12_10:01.md)
- [2026-01-12 07:01](newsitems/CyberNews-2026-01-12_07:01.md)
- [2025-12-26 10:01](newsitems/CyberNews-2025-12-26_10:01.md)
- [2025-12-26 07:00](newsitems/CyberNews-2025-12-26_07:00.md)
- [2025-12-25 10:00](newsitems/CyberNews-2025-12-25_10:00.md)
- [2025-12-25 07:02](newsitems/CyberNews-2025-12-25_07:02.md)
- [2025-12-24 10:01](newsitems/CyberNews-2025-12-24_10:01.md)
- [2025-12-24 07:01](newsitems/CyberNews-2025-12-24_07:01.md)
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

