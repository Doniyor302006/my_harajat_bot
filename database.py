import sqlite3

def get_connection():
    return sqlite3.connect('smart_finance_bot.db', timeout=20)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # Foydalanuvchilar jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            daily_limit REAL DEFAULT 0,
            currency TEXT DEFAULT 'UZS'
        )
    ''')
    # Tranzaksiyalar jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT CHECK(type IN ('income', 'expense')), 
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            exchange_rate REAL DEFAULT 1.0,
            category TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_date ON transactions(user_id, date)')
    conn.commit()
    conn.close()

def add_transaction(user_id, t_type, amount, currency, rate, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (user_id, type, amount, currency, exchange_rate, category)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, t_type, amount, currency, rate, category))
    conn.commit()
    conn.close()

def delete_last_transaction(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM transactions WHERE user_id = ? ORDER BY date DESC LIMIT 1', (user_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute('DELETE FROM transactions WHERE id = ?', (row[0],))
        conn.commit()
        return True
    return False

def add_user(user_id, full_name):
    conn = get_connection()
    cursor = conn.cursor()
    # INSERT OR IGNORE - agar foydalanuvchi bazada bo'lsa, xato bermaydi
    cursor.execute('INSERT OR IGNORE INTO users (user_id, full_name) VALUES (?, ?)', (user_id, full_name))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()
    conn.close()
    return [u[0] for u in users] # ID-larni ro'yxat qilib qaytaradi