import os
import sys
import asyncio
import django
from pathlib import Path
import logging

from decouple import config  # читаем .env
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto, BufferedInputFile
from aiogram.filters import Command
from asgiref.sync import sync_to_async

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Добавляем корень проекта в Python path ---
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# --- Настройка Django ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# --- Импорт моделей Django ---
from car.models import CarContent, CONDITION_CHOICES, COLOR_CHOICES, BODY_CHOICES, FUEL_CHOICES, PRICE_CHOICES

# --- Читаем токен из .env ---
TOKEN = config("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Ошибка: не задан BOT_TOKEN в переменных окружения")

# --- Словарь для хранения выбора пользователя ---
user_choices = {}

# --- Обработчики ---
async def start(message: types.Message):
    user_choices[message.from_user.id] = {}
    buttons = [[KeyboardButton(text=label)] for _, label in CONDITION_CHOICES]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Выберите состояние автомобиля:", reply_markup=keyboard)


async def handle_choice(message: types.Message):
    try:
        user_id = message.from_user.id
        text = message.text

        if user_id not in user_choices:
            await start(message)
            return

        # --- Шаг 1: состояние ---
        if text in [label for _, label in CONDITION_CHOICES]:
            for key, label in CONDITION_CHOICES:
                if label == text:
                    user_choices[user_id]["condition"] = key

            buttons = [[KeyboardButton(text=label)] for _, label in COLOR_CHOICES]
            keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
            await message.answer("Выберите цвет:", reply_markup=keyboard)
            return

        # --- Шаг 2: цвет ---
        if text in [label for _, label in COLOR_CHOICES]:
            for key, label in COLOR_CHOICES:
                if label == text:
                    user_choices[user_id]["color"] = key

            buttons = [[KeyboardButton(text=label)] for _, label in BODY_CHOICES]
            keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
            await message.answer("Выберите кузов:", reply_markup=keyboard)
            return

        # --- Шаг 3: кузов ---
        if text in [label for _, label in BODY_CHOICES]:
            for key, label in BODY_CHOICES:
                if label == text:
                    user_choices[user_id]["body_type"] = key

            buttons = [[KeyboardButton(text=label)] for _, label in FUEL_CHOICES]
            keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
            await message.answer("Выберите топливо:", reply_markup=keyboard)
            return

        # --- Шаг 4: топливо ---
        if text in [label for _, label in FUEL_CHOICES]:
            for key, label in FUEL_CHOICES:
                if label == text:
                    user_choices[user_id]["fuel_type"] = key

            buttons = [[KeyboardButton(text=label)] for _, label in PRICE_CHOICES]
            keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
            await message.answer("Выберите диапазон цен:", reply_markup=keyboard)
            return

        # --- Шаг 5: цена ---
        if text in [label for _, label in PRICE_CHOICES]:
            for key, label in PRICE_CHOICES:
                if label == text:
                    user_choices[user_id]["price_range"] = key

            choices = user_choices[user_id]

            # Асинхронный запрос к Django ORM
            cars = await sync_to_async(list)(
                CarContent.objects.filter(
                    condition=choices["condition"],
                    color=choices["color"],
                    body_type=choices["body_type"],
                    fuel_type=choices["fuel_type"],
                    price_range=choices["price_range"]
                )
            )

            if cars:
                for car in cars:
                    # --- Фото ---
                    photos = []
                    for i in range(1, 6):
                        photo_field = getattr(car, f"photo{i}", None)
                        if photo_field and hasattr(photo_field, 'path') and os.path.exists(photo_field.path):
                            photos.append(photo_field.path)

                    if photos:
                        if len(photos) > 1:
                            media_group = []
                            for photo_path in photos:
                                try:
                                    with open(photo_path, "rb") as f:
                                        media_group.append(
                                            InputMediaPhoto(
                                                media=BufferedInputFile(f.read(), filename=os.path.basename(photo_path))
                                            )
                                        )
                                except Exception as e:
                                    logger.error(f"Ошибка загрузки фото {photo_path}: {e}")
                            if media_group:
                                await message.answer_media_group(media_group)
                        else:
                            try:
                                with open(photos[0], "rb") as f:
                                    await message.answer_photo(
                                        BufferedInputFile(f.read(), filename=os.path.basename(photos[0]))
                                    )
                            except Exception as e:
                                logger.error(f"Ошибка отправки фото: {e}")

                    # --- Видео ---
                    if car.video and hasattr(car.video, 'path') and os.path.exists(car.video.path):
                        try:
                            with open(car.video.path, "rb") as f:
                                await message.answer_video(
                                    BufferedInputFile(f.read(), filename=os.path.basename(car.video.path))
                                )
                        except Exception as e:
                            logger.error(f"Ошибка отправки видео: {e}")
                            await message.answer("⚠️ Не удалось отправить видео")

                    # --- Текстовая информация ---
                    text_info = (
                        f"🚘 {car.title}\n\n"
                        f"{car.description or 'Без описания'}\n\n"
                        f"💰 Цена: {car.get_price_range_display()}\n"
                        f"⚙️ Кузов: {car.get_body_type_display()}\n"
                        f"🎨 Цвет: {car.get_color_display()}\n"
                        f"⛽ Топливо: {car.get_fuel_type_display()}\n"
                        f"📌 Состояние: {car.get_condition_display()}\n"
                        f"👤 Владелец: {car.user}"
                    )
                    await message.answer(text_info)
            else:
                await message.answer("🚘 Машин с такими параметрами пока нет.")

            # Чистим выбор и убираем клавиатуру
            user_choices.pop(user_id, None)
            await message.answer("🔎 Поиск завершён. Введите /start для нового поиска.",
                                 reply_markup=types.ReplyKeyboardRemove())

    except Exception as e:
        logger.error(f"Ошибка в обработке выбора: {e}")
        await message.answer("Произошла ошибка при обработке вашего выбора. Попробуйте снова /start")


# --- Регистрируем обработчики ---
def register_user_handlers(dp: Dispatcher):
    dp.message.register(start, Command(commands=["start"]))
    dp.message.register(handle_choice)


# --- Основная функция запуска ---
async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    register_user_handlers(dp)
    logger.info("Бот запущен...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Бот корректно завершил работу")


# --- Точка входа ---
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен (Ctrl+C)")
