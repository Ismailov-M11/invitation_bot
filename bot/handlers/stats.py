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
    "card_copied": "💌 Karta nusxalandi (to'yona niyati)",
}


@router.message(F.text == "📊 Statistika")
async def show_stats(message: Message) -> None:
    if message.from_user.id not in AUTHENTICATED:
        await message.answer("🔐 /start")
        return

    try:
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
    except Exception as e:
        await message.answer(f"❌ Xato: `{e}`", parse_mode="Markdown")


@router.message(F.text == "💌 To'yona ro'yxati")
async def show_card_copies(message: Message) -> None:
    if message.from_user.id not in AUTHENTICATED:
        await message.answer("🔐 /start")
        return

    try:
        rows = await database.get_card_copies(50)

        if not rows:
            await message.answer("_Hali hech kim karta raqamini nusxalamagan_", parse_mode="Markdown")
            return

        def parse_sum(s: str | None) -> int:
            if not s:
                return 0
            digits = "".join(c for c in s if c.isdigit())
            return int(digits) if digits else 0

        total = sum(parse_sum(r["amount"]) for r in rows)
        lines = [f"💌 *To’yona niyati ro’yxati* ({len(rows)} ta)\n"]
        for i, r in enumerate(rows, 1):
            name = r["name"]
            amount = f" — *{r[‘amount’]}*" if r["amount"] else ""
            guest = ""
            if r["guest_uz"]:
                guest = f"\n   \U0001f39f _{r[‘guest_uz’]}"
                if r["guest_ru"]:
                    guest += f" / {r[‘guest_ru’]}"
                guest += "_"
            dt = r["copied_at"].strftime("%d.%m %H:%M") if r["copied_at"] else ""
            lines.append(f"{i}. *{name}*{amount} `{dt}`{guest}")

        if total:
            lines.append(f"\n💵 *Jami: {total:,} so’m*")

        await message.answer("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Xato: `{e}`", parse_mode="Markdown")
