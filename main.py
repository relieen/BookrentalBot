import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests


BACKEND_URL = "http://127.0.0.1:8000/api/v1/books/"
BOT_TOKEN = "8277626758:AAEAhuLXfB9Xf0xxkX5o4M1aY9mkwDuTIS0"

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Відповідає на команду /start."""
    user = update.effective_user
    logger.info(f"Користувач {user.username} запустив бота.")
    

    welcome_message = f"Привіт, {user.first_name}! 👋\n\n" \
                      f"Я BookRentalBot - Ваш помічник для оренди книг. "\
                      f"Оберіть 'Каталог', щоб переглянути доступні книги."
                      
    await update.message.reply_html(
        welcome_message,
 
    )
async def catalog_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отримує список книг з API та відображає їх."""
    
    await update.message.reply_text("Завантажую каталог доступних книг...")
    
    try:
        # 1. Виклик реального API
        response = requests.get(BACKEND_URL)
        response.raise_for_status() # Викличе помилку для 4xx/5xx статусів
        books = response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Помилка при запиті до API: {e}")
        await update.message.reply_text("Помилка підключення до сервера або отримання даних. Спробуйте пізніше.")
        return

    if not books:
        await update.message.reply_text("Наразі доступних книг немає.")
        return

    # 2. Формування інтерфейсу
    
    reply_text = "📚 Доступні книги:\n\n"
    keyboard = []

    for book in books:
        book_id = book.get("id")
        title = book.get("title", "Без назви")
        author = book.get("author", "Невідомий автор")
        
        reply_text += f"**{title}**\n *Автор:* {author}\n\n"

        # Кнопка оренди (Вимога: Логіка кнопки 'Орендувати' - підготовка)
        # Callback-дані: RENT_ + book_id
        keyboard.append([
            InlineKeyboardButton("Орендувати", callback_data=f"RENT_{book_id}")
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        reply_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
def main() -> None:
    """Запускає бота."""

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))

    print("Бот запущено...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    application.add_handler(CommandHandler("catalog", catalog_command)) 
    

if __name__ == "__main__":
    main()