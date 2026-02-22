import sqlite3
import pandas as pd
import requests

def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            category TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_expense(user_id, amount, category):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO expenses (user_id, amount, category) VALUES (?, ?, ?)', 
                   (user_id, amount, category))
    conn.commit()
    conn.close()

def get_today_expenses(user_id):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('SELECT amount, category FROM expenses WHERE user_id = ? AND date(date) = date("now")', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_last_expense(user_id):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM expenses WHERE id = (
            SELECT id FROM expenses WHERE user_id = ? 
            ORDER BY id DESC LIMIT 1
        )
    ''', (user_id,))
    conn.commit()
    conn.close()

def get_expense_stats(user_id):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('SELECT category, SUM(amount) FROM expenses WHERE user_id = ? GROUP BY category', (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_rates():
    try:
        url = "https://nbu.uz/uz/exchange-rates/json/"
        res = requests.get(url).json()
        rates = {item['code']: float(item['cb_price']) for item in res if item['code'] in ['USD', 'EUR', 'RUB']}
        return rates
    except:
        return {"USD": 12700, "EUR": 13800, "RUB": 145}