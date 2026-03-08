"""
Test data generator for Prostor Core
Run: python data_test.py
"""

from database import get_db_connection


def add_test_data():
    """
    Add sample data to empty tables.
    Safe to run multiple times (checks for existing data).
    """
    conn = get_db_connection()

    # Check if data already exists
    existing = conn.execute('SELECT COUNT(*) FROM skills').fetchone()[0]
    if existing > 0:
        print(f'⚠️ База уже содержит данные ({existing} навыков). Пропускаем.')
        conn.close()
        return

    print('📦 Добавляем тестовые данные...')

    # 1. Тестовый пользователь
    conn.execute('''
        INSERT INTO users (username, display_name, password_hash, email)
        VALUES ('testuser', 'Тестовый Пользователь', 'hashed_password', 'test@example.com')
    ''')
    user_id = conn.execute('SELECT id FROM users WHERE username = "testuser"').fetchone()[0]

    # 2. Корневые навыки
    skills = [
        (user_id, None, 'Программирование', 1, 0, 100, '#f8f9fa', '💻'),
        (user_id, None, 'Здоровье', 1, 0, 100, '#4CAF50', '🏋️'),
        (user_id, None, 'Учёба', 1, 0, 100, '#0061ff', '📚'),
        (user_id, None, 'Ораторское', 1, 0, 100, '#764ba2', '🎤'),
    ]
    conn.executemany('''
        INSERT INTO skills (user_id, parent_id, name, level, xp, xp_to_next, color, icon)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', skills)

    # 3. Поднавыки (получаем ID родителей)
    programming_id = conn.execute('SELECT id FROM skills WHERE name = "Программирование"').fetchone()[0]
    health_id = conn.execute('SELECT id FROM skills WHERE name = "Здоровье"').fetchone()[0]

    subskills = [
        (user_id, programming_id, 'Python', 1, 50, 200, '#4CAF50', '🐍'),
        (user_id, programming_id, 'Flask', 1, 30, 200, '#764ba2', '🧪'),
        (user_id, health_id, 'Тренажёрный зал', 1, 100, 300, '#4CAF50', '💪'),
    ]
    conn.executemany('''
        INSERT INTO skills (user_id, parent_id, name, level, xp, xp_to_next, color, icon)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', subskills)

    # 4. Цель для навыка
    conn.execute('''
        INSERT INTO goals (user_id, skill_id, title, description)
        VALUES (?, ?, ?, ?)
    ''', (user_id, programming_id, 'Стать Python-разработчиком', 'Изучить основы и создать проект'))

    goal_id = conn.execute('SELECT id FROM goals WHERE skill_id = ?', (programming_id,)).fetchone()[0]

    # 5. Подцели
    subgoals = [
        (user_id, goal_id, 'Пройти курс по основам', 0, 1),
        (user_id, goal_id, 'Сделать 3 пет-проекта', 0, 2),
        (user_id, goal_id, 'Найти стажировку', 0, 3),
    ]
    conn.executemany('''
        INSERT INTO subgoals (user_id, goal_id, title, is_completed, position)
        VALUES (?, ?, ?, ?, ?)
    ''', subgoals)

    # 6. Задачи
    python_id = conn.execute('SELECT id FROM skills WHERE name = "Python"').fetchone()[0]
    subgoal_id = conn.execute('SELECT id FROM subgoals LIMIT 1').fetchone()[0]

    tasks = [
        (user_id, subgoal_id, python_id, 'Решить 5 задач на Codewars', 'recurring', 20, 0, 0, None, '03:00', None, 1,
         None, 1),
        (user_id, subgoal_id, python_id, 'Прочитать главу про декораторы', 'short', 50, 0, 0, None, None, None, 2, None,
         2),
        (user_id, subgoal_id, python_id, 'Написать первый Flask-сервер', 'medium', 100, 0, 0, None, None, None, 3, None,
         3),
    ]
    conn.executemany('''
        INSERT INTO tasks (user_id, subgoal_id, skill_id, title, task_type, xp_reward, 
                          is_completed, is_archived, completed_at, reset_time, last_reset_date, 
                          position, deadline, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', tasks)

    conn.commit()
    conn.close()

    print('✅ Тестовые данные добавлены!')


if __name__ == '__main__':
    add_test_data()