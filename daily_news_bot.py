#!/usr/bin/env python3
"""
Daily Cyber Security News Bot
Fetches RSS feeds from multiple security news sources and generates a daily markdown file.
"""

import feedparser
from datetime import datetime, timedelta
import os
import sys
import re
import html
from git import Repo


# RSS Feed URLs
RSS_FEEDS = {
    "Bleeping Computer": "https://www.bleepingcomputer.com/feed/",
    "Security Week": "https://www.securityweek.com/feed/",
    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
    "The Register": "https://www.theregister.com/security/headlines.atom"
}


def fetch_articles_from_feeds(cutoff_time):
    """
    Fetch articles from all RSS feeds published after cutoff_time.
    
    Args:
        cutoff_time: datetime object representing the cutoff for article age
        
    Returns:
        List of article dictionaries with title, summary, link, published, and source
    """
    articles = []
    
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            print(f"Fetching from {source_name}...")
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries:
                # Parse published date
                published_time = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_time = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_time = datetime(*entry.updated_parsed[:6])
                
                # Filter articles from last 24 hours
                if published_time and published_time >= cutoff_time:
                    article = {
                        'title': entry.get('title', 'No Title'),
                        'summary': entry.get('summary', entry.get('description', 'No description available')),
                        'link': entry.get('link', ''),
                        'published': published_time,
                        'source': source_name
                    }
                    articles.append(article)
                    
        except Exception as e:
            print(f"Error fetching from {source_name}: {e}")
            continue
    
    # Sort articles by published time (newest first)
    articles.sort(key=lambda x: x['published'], reverse=True)
    return articles


def clean_html_tags(text):
    """Remove HTML tags from text using simple string manipulation."""
    # Remove HTML tags
    text = re.sub('<[^<]+?>', '', text)
    # Decode HTML entities
    text = html.unescape(text)
    return text.strip()


def generate_markdown_content(articles, date_str):
    """
    Generate markdown content for the daily news file.
    
    Args:
        articles: List of article dictionaries
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        String containing the markdown content
    """
    content = f"# Cyber Security News - {date_str}\n\n"
    
    if not articles:
        content += "*No new articles found in the last 24 hours.*\n"
        return content
    
    content += f"*{len(articles)} articles found*\n\n"
    content += "---\n\n"
    
    for article in articles:
        content += f"## **{article['title']}**\n\n"
        
        # Clean and format summary
        summary = clean_html_tags(article['summary'])
        # Limit summary length if too long
        if len(summary) > 500:
            summary = summary[:500] + "..."
        content += f"**Description:** {summary}\n\n"
        
        content += f"**Link:** [{article['link']}]({article['link']})\n\n"
        content += f"**Source:** {article['source']} | **Published:** {article['published'].strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        content += "---\n\n"
    
    return content


def create_daily_news_file(articles, repo_path):
    """
    Create the daily news markdown file.
    
    Args:
        articles: List of article dictionaries
        repo_path: Path to the repository root
        
    Returns:
        Tuple of (filename, filepath)
    """
    # Get current date
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    filename = f"{date_str}.md"
    
    # Create NewsArticles directory if it doesn't exist
    news_dir = os.path.join(repo_path, 'NewsArticles')
    os.makedirs(news_dir, exist_ok=True)
    
    # Generate file path
    filepath = os.path.join(news_dir, filename)
    
    # Generate markdown content
    content = generate_markdown_content(articles, date_str)
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created news file: {filepath}")
    return filename, filepath


def update_readme(filename, repo_path):
    """
    Update README.md to include link to the new daily news file.
    
    Args:
        filename: Name of the news file (e.g., '2025-12-11.md')
        repo_path: Path to the repository root
    """
    readme_path = os.path.join(repo_path, 'README.md')
    
    # Read current README content
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "# DailyNews\n\nA simple page to show the daily news\n"
    
    # Create the link to the new file
    date_str = filename.replace('.md', '')
    new_link = f"- [{date_str}](NewsArticles/{filename})\n"
    
    # Check if "Latest News" section exists
    if "## Latest News" in content:
        # Find the position right after "## Latest News" line
        lines = content.split('\n')
        new_lines = []
        inserted = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            if line.strip() == "## Latest News" and not inserted:
                # Add empty line if not present
                if i + 1 < len(lines) and lines[i + 1].strip() != '':
                    new_lines.append('')
                # Insert the new link at the top of the list
                new_lines.append(new_link.rstrip())
                inserted = True
        
        content = '\n'.join(new_lines)
    else:
        # Add Latest News section at the end
        if not content.endswith('\n'):
            content += '\n'
        content += '\n## Latest News\n\n'
        content += new_link
    
    # Write updated content
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated README.md with link to {filename}")


def git_commit_and_push(repo_path, date_str):
    """
    Git add, commit, and push changes.
    
    Args:
        repo_path: Path to the repository root
        date_str: Date string for commit message
    """
    try:
        repo = Repo(repo_path)
        
        # Add all changes
        repo.git.add('--all')
        
        # Check if there are changes to commit
        if repo.is_dirty() or repo.untracked_files:
            # Commit with date message
            commit_message = f"Daily news update - {date_str}"
            repo.index.commit(commit_message)
            print(f"Committed changes: {commit_message}")
            
            # Push to origin main (or HEAD if main doesn't exist)
            try:
                origin = repo.remote('origin')
                # Try to push to main branch
                try:
                    origin.push('main')
                    print("Pushed changes to origin main")
                except Exception:
                    # If main doesn't exist, try pushing HEAD to current branch
                    current_branch = repo.active_branch.name
                    origin.push(current_branch)
                    print(f"Pushed changes to origin {current_branch}")
            except Exception as push_error:
                print(f"Note: Could not push to origin: {push_error}")
                print("The changes have been committed locally.")
        else:
            print("No changes to commit")
            
    except Exception as e:
        print(f"Error during git operations: {e}")
        print("Note: Changes may still need to be committed and pushed manually")
        # Don't exit with error code, just continue
        return


def main():
    """Main function to run the daily news bot."""
    print("=" * 60)
    print("Daily Cyber Security News Bot")
    print("=" * 60)
    
    # Get repository path (assuming script is in repo root)
    repo_path = os.path.dirname(os.path.abspath(__file__))
    
    # Calculate cutoff time (24 hours ago)
    cutoff_time = datetime.now() - timedelta(hours=24)
    print(f"Fetching articles published after: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Fetch articles
    articles = fetch_articles_from_feeds(cutoff_time)
    print(f"\nFound {len(articles)} articles from the last 24 hours\n")
    
    # Create daily news file
    filename, filepath = create_daily_news_file(articles, repo_path)
    
    # Update README
    update_readme(filename, repo_path)
    
    # Git commit and push
    date_str = datetime.now().strftime('%Y-%m-%d')
    git_commit_and_push(repo_path, date_str)
    
    print("\n" + "=" * 60)
    print("Daily news bot completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
