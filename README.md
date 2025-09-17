# Telegram Filter Bot

A Telegram bot that allows you to create custom text filters with automatic responses.

## Features

- `/start` - Welcome message
- `/filterr [trigger]` - Add a new filter (reply to a message with this command)
- `/stopalll` - Remove all filters
- `/list` - List all active filters
- Auto-response to trigger words

## Deployment to Heroku

1. Fork this repository to your GitHub account
2. Create a new app on [Heroku](https://heroku.com)
3. Connect your GitHub repository to Heroku
4. Enable automatic deployments
5. Deploy the app

## Important Notes

1. Replace "your-telegram-filter-bot" in app.py with your actual Heroku app name
2. The bot uses in-memory storage, so filters will be lost when the app restarts
3. Make sure to set your bot's webhook in the BotFather on Telegram
