from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("id"))
async def cmd_id(message: Message) -> None:
    thread = message.message_thread_id
    lines = [
        f"*chat\\_id:* `{message.chat.id}`",
        f"*thread\\_id:* `{thread}`" if thread else "*thread\\_id:* нет (обычный чат)",
        "",
        "Скопируй эти числа в Railway Variables:",
        "`OWNER_CHAT_ID` и `OWNER_THREAD_ID`",
    ]
    await message.reply("\n".join(lines), parse_mode="Markdown")
