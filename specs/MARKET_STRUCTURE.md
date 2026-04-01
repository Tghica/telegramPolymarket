# Bot Market Structure - Specs

## House Model: AMM Liquidity Market

### Overview
Bot = House (Market Maker)
Users = Traders betting against the house
No peer-to-peer trading - bot is the counterparty

### Market Example
- **Question:** "Will Bitcoin reach $100k by end of April?"
- **YES Price:** $0.65 (65% chance, bot's estimate)
- **NO Price:** $0.35 (35% chance)
- **Total:** Always $1.00

### User Betting Flow
1. User sees market: "Will BTC reach $100k?"
2. User thinks YES is likely
3. User bets $10 on YES at $0.65
4. User's potential winnings: $10 / $0.65 = $15.38 (if YES wins)
5. User's bet: $10
6. Bot took the other side (NO position)

### Bot Economics
- Bot collects fees on bets
- Bot profits if prices are accurate
- Bot loses if market outcome differs from price
- Bot can adjust prices to balance exposure

### Key Rules
- Prices set by bot algorithm (not by users)
- All users bet against bot, not against each other
- Bot always has liquidity (always accepts bets)
- No order books or matching needed
- Simpler than other Polymarket models

---
**Next Step:** Design the price calculation algorithm and betting logic
