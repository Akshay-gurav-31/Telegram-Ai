import json
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables with demo keys as defaults
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7922723989:AAEAfUu84zbNTqCg0m5PcrDa_RLZcQ9sj7g")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCzttZnO6DLgH8obqo0W6tlrRSq7HxMlzY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I'm Tiny AI, Ask me anything!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "I'm Tiny AI! Send a message, and I'll respond with Gemini AI answers. Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is not set")
            raise ValueError("GEMINI_API_KEY is not set")
        payload = {
            "contents": [{"parts": [{"text": user_message}]}]
        }
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        if "candidates" in result and len(result["candidates"]) > 0:
            ai_response = result["candidates"][0]["content"]["parts"][0]["text"]
            logger.info("Gemini API response received")
        else:
            logger.warning("No candidates in Gemini response")
            ai_response = "Sorry, no AI response available."
        await update.message.reply_text(ai_response)
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Gemini API error: {http_err}")
        await update.message.reply_text(f"Gemini API error: {http_err}")
    except Exception as e:
        logger.error(f"Something went wrong: {str(e)}")
        await update.message.reply_text(f"Something went wrong: {str(e)}")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    await update.message.reply_text("Something's wrong! Try again later.")

def main():
    logger.info("Starting Tiny AI bot...")
    try:
        if not TELEGRAM_TOKEN:
            logger.error("TELEGRAM_TOKEN is not set")
            raise ValueError("TELEGRAM_TOKEN is not set")
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_error_handler(error)
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    main()
