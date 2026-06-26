from aiogram import Router, F
from aiogram.types import Message

from bot.session import AUTHENTICATED
from bot import database

router = Router()

ACTION_NAMES = {
    "copied_link_v1": "🌅 Ertalabki havola nusxalandi",
    "copied_link_v2": "🌙 Kechki havola nusxalandi",
    "copied_link_v3": "🎊 Ikki tadbir havolasi nusxalandi",
    "created_guest_link": "👤 Maxsus havola yaratildi",
}


@router.message(F.text == "📊 Statistika")
async def show_stats(message: Message) -> None:
    if message.from_user.id not in AUTHENTICATED:
        await message.answer("🔐 /start")
        return

    stats = await database.get_stats()
    recent = await database.get_recent(8)

    lines = ["📊 *Statistika*\n"]
    if stats:
        for row in stats:
            label = ACTION_NAMES.get(row["action"], row["action"])
            lines.append(f"• {label}: *{row['cnt']}* ta")
    else:
        lines.append("_Hali ma'lumot yo'q_")

    if recent:
        lines.append("\n🕐 *Oxirgi harakatlar:*")
        for r in recent:
            name = r["first_name"] or "—"
            user = f"@{r['username']}" if r["username"] else "?"
            act = ACTION_NAMES.get(r["action"], r["action"])
            extra = f"\n  _{r['extra']}_" if r["extra"] and r["action"] == "created_guest_link" else ""
            lines.append(f"• {name} ({user}) — {act}{extra}")

    await message.answer("\n".join(lines), parse_mode="Markdown")
