import sqlite3
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
from telegram.error import BadRequest

TOKEN = "8152621696:AAHeP8gA3q7VoFr4kgPOySgCh-DADyr57GY"
DATABASE_CHANNEL = "1002381931065"  # کانال دیتابیس
LOCKED_CHANNEL = "@v_hichi"  # کانالی که جوین اجباری دارد

# اتصال به دیتابیس SQLite
conn = sqlite3.connect("files.db", check_same_thread=False)
cursor = conn.cursor()

# ایجاد جدول ذخیره فایل‌ها (اگر وجود نداشت)
cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id TEXT NOT NULL,
    unique_id TEXT NOT NULL
)
""")
conn.commit()

bot = Bot(token=TOKEN)

# بررسی عضویت در کانال
def check_subscription(user_id):
    try:
        chat_member = bot.get_chat_member(LOCKED_CHANNEL, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except BadRequest:
        return False

# دریافت فایل از کانال و ذخیره در دیتابیس
def save_file(update: Update, context: CallbackContext):
    message = update.message
    if message.video or message.document:
        file = message.video or message.document
        file_id = file.file_id
        unique_id = file.file_unique_id  # آی‌دی یکتا برای هر فایل

        # ذخیره در دیتابیس
        cursor.execute("INSERT INTO files (file_id, unique_id) VALUES (?, ?)", (file_id, unique_id))
        conn.commit()

        # ارسال لینک دانلود برای ادمین
        file_link = f"https://t.me/{bot.username}?start={unique_id}"
        message.reply_text(f"✅ فایل ذخیره شد!\n🔗 لینک دریافت: {file_link}")

# پردازش /start و بررسی آی‌دی فایل
def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    args = context.args

    if args:
        file_unique_id = args[0]
        
        # بررسی عضویت کاربر
        if not check_subscription(user_id):
            keyboard = [[InlineKeyboardButton("📢 عضویت در کانال", url=f"https://t.me/{LOCKED_CHANNEL}")],
                        [InlineKeyboardButton("✅ بررسی عضویت", callback_data=f"check_{file_unique_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("🚨 برای دریافت فایل، ابتدا در کانال زیر عضو شوید:", reply_markup=reply_markup)
            return

        # جستجوی فایل در دیتابیس
        cursor.execute("SELECT file_id FROM files WHERE unique_id=?", (file_unique_id,))
        file = cursor.fetchone()

        if file:
            bot.send_document(user_id, file[0], caption="🎬 فایل شما آماده است!")
        else:
            update.message.reply_text("❌ فایل موردنظر یافت نشد!")
    else:
        update.message.reply_text("سلام! برای دریافت فایل، لینک مخصوص آن را کلیک کنید.")

# بررسی مجدد عضویت و ارسال فایل
def check_subscription_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    file_unique_id = query.data.split("_")[1]

    if check_subscription(user_id):
        cursor.execute("SELECT file_id FROM files WHERE unique_id=?", (file_unique_id,))
        file = cursor.fetchone()
        
        if file:
            bot.send_document(user_id, file[0], caption="🎬 فایل شما آماده است!")
            query.message.delete()
        else:
            query.message.edit_text("❌ فایل موردنظر یافت نشد!")
    else:
        query.answer("⛔️ هنوز عضو کانال نشده‌اید!")

# راه‌اندازی ربات
updater = Updater(token=TOKEN, use_context=True)
dp = updater.dispatcher

# اصلاح فیلترها به صورت صحیح
dp.add_handler(MessageHandler(filters.Chat(DATABASE_CHANNEL) & (filters.Video | filters.Document), save_file))
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="check_.*"))

updater.start_polling()
updater.idle()
