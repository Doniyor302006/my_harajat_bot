import logging
import asyncio
import os
import matplotlib.pyplot as plt
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import FSInputFile
import pandas as pd
import sqlite3

# database.py dan funksiyalarni import qilish
from database import init_db, add_expense, get_today_expenses, delete_last_expense, get_expense_stats, get_rates

# TOKENNI SHU YERGA QO'YING
TOKEN = "8094220593:AAGDnYRmLgkjXhVDI97FSNEq3XcyMxuYEAE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📊 Bugungi ro'yxat")
    builder.button(text="📈 Grafik hisobot")
    builder.button(text="💱 Valyuta kursi")
    builder.button(text="📁 Excel hisobot")
    builder.button(text="❌ Oxirgisini o'chirish")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    init_db()
    await message.answer("Xush kelibsiz! \n\n🔹 **Xarajat qo'shish:** `20000 tushlik` \n🔹 **Konvertatsiya:** `10 $` yoki `100000 sum`", 
                         reply_markup=main_menu())

@dp.message(F.text == "📊 Bugungi ro'yxat")
async def today_report(message: types.Message):
    expenses = get_today_expenses(message.from_user.id)
    if not expenses:
        return await message.answer("Bugun hali xarajat kiritmadingiz.")
    report = "📑 **Bugungi xarajatlar:**\n\n"
    total = 0
    for amt, cat in expenses:
        report += f"• {cat}: {amt:,} so'm\n"
        total += amt
    report += f"\n**Jami: {total:,} so'm**"
    await message.answer(report, parse_mode="Markdown")

@dp.message(F.text == "❌ Oxirgisini o'chirish")
async def delete_cmd(message: types.Message):
    delete_last_expense(message.from_user.id)
    await message.answer("✅ Oxirgi kiritilgan xarajat o'chirildi!")

@dp.message(F.text == "💱 Valyuta kursi")
async def curr_cmd(message: types.Message):
    rates = get_rates()
    text = (f"🏦 **Markaziy Bank Kurslari:**\n\n"
            f"🇺🇸 1 USD = {rates['USD']:,} so'm\n"
            f"🇪🇺 1 EUR = {rates['EUR']:,} so'm\n"
            f"🇷🇺 1 RUB = {rates['RUB']:,} so'm")
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "📁 Excel hisobot")
async def send_excel(message: types.Message):
    conn = sqlite3.connect('expenses.db')
    df = pd.read_sql_query(f"SELECT date as Sana, category as Tur, amount as Summa FROM expenses WHERE user_id={message.from_user.id}", conn)
    conn.close()
    if df.empty: return await message.answer("Hali hech qanday ma'lumot yo'q.")
    path = f"report_{message.from_user.id}.xlsx"
    df.to_excel(path, index=False)
    await message.answer_document(FSInputFile(path))
    os.remove(path)

@dp.message(F.text == "📈 Grafik hisobot")
async def send_graph(message: types.Message):
    stats = get_expense_stats(message.from_user.id)
    if not stats: return await message.answer("Grafik chizish uchun ma'lumot yetarli emas.")
    plt.figure(figsize=(6,6))
    plt.pie([s[1] for s in stats], labels=[s[0] for s in stats], autopct='%1.1f%%', startangle=140)
    plt.title("Xarajatlar tahlili")
    path = f"g_{message.from_user.id}.png"
    plt.savefig(path); plt.close()
    await message.answer_photo(FSInputFile(path))
    os.remove(path)

@dp.message()
async def universal_handler(message: types.Message):
    text = message.text.lower().replace(" ", "").replace(",", "")
    rates = get_rates()
    
    try:
        # 1. Valyutadan So'mga (masalan: 10$, 50eur, 100rub)
        if any(x in text for x in ['$', 'usd', 'eur', '€', 'rub']):
            if '$' in text or 'usd' in text:
                val = float(text.replace('$', '').replace('usd', ''))
                return await message.reply(f"🇺🇸 {val:,} $ = {val * rates['USD']:,} so'm")
            elif '€' in text or 'eur' in text:
                val = float(text.replace('€', '').replace('eur', ''))
                return await message.reply(f"🇪🇺 {val:,} € = {val * rates['EUR']:,} so'm")
            elif 'rub' in text:
                val = float(text.replace('rub', ''))
                return await message.reply(f"🇷🇺 {val:,} RUB = {val * rates['RUB']:,} so'm")

        # 2. So'mdan Valyutaga (masalan: 100000sum yoki 100000so'm)
        if 'sum' in text or "so'm" in text:
            val_str = text.replace('sum', '').replace("so'm", "")
            val = float(val_str)
            return await message.reply(
                f"💰 **{val:,} so'mning qiymati:**\n\n"
                f"🇺🇸 {(val/rates['USD']):.2f} $\n"
                f"🇪🇺 {(val/rates['EUR']):.2f} €\n"
                f"🇷🇺 {(val/rates['RUB']):.2f} RUB",
                parse_mode="Markdown"
            )

        # 3. Oddiy xarajat qo'shish
        parts = message.text.split(maxsplit=1)
        amt = int(parts[0].replace(" ", ""))
        cat = parts[1] if len(parts) > 1 else "Boshqa"
        add_expense(message.from_user.id, amt, cat)
        await message.reply(f"✅ Saqlandi: **{amt:,} so'm** ({cat})", parse_mode="Markdown")
        
    except Exception:
        await message.reply("⚠️ Xato! \n\nMisol: \n`50000 bozor` \n`10 $` \n`250000 sum` ")

async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())