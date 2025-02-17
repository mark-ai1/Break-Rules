import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Break management data
break_data = {
    "toilet": {"users": [], "limit": 2, "daily_limit": 5},
    "drinking": {"users": [], "limit": 2, "daily_limit": 5},
    "outside": {"users": [], "limit": 4, "daily_limit": 5}
}

# Command: /start
async def start(update: Update, context: CallbackContext):
    keyboard = [["Toilet Break", "Drinking Break", "Outside Break", "Check Availability"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Please choose a break type:", reply_markup=reply_markup)

# Handle break requests
async def handle_break(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    break_type = update.message.text.lower().replace(" break", "")

    if break_type not in break_data:
        await update.message.reply_text("Invalid break type. Please try again.")
        return

    data = break_data[break_type]

    # Check if user has exceeded daily limit
    if user_id in data["users"] and data["users"].count(user_id) >= data["daily_limit"]:
        await update.message.reply_text(f"You’ve reached your daily {break_type} break limit ({data['daily_limit']}).")
        return

    # Check if break slot is available
    if len(data["users"]) >= data["limit"]:
        await update.message.reply_text(f"Sorry, only {data['limit']} people are allowed on a {break_type} break at a time.")
        return

    # Start break
    data["users"].append(user_id)
    await update.message.reply_text(f"Your {break_type} break has started. You have 15 minutes. Please return on time!")

    # Schedule break end
    async def end_break():
        data["users"].remove(user_id)
        await update.message.reply_text(f"Your {break_type} break has ended. Thank you for returning on time!")

    context.job_queue.run_once(end_break, 15 * 60)  # 15 minutes

# Command: /check
async def check_availability(update: Update, context: CallbackContext):
    message = "Break Availability:\n"
    for break_type, data in break_data.items():
        message += f"- {break_type.capitalize()}: {len(data['users'])}/{data['limit']} people\n"
    await update.message.reply_text(message)

# Main function
def main():
    # Replace '7695331037:AAHzI3d3FzOS_PbZ-sFfY4ERvHn5Ors9jYI' with your actual bot token
    application = ApplicationBuilder().token('YOUR_TELEGRAM_BOT_TOKEN').build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text(["Toilet Break", "Drinking Break", "Outside Break"]), handle_break))
    application.add_handler(CommandHandler("check", check_availability))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
