# Gitea Push Mirror Setup

This repository uses Gitea's push mirroring feature to automatically sync changes to the GitHub repository `sweets9/DailyNews`. The script only pushes to the Gitea repository (origin), and Gitea handles syncing to GitHub.

## Setup Instructions

### 0. Prerequisites

1. **GitHub Repository**: Ensure the repository `sweets9/DailyNews` exists on GitHub
   - If it doesn't exist, create it at: https://github.com/new
   - Repository name: `DailyNews`
   - Owner: `sweets9`
   - You can create it as empty (Gitea will push the content)

2. **GitHub Personal Access Token**: Create a token with `repo` scope
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Name: "Gitea Mirror - DailyNews"
   - Select scope: `repo` (full control of private repositories)
   - Generate and copy the token (you won't see it again!)

### 1. Configure Push Mirror in Gitea

1. Navigate to your Gitea repository: `https://your-gitea-server/Sweet6/DailyNews`
2. Go to **Settings** → **Repository**
3. Scroll down to the **Mirror Settings** section
4. Under **Push Mirror**, click **Add Push Mirror**
5. Configure the mirror:
   - **Remote Repository URL**: `https://github.com/sweets9/DailyNews.git`
   - **Authorization** (required for GitHub):
     - **Username**: Your GitHub username (or `sweets9`)
     - **Password/Token**: Your GitHub Personal Access Token (PAT)
       - Create a token at: https://github.com/settings/tokens
       - Required scopes: `repo` (full control of private repositories)
   - **Sync Interval**: Choose how often to sync (default: every push, or set a time interval)
6. Click **Add Push Mirror**

### 2. Test the Mirror

1. Make a test commit and push to Gitea
2. Check the mirror status in **Settings** → **Repository** → **Mirror Settings**
3. You should see the last sync time and status
4. Verify the changes appear in the GitHub repository: `https://github.com/sweets9/DailyNews`

### 3. Manual Sync

If you need to manually trigger a sync:
- Go to **Settings** → **Repository** → **Mirror Settings**
- Click **Synchronize Now** next to the push mirror

## Benefits

- **Simpler script**: The Python script only needs to push to one remote (Gitea)
- **Automatic sync**: Gitea handles syncing to the second repository
- **Reliable**: Gitea's built-in mirroring is more robust than script-based pushing
- **Configurable**: You can adjust sync intervals and retry logic in Gitea

## Notes

- **GitHub Authentication**: GitHub requires a Personal Access Token (PAT) for HTTPS push mirrors. SSH push mirrors are not directly supported by Gitea, but you can use a `post-receive` hook as an alternative (see below).

- **HTTPS Recommended**: For GitHub, use HTTPS with a Personal Access Token. The URL format is: `https://github.com/sweets9/DailyNews.git`

- **Token Security**: Store your GitHub PAT securely. Never commit tokens to the repository. Use Gitea's mirror settings to store credentials securely.

## Alternative: Post-Receive Hook (for SSH or custom logic)

If you need SSH or custom push logic, you can use a Gitea post-receive hook:

1. Go to **Settings** → **Repository** → **Git Hooks**
2. Edit the `post-receive` hook and add:

```bash
#!/bin/bash
# Push to GitHub repository
git push github main || echo "Failed to push to GitHub"
```

3. Make sure the hook is executable and Gitea has SSH access configured for GitHub (requires SSH key added to GitHub account).

## Troubleshooting

- **Mirror not syncing**: 
  - Check the mirror status in Gitea settings and verify credentials
  - Ensure the GitHub repository exists and is accessible
  - Verify the GitHub Personal Access Token has not expired

- **Authentication errors**: 
  - Ensure the GitHub PAT has the `repo` scope
  - Verify the username matches the GitHub account that owns the token
  - Check that the repository URL is correct: `https://github.com/sweets9/DailyNews.git`

- **Sync delays**: 
  - Check the sync interval setting - you can set it to sync immediately on push
  - Use "Synchronize Now" button to force an immediate sync

- **GitHub repository not found**: 
  - Ensure the repository `sweets9/DailyNews` exists on GitHub
  - Verify the repository name and owner are correct
  - Check that the GitHub account has access to the repository

