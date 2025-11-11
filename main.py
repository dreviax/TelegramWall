from func import cuImage, zipArchive
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import config
import time

BOT_TOKEN = "8365352271:AAH-HzWy4bA1upcYkBrdLP_EF_aBa3y6i8s"

STATUS_EMOJIS = {
    "saving": "💾",
    "cutting": "✂️",
    "archiving": "📦",
    "sending": "📤",
    "done": "✅",
    "error": "❌"
}

async def update_status(message, status_text, emoji_key="processing"):
    emoji = STATUS_EMOJIS.get(emoji_key, "⏳")
    try:
        await message.edit_text(f"{emoji} {status_text}", parse_mode='HTML')
    except Exception:
        pass

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    status_message = await update.message.reply_text("<b>💾 $ Saving...</b>", parse_mode='HTML')
    
    try:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_name = f"photo_{update.message.from_user.id}_{photo.file_id}.jpg"
        file_path = os.path.join("input", file_name)
        os.makedirs("input", exist_ok=True)
        
        await file.download_to_drive(file_path)
        await update_status(status_message, "<b>$ Cutting...</b>", "cutting")
        output_folder = await cuImage(file_path)
        await update_status(status_message, "<b>$ Archiving...</b>", "archiving")
        zip_path = await zipArchive(output_folder)
        await update_status(status_message, "<b>$ Sending...</b>", "sending")

        with open(zip_path, 'rb') as document:
            await context.bot.send_document(
                chat_id=chat_id, 
                document=document,
                caption="<b>✅ $ Done!</b>",
                parse_mode='HTML'
            )

        await status_message.delete()
        try:
            os.remove(file_path)
            import shutil
            shutil.rmtree(output_folder)
            os.remove(zip_path)
        except Exception as e:
            print(f"Ошибка при очистке: {e}")
            
    except Exception as e:
        await update_status(status_message, f"Error: {str(e)}", "error")
        print(f"Ошибка обработки: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = config.welcome_text

    welcome_image_url = "source/banner.jpg"
    
    try:
        await update.message.reply_photo(
            photo=welcome_image_url,
            caption=welcome_text,
            parse_mode='HTML'
        )
    except Exception:
        await update.message.reply_text(welcome_text, parse_mode='HTML')

def main():
    while True:
        try:
            application = Application.builder().token(BOT_TOKEN).build()
            application.add_handler(CommandHandler("start", start))
            application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
            application.run_polling()
            
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            print("Перезапуск бота через 5 секунд...")
            time.sleep(5)

if __name__ == "__main__":
    main()