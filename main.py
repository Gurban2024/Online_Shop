import aiogram
from aiogram import filters, types, Bot, Dispatcher, F
import asyncio
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from config import TOKEN, ADMIN
from buttons.reply_keyboard import user_buttons, admin_button
from database import Database

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)
db = Database()

class ClothesStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_clothes_name = State()
    waiting_for_clothes_price = State()

class UpdateClothesStates(StatesGroup):
    waiting_for_old_item_name = State()
    waiting_for_category = State()
    waiting_for_new_item_name = State()
    waiting_for_new_item_price = State()

class DeleteClothesStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_item_name = State()

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def generate_item_buttons(items, category):
    buttons = []
    for item in items:
        buttons.append([KeyboardButton(text=f"{item[1]} - {item[2]} рублей", callback_data=f"{category}_{item[0]}")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

user_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Одежда')], [KeyboardButton(text='Обувь')],
        [KeyboardButton(text='Профиль')],
    ],
    resize_keyboard=True
)

admin_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить позицию')], [KeyboardButton(text='Все позиции')], 
        [KeyboardButton(text='Изменить')], [KeyboardButton(text='Удалить')], [KeyboardButton(text='Список пользователей')]
    ],
    resize_keyboard=True
)

@dp.message(filters.Command("start"))
async def start(message: types.Message):
    db.users_table()
    db.clothes_table()
    db.footwear_table()

    if message.from_user.id == ADMIN:
        await message.answer("Здравствуйте, Админ. Выберите опцию.", reply_markup=admin_button)
    else:
        await message.answer("Здравствуйте, вы попали в магазин одежды. Выберите опцию.", reply_markup=user_buttons)

    user_full_name = message.from_user.full_name or message.from_user.first_name or "User"
    user_id = message.from_user.id

    db.add_data(user_id, user_full_name)

@dp.message(F.text == "Добавить позицию")
async def add_clothes(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN:
        await message.answer("Выберите категорию: Одежда или Обувь")
        await state.set_state(ClothesStates.waiting_for_category)
    else:
        await message.answer("У вас нет прав на выполнение этого действия.")

@dp.message(ClothesStates.waiting_for_category)
async def category_received(message: types.Message, state: FSMContext):
    category = message.text.lower()
    if category == "одежда":
        await state.update_data(category="clothes")
    elif category == "обувь":
        await state.update_data(category="footwear")
    else:
        await message.answer("Неверный выбор. Пожалуйста, выберите категорию: Одежда или Обувь.")
        return
    await message.answer("Введите название позиции:")
    await state.set_state(ClothesStates.waiting_for_clothes_name)

@dp.message(ClothesStates.waiting_for_clothes_name)
async def clothes_name_received(message: types.Message, state: FSMContext):
    await state.update_data(clothes_name=message.text)
    await message.answer("Введите цену позиции:")
    await state.set_state(ClothesStates.waiting_for_clothes_price)

@dp.message(ClothesStates.waiting_for_clothes_price)
async def clothes_price_received(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    clothes_name = user_data['clothes_name']
    clothes_price = int(message.text)
    category = user_data.get('category')

    if category == "clothes":
        db.add_data_to_clothes(clothes_name, clothes_price)
    elif category == "footwear":
        db.add_data_to_footwear(clothes_name, clothes_price)

    await message.answer(f"Позиция '{clothes_name}' добавлена с ценой {clothes_price}.", reply_markup=admin_button)
    await state.clear()

@dp.message(F.text == "Все позиции")
async def show_all_clothes(message: types.Message):
    clothes = db.all_data_clothes()
    footwear = db.all_data_footwear()
    if clothes or footwear:
        response = ""
        if clothes:
            response += "\n".join([f"Одежда: {item[1]} - {item[2]} рублей" for item in clothes]) + "\n"
        if footwear:
            response += "\n".join([f"Обувь: {item[1]} - {item[2]} рублей" for item in footwear])
    else:
        response = "Товары отсутствуют."
    await message.answer(response)

@dp.message(F.text == "Изменить")
async def update_clothes(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN:
        await message.answer("Введите название позиции, которую хотите изменить:")
        await state.set_state(UpdateClothesStates.waiting_for_old_item_name)
    else:
        await message.answer("У вас нет прав на выполнение этого действия.")

@dp.message(UpdateClothesStates.waiting_for_old_item_name)
async def old_item_name_received(message: types.Message, state: FSMContext):
    await state.update_data(old_item_name=message.text)
    await message.answer("Введите новую категорию позиции:\n1. Одежда\n2. Обувь")
    await state.set_state(UpdateClothesStates.waiting_for_category)

@dp.message(UpdateClothesStates.waiting_for_category)
async def category_for_update_received(message: types.Message, state: FSMContext):
    category = message.text.lower()
    if category == "одежда":
        await state.update_data(category="clothes")
    elif category == "обувь":
        await state.update_data(category="footwear")
    else:
        await message.answer("Неверный выбор. Пожалуйста, выберите категорию: Одежда или Обувь.")
        return
    await message.answer("Введите новое название позиции:")
    await state.set_state(UpdateClothesStates.waiting_for_new_item_name)

@dp.message(UpdateClothesStates.waiting_for_new_item_name)
async def new_item_name_received(message: types.Message, state: FSMContext):
    await state.update_data(new_item_name=message.text)
    await message.answer("Введите новую цену позиции:")
    await state.set_state(UpdateClothesStates.waiting_for_new_item_price)

@dp.message(UpdateClothesStates.waiting_for_new_item_price)
async def new_item_price_received(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    old_name = user_data.get('old_item_name')
    new_name = user_data.get('new_item_name')
    new_price = int(message.text)
    category = user_data.get('category')

    if category == "clothes":
        db.update_clothes(old_name, new_name, new_price)
    elif category == "footwear":
        db.update_footwear(old_name, new_name, new_price)

    await message.answer(f"Позиция '{old_name}' изменена на '{new_name}' с новой ценой {new_price}.", reply_markup=admin_button)
    await state.clear()

@dp.message(F.text == "Удалить")
async def delete_clothes(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN:
        await message.answer("Введите категорию позиции для удаления:\n1. Одежда\n2. Обувь")
        await state.set_state(DeleteClothesStates.waiting_for_category)
    else:
        await message.answer("У вас нет прав на выполнение этого действия.")

@dp.message(DeleteClothesStates.waiting_for_category)
async def category_for_delete_received(message: types.Message, state: FSMContext):
    category = message.text.lower()
    if category == "одежда":
        await state.update_data(category="clothes")
    elif category == "обувь":
        await state.update_data(category="footwear")
    else:
        await message.answer("Неверный выбор. Пожалуйста, выберите категорию: Одежда или Обувь.")
        return
    await message.answer("Введите название позиции для удаления:")
    await state.set_state(DeleteClothesStates.waiting_for_item_name)

@dp.message(DeleteClothesStates.waiting_for_item_name)
async def item_name_to_delete(message: types.Message, state: FSMContext):
    item_name = message.text
    category = (await state.get_data()).get('category')

    if category == "clothes":
        db.delete_clothes(item_name)
    elif category == "footwear":
        db.delete_footwear(item_name)

    await message.answer(f"Позиция '{item_name}' была удалена.", reply_markup=admin_button)
    await state.clear()

@dp.message(F.text == "Список пользователей")
async def list_users(message: types.Message):
    if message.from_user.id == ADMIN:
        users = db.all_data_users()
        if users:
            response = "\n".join([f"ID: {user[0]}, Имя: {user[1]}" for user in users])
        else:
            response = "Пользователи отсутствуют."
        await message.answer(response)
    else:
        await message.answer("У вас нет прав на выполнение этого действия.")

@dp.message(F.text == "Одежда")
async def show_clothes(message: types.Message):
    clothes = db.all_data_clothes()
    if clothes:
        clothes_buttons = generate_item_buttons(clothes, "clothes")
        await message.answer("Вот доступная одежда:", reply_markup=clothes_buttons)
    else:
        await message.answer("Нет доступных товаров.")

@dp.message(F.text == "Обувь")
async def show_footwear(message: types.Message):
    footwear = db.all_data_footwear()
    if footwear:
        footwear_buttons = generate_item_buttons(footwear, "footwear")
        await message.answer("Вот доступная обувь:", reply_markup=footwear_buttons)
    else:
        await message.answer("Нет доступных товаров.")

@dp.callback_query(lambda c: c.data.startswith("clothes_") or c.data.startswith("footwear_"))
async def process_item_selection(callback_query: types.CallbackQuery):
    category, item_id = callback_query.data.split("_", 1)
    
    if category == "clothes":
        item = next((x for x in db.all_data_clothes() if str(x[0]) == item_id), None)
    elif category == "footwear":
        item = next((x for x in db.all_data_footwear() if str(x[0]) == item_id), None)
    
    if item:
        item_name = item[1]
        item_price = item[2]
        await bot.send_message(
            callback_query.from_user.id,
            f"Спасибо за покупку! Вы купили {item_name} по цене {item_price} рублей."
        )
    else:
        await bot.send_message(
            callback_query.from_user.id,
            "Не удалось найти выбранный товар."
        )

@dp.message(F.text == "Профиль")
async def show_profile(message: types.Message):
    user_id = message.from_user.id
    user_data = db.get_user_data(user_id)
    
    if user_data:
        if len(user_data) == 2:
            user_id, full_name = user_data
            profile_info = (
                f"ID: {user_id}\n"
                f"Имя: {full_name}"
            )
        else:
            profile_info = "Не удалось получить правильную информацию о вашем профиле."
    else:
        profile_info = "Не удалось найти информацию о вашем профиле."
    
    await message.answer(profile_info, reply_markup=user_buttons)

@dp.message()
async def process_text_message(message: types.Message):
    user_text = message.text.lower().strip()  

    if " - " in user_text:
        user_text = user_text.split(" - ")[0].strip() 
        
    clothes = db.all_data_clothes()
    footwear = db.all_data_footwear()

    for item in clothes:
        if user_text == item[1].lower().strip():
            await message.answer(f"Спасибо за покупку! Вы купили {item[1]} по цене {item[2]} рублей.", reply_markup=user_buttons)
            return

    for item in footwear:
        if user_text == item[1].lower().strip():
            await message.answer(f"Спасибо за покупку! Вы купили {item[1]} по цене {item[2]} рублей.", reply_markup=user_buttons)
            return

    await message.answer("Извините, товар не найден. Пожалуйста, попробуйте снова.", reply_markup=user_buttons)





async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
