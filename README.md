# Telegram Polymarket Bot

A Telegram bot that functions as a prediction market platform (like Polymarket), allowing users to create markets, place bets, and track outcomes.

## Features

- **Market Creation**: Users can create prediction markets
- **Betting**: Place bets on market outcomes
- **Market Management**: Track and resolve markets
- **User Profiles**: Track user balances and bet history
- **Real-time Updates**: Live market status and odds

## Project Structure

```
telegramBot/
├── bot.py                 # Main bot entry point
├── config.py             # Configuration and constants
├── handlers.py           # Telegram message and callback handlers
├── database.py           # Database operations and models
├── utils.py              # Utility functions (math, formatting, etc)
├── requirements.txt      # Python dependencies
├── specs/                # Project specifications and requirements
│   └── requirements.txt   # Detailed feature specifications
└── README.md            # This file
```

## Installation

1. Clone/download this project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with:
```
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=your_database_url
```

## Usage

```bash
python bot.py
```

## Configuration

Edit `config.py` to customize:
- Bot command prefixes
- Market parameters (fees, limits)
- Database settings
- Message templates

## Development

Use the `specs/requirements.txt` file to document:
- Feature requirements
- API endpoints needed
- Database schema
- User workflows
- Technical specifications

## Dependencies

See `requirements.txt` for all Python packages required.

## License

MIT
