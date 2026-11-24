import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import config
import database as db

# Log sozlamalari
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Holatlar (States)
class BookForm(StatesGroup):
    waiting_for_doc = State()
    waiting_for_title = State()
    waiting_for_author = State()
    waiting_for_section = State()

class SearchForm(StatesGroup):
    waiting_for_query = State()

class RequestForm(StatesGroup):
    waiting_for_text = State()

# Asosiy menyu klaviaturasi
def get_main_menu(is_admin=False):
    kb = [
        [KeyboardButton(text="🎓 Kurslar bo'yicha darsliklar")],
        [KeyboardButton(text="📚 Elektron kutubxona"), KeyboardButton(text="🔍 Kitob qidirish")],
        [KeyboardButton(text="📝 Kitob so'rash"), KeyboardButton(text="ℹ️ ARM haqida")]
    ]
    if is_admin:
        kb.append([KeyboardButton(text="⚙️ Admin Panel")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# Kurslar klaviaturasi (Inline)
def get_courses_keyboard():
    courses = db.get_courses()
    buttons = []
    for c in courses:
        buttons.append([InlineKeyboardButton(text=f"📚 {c['name']}", callback_data=f"course_{c['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Umumiy kutubxona bo'limlari klaviaturasi
def get_library_keyboard():
    categories = db.get_library_categories()
    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(text=cat['name'], callback_data=f"category_{cat['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# START buyrug'i
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    db.add_user(user.id, user.full_name, user.username)
    is_admin = user.id in config.ADMIN_IDS
    
    await message.answer(
        f"Assalomu alaykum, {user.first_name}!\n\n"
        "🏛 **Axborot-Resurs Markazi (ARM) elektron kutubxonasiga xush kelibsiz!**\n\n"
        "Bu bot orqali siz o'z kursingizga tegishli barcha darsliklarni, "
        "badiiy va ilmiy adabiyotlarni topishingiz va yuklab olishingiz mumkin.\n\n"
        "Kerakli bo'limni quyidagi menyudan tanlang:",
        reply_markup=get_main_menu(is_admin),
        parse_mode="Markdown"
    )

# 1. Kurslar bo'limi
@dp.message(F.text == "🎓 Kurslar bo'yicha darsliklar")
async def show_courses(message: types.Message):
    await message.answer(
        "🎓 **Iltimos, o'zingiz o'qiydigan kursni tanlang:**\n"
        "Siz tanlagan kursga tegishli barcha darslik va qo'llanmalar ro'yxati chiqadi.",
        reply_markup=get_courses_keyboard(),
        parse_mode="Markdown"
    )

# Kurs tanlanganda kitoblar ro'yxati
@dp.callback_query(F.data.startswith("course_"))
async def on_course_selected(callback: types.CallbackQuery):
    course_id = int(callback.data.split("_")[1])
    books = db.get_books_by_course(course_id)
    
    if not books:
        await callback.message.edit_text(
            "⚠️ Ushbu kurs uchun hozircha elektron kitoblar yuklanmagan.\n"
            "Tez orada ARM xodimlari tomonidan kitoblar joylanadi.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Kurslarga qaytish", callback_data="back_to_courses")]
            ])
        )
        return

    buttons = []
    for b in books:
        author_name = b['author'] if b['author'] else "Muallif ko'rsatilmagan"
        btn_text = f"📖 {b['title']} ({author_name})"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"getbook_{b['id']}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Kurslarga qaytish", callback_data="back_to_courses")])

    await callback.message.edit_text(
        "📚 **Ushbu kursga tegishli elektron kitoblar:**\n"
        "Yuklab olish uchun kitob ustiga bosing:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "back_to_courses")
async def back_to_courses(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🎓 **Iltimos, o'zingiz o'qiydigan kursni tanlang:**",
        reply_markup=get_courses_keyboard(),
        parse_mode="Markdown"
    )

# 2. Umumiy elektron kutubxona bo'limi
@dp.message(F.text == "📚 Elektron kutubxona")
async def show_library(message: types.Message):
    await message.answer(
        "📚 **Elektron kutubxona bo'limlari:**\n"
        "Qaysi yo'nalishdagi adabiyotlarni o'qimoqchisiz?",
        reply_markup=get_library_keyboard(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("category_"))
async def on_category_selected(callback: types.CallbackQuery):
    cat_id = int(callback.data.split("_")[1])
    books = db.get_books_by_category(cat_id)

    if not books:
        await callback.message.edit_text(
            "⚠️ Ushbu bo'limda hozircha kitoblar yo'q.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Bo'limlarga qaytish", callback_data="back_to_library")]
            ])
        )
        return

    buttons = []
    for b in books:
        btn_text = f"📖 {b['title']} ({b['author'] or ''})"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"getbook_{b['id']}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Bo'limlarga qaytish", callback_data="back_to_library")])

    await callback.message.edit_text(
        "📖 **Bo'lim kitoblari:**\nYuklab olish uchun tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "back_to_library")
async def back_to_library(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📚 **Elektron kutubxona bo'limlari:**",
        reply_markup=get_library_keyboard(),
        parse_mode="Markdown"
    )

# Kitobni yuborish
@dp.callback_query(F.data.startswith("getbook_"))
async def send_book_file(callback: types.CallbackQuery):
    book_id = int(callback.data.split("_")[1])
    book = db.get_book_by_id(book_id)

    if not book:
        await callback.answer("Kechirasiz, bu kitob topilmadi!", show_alert=True)
        return

    author_str = book['author'] if book['author'] else "Noma'lum"
    desc_str = f"📝 {book['description']}\n" if book['description'] else ""
    caption = (
        f"📖 **Kitob:** {book['title']}\n"
        f"✍️ **Muallif:** {author_str}\n"
        f"📥 **Yuklab olingan:** {book['downloads_count']} marta\n"
        f"{desc_str}\n"
        "🏛 *Axborot-Resurs Markazi (ARM)*"
    )

    await callback.message.answer_document(
        document=book['file_id'],
        caption=caption,
        parse_mode="Markdown"
    )
    await callback.answer("Kitob yuborildi!")

# 3. Kitob qidirish
@dp.message(F.text == "🔍 Kitob qidirish")
async def start_search(message: types.Message, state: FSMContext):
    await state.set_state(SearchForm.waiting_for_query)
    await message.answer("🔍 Qidirayotgan kitobingiz nomini yoki muallifini yozib yuboring:")

@dp.message(SearchForm.waiting_for_query)
async def process_search(message: types.Message, state: FSMContext):
    query = message.text.strip()
    await state.clear()
    
    results = db.search_books(query)
    if not results:
        await message.answer(
            f"🔍 '{query}' bo'yicha hech qanday kitob topilmadi.\n"
            "Agar kitob bazada bo'lmasa, '📝 Kitob so'rash' bo'limi orqali ARM xodimlariga buyurtma qoldirishingiz mumkin."
        )
        return

    buttons = []
    for b in results:
        btn_text = f"📖 {b['title']} - {b['author'] or ''}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"getbook_{b['id']}")])

    await message.answer(
        f"🔍 **'{query}' bo'yicha topilgan kitoblar:**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="Markdown"
    )

# 4. Kitob so'rash (Buyurtma qoldirish)
@dp.message(F.text == "📝 Kitob so'rash")
async def request_book(message: types.Message, state: FSMContext):
    await state.set_state(RequestForm.waiting_for_text)
    await message.answer(
        "📝 O'zingizga kerakli bo'lgan, lekin botda topilmagan kitob nomi, muallifi va qaysi kursda o'qishingizni yozib qoldiring.\n\n"
        "ARM xodimlari bu kitobni topib, bazaga joylashadi."
    )

@dp.message(RequestForm.waiting_for_text)
async def process_request(message: types.Message, state: FSMContext):
    req_text = message.text.strip()
    user_id = message.from_user.id
    db.add_book_request(user_id, req_text)
    await state.clear()
    
    await message.answer("✅ Rahmat! So'rovingiz qabul qilindi. Tez orada ARM xodimlari uni ko'rib chiqishadi.")
    
    # Adminlarga xabar berish
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"🔔 **Yangi kitob so'rovi!**\n"
                f"👤 Foydalanuvchi: {message.from_user.full_name} (@{message.from_user.username})\n"
                f"📝 So'rov: {req_text}",
                parse_mode="Markdown"
            )
        except Exception:
            pass

# 5. ARM Haqida
@dp.message(F.text == "ℹ️ ARM haqida")
async def arm_info(message: types.Message):
    await message.answer(
        "🏛 **Axborot-Resurs Markazi (ARM)**\n\n"
        "Bizning vazifamiz talabalar va o'qituvchilarni zarur darsliklar, "
        "qo'llanmalar va ilmiy adabiyotlar bilan ta'minlashdan iborat.\n\n"
        "🕒 Ish vaqti: 08:30 dan 18:00 gacha\n"
        "📍 Manzil: Asosiy bino, ARM zali"
    )

# 6. Admin Panel
@dp.message(F.text == "⚙️ Admin Panel")
async def admin_panel(message: types.Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("Kechirasiz, siz admin emassiz.")
        return

    stats = db.get_stats()
    text = (
        "⚙️ **ARM Boshqaruv Paneli (Admin)**\n\n"
        f"👥 Foydalanuvchilar: {stats['users']} ta\n"
        f"📚 Jami kitoblar: {stats['books']} ta\n"
        f"📥 Jami yuklab olingan: {stats['downloads']} marta\n"
        f"📝 Talabalar so'rovlari: {stats['requests']} ta\n\n"
        "Yangi kitob qo'shish uchun quyidagi tugmani bosing:"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yangi kitob qo'shish", callback_data="admin_add_book")],
    ])
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "admin_add_book")
async def start_add_book(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in config.ADMIN_IDS:
        return
    await state.set_state(BookForm.waiting_for_doc)
    await callback.message.answer("📄 Iltimos, kitob faylini (PDF yoki DOCX formatda) yuboring:")
    await callback.answer()

@dp.message(BookForm.waiting_for_doc, F.document)
async def process_doc(message: types.Message, state: FSMContext):
    doc = message.document
    await state.update_data(file_id=doc.file_id, file_name=doc.file_name)
    await state.set_state(BookForm.waiting_for_title)
    await message.answer("✍️ Kitob nomini kiriting:")

@dp.message(BookForm.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(BookForm.waiting_for_author)
    await message.answer("✍️ Kitob muallifini kiriting (yoki 'Noma\\'lum' deb yozing):")

@dp.message(BookForm.waiting_for_author)
async def process_author(message: types.Message, state: FSMContext):
    await state.update_data(author=message.text.strip())
    await state.set_state(BookForm.waiting_for_section)
    
    # Bo'limni tanlash
    buttons = [
        [InlineKeyboardButton(text="1-kurs", callback_data="sec_c_1"), InlineKeyboardButton(text="2-kurs", callback_data="sec_c_2")],
        [InlineKeyboardButton(text="3-kurs", callback_data="sec_c_3"), InlineKeyboardButton(text="4-kurs", callback_data="sec_c_4")],
        [InlineKeyboardButton(text="Magistratura", callback_data="sec_c_5")],
        [InlineKeyboardButton(text="📖 Badiiy adabiyot", callback_data="sec_l_1")],
        [InlineKeyboardButton(text="🔬 Ilmiy adabiyot", callback_data="sec_l_2")],
        [InlineKeyboardButton(text="💻 Dasturlash / IT", callback_data="sec_l_4")]
    ]
    await message.answer("🎯 Bu kitob qaysi bo'lim yoki kursga tegishli?", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(BookForm.waiting_for_section, F.data.startswith("sec_"))
async def finalize_add_book(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    sec_code = callback.data # sec_c_1 yoki sec_l_1
    parts = sec_code.split("_")
    
    course_id = None
    category_id = None
    if parts[1] == "c":
        course_id = int(parts[2])
    else:
        category_id = int(parts[2])

    db.add_book(
        title=data['title'],
        author=data['author'],
        course_id=course_id,
        category_id=category_id,
        file_id=data['file_id'],
        file_name=data['file_name']
    )
    await state.clear()
    await callback.message.answer("🎉 Kitob muvaffaqiyatli bazaga qo'shildi va talabalar uchun ochiq!")
    await callback.answer()

async def main():
    print("ARM Telegram Boti ishga tushmoqda...")
    db.init_db()
    
    # Telegram xavfsizlik cheklovlariga tushmaslik uchun
    while True:
        try:
            print("Telegramga ulanish...")
            await dp.start_polling(bot, polling_timeout=30)
            break
        except Exception as e:
            print(f"Kutilmoqda: {e}")
            await asyncio.sleep(35)

if __name__ == "__main__":
    asyncio.run(main())
