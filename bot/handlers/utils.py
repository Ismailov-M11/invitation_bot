from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot import database

router = Router()


@router.message(Command("id"))
async def cmd_id(message: Message) -> None:
    thread = message.message_thread_id
    lines = [
        f"*chat\\_id:* `{message.chat.id}`",
        f"*thread\\_id:* `{thread}`" if thread else "*thread\\_id:* yo'q (oddiy chat)",
    ]

    if message.chat.type in ("group", "supergroup"):
        await database.add_notify_group(
            chat_id=message.chat.id,
            thread_id=thread or 0,
            title=message.chat.title,
        )
        lines.append("")
        lines.append("✅ Ushbu guruh/mavzu bildirishnomalar ro'yxatiga qo'shildi")

    await message.reply("\n".join(lines), parse_mode="Markdown")
