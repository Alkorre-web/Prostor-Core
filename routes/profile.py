"""
Маршруты: Профиль пользователя и главная страница
"""

from flask import Blueprint, render_template, session
from database import get_db_connection

bp = Blueprint('profile', __name__)


def row_to_dict(row):
    """Конвертирует sqlite3.Row в словарь"""
    return dict(row) if row else None


def rows_to_dicts(rows):
    """Конвертирует список sqlite3.Row в список словарей"""
    return [dict(row) for row in rows]


@bp.route('/')
@bp.route('/profile')
def profile_page():
    """Страница профиля пользователя"""
    conn = get_db_connection()
    user_id = session.get('user_id')

    # ===== 1. ДАННЫЕ ПОЛЬЗОВАТЕЛЯ =====
    user = conn.execute(
        'SELECT username, display_name, total_xp, level FROM users WHERE id = ?',
        (user_id,)
    ).fetchone()

    # ===== 2. НАВЫКИ =====
    top_parent_skills = conn.execute('''
        SELECT id, name, level, xp, icon, color 
        FROM skills WHERE user_id = ? AND parent_id IS NULL 
        ORDER BY level DESC, xp DESC LIMIT 4
    ''', (user_id,)).fetchall()

    top_child_skills = conn.execute('''
        SELECT id, name, level, xp, icon, color 
        FROM skills WHERE user_id = ? AND parent_id IS NOT NULL 
        ORDER BY level DESC, xp DESC LIMIT 4
    ''', (user_id,)).fetchall()

    low_parent_skills = conn.execute('''
        SELECT id, name, level, xp, icon, color 
        FROM skills WHERE user_id = ? AND parent_id IS NULL 
        ORDER BY level ASC, xp ASC LIMIT 2
    ''', (user_id,)).fetchall()

    low_child_skills = conn.execute('''
        SELECT id, name, level, xp, icon, color 
        FROM skills WHERE user_id = ? AND parent_id IS NOT NULL 
        ORDER BY level ASC, xp ASC LIMIT 2
    ''', (user_id,)).fetchall()

    # ===== 3. ЗАДАЧИ =====
    tasks = conn.execute('''
        SELECT id, title, task_type, xp_reward, is_completed, deadline, skill_id,
               (SELECT name FROM skills WHERE id = tasks.skill_id) as skill_name,
               (SELECT icon FROM skills WHERE id = tasks.skill_id) as skill_icon
        FROM tasks WHERE user_id = ? 
        ORDER BY 
            CASE task_type 
                WHEN 'recurring' THEN 1 WHEN 'short' THEN 2 
                WHEN 'medium' THEN 3 WHEN 'long' THEN 4 ELSE 5 
            END,
            priority ASC, created_at DESC
        LIMIT 8
    ''', (user_id,)).fetchall()

    conn.close()

    return render_template('profile.html',
                           user=row_to_dict(user),
                           top_parent_skills=rows_to_dicts(top_parent_skills),
                           top_child_skills=rows_to_dicts(top_child_skills),
                           low_parent_skills=rows_to_dicts(low_parent_skills),
                           low_child_skills=rows_to_dicts(low_child_skills),
                           tasks=rows_to_dicts(tasks))