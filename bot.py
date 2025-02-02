import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

# 🔹 Вставляем ТВОЙ Telegram ID
ADMIN_ID = 143274359  

# 🔹 Вставь свой токен от @BotFather
TOKEN = "7492007728:AAGSIL02Wkg059uj6lTcnyvn3RJ6ZlvEawQ"

# Настройки бота
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Включаем логирование
logging.basicConfig(level=logging.INFO)


# Определяем состояния для опроса пользователя
class Form(StatesGroup):
    experience = State()
    emotions = State()  # 🔥 Добавили вопрос про эмоции
    name = State()
    contact = State()


# ✅ Клавиатура выбора опыта
experience_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔰 Новичок")],
        [KeyboardButton(text="🎛 Уже пробовал")]
    ],
    resize_keyboard=True
)


# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await message.answer(
        "👋 Привет! Это *Shining DJ Academy*.\n\n"
        "Ответь на пару вопросов, и я подберу для тебя курс!",
        parse_mode="Markdown"
    )
    await message.answer("Какой у тебя уровень опыта в диджеинге?", reply_markup=experience_keyboard)
    await state.set_state(Form.experience)


# Вопрос про опыт
@dp.message(Form.experience)
async def process_experience(message: types.Message, state: FSMContext):
    user_experience = message.text
    await state.update_data(experience=user_experience)
    
    # 🔥 Новый эмоциональный вопрос
    await message.answer(
        "🔥 Представь, что ты выходишь на сцену. Зал полон, все ждут твоего первого трека.\n"
        "Какие эмоции ты хочешь испытать в этот момент?"
    )
    await state.set_state(Form.emotions)


# Вопрос про эмоции
@dp.message(Form.emotions)
async def process_emotions(message: types.Message, state: FSMContext):
    user_emotions = message.text
    await state.update_data(emotions=user_emotions)
    
    # Поддержка ответа пользователя
    await message.answer(f"💥 Это мощно! Мы научим тебя испытать эти эмоции по-настоящему! 🚀")
    
    # Переход к имени
    await message.answer("Теперь напиши свое *Имя*.", parse_mode="Markdown")
    await state.set_state(Form.name)


# Вопрос про имя
@dp.message(Form.name)
async def process_name(message: types.Message, state: FSMContext):
    user_name = message.text
    await state.update_data(name=user_name)
    await message.answer("Спасибо! Теперь отправь свой *номер телефона* 📲.", parse_mode="Markdown",
                         reply_markup=ReplyKeyboardMarkup(
                             keyboard=[[KeyboardButton(text="📞 Отправить контакт", request_contact=True)]],
                             resize_keyboard=True))
    await state.set_state(Form.contact)


# ✅ Обработка контакта с проверкой `get_chat()`
@dp.message(Form.contact, F.contact)
async def process_contact(message: types.Message, state: FSMContext):
    try:
        user_contact = message.contact.phone_number
        user_data = await state.get_data()

        # ✅ Проверяем, может ли бот отправлять сообщения админу
        try:
            chat_info = await bot.get_chat(ADMIN_ID)
            logging.info(f"✅ Бот имеет доступ к чату {chat_info.id} ({chat_info.type})")
        except Exception as e:
            logging.error(f"❌ Ошибка: бот НЕ МОЖЕТ отправлять сообщения админу! Проверь, не заблокирован ли бот.")
            await message.answer(
                "⚠️ Ошибка при отправке заявки. Возможно, бот не имеет доступа к чату с админом.\n"
                "Проверь, не заблокировал ли админ бота, и попробуй снова."
            )
            return

        # ✅ Отправляем сообщение админу
        admin_message = (
            f"📌 *Новая заявка!*\n"
            f"👤 Имя: {user_data.get('name', 'Не указано')}\n"
            f"🔥 Эмоции при выходе на сцену: {user_data.get('emotions', 'Не указано')}\n"
            f"🎛 Опыт: {user_data.get('experience', 'Не указано')}\n"
            f"📞 Контакт: {user_contact}"
        )

        await bot.send_message(ADMIN_ID, admin_message, parse_mode="Markdown")
        logging.info("✅ Сообщение админу успешно отправлено!")

        # Отправляем пользователю стоимость курсов
        price_message = (
            "🎛 *Стоимость курсов:*\n\n"
            "🎧 *Базовый курс:* 18 000 ₽\n"
            "🔥 *Продвинутый курс:* 30 000 ₽\n"
            "🚀 *Профессиональный курс:* 50 000 ₽\n\n"
            "📩 Наш менеджер скоро с тобой свяжется!"
        )
        await message.answer(price_message, parse_mode="Markdown")

        await state.clear()

    except Exception as e:
        logging.error(f"❌ Ошибка при отправке админу: {e}")
        await message.answer("⚠️ Ошибка при отправке заявки. Проверьте данные или попробуйте снова!")


# ✅ Исправленный запуск бота
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
