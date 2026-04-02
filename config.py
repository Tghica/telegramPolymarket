"""
Configuration and constants for the bot
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_token_here")
LOG_LEVEL = logging.INFO

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///polymarket.db")

# Market Configuration
INITIAL_BALANCE = 1000  # Starting balance for new users
MIN_BET = 1
MAX_BET = 10000
MARKET_DURATION_DAYS = 7
MARKET_FEE_PERCENT = 2  # Creator fee percentage

# Message Templates
START_MESSAGE = """
Welcome to Polymarket Bot! 🎯

Predict outcomes and earn rewards.

Available commands:
/balance - Check your account balance
/markets - View active markets
/create - Create a new market
/bet - Place a bet
/help - Show all commands
"""

HELP_MESSAGE = """
📖 **Help Guide**

/markets - See all active prediction markets
/create - Create a new market
/bet - Place bet on a market
/history - View your betting history
/balance - Check your account balance
"""

# Odds calculation (you can modify this)
BASE_ODDS = 1.5
