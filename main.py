"""
Prostor Core — Main Application Entry Point
Flask backend for RPG-style productivity tracker
"""

from flask import Flask
from database import init_db
from data_test import add_test_data
from models.recurring import reset_recurring_tasks
from routes import register_blueprints
import sqlite3
from datetime import datetime

# Фикс для предупреждения о датах в Python 3.12+
def adapt_datetime(val):
    return val.isoformat() if val else None

sqlite3.register_adapter(datetime, adapt_datetime)

# Создание приложения
app = Flask(__name__)
app.secret_key = 'dev_secret_key_123'

# Регистрация всех маршрутов
register_blueprints(app)

# =============================================================================
# AUTO-LOGIN ДЛЯ РАЗРАБОТКИ (временное решение)
# =============================================================================

@app.before_request
def force_login():
    """Временно входит под admin без пароля"""
    from flask import session
    session['user_id'] = 1
    session['username'] = 'admin'

# =============================================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# =============================================================================

if __name__ == '__main__':
    # 1. Создаём таблицы (если нет)
    init_db()

    # 2. Добавляем тестовые данные (если база пустая)
    add_test_data()

    # 3. Сброс повторяющихся задач
    reset_recurring_tasks()

    print('🚀 Server starting: http://127.0.0.1:5000')
    app.run(debug=True)