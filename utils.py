"""
Utility functions for the bot
"""

from typing import List, Dict
from datetime import datetime


def format_market_list(markets: List) -> str:
    """Format market list for display"""
    if not markets:
        return "No markets available"

    output = "📊 <b>Active Markets</b>\n\n"

    for i, market in enumerate(markets, 1):
        # TODO: Implement based on your Market model structure
        output += f"{i}. Market question\n"
        output += f"   Status: Active | Ends: Date\n\n"

    return output


def format_odds(yes_amount: float, no_amount: float) -> Dict[str, float]:
    """Calculate odds based on amounts bet on each side"""
    total = yes_amount + no_amount
    if total == 0:
        return {'yes': 1.0, 'no': 1.0}

    yes_odds = total / yes_amount if yes_amount > 0 else 0
    no_odds = total / no_amount if no_amount > 0 else 0

    return {'yes': round(yes_odds, 2), 'no': round(no_odds, 2)}


def calculate_winnings(bet_amount: float, odds: float) -> float:
    """Calculate potential winnings"""
    return round(bet_amount * odds, 2)


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"


def time_remaining(end_time: datetime) -> str:
    """Get human-readable time remaining"""
    remaining = end_time - datetime.now()
    days = remaining.days
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60

    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def validate_bet_amount(amount: float, user_balance: float, min_bet: float, max_bet: float) -> tuple[bool, str]:
    """Validate if bet amount is valid"""
    if amount < min_bet:
        return False, f"Minimum bet is {format_currency(min_bet)}"
    if amount > max_bet:
        return False, f"Maximum bet is {format_currency(max_bet)}"
    if amount > user_balance:
        return False, f"Insufficient balance. You have {format_currency(user_balance)}"

    return True, "Valid"
