"""
Database operations and SQLAlchemy ORM models
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, select
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import IntegrityError

from config import DATABASE_URL, INITIAL_BALANCE

logger = logging.getLogger(__name__)

# Create base class for ORM models
Base = declarative_base()


# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(Base):
    """User model for tracking account balances and profile"""
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    balance = Column(Float, default=INITIAL_BALANCE)
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'balance': self.balance,
            'created_at': self.created_at
        }


class Market(Base):
    """Market model for prediction markets"""
    __tablename__ = "markets"

    market_id = Column(String(255), primary_key=True)
    creator_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    question = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    ends_at = Column(DateTime)
    status = Column(String(50), default="ACTIVE")  # ACTIVE, RESOLVED
    outcome = Column(String(50), nullable=True)  # YES, NO, or None if not resolved
    yes_price = Column(Float, default=0.5)  # Price of YES bond
    no_price = Column(Float, default=0.5)   # Price of NO bond

    def to_dict(self):
        return {
            'market_id': self.market_id,
            'creator_id': self.creator_id,
            'question': self.question,
            'created_at': self.created_at,
            'ends_at': self.ends_at,
            'status': self.status,
            'outcome': self.outcome,
            'yes_price': self.yes_price,
            'no_price': self.no_price
        }


class Bet(Base):
    """Bet model for tracking user predictions"""
    __tablename__ = "bets"

    bet_id = Column(String(255), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    market_id = Column(String(255), ForeignKey('markets.market_id'), nullable=False)
    amount = Column(Float, nullable=False)
    prediction = Column(String(50), nullable=False)  # YES or NO
    placed_at = Column(DateTime, default=datetime.now)
    status = Column(String(50), default="PENDING")  # PENDING, WON, LOST

    def to_dict(self):
        return {
            'bet_id': self.bet_id,
            'user_id': self.user_id,
            'market_id': self.market_id,
            'amount': self.amount,
            'prediction': self.prediction,
            'placed_at': self.placed_at,
            'status': self.status
        }


# ============================================================================
# DATABASE CONNECTION SETUP
# ============================================================================

# Configure SQLite connection with proper pool settings
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite:"):
    engine_kwargs = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
        "echo": False  # Set to True for SQL debugging
    }

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def init_db():
    """Initialize database - create all tables"""
    try:
        Base.metadata.create_all(engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


# ============================================================================
# SYNCHRONOUS DATABASE OPERATIONS
# ============================================================================

def get_user(user_id: int, username: str = None) -> Optional[User]:
    """Get existing user or create new user with initial balance"""
    session = SessionLocal()
    try:
        # Check if user exists
        user = session.query(User).filter_by(user_id=user_id).first()

        if user:
            return user

        # Create new user if doesn't exist
        if username is None:
            username = f"user_{user_id}"

        new_user = User(
            user_id=user_id,
            username=username,
            balance=INITIAL_BALANCE,
            created_at=datetime.now()
        )
        session.add(new_user)
        session.commit()
        logger.info(f"Created new user: {user_id} ({username}) with balance {INITIAL_BALANCE}")
        return new_user

    except IntegrityError as e:
        session.rollback()
        logger.warning(f"Duplicate user creation attempt: {user_id}")
        # Retry once - other thread may have created it
        user = session.query(User).filter_by(user_id=user_id).first()
        return user
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating/getting user {user_id}: {e}")
        return None
    finally:
        session.close()


def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID without auto-creating"""
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        return user
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        return None
    finally:
        session.close()


def update_user_balance(user_id: int, amount: float) -> bool:
    """Update user balance by amount (positive or negative)"""
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            logger.warning(f"User {user_id} not found for balance update")
            return False

        new_balance = user.balance + amount
        if new_balance < 0:
            logger.warning(f"Insufficient balance for user {user_id}: {user.balance} + {amount}")
            return False

        user.balance = new_balance
        session.commit()
        logger.info(f"Updated user {user_id} balance to {new_balance}")
        return True

    except Exception as e:
        session.rollback()
        logger.error(f"Error updating user {user_id} balance: {e}")
        return False
    finally:
        session.close()


def get_active_markets() -> List[Market]:
    """Get all active markets ordered by creation time (newest first)"""
    session = SessionLocal()
    try:
        markets = session.query(Market)\
            .filter_by(status="ACTIVE")\
            .order_by(Market.created_at.desc())\
            .all()
        return markets
    except Exception as e:
        logger.error(f"Error fetching active markets: {e}")
        return []
    finally:
        session.close()


def get_market(market_id: str) -> Optional[Market]:
    """Get market by ID"""
    session = SessionLocal()
    try:
        market = session.query(Market).filter_by(market_id=market_id).first()
        return market
    except Exception as e:
        logger.error(f"Error fetching market {market_id}: {e}")
        return None
    finally:
        session.close()


def create_market_db(market_id: str, creator_id: int, question: str, duration_days: int = 7, yes_price: float = 0.5, no_price: float = 0.5) -> Optional[Market]:
    """Create new market with fixed YES/NO prices"""
    session = SessionLocal()
    try:
        # Verify creator exists
        creator = session.query(User).filter_by(user_id=creator_id).first()
        if not creator:
            logger.warning(f"Creator user {creator_id} not found")
            return None

        created_at = datetime.now()
        market = Market(
            market_id=market_id,
            creator_id=creator_id,
            question=question,
            created_at=created_at,
            ends_at=created_at + timedelta(days=duration_days),
            status="ACTIVE",
            yes_price=yes_price,
            no_price=no_price
        )
        session.add(market)
        session.commit()
        logger.info(f"Created market: {market_id} (YES: ${yes_price:.2f}, NO: ${no_price:.2f})")
        return market

    except Exception as e:
        session.rollback()
        logger.error(f"Error creating market: {e}")
        return None
    finally:
        session.close()


def place_bet(user_id: int, market_id: str, amount: float, prediction: str, bet_id: str = None) -> Optional[Bet]:
    """Place a bet - deducts amount from user balance and creates bet record"""
    if bet_id is None:
        bet_id = f"bet_{user_id}_{market_id}_{datetime.now().timestamp()}"

    session = SessionLocal()
    try:
        # Verify user exists and has balance
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            logger.warning(f"User {user_id} not found for betting")
            return None

        if user.balance < amount:
            logger.warning(f"User {user_id} insufficient balance: {user.balance} < {amount}")
            return None

        # Verify market exists
        market = session.query(Market).filter_by(market_id=market_id).first()
        if not market:
            logger.warning(f"Market {market_id} not found for betting")
            return None

        # Create bet and deduct balance
        bet = Bet(
            bet_id=bet_id,
            user_id=user_id,
            market_id=market_id,
            amount=amount,
            prediction=prediction,
            placed_at=datetime.now(),
            status="PENDING"
        )

        user.balance -= amount
        session.add(bet)
        session.commit()
        logger.info(f"Placed bet {bet_id}: user {user_id}, market {market_id}, amount {amount}")
        return bet

    except Exception as e:
        session.rollback()
        logger.error(f"Error placing bet: {e}")
        return None
    finally:
        session.close()


def get_user_bets(user_id: int) -> List[Bet]:
    """Get all bets for a user, ordered by most recent first"""
    session = SessionLocal()
    try:
        bets = session.query(Bet)\
            .filter_by(user_id=user_id)\
            .order_by(Bet.placed_at.desc())\
            .all()
        return bets
    except Exception as e:
        logger.error(f"Error fetching bets for user {user_id}: {e}")
        return []
    finally:
        session.close()


def resolve_market(market_id: str, outcome: str) -> bool:
    """Resolve a market with outcome and settle bets"""
    session = SessionLocal()
    try:
        market = session.query(Market).filter_by(market_id=market_id).first()
        if not market:
            logger.warning(f"Market {market_id} not found for resolution")
            return False

        market.status = "RESOLVED"
        market.outcome = outcome

        # TODO: Phase 4 - implement bet settlement logic
        # For now, just mark market as resolved

        session.commit()
        logger.info(f"Resolved market {market_id} with outcome {outcome}")
        return True

    except Exception as e:
        session.rollback()
        logger.error(f"Error resolving market {market_id}: {e}")
        return False
    finally:
        session.close()


# ============================================================================
# ASYNC WRAPPERS FOR TELEGRAM HANDLERS
# ============================================================================

async def async_get_user(user_id: int, username: str = None) -> Optional[User]:
    """Async wrapper for get_user"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: get_user(user_id, username))


async def async_get_user_by_id(user_id: int) -> Optional[User]:
    """Async wrapper for get_user_by_id"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: get_user_by_id(user_id))


async def async_update_user_balance(user_id: int, amount: float) -> bool:
    """Async wrapper for update_user_balance"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: update_user_balance(user_id, amount))


async def async_get_active_markets() -> List[Market]:
    """Async wrapper for get_active_markets"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_active_markets)


async def async_get_market(market_id: str) -> Optional[Market]:
    """Async wrapper for get_market"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: get_market(market_id))


async def async_place_bet(user_id: int, market_id: str, amount: float, prediction: str, bet_id: str = None) -> Optional[Bet]:
    """Async wrapper for place_bet"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: place_bet(user_id, market_id, amount, prediction, bet_id))


async def async_get_user_bets(user_id: int) -> List[Bet]:
    """Async wrapper for get_user_bets"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: get_user_bets(user_id))


async def async_resolve_market(market_id: str, outcome: str) -> bool:
    """Async wrapper for resolve_market"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: resolve_market(market_id, outcome))


async def async_create_market_db(market_id: str, creator_id: int, question: str, duration_days: int = 7, yes_price: float = 0.5, no_price: float = 0.5) -> Optional[Market]:
    """Async wrapper for create_market_db"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: create_market_db(market_id, creator_id, question, duration_days, yes_price, no_price))
