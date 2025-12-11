#!/usr/bin/env python3
"""
Daily Cyber Security News Fetcher
Fetches latest cyber security news using gemini-cli and saves to newsitems directory.
"""

import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path

# Get the script directory (repo root)
SCRIPT_DIR = Path(__file__).parent.absolute()
NEWS_DIR = SCRIPT_DIR / "newsitems"
README_FILE = SCRIPT_DIR / "README.md"

# Prompt template
PROMPT = """Role: Expert in Security Research and News Writing

Task: Search for the latest cyber security news specifically focused on enterprise data security, vulnerability awareness, and general cyber security updates.

Sources: Restrict your search to Bleeping Computer, Security Week, The Hacker News, The Register, Dark Reading, and Risky Biz.

Timeframe:

If today is Monday: Search for news from the last 72 hours.

If today is Tuesday through Sunday: Search for news from the last 24 hours.

Output Instructions:

Consolidate: Combine similar stories from different sources into single news items to avoid duplicates.

Sort: Order results from most serious (critical zero-day vulnerabilities, active exploits, major enterprise breaches) to least serious.

Style: Use simple, clear language suitable for a general audience. Explain technical jargon. Focus on the business impact and risk.

Format per Item: {Title in bold} {Description} Why it Matters: {Quick explanation of the risk and business impact} Link: {URL}"""


def get_timeframe():
    """Determine timeframe based on day of week."""
    today = datetime.now()
    day_of_week = today.weekday()  # 0 = Monday, 6 = Sunday
    
    if day_of_week == 0:  # Monday
        return "72 hours"
    else:  # Tuesday through Sunday
        return "24 hours"


def run_gemini_cli():
    """Run gemini-cli with the prompt and return output."""
    try:
        # Use npx to run gemini-cli
        result = subprocess.run(
            ["npx", "@google/gemini-cli", "--prompt", PROMPT],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            print(f"Error running gemini-cli: {result.stderr}", file=sys.stderr)
            return None
        
        return result.stdout
    except subprocess.TimeoutExpired:
        print("Error: gemini-cli timed out after 5 minutes", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error running gemini-cli: {e}", file=sys.stderr)
        return None


def save_news_item(content):
    """Save news content to a timestamped file."""
    NEWS_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M")
    filename = f"CyberNews-{timestamp}.md"
    filepath = NEWS_DIR / filename
    
    # Add header to the content
    header = f"# Cyber Security News - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    header += f"*Timeframe: Last {get_timeframe()}*\n\n---\n\n"
    
    full_content = header + content
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    return filename, filepath


def update_readme(filename):
    """Add link to news item in README.md."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    link_text = f"- [{timestamp}](newsitems/{filename})"
    
    # Read existing README or create new one
    if README_FILE.exists():
        with open(README_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "# Daily News\n\n## Cyber Security News\n\n"
    
    # Check if link already exists (for 10am update scenario)
    if link_text in content:
        print(f"Link already exists in README, skipping update")
        return False
    
    # Add link at the top of the Cyber Security News section
    if "## Cyber Security News" in content:
        # Insert after the header
        lines = content.split('\n')
        insert_index = None
        for i, line in enumerate(lines):
            if line.strip() == "## Cyber Security News":
                insert_index = i + 1
                break
        
        if insert_index:
            lines.insert(insert_index, link_text)
            content = '\n'.join(lines)
    else:
        # Add section if it doesn't exist
        if not content.endswith('\n'):
            content += '\n'
        content += "## Cyber Security News\n\n" + link_text + "\n"
    
    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def load_env_file():
    """Load .env file into environment variables."""
    env_file = SCRIPT_DIR / ".env"
    
    if not env_file.exists():
        return {}
    
    env_vars = {}
    
    # Try to use python-dotenv if available
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        # Also read into dict for use in this function
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except ImportError:
        # If dotenv not available, manually load .env file
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
                    # Also set in environment
                    os.environ[key.strip()] = value.strip()
    
    return env_vars


def configure_git_remotes():
    """Configure git remotes using credentials from .env file."""
    env_vars = load_env_file()
    
    if not env_vars:
        print("Warning: .env file not found or empty. Git remotes may not be configured.", file=sys.stderr)
        return
    
    # Configure origin (Gitea) remote
    gitea_url = env_vars.get('GITEA_URL', '')
    gitea_username = env_vars.get('GITEA_USERNAME', '')
    gitea_password = env_vars.get('GITEA_PASSWORD', '')
    use_ssh = env_vars.get('GITEA_USE_SSH', 'false').lower() == 'true'
    
    if gitea_url and not use_ssh and gitea_username and gitea_password:
        # Update origin URL with credentials
        origin_url = gitea_url.replace('https://', f'https://{gitea_username}:{gitea_password}@')
        subprocess.run(
            ["git", "remote", "set-url", "origin", origin_url],
            capture_output=True,
            cwd=SCRIPT_DIR,
            timeout=10
        )
    
    # Configure github remote
    github_url = env_vars.get('GITHUB_URL', 'https://github.com/sweets9/DailyNews.git')
    github_username = env_vars.get('GITHUB_USERNAME', 'sweets9')
    github_token = env_vars.get('GITHUB_TOKEN', '')
    use_ssh_github = env_vars.get('GITHUB_USE_SSH', 'false').lower() == 'true'
    
    # Check if github remote exists
    result = subprocess.run(
        ["git", "remote", "show", "github"],
        capture_output=True,
        text=True,
        cwd=SCRIPT_DIR,
        timeout=10
    )
    
    if result.returncode != 0:
        # Add github remote if it doesn't exist
        if not use_ssh_github and github_token:
            github_url_with_auth = github_url.replace('https://', f'https://{github_username}:{github_token}@')
        else:
            github_url_with_auth = github_url
        
        subprocess.run(
            ["git", "remote", "add", "github", github_url_with_auth],
            capture_output=True,
            cwd=SCRIPT_DIR,
            timeout=10
        )
    elif not use_ssh_github and github_token:
        # Update existing github remote with credentials
        github_url_with_auth = github_url.replace('https://', f'https://{github_username}:{github_token}@')
        subprocess.run(
            ["git", "remote", "set-url", "github", github_url_with_auth],
            capture_output=True,
            cwd=SCRIPT_DIR,
            timeout=10
        )


def git_commit_and_push(filename):
    """Commit changes and push to both remotes: origin (Gitea) and github (GitHub)."""
    try:
        # Configure remotes from .env file
        configure_git_remotes()
        # Check if we're in a git repository
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
            timeout=10
        )
        
        if result.returncode != 0:
            print("Warning: Not a git repository, skipping git operations", file=sys.stderr)
            return False
        
        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
            timeout=10
        )
        
        if not result.stdout.strip():
            print("No changes to commit")
            return True
        
        # Add all changes
        result = subprocess.run(
            ["git", "add", "newsitems/", "README.md"],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"Error adding files to git: {result.stderr}", file=sys.stderr)
            return False
        
        # Commit changes
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        commit_message = f"Add cyber security news update - {timestamp}"
        
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"Error committing changes: {result.stderr}", file=sys.stderr)
            return False
        
        # Push to origin (Gitea)
        result = subprocess.run(
            ["git", "push", "origin", "main"],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"Warning: Failed to push to origin (Gitea): {result.stderr}", file=sys.stderr)
            # Continue to try GitHub push even if Gitea fails
        else:
            print("Pushed changes to Gitea (origin)")
        
        # Push to github remote (if configured)
        result = subprocess.run(
            ["git", "remote", "show", "github"],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
            timeout=10
        )
        
        if result.returncode == 0:
            # GitHub remote exists, push to it
            result = subprocess.run(
                ["git", "push", "github", "main"],
                capture_output=True,
                text=True,
                cwd=SCRIPT_DIR,
                timeout=60
            )
            
            if result.returncode != 0:
                print(f"Warning: Failed to push to GitHub: {result.stderr}", file=sys.stderr)
            else:
                print("Pushed changes to GitHub (github remote)")
        else:
            print("Note: GitHub remote not configured. Add it with: git remote add github https://github.com/sweets9/DailyNews.git")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("Error: Git operation timed out", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error in git operations: {e}", file=sys.stderr)
        return False


def main():
    """Main execution function."""
    print(f"Fetching cyber security news (timeframe: last {get_timeframe()})...")
    
    # Run gemini-cli
    output = run_gemini_cli()
    
    if not output or not output.strip():
        print("No output from gemini-cli", file=sys.stderr)
        sys.exit(1)
    
    # Save to file
    filename, filepath = save_news_item(output)
    print(f"Saved news to: {filepath}")
    
    # Update README
    readme_updated = update_readme(filename)
    if readme_updated:
        print(f"Updated README.md with link to {filename}")
    
    # Commit and push changes to git
    print("Committing and pushing changes to git...")
    git_commit_and_push(filename)
    
    print("Done!")


if __name__ == "__main__":
    main()

