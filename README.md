# DailyNews

A simple page to show the daily news

## How to Use

This repository includes an automated daily cyber security news bot that fetches articles from multiple sources.

### Running the Bot

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the bot:
   ```bash
   python3 daily_news_bot.py
   ```

The bot will:
- Fetch RSS feeds from Bleeping Computer, Security Week, The Hacker News, and The Register
- Filter articles from the last 24 hours
- Generate a markdown file in `/NewsArticles/` with today's date
- Update this README with a link to the new file
- Automatically commit and push changes to the repository

## Latest News
