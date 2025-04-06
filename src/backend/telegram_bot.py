import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = "7890263759:AAEVLEqpYVEXH11aIGeErsxQO1N-51ZpYdk"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет, я бот для отправки уведомлений!")

@dp.message(Command("authorization"))
async def cmd_register(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Используйте: /authorization <email> <password>")
        return

    email = parts[1]
    password = parts[2]
    
    loop = asyncio.get_running_loop()
    from db import login_user, set_telegram

    success = await loop.run_in_executor(None, login_user, email, password,)
    if success:
        telegram_id = str(message.from_user.id)
        telegram_chat_id = str(message.chat.id)
        await loop.run_in_executor(None, set_telegram, email, telegram_id, telegram_chat_id)
        await message.answer("Авторизация прошла успешно!")
    else:
        await message.answer("Ошибка авторизации")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "Доступные команды:\n"
        "/start - запустить бота\n"
        "/help - получить помощь\n"
        "/authorization - авторизация пользователя для получения уведомлений"
    )
    await message.answer(help_text)

async def run_bot():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(run_bot())
