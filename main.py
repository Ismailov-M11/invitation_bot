import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, DATABASE_URL
from bot import database
from bot.handlers import auth, links, guest, stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


async def main() -> None:
    await database.init_db(DATABASE_URL)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Order matters: cancel handler in guest.py must catch F.text=="❌ Bekor qilish"
    # before GuestState handlers — so guest router goes first after auth
    dp.include_router(auth.router)
    dp.include_router(guest.router)
    dp.include_router(links.router)
    dp.include_router(stats.router)

    logging.info("Bot ishga tushdi ✅")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
