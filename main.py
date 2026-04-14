import asyncio
from aiogram import Bot, Dispatcher, types, F # pyright: ignore[reportMissingImports]
from aiogram.filters import Command # pyright: ignore[reportMissingImports]
import aiogram.types # pyright: ignore[reportMissingImports]
import database, utils, visuals



TOKEN = "8094220593:AAGDnYRmLgkjXhVDI97FSNEq3XcyMxuYEAE"
bot = Bot(token=TOKEN)
dp = Dispatcher()

ADMIN_ID = 7845822609  # <--- O'zingizning ID raqamingizni yozing!

class AdminState:
    is_broadcasting = False

@dp.message(Command("start"))
async def start(message: types.Message):
    database.init_db()
    # Foydalanuvchini bazaga ro'yxatga olamiz
    database.add_user(message.from_user.id, message.from_user.full_name)
    
    kb = [
        [types.KeyboardButton(text="📊 Hisobot"), types.KeyboardButton(text="❌ Xatoni o'chirish")],
        [types.KeyboardButton(text="📄 Excel yuklash")]
    ]
    markup = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(f"Assalomu alaykum {message.from_user.full_name}!", reply_markup=markup)
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Admin panel:\n/reklama - Xabar yuborish\n/stats - Statistika")

@dp.message(Command("stats"))
async def get_stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        users = database.get_all_users()
        await message.answer(f"Bot a'zolari: {len(users)} ta")

@dp.message(Command("reklama"))
async def start_broadcast(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        AdminState.is_broadcasting = True
        await message.answer("Reklama xabarini yuboring (rasm, matn yoki video)...")

@dp.message(F.text == "❌ Xatoni o'chirish")
async def delete_item(message: types.Message):
    if database.delete_last_transaction(message.from_user.id):
        await message.answer("✅ Oxirgi amal o'chirildi.")
    else:
        await message.answer("⚠️ O'chirish uchun ma'lumot topilmadi.")

@dp.message(F.text == "📊 Hisobot")
async def send_chart(message: types.Message):
    path = visuals.generate_chart(message.from_user.id)
    if path:
        await message.answer_photo(aiogram.types.FSInputFile(path), caption="Sizning xarajatlaringiz grafigi")
    else:
        await message.answer("❌ Hisobot uchun ma'lumot yetarli emas. Avval xarajatlarni kiriting.")

@dp.message(F.text == "📄 Excel yuklash")
async def send_excel(message: types.Message):
    path = visuals.generate_excel(message.from_user.id)
    if path:
        await message.answer_document(aiogram.types.FSInputFile(path), caption="Barcha tranzaksiyalar tarixi")
    else:
        await message.answer("❌ Ma'lumotlar topilmadi.")

@dp.message()
async def handle_all(message: types.Message):
    # REKLAMA QISMI
    if AdminState.is_broadcasting and message.from_user.id == ADMIN_ID:
        users = database.get_all_users()
        count = 0
        for user_id in users:
            try:
                await message.copy_to(chat_id=user_id)
                count += 1
                await asyncio.sleep(0.05)
            except:
                pass
        AdminState.is_broadcasting = False
        await message.answer(f"Xabar {count} kishiga yetkazildi!")
        return

    # XARAJATLAR QISMI (avvalgi kodingiz shu yerda davom etadi)
    amount, curr, cat = utils.parse_message(message.text)
    # ... qolgan kodlar

@dp.message()
async def handle_all(message: types.Message):
    if not message.text: return
    
    amount, curr, cat = utils.parse_message(message.text)
    if amount:
        database.add_transaction(message.from_user.id, 'expense', amount, curr, 1.0, cat)
        # Endi bu yerda cat = "osh" bo'ladi
        await message.answer(f"✅ Saqlandi!\n💰 Miqdor: {amount:,} {curr}\n📝 Nima uchun: {cat}")
    else:
        await message.answer("❓ Miqdor va sababni yozing.\nMasalan: '5000 osh'")

async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi.")