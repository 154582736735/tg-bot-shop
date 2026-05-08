from aiogram import Router,F
from aiogram.filters import CommandStart,Command
from aiogram.types import Message, CallbackQuery
from aiogram_templates.keyboards import main_reply, main_inline, contact
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext
router = Router()

class Reg(StatesGroup):
    name = State()
    number = State()

@router.message(CommandStart())
async def start_mess(message: Message,state: FSMContext):
    await state.clear()
    await message.reply(f"Привет {message.from_user.first_name}!",reply_markup=main_inline)

@router.message(Command("help"))
async def help_message(message: Message):
    await message.answer("это команда /help")

@router.message(F.text == "Как дела?")
async def ok(message: Message):
    await message.reply("OK!")

@router.message(F.photo)
async def photo(message: Message):
    await message.reply(f"ID:{message.photo[-1].file_id}")
    await message.answer_photo(photo="https://th.bing.com/th/id/R.6479027fd8ece4e9179da91fc3e6f2b6?rik=N9dWMoc1pmqbdA&riu=http%3a%2f%2fpngimg.com%2fuploads%2ftelegram%2ftelegram_PNG34.png&ehk=9b0L6qAOL1YMPYBg0z60RHRZJFB71xQbIKog3VdZS6o%3d&risl=&pid=ImgRaw&r=0",
                               caption="Это фото тг")

@router.callback_query(F.data == "button_1")
async def callbacker(callback: CallbackQuery):
    await callback.answer("Вы выбрали кнопку 1",show_alert=True)
    await callback.message.answer("ответ на кнопку 1",reply_markup=main_reply)

@router.message(Command("reg"))
async def reg_one(message: Message,state: FSMContext):
    await state.set_state(Reg.name)
    await message.answer("Введите ваше имя!!!")

@router.message(Reg.name)
async def reg_two(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.number)
    await message.answer("Введите номер телефона",reply_markup=contact)

@router.message(Reg.number,F.contact)
async def two_three(message: Message,state: FSMContext):

    number = message.contact.phone_number
    await state.update_data(number=number)
    data = await state.get_data()
    await state.clear()
    await message.answer(f"Регистрация завершена. \nИмя {data['name']},\nНомер {data['number']}")
