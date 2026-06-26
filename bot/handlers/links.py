from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from bot.keyboards import versions_kb
from bot.session import AUTHENTICATED
from config import BASE_URL, VERSIONS

router = Router()


@router.message(F.text == "🔗 Universal havolalar")
async def universal_links(message: Message) -> None:
    if message.from_user.id not in AUTHENTICATED:
        await message.answer("🔐 /start")
        return
    await message.answer(
        "Qaysi versiyani yuborasiz?\n\n"
        "🌅 *V1* — faqat ertalabki tadbir (Osh)\n"
        "🌙 *V2* — faqat kechki tadbir (Visol oqshomi)\n"
        "🎊 *V3* — ikki tadbir ham",
        parse_mode="Markdown",
        reply_markup=versions_kb(),
    )


@router.callback_query(F.data.startswith("link:"))
async def send_link(callback: CallbackQuery) -> None:
    if callback.from_user.id not in AUTHENTICATED:
        await callback.answer("❌ Avval /start yuboring", show_alert=True)
        return

    version = int(callback.data.split(":")[1])
    url = f"{BASE_URL}?v={version}"

    await callback.message.answer(
        f"{VERSIONS[version]}\n\n"
        f"🔗 Havola (nusxalash uchun bosing):\n`{url}`",
        parse_mode="Markdown",
    )
    await callback.answer("✅ Havola yuborildi!")
