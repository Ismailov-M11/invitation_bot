from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import URLInputFile

from bot.keyboards import versions_kb
from bot.session import AUTHENTICATED
from config import BASE_URL, VERSIONS

router = Router()

_OG = f"{BASE_URL}/og.jpg"


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

    await callback.message.answer_photo(
        photo=URLInputFile(_OG),
        caption=url,
    )
    await callback.answer("✅ Havola yuborildi!")
