import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Bot Token & API Key
BOT_TOKEN = "8440060284:AAHFmeL_HNoubfvQYFaK_DPmWXHjiRpizMw"
IMGBB_API_KEY = "d5c093aa50131bc0d2c57ce3ddf62a99"

# Conversation state
ASK_PHOTO = 1

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "User"
    keyboard = [["Upload photo"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"👋 Welcome {user_name}!\n\n"
        "This bot allows you to upload an image and get its direct URL.\n\n"
        "📌 How to use:\n"
        "1️⃣ Click 'Upload photo'.\n"
        "2️⃣ Send your image.\n"
        "3️⃣ The bot will return the image link.",
        reply_markup=reply_markup
    )

# When "Upload photo" button is clicked
async def ask_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📷 Please send your photo.")
    return ASK_PHOTO

# Handle photo upload
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    loading_msg = await update.message.reply_text("⏳ Uploading your image...")

    photo_file = await photo.get_file()
    photo_path = "temp.jpg"
    await photo_file.download(photo_path)  # fixed here

    with open(photo_path, "rb") as file:
        response = requests.post(
            f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}",
            files={"image": file}
        )

    try:
        os.remove(photo_path)
    except Exception as e:
        print(f"Error deleting temp file: {e}")

    await loading_msg.delete()

    if response.status_code == 200 and response.json().get("success"):
        image_url = response.json()["data"]["url"]
        await update.message.reply_text(image_url)
        await update.message.reply_text("📷 To upload more images, click 'Upload photo'.")
    else:
        await update.message.reply_text("❌ Failed to upload image. Please try again later.")

    return ASK_PHOTO

# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex("^Upload photo$"), ask_photo)
        ],
        states={
            ASK_PHOTO: [
                MessageHandler(filters.PHOTO, handle_photo),
                MessageHandler(filters.Regex("^Upload photo$"), ask_photo)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    app.add_handler(conv_handler)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
