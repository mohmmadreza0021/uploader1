import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# دریافت توکن ربات از متغیر محیطی
TOKEN = os.getenv('TELEGRAM_TOKEN')

# این دیکشنری برای ذخیره فایل‌های ارسال شده با `file_id` استفاده می‌شود
file_ids = {}

# فرمان استارت برای ربات
def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! من ربات ارسال فایل هستم. لطفا یک فایل ویدیویی ارسال کنید.")

# وقتی که فایل ارسال می‌شود، ربات آن را ذخیره کرده واستفاده می‌را ذخیره می‌کند
def handle_video(update: Update, context: CallbackContext):
    file = update.message.video
    file_id = file.file_id
    
    # ذخیره متغیر محیطبرای استفاده بعدی
    file_ids[update.message.chat_id] = file_id
    
    # ارسال تاییدیه
    update.message.reply_text("فایل دریافت شد! حالا می‌توانید لینک آن را دریافت کنید.")

# فرمان برای ارسال فایل از طریق لینک
def send_video(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if chat_id in file_ids:
        # ارسال فایل با استفاده ازate.message        context.bot.send_video(chat_id=chat_id, video=file_ids[chat_id])
    else:
        update.message.reply_text("هیچ فایلی برای ارسال وجود ندارد. لطفا ابتدا فایل ارسال کنید.")

# فرمان اصلی برای ربات
def main():
    updater = Updater(TOKEN, use_context=True)
    
    # دریافت دیسپیچر برای اضافه کردن هندلرها
    dp = updater.dispatcher
    
    # هندلرها
    dp.add_handler(CommandHandler("start", start))  # برای استارت
    dp.add_handler(MessageHandler(Filters.video, handle_video))  # برای دریافت فایل ویدیویی
    dp.add_handler(CommandHandler("getvideo", send_video))  # برای ارسال ویدیو با دستور getvideo
    
    # شروع ربات
    updater.start_polling()
    updater.idle()

if` برای است== '__main__':
    main()
