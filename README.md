# Bitcoin Roller Coaster Twitter Bot

A Python-based bot that generates dynamic Bitcoin roller coaster GIFs and posts them to Twitter. The bot fetches real-time Bitcoin price data, historical trends, and Google Trends data to create an engaging visualization.

---

## Features

- Fetches real-time Bitcoin price using the [CoinGecko API](https://www.coingecko.com/en/api).
- Retrieves historical Bitcoin prices for different intervals (e.g., 1 hour, 1 week, 1 month).
- Pulls Google Trends data for Bitcoin searches over the last 12 months.
- Generates dynamic roller coaster GIFs that visualize price trends.
- Posts the GIFs along with relevant stats to Twitter using the Twitter API v2.
- 
![Capture](https://github.com/user-attachments/assets/04589949-6248-4c03-9ab0-7d3a0be0aa7e)

---
![bitcoin_roller_coaster](https://github.com/user-attachments/assets/c037ef35-a7c3-4816-8b42-d539ee4a99b1)


## Prerequisites

### 1. APIs and Credentials
- Twitter Developer Account for API access.
  - Obtain API keys and access tokens for both v1.1 and v2.
- [CoinGecko API](https://www.coingecko.com/en/api) (no authentication required).
- [Google Trends API](https://pypi.org/project/pytrends/).

### 2. Python Dependencies
Install the following Python packages:
- `tweepy` for Twitter API integration
- `requests` for API calls
- `pytrends` for Google Trends data
- `Pillow` for image and GIF manipulation

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/bitcoin-roller-coaster-bot.git
   cd bitcoin-roller-coaster-bot

## Add secrets in secrets_original.py file
consumer_key = "YOUR_TWITTER_CONSUMER_KEY"
consumer_secret = "YOUR_TWITTER_CONSUMER_SECRET"
access_token = "YOUR_TWITTER_ACCESS_TOKEN"
access_token_secret = "YOUR_TWITTER_ACCESS_TOKEN_SECRET"
bearer_token = "YOUR_TWITTER_BEARER_TOKEN"
