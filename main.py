import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# دریافت توکن ربات از متغیر محیطی
TOKEN = os.getenv('TELEGRAM_TOKEN')

# دیکشنری برای ذخیره فایل‌های ارسال شده
file_ids = {}

# فرمان استارت
def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! من ربات ارسال فایل هستم. لطفا یک فایل ویدیویی ارسال کنید.")

# پردازش و ذخیره فایل ویدیویی
def handle_video(update: Update, context: CallbackContext):
    file = update.message.video
    file_id = file.file_id
    
    # ذخیره file_id برای ارسال بعدی
    file_ids[update.message.chat_id] = file_id
    
    # ارسال تاییدیه
    update.message.reply_text("فایل دریافت شد! حالا می‌توانید لینک آن را دریافت کنید.")

# ارسال ویدیو ذخیره‌شده برای کاربر
def send_video(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if chat_id in file_ids:
        # ارسال فایل با استفاده از file_id
        context.bot.send_video(chat_id=chat_id, video=file_ids[chat_id])
    else:
        update.message.reply_text("هیچ فایلی برای ارسال وجود ندارد. لطفا ابتدا یک فایل ارسال کنید.")

# تابع اصلی برای راه‌اندازی ربات
def main():
    updater = Updater(TOKEN, use_context=True)
    
    # اضافه کردن هندلرها
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.video, handle_video))
    dp.add_handler(CommandHandler("getvideo", send_video))
    
    # اجرای ربات
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
