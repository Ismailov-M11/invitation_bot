from aiogram import Router, F
from aiogram.types import Message

from bot.session import AUTHENTICATED
from bot import database

router = Router()


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

        def parse_sum(s) -> int:
            if not s:
                return 0
            digits = "".join(c for c in s if c.isdigit())
            return int(digits) if digits else 0

        total = sum(parse_sum(r["amount"]) for r in rows)
        lines = [f"\U0001f48c *To'yona niyati ro'yxati* ({len(rows)} ta)\n"]
        for i, r in enumerate(rows, 1):
            name = r["name"]
            amount = f" — *{r['amount']}*" if r["amount"] else ""
            guest = ""
            if r["guest_uz"]:
                guest = f"\n   \U0001f39f _{r['guest_uz']}"
                if r["guest_ru"]:
                    guest += f" / {r['guest_ru']}"
                guest += "_"
            dt = r["copied_at"].strftime("%d.%m %H:%M") if r["copied_at"] else ""
            lines.append(f"{i}. *{name}*{amount} `{dt}`{guest}")

        if total:
            lines.append(f"\n\U0001f4b5 *Jami: {total:,} so'm*")

        await message.answer("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Xato: `{e}`", parse_mode="Markdown")
