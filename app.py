import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Dictionary to store filters {trigger_word: response}
filters_dict = {}

# Command handlers
def start(update, context):
    update.message.reply_text('Hi! I am your filter bot. Use /filterr to add new filters.')

def add_filter(update, context):
    """Add a new filter when user replies to a message with /filterr trigger"""
    reply = update.message.reply_to_message
    if not reply:
        update.message.reply_text('You need to reply to a message to set a filter!')
        return
    
    try:
        trigger = context.args[0].lower()
    except IndexError:
        update.message.reply_text('Please provide a trigger word!\nUsage: /filterr trigger_word')
        return
    
    response = reply.text
    filters_dict[trigger] = response
    update.message.reply_text(f'Filter added!\nTrigger: {trigger}\nResponse: {response}')

def stop_all(update, context):
    """Remove all filters"""
    global filters_dict
    if not filters_dict:
        update.message.reply_text('No filters to remove!')
        return
    
    count = len(filters_dict)
    filters_dict = {}
    update.message.reply_text(f'Removed all {count} filters!')

def list_filters(update, context):
    """List all active filters"""
    if not filters_dict:
        update.message.reply_text('No active filters!')
        return
    
    filters_list = "\n".join([f"• {trigger}: {response}" for trigger, response in filters_dict.items()])
    update.message.reply_text(f"Active filters:\n{filters_list}")

def handle_message(update, context):
    """Check messages for triggers and respond accordingly"""
    message_text = update.message.text.lower()
    if message_text in filters_dict:
        update.message.reply_text(filters_dict[message_text])

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    # Your bot token
    token = "8323688902:AAHPzoJ4DIFd2MnZgcOB_cUAf1BhWzpNHrs"
    
    # Create Updater
    updater = Updater(token, use_context=True)

    # Get dispatcher to register handlers
    dp = updater.dispatcher

    # Add command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("filterr", add_filter))
    dp.add_handler(CommandHandler("stopalll", stop_all))
    dp.add_handler(CommandHandler("list", list_filters))

    # Add message handler
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Log all errors
    dp.add_error_handler(error)

    # Start the Bot
    print("Bot started...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
