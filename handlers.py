"""
Telegram message and callback handlers
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import START_MESSAGE, HELP_MESSAGE
from database import get_user, create_market as db_create_market
from utils import format_market_list


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user_id = update.effective_user.id

    # Create user if doesn't exist
    get_user(user_id)

    await update.message.reply_text(START_MESSAGE)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    await update.message.reply_text(HELP_MESSAGE, parse_mode="HTML")


async def markets_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /markets command - show active markets"""
    # TODO: Fetch active markets from database
    markets = []

    if not markets:
        await update.message.reply_text("No active markets yet. Create one with /create")
        return

    market_list = format_market_list(markets)
    await update.message.reply_text(market_list, parse_mode="HTML")


async def create_market(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /create command - initiate market creation"""
    user_id = update.effective_user.id

    await update.message.reply_text(
        "📝 Enter market question:\n\nExample: Will BTC reach $100k by end of 2024?"
    )

    # TODO: Set up conversation handler for market creation flow


async def place_bet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /bet command - place a bet"""
    user_id = update.effective_user.id

    await update.message.reply_text(
        "🎲 Select a market to bet on:\n\nUse /markets to see available markets"
    )

    # TODO: Set up conversation handler for betting flow


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback query for inline buttons"""
    query = update.callback_query
    await query.answer()

    # TODO: Route callbacks based on data
