import logging
import asyncio

from aiogram import F
from aiogram import Bot, Dispatcher, types
from app.hendlers import router
from app import database as db
from confing import TOKEN   
# Token 
bot = Bot(token=TOKEN)
dp = Dispatcher()   

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
