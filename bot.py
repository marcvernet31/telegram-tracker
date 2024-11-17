import os
import time
import telebot # type: ignore
from datetime import datetime
from dotenv import load_dotenv

from config import conditions, TARGET_GROUP_ID, BOT_USER_ID
load_dotenv()

bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))
user_info = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handle the /start command"""
    welcome_text = (
        "👋 Welcome! I'll forward all your messages to the group chat.\n"
        "Just start sending messages and I'll relay them."
    )
    bot.reply_to(message, welcome_text)
    
    # Store user information
    user_info[message.from_user.id] = {
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
        'start_time': datetime.now()
    }

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker'])
def forward_message(message):
    """Forward any type of message to the target group"""
    try:       
        # Add a delay to avoid rate limiting
        time.sleep(2) 
        if message.content_type == 'text':
            bot.send_message(TARGET_GROUP_ID,  message.text)
        else:
            # For media messages, forward the content
            bot.forward_message(TARGET_GROUP_ID, message.chat.id, message.message_id)
        
        bot.reply_to(message, "✅ Message forwarded to the group!")
        
    except Exception as e:
        error_message = f"❌ Failed to forward message: {str(e)}"
        bot.reply_to(message, error_message)
        print(f"Error: {str(e)}")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    """Show statistics about the user's interaction with the bot"""
    if message.from_user.id in user_info:
        user = user_info[message.from_user.id]
        start_time = user['start_time']
        duration = datetime.now() - start_time
        
        stats_message = (
            f"📊 Your Statistics:\n"
            f"Started using bot: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Time since start: {duration.days} days, {duration.seconds//3600} hours"
        )
        bot.reply_to(message, stats_message)
    else:
        bot.reply_to(message, "No statistics available. Please start the bot with /start first.")

def main():
    """Main function to run the bot"""
    print("Bot started...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Bot polling error: {e}")
        # You might want to implement a retry mechanism here

if __name__ == "__main__":
    main()
