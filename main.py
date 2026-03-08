"""
Prostor Core — Main Application Entry Point
Flask backend for RPG-style productivity tracker
"""

from flask import Flask, render_template, request, jsonify, session  # <--- 1. Добавили session
from database import get_db_connection, init_db
import sqlite3
from datetime import datetime
from data_test import add_test_data

# Фикс для предупреждения о датах в Python 3.12+
def adapt_datetime(val):
    return val.isoformat() if val else None

sqlite3.register_adapter(datetime, adapt_datetime)

app = Flask(__name__)
app.secret_key = 'dev_secret_key_123'  # <--- 2. Обязательный ключ для сессий!

# =============================================================================
# AUTO-LOGIN ДЛЯ РАЗРАБОТКИ (временное решение)
# =============================================================================

@app.before_request
def force_login():
    """Временно входит под admin без пароля"""
    # Принудительно ставим сессию для пользователя с ID 1
    session['user_id'] = 1
    session['username'] = 'admin'

# =============================================================================
# ROUTES: Placeholder pages (temporary)
# =============================================================================

# Все эти страницы будут показывать один и тот же шаблон
@app.route('/')
@app.route('/api')
@app.route('/search')
@app.route('/settings')
@app.route('/help')
def placeholder():
    return render_template('placeholder.html')


# =============================================================================
# ROUTES: Goals page (two-panel layout)
# =============================================================================

@app.route('/goals')
def goals_page():
    conn = get_db_connection()
    user_id = session.get('user_id')  # <--- Получаем ID из сессии

    # Добавь WHERE user_id = ? во все запросы
    skills = conn.execute(
        'SELECT * FROM skills WHERE user_id = ? ORDER BY id',
        (user_id,)
    ).fetchall()

    # ⚠️ Таблицы 'goals' нет в твоей БД! Замени на задачи или создай таблицу
    tasks = conn.execute(
        'SELECT * FROM tasks WHERE user_id = ? ORDER BY priority',
        (user_id,)
    ).fetchall()

    subgoals = conn.execute(
        'SELECT * FROM task_tags WHERE task_id IN (SELECT id FROM tasks WHERE user_id = ?)',
        (user_id,)
    ).fetchall()

    conn.close()
    return render_template('goals.html', skills=skills, goals=tasks, subgoals=subgoals)


@app.route('/api/goals/skill/<int:skill_id>')
def get_goal_for_skill(skill_id):
    conn = get_db_connection()
    user_id = session.get('user_id')  # <--- Получаем ID

    # Проверяем, что навык принадлежит пользователю
    skill = conn.execute(
        'SELECT * FROM skills WHERE id = ? AND user_id = ?',
        (skill_id, user_id)
    ).fetchone()

    if not skill:
        conn.close()
        return jsonify({'error': 'Skill not found'}), 404

    # Фильтруем цели по пользователю
    goal = conn.execute(
        'SELECT * FROM goals WHERE skill_id = ? AND user_id = ?',
        (skill_id, user_id)
    ).fetchone()

    # Подцели тоже фильтруем
    subgoals = conn.execute('''
        SELECT sg.* FROM subgoals sg
        JOIN goals g ON sg.goal_id = g.id
        WHERE g.skill_id = ? AND g.user_id = ?
        ORDER BY sg.position
    ''', (skill_id, user_id)).fetchall()

    conn.close()

    return jsonify({
        'skill_id': skill['id'],
        'skill_name': f"{skill['icon']} {skill['name']}",
        'goal': dict(goal) if goal else None,
        'subgoals': [dict(sg) for sg in subgoals]
    })


# =============================================================================
# ROUTES: Skills tree page
# =============================================================================

@app.route('/skills')
@app.route('/skills-tree')
def skills_tree():
    conn = get_db_connection()
    user_id = session.get('user_id')  # <--- Добавили фильтрацию

    all_skills = conn.execute(
        'SELECT * FROM skills WHERE user_id = ? ORDER BY level, name',
        (user_id,)
    ).fetchall()
    conn.close()

    tree = build_skill_tree(all_skills)
    return render_template('skills.html', tree=tree)


def build_skill_tree(skills, parent_id=None, user_id=None):
    tree = []
    for skill in skills:
        # Дополнительная защита: проверяем владельца
        if user_id and skill['user_id'] != user_id:
            continue

        if skill['parent_id'] == parent_id:
            children = build_skill_tree(skills, parent_id=skill['id'], user_id=user_id)
            tree.append({
                'id': skill['id'],
                'name': skill['name'],
                # ... остальные поля
                'children': children
            })
    return tree

# =============================================================================
# ROUTES: tasks page
# =============================================================================

@app.route('/tasks')
def tasks_page():
    conn = get_db_connection()
    user_id = session.get('user_id')

    tasks = conn.execute('''
        SELECT t.*, s.name as skill_name, s.icon as skill_icon
        FROM tasks t
        LEFT JOIN skills s ON t.skill_id = s.id
        WHERE t.user_id = ?
        ORDER BY t.priority, t.deadline
    ''', (user_id,)).fetchall()

    conn.close()
    return render_template('tasks.html', tasks=tasks, username=session.get('username'))


@app.route('/test-skills')
def test_skills():
    conn = get_db_connection()
    user_id = session.get('user_id')  # <--- Добавили фильтрацию

    all_skills = conn.execute(
        'SELECT * FROM skills WHERE user_id = ? ORDER BY id',
        (user_id,)
    ).fetchall()
    conn.close()

    tree = build_skill_tree(all_skills)
    return render_template('test_skills.html', tree=tree)

# =============================================================================
# BUSINESS LOGIC: XP system
# =============================================================================

def calculate_level(xp):
    """
    Calculate skill level from total XP.
    Formula: level = sqrt(xp / 10) + 1
    """
    import math
    return int(math.sqrt(xp / 10)) + 1


def add_xp_to_skill(skill_id, xp_amount):
    """
    Add XP to a skill and propagate to parent skills on level-up.

    Args:
        skill_id: ID of the skill to update
        xp_amount: Amount of XP to add

    Returns:
        Dict with new XP, level, and level-up status
    """
    conn = get_db_connection()

    skill = conn.execute(
        'SELECT * FROM skills WHERE id = ?', (skill_id,)
    ).fetchone()

    if not skill:
        conn.close()
        return None

    # Update XP
    new_xp = skill['xp'] + xp_amount
    conn.execute(
        'UPDATE skills SET xp = ? WHERE id = ?', (new_xp, skill_id)
    )

    # Check for level-up
    old_level = skill['level']
    new_level = calculate_level(new_xp)

    if new_level > old_level:
        conn.execute(
            'UPDATE skills SET level = ? WHERE id = ?', (new_level, skill_id)
        )

        # Propagate bonus XP to parent skill
        if skill['parent_id']:
            parent_bonus = new_level * 50
            add_xp_to_skill(skill['parent_id'], parent_bonus)

    conn.commit()
    conn.close()

    return {
        'skill_id': skill_id,
        'new_xp': new_xp,
        'new_level': new_level,
        'leveled_up': new_level > old_level
    }


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/api/skills/<int:skill_id>/add-xp', methods=['POST'])
def add_xp(skill_id):
    """API: Add XP to a skill via POST request"""
    data = request.json
    xp_amount = data.get('xp', 10)

    result = add_xp_to_skill(skill_id, xp_amount)
    return jsonify(result)


@app.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """API: Mark task as complete and award XP"""
    from datetime import datetime

    conn = get_db_connection()
    task = conn.execute(
        'SELECT * FROM tasks WHERE id = ?', (task_id,)
    ).fetchone()

    if not task:
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    # Mark as completed and archived
    now = datetime.now()
    conn.execute('''
        UPDATE tasks 
        SET is_completed = 1, is_archived = 1, completed_at = ?
        WHERE id = ?
    ''', (now, task_id))

    # Award XP to associated skill
    if task['skill_id']:
        add_xp_to_skill(task['skill_id'], task['xp_reward'])

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'xp_reward': task['xp_reward']})


# =============================================================================
# BACKGROUND TASKS: Recurring task reset
# =============================================================================

def reset_recurring_tasks():
    """
    Reset recurring tasks at 03:00 Yekaterinburg time.
    Call this on app startup or via scheduled job.
    """
    from datetime import datetime, time
    import pytz

    conn = get_db_connection()

    yekaterinburg_tz = pytz.timezone('Asia/Yekaterinburg')
    now = datetime.now(yekaterinburg_tz)
    current_time = now.time()
    current_date = now.date()

    # Find archived recurring tasks that need reset
    tasks = conn.execute('''
        SELECT * FROM tasks 
        WHERE task_type = 'recurring' 
        AND is_archived = 1
        AND (last_reset_date IS NULL OR last_reset_date < ?)
    ''', (current_date,)).fetchall()

    for task in tasks:
        reset_hour, reset_min = map(int, task['reset_time'].split(':'))
        reset_time = time(reset_hour, reset_min)

        if current_time >= reset_time:
            conn.execute('''
                UPDATE tasks 
                SET is_completed = 0, is_archived = 0, 
                    completed_at = NULL, last_reset_date = ?
                WHERE id = ?
            ''', (current_date, task['id']))

    conn.commit()
    conn.close()


# =============================================================================
# APPLICATION ENTRY POINT
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