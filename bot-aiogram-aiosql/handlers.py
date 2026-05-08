from aiogram import Router
from aiogram.filters import CommandStart,Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext
from project.config import ADMIN_ID
import project.database.models as db



class Idea(StatesGroup):
    idea = State()

class Bots(StatesGroup):
    id = State()

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Бот для сбора идей Telegram-ботов.\nчтобы предложить свою идею напишите /idea")
    if message.from_user.id == ADMIN_ID:
        await message.answer("Здравствуйте администратор")

@router.message(Command('admin-help'))
async def admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Админ-команды:\n/bots - просмотр идей по ID")

@router.message(Command('idea'))
async def idea(message:Message,state:FSMContext):
    await state.set_state(Idea.idea)
    await message.answer( "Введите идею для Telegram-бота:\n\n"
        "текст должен быть чётко сформулирован\n"
        "без грамматических ошибок\n"
        "длина от 100 до 500 символов"
    )
@router.message(Idea.idea)
async def idea(message: Message,state: FSMContext):
    if 500 >= len(message.text) >= 100:
        await db.add(message.from_user.id,message.from_user.username,message.text)
        await message.answer("Спасибо за идею! Администратор рассмотрит её.")
        await state.clear()
    elif len(message.text) <= 99:
        await message.answer(f"Добавьте {100 - len(message.text)} символов (минимум 100).")
    elif len(message.text) >= 501:
        await message.answer(f"Уберите {len(message.text) - 500} символов (максимум 500).")

@router.message(Command('bots'))
async def bots(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await state.set_state(Bots.id)
        await message.answer("Введите ID заявки (число):")
    else:
        return

@router.message(Bots.id)
async def bots(message: Message, state: FSMContext):
    try:
        idea_id = int(message.text)
    except (IndexError, ValueError):
        await message.answer("Используйте: /bots <id>")
        return

    result = await db.read(idea_id)

    if result is None:
        await message.answer(f" Идея с ID {idea_id} не найдена")
        return


    user_id, username, idea, count = result

    await message.answer(f"Идея от пользователя: {username},ID: {user_id},\nидея:{idea},\nколичество идей:{count}")
    await state.clear()
