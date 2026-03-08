
import sqlite3

conn = sqlite3.connect('prostor_core.db')
conn.row_factory = sqlite3.Row

# Проверяем пользователя
user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
print(f"👤 Пользователь: {user['username'] if user else 'НЕ НАЙДЕН'}")

# Проверяем задачи
tasks = conn.execute('SELECT COUNT(*) FROM tasks WHERE user_id = 1').fetchone()[0]
print(f"📋 Задач у пользователя: {tasks}")

# Проверяем ВСЕ задачи в базе
all_tasks = conn.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
print(f"📋 ВСЕГО задач в базе: {all_tasks}")

conn.close()