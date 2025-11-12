import os
import logging
import re
import threading
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update
from http.server import BaseHTTPRequestHandler, HTTPServer
import signal
import sys

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Dictionary to store filters {trigger_word: response}
filters_dict = {}

# Authorized user ID
AUTHORIZED_USER_ID = 7598086737

def is_authorized_user(update, context):
    """Check if the user is the authorized user"""
    user_id = update.message.from_user.id
    return user_id == AUTHORIZED_USER_ID

# Command handlers (keep your existing handlers the same)
def start(update, context):
    if not is_authorized_user(update, context):
        update.message.reply_text("🚫 You are not authorized to use this command!")
        return
    update.message.reply_text('Hi! I am your filter bot. Use /filterr to add new filters.')

def add_filter(update, context):
    if not is_authorized_user(update, context):
        update.message.reply_text("🚫 You are not authorized to use this command!")
        return
    
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
    update.message.reply_text(f'✅ Filter "{trigger}" added successfully!')

def stop_all(update, context):
    if not is_authorized_user(update, context):
        update.message.reply_text("🚫 You are not authorized to use this command!")
        return
    
    global filters_dict
    if not filters_dict:
        update.message.reply_text('No filters to remove!')
        return
    
    count = len(filters_dict)
    filters_dict = {}
    update.message.reply_text(f'🗑️ Removed all {count} filters!')

def list_filters(update, context):
    if not is_authorized_user(update, context):
        update.message.reply_text("🚫 You are not authorized to use this command!")
        return
    
    if not filters_dict:
        update.message.reply_text('No active filters!')
        return
    
    filters_list = "\n".join([f"• {trigger}" for trigger in filters_dict.keys()])
    update.message.reply_text(f"Active filters:\n{filters_list}")

def handle_message(update, context):
    message_text = update.message.text.lower()
    
    for trigger in filters_dict:
        if re.search(r'\b' + re.escape(trigger) + r'\b', message_text):
            update.message.reply_text(filters_dict[trigger])
            break

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Telegram Bot is running!')
    
    def log_message(self, format, *args):
        return

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

def run_http_server():
    """Run a simple HTTP server to satisfy Heroku's requirements"""
    port = int(os.environ.get('PORT', 5000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    logger.info(f"HTTP server running on port {port}")
    server.serve_forever()

def run_bot():
    """Run the Telegram bot with restart capability"""
    token = "8424898200:AAFTGqucscLcbXfCXl9zFrYkAEfTdWBP4_4"
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            updater = Updater(token, use_context=True)
            dp = updater.dispatcher

            dp.add_handler(CommandHandler("start", start))
            dp.add_handler(CommandHandler("filterr", add_filter))
            dp.add_handler(CommandHandler("stopalll", stop_all))
            dp.add_handler(CommandHandler("list", list_filters))
            dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
            dp.add_error_handler(error)

            logger.info("Bot started...")
            updater.start_polling(drop_pending_updates=True)
            updater.idle()
            
        except Exception as e:
            logger.error(f"Bot crashed with error: {e}")
            retry_count += 1
            if retry_count < max_retries:
                logger.info(f"Restarting bot in 10 seconds... (Attempt {retry_count}/{max_retries})")
                time.sleep(10)
            else:
                logger.error("Max retries reached. Exiting.")
                break

if __name__ == '__main__':
    # Start HTTP server in a daemon thread
    http_thread = threading.Thread(target=run_http_server)
    http_thread.daemon = True
    http_thread.start()
    
    # Run the bot
    run_bot()
