# HOTEL Telegram Bot

This project is a Telegram bot designed to manage hotel room bookings and fitness club subscriptions. The bot offers features for both users (booking rooms and subscriptions) and managers (managing statuses, prices, and notifications).

## Key Features

### For Users:
- View and book hotel rooms with category selection (Standard, Junior Suite, Suite).
- Purchase fitness club subscriptions with type and duration options.
- Access hotel information (contacts, FAQ).
- Receive notifications about subscription status (activation, expiration).

### For Managers:
- Manage room bookings (`/book`, `/unbook`, `/status`, `/price`).
- Manage subscriptions (`/accept`, `/active`, `/endabon`, `/deleteabon`).
- View subscription lists by status (`/waitbooks`, `/notactivebooks`, `/activebooks`, `/pastbooks`).
- Send bulk messages to users (`/allmessage`).
- Automatically update statuses and remove outdated records.

## Project Structure

- **`config.py`**: Constants, room and category data, environment variable loading.
- **`handlers.py`**: Handlers for room booking and core bot functionality.
- **`handlers2.py`**: Handlers for managing fitness club subscriptions.
- **`main.py`**: Main file to launch the bot and configure handlers.
- **`.env`**: File with environment variables (bot token, supergroup ID).
- **`create_db.py`**: Script to create the SQLite database for storing subscriptions.
- **`abonements.db`**: SQLite database (created automatically by `create_db.py`).

## Requirements

- Python 3.8+
- Libraries:
  - `python-telegram-bot==20.6`
  - `python-dotenv`
  - `sqlite3` (built into Python)
  - `python-dateutil`

Install dependencies with:
```bash
pip install -r requirements.txt
