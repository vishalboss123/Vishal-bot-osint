import os
import json
import time
import threading
import traceback
import requests
import telebot

from pymongo import MongoClient
import ssl

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ============================================================
#                    CONFIGURATION
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# Put ONLY an authorized/non-sensitive API here.
AUTHORIZED_API_URL = os.getenv("AUTHORIZED_API_URL", "")

OWNER_ID = int(os.getenv("OWNER_ID", "0"))

OWNER_USERNAME = "YTT_BISHAL"
BOT_USERNAME = os.getenv("BOT_USERNAME", "VishalNumInfoBot")

SUPPORT_URL = "https://t.me/+rIQdb64h9NpiYjk1"
OWNER_URL = "https://t.me/YTT_BISHAL"
CHANNEL_URL = "https://t.me/YTN_BISHAL"
NIKI_URL = "https://t.me/iim_Nikibot"
BOT_URL = "https://t.me/Vishalcrimebot"

START_CREDITS = 10
REFERRAL_TARGET = 5
REFERRAL_REWARD = 10

AUTO_DELETE_SECONDS = 30

# Example pricing
PAY_URL = OWNER_URL


# ============================================================
#                    BASIC CHECKS
# ============================================================

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing from Render Environment Variables.")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI is missing from Render Environment Variables.")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


# ============================================================
#                       MONGODB
# ============================================================


# ============================================================
#                       MONGODB
# ============================================================

mongo_client = MongoClient(
    MONGO_URI,
    tls=True,
    serverSelectionTimeoutMS=15000,
    connectTimeoutMS=15000,
    socketTimeoutMS=30000,
    retryWrites=True
)

db = mongo_client["vishal_num_info"]
users_col = db["users"]


# ============================================================
#                  MONGODB CONNECTION TEST
# ============================================================

try:
    mongo_client.admin.command("ping")
    print("✅ MongoDB connected successfully!")
except Exception as e:
    print("❌ MongoDB connection failed!")
    print("ERROR:", e)
    raise

# ============================================================
#                    DATABASE HELPERS
# ============================================================

def get_user(user_id, username=None, first_name=None):
    user = users_col.find_one({"user_id": user_id})

    if not user:
        user = {
            "user_id": user_id,
            "username": username or "",
            "first_name": first_name or "",
            "credits": START_CREDITS,
            "referrals": 0,
            "referred_by": None,
            "referred_users": [],
            "referral_reward_claimed": False,
            "created_at": int(time.time()),
        }

        users_col.insert_one(user)

    else:
        users_col.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "username": username or user.get("username", ""),
                    "first_name": first_name or user.get("first_name", "")
                }
            }
        )

    return users_col.find_one({"user_id": user_id})


def get_credits(user_id):
    user = users_col.find_one({"user_id": user_id})

    if not user:
        get_user(user_id)
        return START_CREDITS

    return int(user.get("credits", 0))


def add_credits(user_id, amount):
    users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"credits": amount}},
        upsert=True
    )


def remove_credit(user_id):
    result = users_col.update_one(
        {
            "user_id": user_id,
            "credits": {"$gt": 0}
        },
        {
            "$inc": {"credits": -1}
        }
    )

    return result.modified_count == 1


# ============================================================
#                  STYLISH MAIN KEYBOARD
# ============================================================

def main_keyboard():

    keyboard = [

        [
            InlineKeyboardButton(
                "𓆩 𝐌ᴇ 𓆪",
                url=BOT_URL,
                style="primary"
            ),

            InlineKeyboardButton(
                "✦ 𝐒ᴜᴘᴘᴏʀᴛ",
                url=SUPPORT_URL,
                style="success"
            )
        ],

        [
            InlineKeyboardButton(
                "𓆩 𝐕ɪsʜᴀʟxᴅᴇᴠɪʟ 𓆪",
                url=OWNER_URL,
                style="danger"
            ),

            InlineKeyboardButton(
                "𓆩 𝐂ʜᴀɴɴᴇʟ 𓆪",
                url=CHANNEL_URL,
                style="primary"
            )
        ],

        [
            InlineKeyboardButton(
                "𓆩 𝐍ɪᴋɪ 𓆪",
                url=NIKI_URL,
                style="success"
            )
        ],

        [
            InlineKeyboardButton(
                "🎁 𝐑ᴇғᴇʀ",
                callback_data="referral",
                style="success"
            ),

            InlineKeyboardButton(
                "💳 𝐏ᴀʏ",
                url=PAY_URL,
                style="danger"
            )
        ],

        [
            InlineKeyboardButton(
                "💰 𝐂ʀᴇᴅɪᴛs",
                callback_data="credits",
                style="primary"
            ),

            InlineKeyboardButton(
                "➕ 𝐀ᴅᴅ ᴛᴏ 𝐆ʀᴏᴜᴘ",
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                style="success"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


# ============================================================
#                     START MESSAGE
# ============================================================

def start_text(user):

    credits = get_credits(user.id)

    return f"""
☠️ <b>乂 𝐕ɪsʜᴀʟ 𝐍ᴜᴍ 𝐈ɴғᴏ 乂</b> ☠️

╔══════════════════════════════╗
║   🖥️ <b>𝐒ʏsᴛᴇᴍ 𝐀ᴄᴄᴇss</b> ⚡
║   <code>████████████████████</code>
║   <b>𝐎𝐒𝐈𝐍𝐓 𝐒ʏsᴛᴇᴍ</b> • <b>𝐕𝟑.𝟎</b>
╚══════════════════════════════╝

👤 <b>𝐔sᴇʀ:</b> {user.first_name}
🆔 <b>𝐈ᴅ:</b> <code>{user.id}</code>
💎 <b>𝐂ʀᴇᴅɪᴛs:</b> <code>{credits}/10</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━
🖥️ <b>𝐂ᴏᴍᴍᴀɴᴅ 𝐂ᴇɴᴛᴇʀ</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ <code>/start</code> — 𝐎ᴘᴇɴ 𝐒ʏsᴛᴇᴍ
💰 <code>/credits</code> — 𝐂ʜᴇᴄᴋ 𝐂ʀᴇᴅɪᴛs
📞 <code>/num &lt;number&gt;</code> — 𝐀ᴜᴛʜᴏʀɪᴢᴇᴅ 𝐋ᴏᴏᴋᴜᴘ
🎁 <code>/referral</code> — 𝐑ᴇғᴇʀ &amp; 𝐄ᴀʀɴ
🔄 <code>/reset &lt;user_id&gt;</code> — 𝐎ᴡɴᴇʀ 𝐎ɴʟʏ
➕ <code>/addcredits &lt;user_id&gt; &lt;amount&gt;</code> — 𝐎ᴡɴᴇʀ 𝐎ɴʟʏ

━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 <b>𝐐ᴜɪᴄᴋ 𝐀ᴄᴄᴇss</b>

➜ Send a <b>10-digit number</b>
➜ Or use <code>/num 9876543210</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎁 <b>𝐑ᴇғᴇʀ 𝐑ᴇᴡᴀʀᴅ</b>

Invite <b>5 unique users</b> → 🎁 <b>+10 𝐂ʀᴇᴅɪᴛs</b>

🔒 Same user can only count once.

━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 <b>𝐂ʀᴇᴅɪᴛ 𝐏ʀɪᴄɪɴɢ</b>

20 𝐂ʀᴇᴅɪᴛs → ₹50
50 𝐂ʀᴇᴅɪᴛs → ₹100
100 𝐂ʀᴇᴅɪᴛs → ₹200

━━━━━━━━━━━━━━━━━━━━━━━━━━

👾 <b>𝐃ᴇᴠᴇʟᴏᴘᴇʀ:</b> @{OWNER_USERNAME}

🔐 <b>𝐒ᴇᴄᴜʀᴇ</b> • ⚡ <b>𝐅ᴀsᴛ</b> • 🛡️ <b>𝐏ʀɪᴠᴀᴛᴇ</b>

☠️ <i>𝐖ᴇʟᴄᴏᴍᴇ 𝐓ᴏ 𝐓ʜᴇ 𝐒ʏsᴛᴇᴍ...</i>
━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# ============================================================
#                        /START
# ============================================================

@bot.message_handler(commands=["start"])
def start_command(message):

    user = message.from_user

    get_user(
        user.id,
        user.username,
        user.first_name
    )

    # --------------------------------------------------------
    # Referral start parameter
    # /start ref_USERID
    # --------------------------------------------------------

    parts = message.text.split(maxsplit=1)

    if len(parts) == 2:

        ref_code = parts[1].strip()

        if ref_code.startswith("ref_"):

            try:
                referrer_id = int(ref_code.replace("ref_", ""))

                process_referral(
                    new_user_id=user.id,
                    referrer_id=referrer_id
                )

            except ValueError:
                pass

    bot.send_message(
        message.chat.id,
        start_text(user),
        reply_markup=main_keyboard()
    )


# ============================================================
#                     REFERRAL SYSTEM
# ============================================================

def process_referral(new_user_id, referrer_id):

    if new_user_id == referrer_id:
        return False

    new_user = users_col.find_one({"user_id": new_user_id})
    referrer = users_col.find_one({"user_id": referrer_id})

    if not referrer:
        return False

    # User already referred before
    if new_user and new_user.get("referred_by"):
        return False

    # Same user cannot be counted twice
    referred_users = referrer.get("referred_users", [])

    if new_user_id in referred_users:
        return False

    # Save referred_by
    users_col.update_one(
        {"user_id": new_user_id},
        {
            "$set": {
                "referred_by": referrer_id
            }
        }
    )

    # Add unique referral
    result = users_col.update_one(
        {
            "user_id": referrer_id,
            "referred_users": {"$ne": new_user_id}
        },
        {
            "$addToSet": {
                "referred_users": new_user_id
            },
            "$inc": {
                "referrals": 1
            }
        }
    )

    if result.modified_count == 0:
        return False

    referrer = users_col.find_one({"user_id": referrer_id})

    referrals = int(referrer.get("referrals", 0))

    # Every 5 unique referrals -> 10 credits
    if referrals % REFERRAL_TARGET == 0:

        add_credits(
            referrer_id,
            REFERRAL_REWARD
        )

        try:
            bot.send_message(
                referrer_id,
                f"""
🎉 <b>𝐑ᴇғᴇʀʀᴀʟ 𝐑ᴇᴡᴀʀᴅ 𝐔ɴʟᴏᴄᴋᴇᴅ!</b> 🎉

👥 <b>𝐑ᴇғᴇʀʀᴀʟs:</b> {referrals}
💎 <b>+{REFERRAL_REWARD} 𝐂ʀᴇᴅɪᴛs</b> added!

🔥 Keep inviting unique users.
"""
            )
        except Exception:
            pass

    return True


# ============================================================
#                      /CREDITS
# ============================================================

@bot.message_handler(commands=["credits"])
def credits_command(message):

    user = message.from_user

    get_user(
        user.id,
        user.username,
        user.first_name
    )

    user_data = users_col.find_one(
        {"user_id": user.id}
    )

    credits = int(
        user_data.get("credits", 0)
    )

    referrals = int(
        user_data.get("referrals", 0)
    )

    remaining = max(
        0,
        REFERRAL_TARGET - (referrals % REFERRAL_TARGET)
    )

    if credits <= 0:

        text = f"""
☠️ <b>𝐂ʀᴇᴅɪᴛs 𝐄xʜᴀᴜsᴛᴇᴅ</b>

💎 <b>𝐂ᴜʀʀᴇɴᴛ:</b> <code>0</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 <b>𝐆ᴇᴛ +10 𝐂ʀᴇᴅɪᴛs</b>

👥 Invite <b>5 unique users</b>
🔒 Each user counts only once.

📊 <b>𝐏ʀᴏɢʀᴇss:</b>
<code>{referrals % 5}/5</code>

👥 <b>𝐑ᴇᴍᴀɪɴɪɴɢ:</b> {remaining}

━━━━━━━━━━━━━━━━━━━━━━━━━━

💳 <b>𝐏ʀɪᴄᴇs</b>

20 → ₹50
50 → ₹100
100 → ₹200

━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    else:

        text = f"""
💎 <b>乂 𝐂ʀᴇᴅɪᴛ 𝐂ᴇɴᴛᴇʀ 乂</b>

👤 <b>𝐔sᴇʀ:</b> {user.first_name}

💰 <b>𝐀ᴠᴀɪʟᴀʙʟᴇ:</b>
<code>{credits}</code> / 10+

👥 <b>𝐑ᴇғᴇʀʀᴀʟs:</b>
<code>{referrals}</code>

🎁 <b>𝐍ᴇxᴛ 𝐑ᴇᴡᴀʀᴅ:</b>
<code>{referrals % 5}/5</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━

20 𝐂ʀᴇᴅɪᴛs → ₹50
50 𝐂ʀᴇᴅɪᴛs → ₹100
100 𝐂ʀᴇᴅɪᴛs → ₹200

━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    markup = InlineKeyboardMarkup()

    markup.row(
        InlineKeyboardButton(
            "🎁 𝐑ᴇғᴇʀ",
            callback_data="referral",
            style="success"
        ),
        InlineKeyboardButton(
            "💳 𝐏ᴀʏ",
            url=PAY_URL,
            style="danger"
        )
    )

    markup.row(
        InlineKeyboardButton(
            "🏠 𝐇ᴏᴍᴇ",
            callback_data="home",
            style="primary"
        )
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup
    )


# ============================================================
#                     /REFERRAL
# ============================================================

@bot.message_handler(commands=["referral"])
def referral_command(message):

    user = message.from_user

    get_user(
        user.id,
        user.username,
        user.first_name
    )

    data = users_col.find_one(
        {"user_id": user.id}
    )

    referrals = int(
        data.get("referrals", 0)
    )

    referral_link = (
        f"https://t.me/{BOT_USERNAME}"
        f"?start=ref_{user.id}"
    )

    progress = referrals % REFERRAL_TARGET

    text = f"""
🎁 <b>乂 𝐑ᴇғᴇʀʀᴀʟ 𝐂ᴇɴᴛᴇʀ 乂</b>

👥 <b>𝐘ᴏᴜʀ 𝐑ᴇғᴇʀʀᴀʟs:</b>
<code>{referrals}</code>

🎯 <b>𝐏ʀᴏɢʀᴇss:</b>
<code>{progress}/5</code>

🎁 <b>𝐑ᴇᴡᴀʀᴅ:</b>
+10 𝐂ʀᴇᴅɪᴛs

━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 <b>𝐘ᴏᴜʀ 𝐑ᴇғᴇʀʀᴀʟ 𝐋ɪɴᴋ:</b>

<code>{referral_link}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ <i>Only unique Telegram users count.</i>
"""

    markup = InlineKeyboardMarkup()

    markup.row(
        InlineKeyboardButton(
            "🎁 𝐒ʜᴀʀᴇ 𝐑ᴇғᴇʀʀᴀʟ",
            url=(
                "https://t.me/share/url"
                f"?url={referral_link}"
                "&text=Join%20Vishal%20Num%20Info"
            ),
            style="success"
        )
    )

    markup.row(
        InlineKeyboardButton(
            "💰 𝐂ʀᴇᴅɪᴛs",
            callback_data="credits",
            style="primary"
        ),

        InlineKeyboardButton(
            "🏠 𝐇ᴏᴍᴇ",
            callback_data="home",
            style="primary"
        )
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup
    )


# ============================================================
#                    OWNER ADD CREDITS
# ============================================================

@bot.message_handler(commands=["addcredits"])
def addcredits_command(message):

    if message.from_user.id != OWNER_ID:
        bot.reply_to(
            message,
            "⛔ <b>𝐀ᴄᴄᴇss 𝐃ᴇɴɪᴇᴅ</b>"
        )
        return

    parts = message.text.split()

    if len(parts) != 3:

        bot.reply_to(
            message,
            """
⚠️ <b>𝐖ʀᴏɴɢ 𝐅ᴏʀᴍᴀᴛ</b>

Use:

<code>/addcredits user_id amount</code>

Example:

<code>/addcredits 123456789 20</code>
"""
        )
        return

    try:

        target_id = int(parts[1])
        amount = int(parts[2])

        if amount <= 0:
            raise ValueError

    except ValueError:

        bot.reply_to(
            message,
            "❌ <b>𝐈ɴᴠᴀʟɪᴅ 𝐈ᴅ ᴏʀ 𝐀ᴍᴏᴜɴᴛ.</b>"
        )
        return

    get_user(target_id)

    add_credits(
        target_id,
        amount
    )

    new_balance = get_credits(target_id)

    bot.reply_to(
        message,
        f"""
✅ <b>𝐂ʀᴇᴅɪᴛs 𝐀ᴅᴅᴇᴅ</b>

👤 <b>𝐔sᴇʀ 𝐈ᴅ:</b>
<code>{target_id}</code>

💎 <b>𝐀ᴅᴅᴇᴅ:</b>
+{amount}

💰 <b>𝐍ᴇᴡ 𝐁ᴀʟᴀɴᴄᴇ:</b>
{new_balance}
"""
    )

    try:

        bot.send_message(
            target_id,
            f"""
🎉 <b>𝐂ʀᴇᴅɪᴛs 𝐀ᴅᴅᴇᴅ!</b>

💎 <b>+{amount} 𝐂ʀᴇᴅɪᴛs</b>

💰 <b>𝐍ᴇᴡ 𝐁ᴀʟᴀɴᴄᴇ:</b>
{new_balance}
"""
        )

    except Exception:
        pass


# ============================================================
#                       /RESET
# ============================================================

@bot.message_handler(commands=["reset"])
def reset_command(message):

    if message.from_user.id != OWNER_ID:

        bot.reply_to(
            message,
            "⛔ <b>𝐎ᴡɴᴇʀ 𝐎ɴʟʏ</b>"
        )
        return

    parts = message.text.split()

    if len(parts) != 2:

        bot.reply_to(
            message,
            "Use <code>/reset user_id</code>"
        )
        return

    try:
        target_id = int(parts[1])
    except ValueError:
        bot.reply_to(
            message,
            "❌ Invalid user ID."
        )
        return

    users_col.update_one(
        {"user_id": target_id},
        {
            "$set": {
                "credits": START_CREDITS
            }
        },
        upsert=True
    )

    bot.reply_to(
        message,
        f"""
✅ <b>𝐂ʀᴇᴅɪᴛs 𝐑ᴇsᴇᴛ</b>

👤 <code>{target_id}</code>
💎 <b>𝐁ᴀʟᴀɴᴄᴇ:</b> {START_CREDITS}
"""
    )


# ============================================================
#                   NUMBER VALIDATION
# ============================================================

def validate_number(number):

    number = number.strip()

    return (
        number.isdigit()
        and len(number) == 10
    )


# ============================================================
#                 PROCESS AUTHORIZED LOOKUP
# ============================================================

def process_number(message, number):

    user_id = message.from_user.id

    get_user(
        user_id,
        message.from_user.username,
        message.from_user.first_name
    )

    credits = get_credits(user_id)

    if credits <= 0:

        bot.send_message(
            message.chat.id,
            """
☠️ <b>𝐂ʀᴇᴅɪᴛs 𝐅ɪɴɪsʜᴇᴅ</b>

💎 <b>𝐘ᴏᴜʀ 𝐁ᴀʟᴀɴᴄᴇ:</b> <code>0</code>

🎁 Invite <b>5 unique users</b>
and get <b>+10 credits</b>.

💳 Or contact the owner for credits.
""",
            reply_markup=credits_keyboard()
        )

        return

    if not validate_number(number):

        bot.reply_to(
            message,
            """
❌ <b>𝐈ɴᴠᴀʟɪᴅ 𝐍ᴜᴍʙᴇʀ</b>

Please send exactly <b>10 digits</b>.
"""
        )

        return

    # Deduct one credit before lookup.
    if not remove_credit(user_id):

        bot.reply_to(
            message,
            "❌ <b>𝐍ᴏ 𝐂ʀᴇᴅɪᴛs 𝐀ᴠᴀɪʟᴀʙʟᴇ.</b>"
        )

        return

    remaining = get_credits(user_id)

    loading = bot.send_message(
        message.chat.id,
        f"""
🔍 <b>𝐒ʏsᴛᴇᴍ 𝐀ɴᴀʟʏsɪs...</b>

<code>[░░░░░░░░░░] 0%</code>

📞 <b>𝐓ᴀʀɢᴇᴛ:</b>
<code>{number}</code>

⚡ <b>𝐒ᴛᴀᴛᴜs:</b> 𝐈ɴɪᴛɪᴀʟɪᴢɪɴɢ...
"""
    )

    # Animation
    animation_steps = [
        ("[██░░░░░░░░] 20%", "𝐂ᴏɴɴᴇᴄᴛɪɴɢ..."),
        ("[████░░░░░░] 40%", "𝐕ᴀʟɪᴅᴀᴛɪɴɢ..."),
        ("[██████░░░░] 60%", "𝐐ᴜᴇʀʏɪɴɢ..."),
        ("[████████░░] 80%", "𝐏ʀᴏᴄᴇssɪɴɢ..."),
        ("[██████████] 100%", "𝐂ᴏᴍᴘʟᴇᴛᴇ"),
    ]

    for bar, status in animation_steps:

        time.sleep(0.35)

        try:

            bot.edit_message_text(
                f"""
🔍 <b>𝐒ʏsᴛᴇᴍ 𝐀ɴᴀʟʏsɪs...</b>

<code>{bar}</code>

📞 <b>𝐓ᴀʀɢᴇᴛ:</b>
<code>{number}</code>

⚡ <b>𝐒ᴛᴀᴛᴜs:</b> {status}
""",
                message.chat.id,
                loading.message_id
            )

        except Exception:
            pass

    # --------------------------------------------------------
    # Authorized API only
    # --------------------------------------------------------

    if not AUTHORIZED_API_URL:

        try:
            bot.delete_message(
                message.chat.id,
                loading.message_id
            )
        except Exception:
            pass

        bot.send_message(
            message.chat.id,
            f"""
⚠️ <b>𝐀ᴜᴛʜᴏʀɪᴢᴇᴅ 𝐀ᴘɪ 𝐍ᴏᴛ 𝐒ᴇᴛ</b>

The credit was consumed for this request.

💎 <b>𝐑ᴇᴍᴀɪɴɪɴɢ:</b> {remaining}

Set <code>AUTHORIZED_API_URL</code> in Render Environment Variables.
"""
        )

        return

    try:

        response = requests.get(
            AUTHORIZED_API_URL + number,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        # Keep output generic and JSON formatted.
        safe_result = {
            "status": True,
            "result": data
        }

        json_result = json.dumps(
            safe_result,
            indent=4,
            ensure_ascii=False
        )

        result_text = f"""
📞 <b>乂 𝐕ɪsʜᴀʟ 𝐍ᴜᴍ 𝐈ɴғᴏ 乂</b>
━━━━━━━━━━━━━━━━━━━━━━

<pre><code class="language-json">{json_result}</code></pre>

━━━━━━━━━━━━━━━━━━━━━━

💎 <b>𝐑ᴇᴍᴀɪɴɪɴɢ 𝐂ʀᴇᴅɪᴛs:</b>
<code>{remaining}</code>

⚡ <b>𝐑ᴇǫᴜᴇsᴛ 𝐂ᴏᴍᴘʟᴇᴛᴇ</b>
"""

        try:
            bot.delete_message(
                message.chat.id,
                loading.message_id
            )
        except Exception:
            pass

        sent = bot.send_message(
            message.chat.id,
            result_text
        )

        # Auto delete after 30 seconds.
        timer = threading.Timer(
            AUTO_DELETE_SECONDS,
            delete_message_safe,
            args=(message.chat.id, sent.message_id)
        )

        timer.daemon = True
        timer.start()

    except Exception as e:

        # Refund credit if authorized API failed.
        add_credits(user_id, 1)

        try:
            bot.delete_message(
                message.chat.id,
                loading.message_id
            )
        except Exception:
            pass

        bot.send_message(
            message.chat.id,
            f"""
❌ <b>𝐑ᴇǫᴜᴇsᴛ 𝐅ᴀɪʟᴇᴅ</b>

The request could not be completed.

💎 <b>𝐂ʀᴇᴅɪᴛ 𝐑ᴇғᴜɴᴅᴇᴅ:</b> +1

🔐 <b>𝐒ᴛᴀᴛᴜs:</b> 𝐒ᴀғᴇ
"""
        )

        print("API ERROR:", e)
        traceback.print_exc()


# ============================================================
#                    DELETE HELPER
# ============================================================

def delete_message_safe(chat_id, message_id):

    try:

        bot.delete_message(
            chat_id,
            message_id
        )

    except Exception:
        pass


# ============================================================
#                    CREDITS KEYBOARD
# ============================================================

def credits_keyboard():

    markup = InlineKeyboardMarkup()

    markup.row(
        InlineKeyboardButton(
            "🎁 𝐑ᴇғᴇʀ",
            callback_data="referral",
            style="success"
        ),

        InlineKeyboardButton(
            "💳 𝐏ᴀʏ",
            url=PAY_URL,
            style="danger"
        )
    )

    markup.row(
        InlineKeyboardButton(
            "📞 𝐂ᴏɴᴛᴀᴄᴛ",
            url=OWNER_URL,
            style="primary"
        ),

        InlineKeyboardButton(
            "💰 𝐂ʀᴇᴅɪᴛs",
            callback_data="credits",
            style="primary"
        )
    )

    return markup


# ============================================================
#                       /NUM
# ============================================================

@bot.message_handler(commands=["num"])
def num_command(message):

    parts = message.text.split()

    if len(parts) != 2:

        bot.reply_to(
            message,
            """
⚠️ <b>𝐔sᴀɢᴇ</b>

<code>/num 9876543210</code>
"""
        )

        return

    process_number(
        message,
        parts[1]
    )


# ============================================================
#                DIRECT 10-DIGIT NUMBER
# ============================================================

@bot.message_handler(
    func=lambda message:
        bool(message.text)
        and message.text.isdigit()
        and len(message.text) == 10
)
def direct_number(message):

    process_number(
        message,
        message.text.strip()
    )


# ============================================================
#                  CALLBACK HANDLER
# ============================================================

@bot.callback_query_handler(
    func=lambda call: True
)
def callback_handler(call):

    try:

        bot.answer_callback_query(call.id)

        if call.data == "credits":

            user = call.from_user

            get_user(
                user.id,
                user.username,
                user.first_name
            )

            data = users_col.find_one(
                {"user_id": user.id}
            )

            credits = int(
                data.get("credits", 0)
            )

            referrals = int(
                data.get("referrals", 0)
            )

            text = f"""
💎 <b>乂 𝐂ʀᴇᴅɪᴛ 𝐂ᴇɴᴛᴇʀ 乂</b>

💰 <b>𝐂ᴜʀʀᴇɴᴛ:</b>
<code>{credits}</code>

👥 <b>𝐑ᴇғᴇʀʀᴀʟs:</b>
<code>{referrals}</code>

🎁 <b>5 𝐔ɴɪǫᴜᴇ 𝐑ᴇғᴇʀʀᴀʟs</b>
→ <b>+10 𝐂ʀᴇᴅɪᴛs</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━

20 → ₹50
50 → ₹100
100 → ₹200
"""

            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=credits_keyboard()
            )

        elif call.data == "referral":

            user = call.from_user

            get_user(
                user.id,
                user.username,
                user.first_name
            )

            data = users_col.find_one(
                {"user_id": user.id}
            )

            referrals = int(
                data.get("referrals", 0)
            )

            link = (
                f"https://t.me/{BOT_USERNAME}"
                f"?start=ref_{user.id}"
            )

            text = f"""
🎁 <b>乂 𝐑ᴇғᴇʀʀᴀʟ 𝐂ᴇɴᴛᴇʀ 乂</b>

👥 <b>𝐑ᴇғᴇʀʀᴀʟs:</b>
<code>{referrals}</code>

🎯 <b>𝐏ʀᴏɢʀᴇss:</b>
<code>{referrals % 5}/5</code>

🎁 <b>𝐑ᴇᴡᴀʀᴅ:</b>
+10 𝐂ʀᴇᴅɪᴛs

━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 <b>𝐘ᴏᴜʀ 𝐋ɪɴᴋ:</b>

<code>{link}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━

🔒 <i>Each Telegram user counts only once.</i>
"""

            markup = InlineKeyboardMarkup()

            markup.row(
                InlineKeyboardButton(
                    "🎁 𝐒ʜᴀʀᴇ",
                    url=(
                        "https://t.me/share/url"
                        f"?url={link}"
                        "&text=Join%20Vishal%20Num%20Info"
                    ),
                    style="success"
                )
            )

            markup.row(
                InlineKeyboardButton(
                    "💰 𝐂ʀᴇᴅɪᴛs",
                    callback_data="credits",
                    style="primary"
                ),

                InlineKeyboardButton(
                    "🏠 𝐇ᴏᴍᴇ",
                    callback_data="home",
                    style="primary"
                )
            )

            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup
            )

        elif call.data == "home":

            user = call.from_user

            bot.edit_message_text(
                start_text(user),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=main_keyboard()
            )

    except Exception as e:

        print("CALLBACK ERROR:", e)
        traceback.print_exc()


# ============================================================
#                       MAIN
# ============================================================

if __name__ == "__main__":

    print("======================================")
    print("☠️ VISHAL NUM INFO BOT")
    print("⚡ Starting...")
    print("======================================")

    try:

        mongo_client.admin.command("ping")

        print("✅ MongoDB connected")

    except Exception as e:

        print("❌ MongoDB connection failed:")
        print(e)
        raise

    print("🤖 Bot is running...")

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    )
