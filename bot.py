import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = "8549965128:AAFfyPIMiNvYPFP3qEHZb_VEw8tL7GIN62I"
NUM_INFO_API_KEY = "33175dfa58d94958"
API_BASE_URL = "https://daily-binny-ryuioggv-391a9381.koyeb.app/api/lookup"

# --- LOGGING SETUP ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    
    welcome_text = (
        f"**Hello {user_first_name}!** 🚓\n\n"
        "**I can help you find details about a phone number**.\n\n"
        "**You can simply send me a 10-digit mobile number**\n\n"
        "**or use the buttons below.**"
    )

    # Inline Buttons
    keyboard = [
        [
            InlineKeyboardButton("Info 🔍", callback_data="track_btn"),
            InlineKeyboardButton("Developer 👨‍💻", url="http://t.me/Zeroo_fuxgiven")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

# --- BUTTON HANDLER ---
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Acknowledge the click

    if query.data == "track_btn":
        await query.message.reply_text("Please send the 10-digit mobile number you want to lookup.")

# --- MESSAGE HANDLER (API LOGIC) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()

    # Basic Validation: Check if text is digits and length is between 10-15
    if not user_text.isdigit() or len(user_text) < 10 or len(user_text) > 15:
        await update.message.reply_text("Invalid format. Please send a valid 10-digit mobile number.")
        return

    # Notify user that processing is happening
    processing_msg = await update.message.reply_text("🔍 Searching details... Please wait.")

    try:
        # Prepare parameters for the API
        params = {
            "key": NUM_INFO_API_KEY,
            "mobile": user_text
        }

        # Make the API Request
        response = requests.get(API_BASE_URL, params=params)
        data = response.json()

        # Check API Logic based on your docs
        if response.status_code == 200 and data.get("success") is True:
            
            # Check if results exist
            if data.get("result") and len(data["result"]) > 0:
                info = data["result"][0]
                

                result_text = (
                    f"🚓 <b>Details Found!</b> ✅\n\n"
                    f"📱 <b>Mobile:</b> <code>{info.get('mobile', 'N/A')}</code>\n\n"
                    f"👤 <b>Name:</b> {info.get('name', 'N/A')}\n\n"
                    f"👨‍🦳 <b>Father Name:</b> {info.get('father_name', 'N/A')}\n\n"
                    f"📍 <b>Address:</b> {info.get('address', 'N/A')}\n\n"
                    f"🌐 <b>Circle:</b> {info.get('circle', 'N/A')}\n\n"
                    f"🆔 <b>Aadhar Number:</b> <code>{info.get('id_number', 'N/A')}</code>\n\n"
                    f"----------------------\n"
                    f"Developed [Toxic Dev](https://t.me/iscxm) 🚓"
                )

                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=processing_msg.message_id,
                    text=result_text,
                    parse_mode='Markdown'
                )
            else:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=processing_msg.message_id,
                    text="No details found for this number."
                )

        elif response.status_code == 429:
             await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                text="**Rate limit exceeded. Please try again later or upgrade your plan.**"
            )
        
        elif response.status_code == 401:
             await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                text="⚠️ API Configuration Error: Invalid API Key."
            )
            
        else:
            error_msg = data.get('error', 'Unknown error')
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                text=f"**Error:** {error_msg}"
            )

    except Exception as e:
        print(f"Error: {e}")
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=processing_msg.message_id,
            text="An internal error occurred. Please try again later."
        )

# --- MAIN APP ---
if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_click))
    
    # This handler catches any text that is NOT a command
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot is running...")
    application.run_polling()

