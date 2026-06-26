from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards import main_menu_kb, cancel_kb
from bot.session import AUTHENTICATED
from bot.states import GuestState
from bot.utils import encode_guest
from bot import database
from config import BASE_URL, VERSIONS

router = Router()


@router.message(F.text == "❌ Bekor qilish")
async def cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=main_menu_kb())


@router.message(F.text == "👤 Maxsus havola yaratish")
async def start_guest_flow(message: Message, state: FSMContext) -> None:
    if message.from_user.id not in AUTHENTICATED:
        await message.answer("🔐 /start")
        return
    await state.set_state(GuestState.waiting_name_uz)
    await message.answer(
        "👤 *Mehmonning ismini kiriting*\n\n"
        "1️⃣ *O'zbek tilida:*\n"
        "_(Masalan: Akbar va Malika oilasi)_",
        parse_mode="Markdown",
        reply_markup=cancel_kb(),
    )


@router.message(GuestState.waiting_name_uz)
async def got_name_uz(message: Message, state: FSMContext) -> None:
    await state.update_data(name_uz=message.text.strip())
    await state.set_state(GuestState.waiting_name_ru)
    await message.answer(
        "2️⃣ *Rus tilida:*\n"
        "_(Masalan: Семья Акбар и Малика)_",
        parse_mode="Markdown",
        reply_markup=cancel_kb(),
    )


@router.message(GuestState.waiting_name_ru)
async def got_name_ru(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    name_uz = data["name_uz"]
    name_ru = message.text.strip()
    await state.clear()

    token = encode_guest(name_uz, name_ru)

    lines = [f"✅ *{name_uz}* / *{name_ru}*\n\nHavolalar:\n"]
    for v, label in VERSIONS.items():
        url = f"{BASE_URL}?v={v}&g={token}"
        lines.append(f"{label}\n`{url}`\n")

    await message.answer("\n".join(lines), parse_mode="Markdown", reply_markup=main_menu_kb())
    await database.log_action(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        action="created_guest_link",
        extra=f"{name_uz}|{name_ru}",
    )
