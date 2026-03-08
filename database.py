import sqlite3



def init_db():
    conn = sqlite3.connect('prostor_core.db')
    cursor = conn.cursor()

    # Таблица навыков с иерархией
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            name TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            xp_to_next INTEGER DEFAULT 100,
            color TEXT DEFAULT '#e94560',
            icon TEXT DEFAULT '📚',
            FOREIGN KEY (parent_id) REFERENCES skills(id)
        )
    ''')

    # Таблица задач
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id INTEGER,
            priority INTEGER DEFAULT 1,
            title TEXT NOT NULL,
            deadline TEXT,
            xp_reward INTEGER DEFAULT 10,
            is_completed BOOLEAN DEFAULT 0,
            FOREIGN KEY (skill_id) REFERENCES skills(id)
        )
    ''')

    # Таблица тегов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            color TEXT DEFAULT '#e94560'
        )
    ''')

    # Таблица связей задач и тегов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_tags (
            task_id INTEGER,
            tag_id INTEGER,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        )
    ''')

    conn.commit()
    conn.close()
    print('✅ База данных инициализирована')



if __name__ == '__main__':
    init_db()