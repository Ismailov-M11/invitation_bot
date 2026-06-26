from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards import main_menu_kb
from bot.session import AUTHENTICATED
from bot.states import AuthState
from config import PASSWORD

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    if message.from_user.id in AUTHENTICATED:
        await message.answer("✅ Xush kelibsiz!", reply_markup=main_menu_kb())
        return
    await state.set_state(AuthState.waiting_password)
    await message.answer(
        "🔐 *To'y taklifnomasi boti*\n\n"
        "Botdan foydalanish uchun parolni kiriting:",
        parse_mode="Markdown",
    )


@router.message(AuthState.waiting_password, ~Command())
async def check_password(message: Message, state: FSMContext) -> None:
    if message.text == PASSWORD:
        AUTHENTICATED.add(message.from_user.id)
        await state.clear()
        await message.answer(
            "✅ Parol to'g'ri! Xush kelibsiz 🎊\n\n"
            "Quyidagi buyruqlardan foydalaning:",
            reply_markup=main_menu_kb(),
        )
    else:
        await message.answer("❌ Parol noto'g'ri. Qaytadan urining:")
