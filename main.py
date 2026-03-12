from flask import Flask
from config import Config
import database as db
from routes import register_blueprints

app = Flask(__name__)
app.config.from_object(Config)

# Инициализация БД
with app.app_context():
    db.init_db()
    print("✅ База данных готова")

# Регистрируем все blueprints
register_blueprints(app)

if __name__ == '__main__':
    print("🚀 Запуск: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)