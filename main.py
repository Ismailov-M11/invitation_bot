import asyncio
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, DATABASE_URL, PORT
from bot import database
from bot.api import setup_app
from bot.handlers import auth, links, guest, stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


async def main() -> None:
    await database.init_db(DATABASE_URL)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(auth.router)
    dp.include_router(guest.router)
    dp.include_router(links.router)
    dp.include_router(stats.router)

    # HTTP API server (runs alongside the bot)
    app = web.Application()
    app["bot"] = bot
    setup_app(app)

    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    logging.info(f"API server: http://0.0.0.0:{PORT}")

    logging.info("Bot ishga tushdi ✅")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
