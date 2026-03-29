"""
Database operations and models
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from config import DATABASE_URL, INITIAL_BALANCE

# TODO: Implement database connection (SQLAlchemy, MongoDB, etc)
# This is a template structure


class User:
    """User model"""

    def __init__(self, user_id: int, username: str, balance: float = INITIAL_BALANCE):
        self.user_id = user_id
        self.username = username
        self.balance = balance
        self.created_at = datetime.now()

    def to_dict(self) -> Dict:
        return {
            'user_id': self.user_id,
            'username': self.username,
            'balance': self.balance,
            'created_at': self.created_at
        }


class Market:
    """Market model"""

    def __init__(self, market_id: str, creator_id: int, question: str, duration_days: int = 7):
        self.market_id = market_id
        self.creator_id = creator_id
        self.question = question
        self.created_at = datetime.now()
        self.ends_at = self.created_at + timedelta(days=duration_days)
        self.status = "ACTIVE"  # ACTIVE, RESOLVED
        self.outcome = None

    def to_dict(self) -> Dict:
        return {
            'market_id': self.market_id,
            'creator_id': self.creator_id,
            'question': self.question,
            'created_at': self.created_at,
            'ends_at': self.ends_at,
            'status': self.status,
            'outcome': self.outcome
        }


class Bet:
    """Bet model"""

    def __init__(self, bet_id: str, user_id: int, market_id: str, amount: float, prediction: str):
        self.bet_id = bet_id
        self.user_id = user_id
        self.market_id = market_id
        self.amount = amount
        self.prediction = prediction  # YES or NO
        self.placed_at = datetime.now()
        self.status = "PENDING"  # PENDING, WON, LOST

    def to_dict(self) -> Dict:
        return {
            'bet_id': self.bet_id,
            'user_id': self.user_id,
            'market_id': self.market_id,
            'amount': self.amount,
            'prediction': self.prediction,
            'placed_at': self.placed_at,
            'status': self.status
        }


# Database Functions

def get_user(user_id: int) -> Optional[User]:
    """Get or create user"""
    # TODO: Implement database query
    pass


def create_market(creator_id: int, question: str) -> Market:
    """Create new market"""
    # TODO: Implement database insert
    pass


def get_market(market_id: str) -> Optional[Market]:
    """Get market by ID"""
    # TODO: Implement database query
    pass


def get_active_markets() -> List[Market]:
    """Get all active markets"""
    # TODO: Implement database query
    pass


def place_bet(user_id: int, market_id: str, amount: float, prediction: str) -> Bet:
    """Place a bet on a market"""
    # TODO: Implement database insert and balance update
    pass


def get_user_bets(user_id: int) -> List[Bet]:
    """Get all bets for a user"""
    # TODO: Implement database query
    pass


def resolve_market(market_id: str, outcome: str) -> None:
    """Resolve a market and settle bets"""
    # TODO: Implement market resolution logic
    pass
