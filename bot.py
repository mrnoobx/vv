import os
import logging
import urllib.parse
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackContext, CallbackQueryHandler, filters
)
from pymongo import MongoClient

# =========================
# Environment Configuration
# =========================
TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
MONGO_URI = os.getenv('MONGO_URI')

# =========================
# MongoDB Setup
# =========================
client = MongoClient(MONGO_URI)
db = client['terabox_bot']
users_collection = db['users']

# =========================
# Bot Settings
# =========================
VERIFICATION_REQUIRED = False  # Verification flag disabled (no ads/token system)
admin_ids = [6025969005, 6018060368]

# =========================
# Logging Setup
# =========================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =========================
# Command Handlers
# =========================

async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    users_collection.update_one(
        {"user_id": user.id},
        {"$set": {"username": user.username, "full_name": user.full_name}},
        upsert=True
    )

    message = (
        f"New user started the bot:\n"
        f"Name: {user.full_name}\n"
        f"Username: @{user.username}\n"
        f"User   ID: {user.id}"
    )
    await context.bot.send_message(chat_id=CHANNEL_ID, text=message)

    photo_url = 'https://ik.imagekit.io/dvnhxw9vq/unnamed.png?updatedAt=1735280750258'
    await update.message.reply_photo(
        photo=photo_url,
        caption=(
            "👋 **Welcome to the TeraBox Online Player!** 🌟\n\n"
            "Send me any TeraBox link and I'll provide you with a direct streaming link without ads or verification!"
        ),
        parse_mode='Markdown'
    )

async def users_count(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id in admin_ids:
        user_count = users_collection.count_documents({})
        await update.message.reply_text(f"Total users: {user_count}")
    else:
        await update.message.reply_text("Access denied.")

async def handle_link(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if update.message.text.startswith('http://') or update.message.text.startswith('https://'):
        original_link = update.message.text
        parsed_link = urllib.parse.quote(original_link, safe='')
        modified_link = f"https://terabox-play.lbni.workers.dev/api?url={parsed_link}"
        sharelink = f"https://t.me/share/url?url=https://t.me/TeraBox_OnlineBot?start=terabox-{original_link.split('/')[-1]}"

        button = [
            [InlineKeyboardButton("🌐Stream Server 1🌐", url=modified_link)],
            [InlineKeyboardButton("◀Share▶", url=sharelink)]
        ]

        await update.message.reply_text(
            "👇👇 YOUR VIDEO LINK IS READY 👇👇\n\n♥ 👇Your Stream Link👇 ♥\n",
            reply_markup=InlineKeyboardMarkup(button),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("Please send only a valid TeraBox link.")

# =========================
# Main Function
# =========================

async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("users", users_count))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
