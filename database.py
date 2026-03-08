import sqlite3
import os

DB_NAME = 'prostor_core.db'
SAFE_MODE = True  # True = НЕ удалять БД при запуске


def init_db():
    if not SAFE_MODE and os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f'🗑️ Удалена старая база данных: {DB_NAME}')
    elif SAFE_MODE and os.path.exists(DB_NAME):
        print(f'✅ База данных найдена: {DB_NAME}')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON')

    # 1. ПОЛЬЗОВАТЕЛИ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            google_id TEXT,
            total_xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        )
    ''')

    # 2. НАВЫКИ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            parent_id INTEGER,
            name TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            xp_to_next INTEGER DEFAULT 100,
            color TEXT DEFAULT '#f8f9fa',
            icon TEXT DEFAULT '📚',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_id) REFERENCES skills(id) ON DELETE CASCADE
        )
    ''')

    # 3. ЦЕЛИ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            target_xp INTEGER DEFAULT 100,
            current_xp INTEGER DEFAULT 0,
            deadline TEXT,
            is_completed BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id) REFERENCES skills(id)
        )
    ''')

    # 4. ПОДЦЕЛИ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subgoals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            goal_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            is_completed BOOLEAN DEFAULT 0,
            position INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
        )
    ''')

    # 5. ЗАДАЧИ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subgoal_id INTEGER,
            skill_id INTEGER,
            title TEXT NOT NULL,
            task_type TEXT NOT NULL,
            xp_reward INTEGER DEFAULT 10,
            is_completed BOOLEAN DEFAULT 0,
            is_archived BOOLEAN DEFAULT 0,
            completed_at TIMESTAMP,
            reset_time TEXT DEFAULT '03:00',
            last_reset_date DATE,
            position INTEGER DEFAULT 0,
            deadline TEXT,
            priority INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (subgoal_id) REFERENCES subgoals(id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL
        )
    ''')

    # 6. ТЕГИ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            color TEXT DEFAULT '#e94560',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # 7. СВЯЗЬ ЗАДАЧ И ТЕГОВ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_tags (
            task_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY (task_id, tag_id),
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
    ''')

    # 8. ЛОГ ОПЫТА
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS xp_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_id INTEGER,
            xp_amount INTEGER NOT NULL,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
        )
    ''')
    # ========================================================================
    # 9. ПАПКИ ДЛЯ ЗАМЕТОК (для базы знаний)
    # ========================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS note_folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            parent_id INTEGER,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_id) REFERENCES note_folders(id) ON DELETE CASCADE
        )
    ''')

    # ========================================================================
    # 10. ЗАМЕТКИ (для базы знаний)
    # ========================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            folder_id INTEGER,
            title TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (folder_id) REFERENCES note_folders(id) ON DELETE CASCADE
        )
    ''')

    print('✅ База данных инициализирована')
    conn.commit()
    conn.close()


def get_db_connection():
    """Получить подключение к БД"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


if __name__ == '__main__':
    init_db()