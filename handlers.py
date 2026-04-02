"""
Telegram message and callback handlers
"""

from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import START_MESSAGE, HELP_MESSAGE
from database import async_get_user, async_get_user_by_id, async_get_user_bets, async_get_active_markets, async_create_market_db
from utils import format_market_list, format_user_balance, format_user_history


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user_id = update.effective_user.id
    username = update.effective_user.username or f"user_{user_id}"

    # Create user if doesn't exist
    user = await async_get_user(user_id, username)

    await update.message.reply_text(START_MESSAGE)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    await update.message.reply_text(HELP_MESSAGE, parse_mode="HTML")


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /balance command - show user account balance"""
    user_id = update.effective_user.id
    user = await async_get_user_by_id(user_id)

    if not user:
        await update.message.reply_text(
            "❌ User not found. Please use /start first to create your account."
        )
        return

    message = format_user_balance(user)
    await update.message.reply_text(message, parse_mode="HTML")


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /history command - show user's betting history"""
    user_id = update.effective_user.id
    bets = await async_get_user_bets(user_id)

    message = format_user_history(bets)
    await update.message.reply_text(message, parse_mode="HTML")


async def markets_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /markets command - show active markets"""
    markets = await async_get_active_markets()

    market_list = format_market_list(markets)
    await update.message.reply_text(market_list, parse_mode="HTML")


async def create_market(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for market creation - /create command"""
    await update.message.reply_text(
        "📝 Enter market question:\n\nExample: Will BTC reach $100k by end of 2024?"
    )
    return 0  # MARKET_QUESTION state


async def market_question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle market question input"""
    question = update.message.text

    if len(question) > 500:
        await update.message.reply_text("❌ Question too long (max 500 characters). Try again:")
        return 0  # Stay in MARKET_QUESTION state

    context.user_data['question'] = question

    await update.message.reply_text(
        f"⏱ How many days until resolution?\n(Press Enter or reply with default: 7 days)"
    )
    return 1  # MARKET_DURATION state


async def market_duration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle market duration input"""
    text = update.message.text.strip()

    # Default to 7 if empty
    if not text:
        duration = 7
    else:
        try:
            duration = int(text)
            if duration < 1 or duration > 365:
                await update.message.reply_text("❌ Duration must be between 1 and 365 days. Try again:")
                return 1  # Stay in MARKET_DURATION state
        except ValueError:
            await update.message.reply_text("❌ Please enter a number. Try again:")
            return 1  # Stay in MARKET_DURATION state

    context.user_data['duration'] = duration

    # Show confirmation
    question = context.user_data['question']
    confirmation = f"""
✅ <b>Confirm Market Creation</b>

<b>Question:</b> {question}
<b>Duration:</b> {duration} days

Reply <code>yes</code> to create, or <code>no</code> to cancel.
"""
    await update.message.reply_text(confirmation, parse_mode="HTML")
    return 2  # MARKET_CONFIRM state


async def market_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle market confirmation"""
    response = update.message.text.strip().lower()

    if response in ['yes', 'ok', 'y', 'yep', 'create']:
        # Extract data
        question = context.user_data['question']
        duration = context.user_data['duration']
        user_id = update.effective_user.id

        # Generate unique market ID
        market_id = f"market_{user_id}_{int(datetime.now().timestamp())}"

        # Create market in database
        market = await async_create_market_db(
            market_id=market_id,
            creator_id=user_id,
            question=question,
            duration_days=duration
        )

        if market:
            success_msg = f"""
✅ <b>Market Created!</b>

<b>Question:</b> {market.question}
<b>Duration:</b> {duration} days
💰 <b>Prices:</b> YES: ${market.yes_price:.2f} | NO: ${market.no_price:.2f}
<b>Market ID:</b> <code>{market_id}</code>

Traders can now place bets! Use /markets to see it.
"""
            await update.message.reply_text(success_msg, parse_mode="HTML")
        else:
            await update.message.reply_text("❌ Failed to create market. Try again with /create")
    else:
        await update.message.reply_text("❌ Market creation cancelled.")

    # Clean up
    context.user_data.clear()
    return -1  # End conversation


async def cancel_market_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel market creation with /cancel command"""
    await update.message.reply_text("❌ Market creation cancelled.")
    context.user_data.clear()
    return -1  # End conversation


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
