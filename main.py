import os, time, shutil
from func import cuImage, zipArchive
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from source.config import *

async def status(msg, text, key="save"):
    try: await msg.edit_text(f"{EMOJI.get(key, '⏳')} {text}", parse_mode='HTML')
    except: pass

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("<b>💾 $ Сохранение...</b>", parse_mode='HTML')
    try:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        os.makedirs("input", exist_ok=True)
        path = f"input/{update.message.from_user.id}_{photo.file_id}.jpg"
        await file.download_to_drive(path)

        await status(msg, "<b>$ Обрезка...</b>", "cut")
        out = await cuImage(path)

        await status(msg, "<b>$ Архивация...</b>", "zip")
        zip_path = await zipArchive(out)

        await status(msg, "<b>$ Отправка...</b>", "send")
        with open(zip_path, 'rb') as doc:
            await context.bot.send_document(update.effective_chat.id, doc, caption="<b>✅ $ Готово!</b>", parse_mode='HTML')

        await msg.delete()
        for p in [path, zip_path]:
            if os.path.exists(p): os.remove(p)
        shutil.rmtree(out, ignore_errors=True)
    except Exception as e:
        await status(msg, f"$ Не удалось обработать", "error")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: await update.message.reply_photo("source/images/banner.jpg", caption=welcome_text, parse_mode='HTML')
    except: await update.message.reply_text(welcome_text, parse_mode='HTML')

def main():
    while True:
        try:
            app = Application.builder().token(BOT_TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
            app.run_polling()
        except Exception as e:
            print(f"ERROR:\n{e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
