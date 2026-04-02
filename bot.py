"""
Main Telegram bot entry point
Initialize and run the bot
"""

import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config import BOT_TOKEN, LOG_LEVEL
from handlers import start, help_command, markets_command, create_market, place_bet, callback_handler, balance_command, history_command
from database import init_db

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=LOG_LEVEL
)
logger = logging.getLogger(__name__)


def main():
    """Start the bot"""

    # Initialize database
    init_db()

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("markets", markets_command))
    application.add_handler(CommandHandler("create", create_market))
    application.add_handler(CommandHandler("bet", place_bet))

    # Callback handler for buttons
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Start bot
    logger.info("Bot started")
    application.run_polling()


if __name__ == '__main__':
    main()
