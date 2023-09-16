import logging
import sqlalchemy as sa
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, ContentTypes
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

bot = Bot(token="6487732130:AAGV4SiRUEnnVDVykWiSkAHG46Foizh5Mjk")

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

DATABASE_URL = "postgresql://aiogrambot:postgres@localhost:5432/aiogrambot"
engine = sa.create_engine(DATABASE_URL)

metadata = sa.MetaData()

users = sa.Table(
    'users', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('user_id', sa.Integer),
    sa.Column('name', sa.String),
    sa.Column('destination', sa.String),
)


class UserFormStates:
    WaitingForName = 'waiting_for_name'
    WaitingForDestination = 'waiting_for_destination'
    WaitingForPhone = 'waiting_phone'
    WaitingForAge = 'waiting_age'
    WaitingForDays = 'waiting_days'


@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    link_travel = "https://traveler.fly.dev"
    await message.answer(f"Здравствуйте, вас приветствует бот сайта <a href='{link_travel}'>TRAVELER</a>",
                         parse_mode="html")
    await message.answer("Введите ваше имя?")

    await state.set_state(UserFormStates.WaitingForName)


@dp.message_handler(state=UserFormStates.WaitingForName)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await message.answer("Отлично✅! Теперь укажите свой возраст.")
    await state.set_state(UserFormStates.WaitingForAge)


@dp.message_handler(state=UserFormStates.WaitingForAge)
async def process_age(message: types.Message, state: FSMContext):

    try:
        async with state.proxy() as data:
            data['age'] = int(message.text)
    except ValueError:
        await message.answer('🙂Возраст должен быть числом. Попробуй еще раз.')
        return

    user_data = await state.get_data()
    await message.answer(f"🙂Спасибо {user_data['name']}", parse_mode=ParseMode.MARKDOWN)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("📲Отправить номер", request_contact=True)
    markup.add(button)
    await message.answer("📲Пожалуйста отправьте ваш телефон номер, нажмите на кнопку отправить номер", reply_markup=markup)
    await state.set_state(UserFormStates.WaitingForPhone)


@dp.message_handler(state=UserFormStates.WaitingForPhone, content_types=ContentTypes.CONTACT)
async def phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.contact.phone_number

    await message.reply(f"Отлично✅! Куда хотите путешествовать?.")

    await state.set_state(UserFormStates.WaitingForDestination)


@dp.message_handler(state=UserFormStates.WaitingForDestination)
async def phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['days'] = message.text

    await message.reply(f"На сколько дней?")
    await state.set_state(UserFormStates.WaitingForDays)


@dp.message_handler(state=UserFormStates.WaitingForDays)
async def process_day(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['age'] = int(message.text)
    except ValueError:
        await message.answer('Пожалуйста пишите числами')
        return
    link_travel = "https://traveler.fly.dev"
    await message.answer(f"Спасибо! Ваше ответ сохранён, скоро с вами свяжется наш оператор.")
    await message.answer(f"Или бронируйте места через наш сайт <a href='{link_travel}'>TRAVELER</a>", parse_mode="html")

if __name__ == "__main__":
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
