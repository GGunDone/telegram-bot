from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import logging
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Загружаем переменные окружения
load_dotenv("config.env")

# Конфигурация
TOKEN = os.getenv("BOT_TOKEN")
BONUS_URL = "https://send4.vodka/?id=14251"
IMAGE_PATH = "bot.jpg.jpg"

# Создаем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    """Обработчик команды /start"""
    
    # Создаем кнопку
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Забрать бонус", url=BONUS_URL)]
    ])
    
    # Текст сообщения
    caption = (
        "WELCOME-БОНУС на первый деп! 🎁\n\n"
        "1. Запускаешь бота\n"
        "2. Тапаешь по кнопке снизу\n"
        "3. Лутаешь +100% к пополнению и 100 FS в The Dog House\n\n"
        "Боровы, вы чё, реально ещё не забрали свой первый бонус? 🤔\n"
        "У вас ещё 3 валяются без дела — в сумме 300 FS\n\n"
        "Жми «Забрать бонус» и пошла возня 🚀🔥"
    )

    try:
        # Отправляем фото с подписью и кнопкой
        with open(IMAGE_PATH, 'rb') as photo:
            await message.answer_photo(
                photo=photo,
                caption=caption,
                reply_markup=keyboard
            )
    except FileNotFoundError:
        # Если фото не найдено, отправляем только текст
        await message.answer(
            caption,
            reply_markup=keyboard
        )

@dp.message()
async def handle_other_messages(message: types.Message):
    """Обработчик всех остальных сообщений"""
    response_text = (
        "🤖 Привет! Используй команду /start для получения бонуса!"
    )
    await message.answer(response_text)

async def main():
    """Основная функция запуска бота"""
    print("🤖 Бонус-бот запускается...")
    print("📊 Бот готов к работе!")
    
    if not TOKEN:
        print("❌ Ошибка: Не найден BOT_TOKEN в переменных окружения!")
        print("Создайте файл .env с содержимым: BOT_TOKEN=ваш_токен")
        return
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
