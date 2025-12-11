# Daily News

Automated daily cyber security news aggregator that fetches the latest security updates and saves them to this repository.

## How It Works

1. Script runs daily at 7:00 AM and 10:00 AM (UTC)
2. Fetches latest cyber security news using Gemini CLI
3. Saves news items to `newsitems/` directory
4. Updates this README with links to new items
5. Commits and pushes changes to both Gitea and GitHub

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

## Cyber Security News

