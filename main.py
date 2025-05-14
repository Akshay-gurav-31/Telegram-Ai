import json
import requests
import asyncio
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from fastapi import FastAPI
import uvicorn
import os

# Telegram Bot Token and Gemini API Key
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7922723989:AAEAfUu84zbNTqCg0m5PcrDa_RLZcQ9sj7g")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCzttZnO6DLgH8obqo0W6tlrRSq7HxMlzY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Telegram AI Bot is running"}

# Telegram bot functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I'm Tiny AI, your friendly chatbot powered by Gemini AI. Ask me anything!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "I'm Tiny AI! Send me a message, and I'll respond with AI-powered answers. Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        payload = {
            "contents": [{
                "parts": [{"text": user_message}]
            }]
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
            await update.message.reply_text(ai_response)
        else:
            await update.message.reply_text("Sorry, I couldn't get an AI response. Try again!")
    except requests.exceptions.HTTPError as http_err:
        await update.message.reply_text(f"AI API error: {http_err}")
    except Exception as e:
        await update.message.reply_text(f"Something went wrong with the AI: {str(e)}")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")
    await update.message.reply_text("Something's wrong! Try again later.")

def run_bot():
    print("Starting Tiny AI bot...")
    try:
        telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()
        telegram_app.add_handler(CommandHandler("start", start))
        telegram_app.add_handler(CommandHandler("help", help_command))
        telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        telegram_app.add_error_handler(error)
        telegram_app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"Failed to start bot: {e}")

if __name__ == "__main__":
    # Start the Telegram bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    # Start the FastAPI server
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
