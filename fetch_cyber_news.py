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
    """Configure git remotes and store credentials securely using git credential helper."""
    env_vars = load_env_file()
    
    if not env_vars:
        print("Warning: .env file not found or empty. Git remotes may not be configured.", file=sys.stderr)
        return
    
    # Ensure credential helper is configured
    subprocess.run(
        ["git", "config", "--global", "credential.helper", "store"],
        capture_output=True,
        cwd=SCRIPT_DIR,
        timeout=10
    )
    
    # Get credential store path
    home_dir = os.path.expanduser("~")
    credential_store = os.path.join(home_dir, ".git-credentials")
    
    # Configure origin (Gitea) remote WITHOUT credentials in URL
    gitea_url = env_vars.get('GITEA_URL', 'https://git.sweet6.net/Sweet6/DailyNews')
    gitea_username = env_vars.get('GITEA_USERNAME', '')
    gitea_password = env_vars.get('GITEA_PASSWORD', '')
    use_ssh = env_vars.get('GITEA_USE_SSH', 'false').lower() == 'true'
    
    # Set remote URL without credentials
    if not use_ssh:
        # Remove credentials from URL if present
        clean_url = gitea_url.replace('https://', '').split('@')[-1]
        if not clean_url.startswith('http'):
            clean_url = f'https://{clean_url}'
        
        subprocess.run(
            ["git", "remote", "set-url", "origin", clean_url],
            capture_output=True,
            cwd=SCRIPT_DIR,
            timeout=10
        )
        
        # Store credentials securely in credential store
        if gitea_username and gitea_password:
            gitea_cred = f"https://{gitea_username}:{gitea_password}@git.sweet6.net"
            # Read existing credentials
            existing_creds = set()
            if os.path.exists(credential_store):
                with open(credential_store, 'r') as f:
                    existing_creds = set(line.strip() for line in f if line.strip())
            
            # Add or update Gitea credential
            existing_creds = {c for c in existing_creds if 'git.sweet6.net' not in c}
            existing_creds.add(gitea_cred)
            
            # Write back to credential store
            os.makedirs(os.path.dirname(credential_store), exist_ok=True)
            with open(credential_store, 'w') as f:
                for cred in existing_creds:
                    f.write(cred + '\n')
            
            # Set proper permissions
            os.chmod(credential_store, 0o600)
    
    # Configure github remote WITHOUT credentials in URL
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
    
    # Set remote URL without credentials
    if not use_ssh_github:
        clean_github_url = github_url.replace('https://', '').split('@')[-1]
        if not clean_github_url.startswith('http'):
            clean_github_url = f'https://{clean_github_url}'
        
        if result.returncode != 0:
            # Add github remote if it doesn't exist
            subprocess.run(
                ["git", "remote", "add", "github", clean_github_url],
                capture_output=True,
                cwd=SCRIPT_DIR,
                timeout=10
            )
        else:
            # Update existing remote
            subprocess.run(
                ["git", "remote", "set-url", "github", clean_github_url],
                capture_output=True,
                cwd=SCRIPT_DIR,
                timeout=10
            )
        
        # Store GitHub credentials securely
        if github_token:
            github_cred = f"https://{github_username}:{github_token}@github.com"
            # Read existing credentials
            existing_creds = set()
            if os.path.exists(credential_store):
                with open(credential_store, 'r') as f:
                    existing_creds = set(line.strip() for line in f if line.strip())
            
            # Add or update GitHub credential
            existing_creds = {c for c in existing_creds if '@github.com' not in c}
            existing_creds.add(github_cred)
            
            # Write back to credential store
            os.makedirs(os.path.dirname(credential_store), exist_ok=True)
            with open(credential_store, 'w') as f:
                for cred in existing_creds:
                    f.write(cred + '\n')
            
            # Set proper permissions
            os.chmod(credential_store, 0o600)


def git_commit_and_push(filename):
    """Commit changes and push to remotes:
    - Gitea (origin): All files including scripts
    - GitHub (github): Only README.md and newsitems/ (scripts excluded)
    """
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
        
        # Set up branch tracking if not already set
        result = subprocess.run(
            ["git", "branch", "--set-upstream-to=origin/main", "main"],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
            timeout=10
        )
        # Ignore errors (branch might already be tracking)
        
        # Pull latest changes before committing to avoid conflicts
        print("Pulling latest changes from repository...")
        result = subprocess.run(
            ["git", "pull", "origin", "main", "--no-edit", "--no-rebase"],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
            timeout=60
        )
        
        if result.returncode != 0:
            # If pull fails, try fetch and merge separately
            print("Pull failed, trying fetch and merge...")
            subprocess.run(
                ["git", "fetch", "origin", "main"],
                capture_output=True,
                text=True,
                cwd=SCRIPT_DIR,
                timeout=60
            )
            result = subprocess.run(
                ["git", "merge", "origin/main", "--no-edit"],
                capture_output=True,
                text=True,
                cwd=SCRIPT_DIR,
                timeout=60
            )
            if result.returncode != 0:
                print(f"Warning: Failed to merge remote changes: {result.stderr}", file=sys.stderr)
                print("Attempting to continue with commit...")
        
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
            # Check if there's nothing to commit
            if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
                print("No changes to commit (may have been merged during pull)")
            else:
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
        
        # Push to github remote (if configured) - only README.md and newsitems/
        result = subprocess.run(
            ["git", "remote", "show", "github"],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
            timeout=10
        )
        
        if result.returncode == 0:
            # GitHub remote exists - push only README.md and newsitems/
            # Use a filtered approach: create a temporary branch with only these files
            try:
                # Get current branch name
                branch_result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    capture_output=True,
                    text=True,
                    cwd=SCRIPT_DIR,
                    timeout=10
                )
                current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "main"
                
                # Create a temporary orphan branch for GitHub (only content, no history)
                github_branch = "github-publish"
                
                # Check if branch exists, delete if it does
                subprocess.run(
                    ["git", "branch", "-D", github_branch],
                    capture_output=True,
                    cwd=SCRIPT_DIR,
                    timeout=10
                )
                
                # Create orphan branch
                subprocess.run(
                    ["git", "checkout", "--orphan", github_branch],
                    capture_output=True,
                    cwd=SCRIPT_DIR,
                    timeout=10
                )
                
                # Remove all files from staging
                subprocess.run(
                    ["git", "rm", "-rf", "--cached", "."],
                    capture_output=True,
                    cwd=SCRIPT_DIR,
                    timeout=10
                )
                
                # Add only README.md and newsitems/
                subprocess.run(
                    ["git", "add", "README.md", "newsitems/"],
                    capture_output=True,
                    cwd=SCRIPT_DIR,
                    timeout=10
                )
                
                # Commit
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                commit_msg = f"Update cyber security news - {timestamp}"
                subprocess.run(
                    ["git", "commit", "-m", commit_msg],
                    capture_output=True,
                    cwd=SCRIPT_DIR,
                    timeout=10
                )
                
                # Push to GitHub
                result = subprocess.run(
                    ["git", "push", "github", f"{github_branch}:main", "--force"],
                    capture_output=True,
                    text=True,
                    cwd=SCRIPT_DIR,
                    timeout=60
                )
                
                # Switch back to original branch
                subprocess.run(
                    ["git", "checkout", current_branch],
                    capture_output=True,
                    cwd=SCRIPT_DIR,
                    timeout=10
                )
                
                # Clean up temporary branch
                subprocess.run(
                    ["git", "branch", "-D", github_branch],
                    capture_output=True,
                    cwd=SCRIPT_DIR,
                    timeout=10
                )
                
                if result.returncode != 0:
                    print(f"Warning: Failed to push to GitHub: {result.stderr}", file=sys.stderr)
                else:
                    print("Pushed README.md and newsitems/ to GitHub (scripts excluded)")
                    
            except Exception as e:
                print(f"Warning: Error pushing to GitHub: {e}", file=sys.stderr)
                # Try to get back to original branch
                try:
                    subprocess.run(
                        ["git", "checkout", current_branch],
                        capture_output=True,
                        cwd=SCRIPT_DIR,
                        timeout=10
                    )
                except:
                    pass
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

