import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
BASE_URL = "https://prod-team-23-j7mhbm13.REDACTED"
APP_URL = f'{BASE_URL}/client/loyal/my?startapp=parameter'


async def start_handler(message: types.Message, bot: Bot):
    try:
        user = message.from_user

        user_data = {
            "id": user.id,
            "first_name": user.first_name,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f'{BASE_URL}/api/client/register/',
                    json=user_data
            ) as response:
                if response.status == 200:
                    logger.info(f"Data sent to backend for user {user.id}")
                else:
                    text = await response.text()
                    logger.error(f"Backend error {response.status}: {text}")

        builder = InlineKeyboardBuilder()
        builder.button(
            text="Open Mini App", web_app=types.WebAppInfo(url=APP_URL)
        )

        await message.answer(
            f"Добро пожаловать, {user.first_name}!",
            reply_markup=builder.as_markup()
        )

    except Exception as e:
        logger.exception("Error in start handler")
        await message.answer("⚠️ Произошла ошибка. Попробуйте позже.")


async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(start_handler, Command(commands=['start']))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())