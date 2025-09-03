import os
import asyncio
import django
import sys
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Добавляем корневую директорию проекта в Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Импортируем обработчики
try:
    from bot.handlers_user import register_user_handlers
    print("Успешно импортированы handlers_user")
except ImportError as e:
    print(f"Ошибка импорта handlers_user: {e}")
    # Альтернативный способ - определяем функции прямо здесь
    from aiogram import types, Dispatcher
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    from aiogram.filters import Command

    user_choices = {}


    def register_user_handlers(dp: Dispatcher):
        dp.message.register(start, Command(commands=["start"]))


    async def start(message: types.Message):
        await message.answer("Привет! Бот работает, но обработчики не загружены правильно.")

# Получаем токен из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    TOKEN = "8344079776:AAE0ECuN72x6NcAzAXeXfqslAt5OA3o_mTg"
    print("Предупреждение: BOT_TOKEN не найден в переменных окружения, используется токен из кода")


async def main():
    if not TOKEN:
        print("Ошибка: Не задан токен бота!")
        return

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Регистрируем обработчики
    register_user_handlers(dp)

    try:
        print("Бот запущен...")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("Бот остановлен")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен (Ctrl+C)")
