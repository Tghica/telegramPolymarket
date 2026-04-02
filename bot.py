"""
Main Telegram bot entry point
Initialize and run the bot
"""

import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, filters

from config import BOT_TOKEN, LOG_LEVEL
from handlers import (
    start, help_command, markets_command, create_market, place_bet, callback_handler,
    balance_command, history_command, market_question_handler, market_duration_handler,
    market_confirm_handler, cancel_market_creation
)
from database import init_db

# Conversation handler states
MARKET_QUESTION = 0
MARKET_DURATION = 1
MARKET_CONFIRM = 2

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
    application.add_handler(CommandHandler("bet", place_bet))

    # Market creation conversation handler
    market_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("create", create_market)],
        states={
            MARKET_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, market_question_handler)],
            MARKET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, market_duration_handler)],
            MARKET_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, market_confirm_handler)]
        },
        fallbacks=[CommandHandler("cancel", cancel_market_creation)]
    )
    application.add_handler(market_conv_handler)

    # Callback handler for buttons
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Start bot
    logger.info("Bot started")
    application.run_polling()


if __name__ == '__main__':
    main()
