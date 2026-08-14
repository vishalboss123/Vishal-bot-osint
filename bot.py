import telebot
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = 'https://osintclodcode.onrender.com/?num='

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome to the VISHAL OSINT Lookup Bot!\n\nSend me any phone number and I'll try to find public data related to it.")

@bot.message_handler(func=lambda message: True)
def handle_number(message):
    number = message.text.strip()

    if not number.isdigit() or len(number) < 7:
        bot.reply_to(message, "❌ Please send a valid phone number (digits only).")
        return

    bot.reply_to(message, f"🔍 Looking up data for `{number}`...\nPlease wait a few seconds.", parse_mode="Markdown")

    try:
        response = requests.get(API_URL + number, timeout=20)
        data = response.json()
        results = data.get("results", [])

        if not results:
            bot.send_message(message.chat.id, "⚠️ No public data found for this number.")
            return

        final_result = f"📄 *OSINT Results for {number}:*\n\n"
        for item in results:
            final_result += f"{item}\n"

        bot.send_message(message.chat.id, final_result, parse_mode="Markdown")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
