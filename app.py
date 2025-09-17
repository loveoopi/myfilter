import os
import logging
import re
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

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
    
    # Simplified confirmation message
    update.message.reply_text(f'✅ Filter "{trigger}" added successfully!')

def stop_all(update, context):
    """Remove all filters"""
    global filters_dict
    if not filters_dict:
        update.message.reply_text('No filters to remove!')
        return
    
    count = len(filters_dict)
    filters_dict = {}
    update.message.reply_text(f'🗑️ Removed all {count} filters!')

def list_filters(update, context):
    """List all active filters"""
    if not filters_dict:
        update.message.reply_text('No active filters!')
        return
    
    filters_list = "\n".join([f"• {trigger}" for trigger in filters_dict.keys()])
    update.message.reply_text(f"Active filters:\n{filters_list}")

def handle_message(update, context):
    """Check messages for triggers and respond accordingly"""
    message_text = update.message.text.lower()
    
    # Check if any trigger word exists in the message (as a whole word or part of a word)
    for trigger in filters_dict:
        # Use regex to find the trigger word anywhere in the message
        if re.search(r'\b' + re.escape(trigger) + r'\b', message_text):
            update.message.reply_text(filters_dict[trigger])
            break  # Only respond to the first match

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Telegram Bot is running!')
    
    def log_message(self, format, *args):
        # Disable logging for HTTP requests
        return

def run_http_server():
    """Run a simple HTTP server to satisfy Heroku's requirements"""
    port = int(os.environ.get('PORT', 5000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"HTTP server running on port {port}")
    server.serve_forever()

def run_bot():
    """Run the Telegram bot"""
    # Your bot token (hardcoded as requested)
    token = "8323688902:AAHnf09xEGuaE7LvVgz2MdUbAGMZbnux3A8"
    
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
    # Start the HTTP server in a separate thread
    http_thread = threading.Thread(target=run_http_server)
    http_thread.daemon = True
    http_thread.start()
    
    # Run the bot in the main thread
    run_bot()
