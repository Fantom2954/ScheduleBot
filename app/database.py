import sqlite3 as sq
from dotenv import load_dotenv
import os

def connect_to_db():
    conn = sq.connect('database.db')
    return conn

db = sq.connect('database.db')
cur = db.cursor()

conn = sq.connect('database.db')
cur = conn.cursor()


cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        status INTEGER DEFAULT 1,  -- 1: User, 2: Admin
        group_name TEXT
    )
""")
conn.commit()

async def cmdstart(user_id, username):
    conn = sq.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cur.fetchone()

    if not user:
        # Новый пользователь - изначально группа не назначена
        status = 1
        cur.execute("INSERT INTO users (user_id, username, status) VALUES (?, ?, ?)",
                    (user_id, username, status))
        conn.commit()
    else:
        # Пользователь есть - при необходимости обновить имя пользователя
        if user[1] != username:
            cur.execute("UPDATE users SET username=? WHERE user_id=?", (username, user_id))
            conn.commit()

#admin
def get_admin_ids():
    try:
        conn = sq.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE status=2")
        admin_ids = [str(row[0]) for row in cursor.fetchall()]
        return admin_ids
    except Exception as e:
        print(f"Error getting admin IDs: {e}")
        return []
    finally:
        if conn:
            conn.close()

async def get_user_group(user_id):
    cursor = db.cursor()
    cursor.execute("SELECT group_name FROM users WHERE user_id = ?", (user_id,))  # Выбрать group_name
    result = cursor.fetchone()
    return result[0] if result else None

async def save_user_group(user_id, group_name):  # Изменили параметр на group_name
    try:
        cursor = db.cursor()
        # Проверяем, существует ли запись для данного пользователя
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        user_exists = cursor.fetchone()

        if user_exists:
            # Если пользователь существует, обновляем группу
            cursor.execute("UPDATE users SET group_name = ? WHERE user_id = ?", (group_name, user_id))
        else:
            # Если пользователя не существует, вставляем новую запись
            cursor.execute("INSERT INTO users (user_id, group_name) VALUES (?, ?)", (user_id, group_name))
        db.commit()  # Фиксация изменений с использованием глобального соединения db
        return True
    except Exception as e:
        print(f"Ошибка при сохранении группы пользователя: {e}")
        return False

async def approve_group_change(user_id, group_name):  
    cursor = db.cursor()
    cursor.execute("UPDATE users SET group_name=? WHERE user_id=?", (group_name, user_id)) 
    db.commit()
    return True

async def decline_group_change(user_id):
    cursor = db.cursor()
    cursor.execute("UPDATE users SET group_name=NULL WHERE user_id=?", (user_id,))
    db.commit()
    return True

async def get_all_applications():
    """
    Возвращает список всех заявок из таблицы applications, 
    где каждая заявка представлена в виде словаря.
    """

    conn = sq.connect('database.db') 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications WHERE status = 'Ожидает подтверждения'")
    rows = cursor.fetchall()
