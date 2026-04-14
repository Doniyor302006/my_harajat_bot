import matplotlib.pyplot as plt # type: ignore
import pandas as pd # type: ignore
import sqlite3
import os

def create_reports_dir():
    if not os.path.exists('reports'):
        os.makedirs('reports')

def generate_chart(user_id):
    create_reports_dir()
    conn = sqlite3.connect('smart_finance_bot.db')
    df = pd.read_sql_query("SELECT category, amount FROM transactions WHERE user_id=? AND type='expense'", conn, params=(user_id,))
    conn.close()
    
    if df.empty: return None
    
    summary = df.groupby('category')['amount'].sum()
    plt.figure(figsize=(8,8))
    summary.plot(kind='pie', autopct='%1.1f%%', title="Xarajatlar")
    path = f"reports/chart_{user_id}.png"
    plt.savefig(path)
    plt.close()
    return path

def generate_excel(user_id):
    create_reports_dir()
    conn = sqlite3.connect('smart_finance_bot.db')
    df = pd.read_sql_query("SELECT * FROM transactions WHERE user_id=?", conn, params=(user_id,))
    conn.close()
    
    if df.empty: return None # Ma'lumot bo'lmasa None qaytaramiz
    
    path = f"reports/report_{user_id}.xlsx"
    # Df bo'sh bo'lmasa saqlaymiz
    df.to_excel(path, index=False, engine='openpyxl') 
    return path