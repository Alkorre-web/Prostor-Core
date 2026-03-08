import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = 'prostor_core.db'

def seed_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
    except Exception as e:
        print(f'❌ Ошибка подключения к БД: {e}')
        print('💡 Сначала запусти database.py для создания таблиц!')
        return

    # Генерируем хеш для тестового пароля
    test_password = 'password123'
    password_hash = generate_password_hash(test_password)
    print(f'🔐 Тестовый пароль для всех пользователей: {test_password}')

    try:
        # 1. ОЧИСТКА ДАННЫХ
        cursor.execute('DELETE FROM task_tags')
        cursor.execute('DELETE FROM xp_log')
        cursor.execute('DELETE FROM tasks')
        cursor.execute('DELETE FROM subgoals')
        cursor.execute('DELETE FROM goals')
        cursor.execute('DELETE FROM skills')
        cursor.execute('DELETE FROM users')
        cursor.execute('DELETE FROM tags')
        print('🗑️ Старые тестовые данные очищены')

        # 2. ПОЛЬЗОВАТЕЛИ (добавлены total_xp и level)
        users = [
            ('admin', 'Администратор', password_hash, 'admin@example.com', None, 0, 1),
            ('ivan', 'Иван Петров', password_hash, 'ivan@example.com', None, 0, 1),
        ]
        cursor.executemany('''
            INSERT INTO users (username, display_name, password_hash, email, google_id, total_xp, level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', users)
        print(f'✅ Добавлено пользователей: {len(users)}')

        # 3. НАВЫКИ
        skills = [
            (1, None, 'Программирование', 1, 0, 100, '#e94560', '💻'),
            (1, None, 'Дизайн', 1, 0, 100, '#45e9a0', '🎨'),
            (1, 1, 'Python', 2, 50, 200, '#3776ab', '🐍'),
            (1, 1, 'JavaScript', 1, 0, 100, '#f7df1e', '📜'),
            (1, 3, 'Flask', 3, 150, 300, '#000000', '🌶️'),
            (2, None, 'Спорт', 1, 0, 100, '#ff5733', '🏋️'),
        ]
        cursor.executemany('''
            INSERT INTO skills (user_id, parent_id, name, level, xp, xp_to_next, color, icon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', skills)
        print(f'✅ Добавлено навыков: {len(skills)}')

        # 4. ЦЕЛИ (новая таблица)
        goals = [
            (1, 1, 'Стать Python-разработчиком', 'Изучить Flask и Django', 1000, 150, '2025-12-31', 0),
            (1, 2, 'Научиться рисовать', 'Освоить Figma', 500, 0, '2025-06-30', 0),
        ]
        cursor.executemany('''
            INSERT INTO goals (user_id, skill_id, title, description, target_xp, current_xp, deadline, is_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', goals)
        print(f'✅ Добавлено целей: {len(goals)}')

        # 5. ПОДЦЕЛИ (новая таблица)
        subgoals = [
            (1, 1, 'Пройти курс по Flask', 0, 1),
            (1, 1, 'Сделать пет-проект', 0, 2),
            (1, 2, 'Нарисовать 5 макетов', 0, 1),
        ]
        cursor.executemany('''
            INSERT INTO subgoals (user_id, goal_id, title, is_completed, position)
            VALUES (?, ?, ?, ?, ?)
        ''', subgoals)
        print(f'✅ Добавлено подцелей: {len(subgoals)}')

        # 6. ЗАДАЧИ (добавлены task_type и subgoal_id)
        tasks = [
            (1, None, 5, 'Сделать CRUD для профиля', 'one_time', 50, 0, 0, None, '03:00', None, 1, '2024-12-31'),
            (1, None, 5, 'Добавить хеширование паролей', 'one_time', 30, 1, 0, None, '03:00', None, 2, '2024-12-25'),
            (1, 1, None, 'Прочитать главу книги', 'one_time', 20, 0, 0, None, '03:00', None, 1, '2024-12-20'),
            (2, None, 6, 'Пробежать 5 км', 'recurring', 25, 0, 0, None, '03:00', None, 1, '2024-12-15'),
        ]
        cursor.executemany('''
            INSERT INTO tasks (user_id, subgoal_id, skill_id, title, task_type, xp_reward, is_completed, is_archived, completed_at, reset_time, last_reset_date, priority, deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tasks)
        print(f'✅ Добавлено задач: {len(tasks)}')

        # 7. ТЕГИ
        tags = [
            (1, 'Срочно', '#ff0000'),
            (1, 'В работе', '#ffa500'),
            (1, 'Готово', '#00ff00'),
        ]
        cursor.executemany('''
            INSERT INTO tags (user_id, name, color) VALUES (?, ?, ?)
        ''', tags)
        print(f'✅ Добавлено тегов: {len(tags)}')

        conn.commit()
        print('\n🎉 База успешно заполнена тестовыми данными!')

    except Exception as e:
        conn.rollback()
        print(f'❌ Ошибка при заполнении БД: {e}')
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    seed_db()