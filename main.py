"""
Prostor Core — Main Application Entry Point
Flask backend for RPG-style productivity tracker
"""

import os
from flask import Flask, render_template, request, jsonify, session
from database import get_db_connection, init_db
from data_test import add_test_data
import sqlite3
from datetime import datetime

# Фикс для предупреждения о датах в Python 3.12+
def adapt_datetime(val):
    return val.isoformat() if val else None

sqlite3.register_adapter(datetime, adapt_datetime)

app = Flask(__name__)
app.secret_key = 'dev_secret_key_123'  # Обязательный ключ для сессий!

# =============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (Исправление ошибки NameError)
# =============================================================================

def row_to_dict(row):
    """Конвертирует sqlite3.Row в словарь"""
    return dict(row) if row else None

def rows_to_dicts(rows):
    """Конвертирует список sqlite3.Row в список словарей"""
    return [dict(row) for row in rows]

# =============================================================================
# AUTO-LOGIN ДЛЯ РАЗРАБОТКИ (временное решение)
# =============================================================================

@app.before_request
def force_login():
    """Временно входит под admin без пароля"""
    session['user_id'] = 1
    session['username'] = 'admin'

# =============================================================================
# ROUTES: Placeholder pages
# =============================================================================

@app.route('/api')
@app.route('/settings')
def placeholder():
    return render_template('placeholder.html')

# =============================================================================
# ROUTES: Goals page
# =============================================================================

@app.route('/goals')
def goals_page():
    conn = get_db_connection()
    user_id = session.get('user_id')

    skills = conn.execute(
        'SELECT * FROM skills WHERE user_id = ? ORDER BY id',
        (user_id,)
    ).fetchall()

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

# =============================================================================
# ROUTES: Help page (with file loading)
# =============================================================================

@app.route('/help')
def help_page():
    """Страница помощи с загрузкой из файлов"""

    arch_folder = os.path.join('help_text', 'architecture')
    code_folder = os.path.join('help_text', 'code')

    # Чтение файлов архитектуры
    arch_files = []
    if os.path.exists(arch_folder):
        for filename in sorted(os.listdir(arch_folder)):
            if filename.endswith('.txt'):
                filepath = os.path.join(arch_folder, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                title = filename[:-4].replace('_', ' ').title()
                arch_files.append({'title': title, 'content': content, 'filename': filename})

    # Чтение файлов с кодом
    code_files = []
    if os.path.exists(code_folder):
        for filename in sorted(os.listdir(code_folder)):
            if filename.endswith('.txt'):
                filepath = os.path.join(code_folder, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                title = filename[:-4].replace('_', ' ').title()
                code_files.append({'title': title, 'content': content, 'filename': filename})

    return render_template('help.html',
                         arch_sections=arch_files,
                         code_sections=code_files)

# =============================================================================
# ROUTES: Profile page (FIXED)
# =============================================================================

@app.route('/')
@app.route('/profile')
def profile_page():
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

    # 🔹 КОНВЕРТАЦИЯ Row → dict
    return render_template('profile.html',
                           user=row_to_dict(user),
                           top_parent_skills=rows_to_dicts(top_parent_skills),
                           top_child_skills=rows_to_dicts(top_child_skills),
                           low_parent_skills=rows_to_dicts(low_parent_skills),
                           low_child_skills=rows_to_dicts(low_child_skills),
                           tasks=rows_to_dicts(tasks))

# =============================================================================
# API: Goals
# =============================================================================

@app.route('/api/goals/skill/<int:skill_id>')
def get_goal_for_skill(skill_id):
    conn = get_db_connection()
    user_id = session.get('user_id')

    skill = conn.execute(
        'SELECT * FROM skills WHERE id = ? AND user_id = ?',
        (skill_id, user_id)
    ).fetchone()

    if not skill:
        conn.close()
        return jsonify({'error': 'Skill not found'}), 404

    goal = conn.execute(
        'SELECT * FROM goals WHERE skill_id = ? AND user_id = ?',
        (skill_id, user_id)
    ).fetchone()

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
        'goal': dict(goal) if goal else None,  # Безопасная обработка, если goal нет
        'subgoals': [dict(sg) for sg in subgoals]
    })

# =============================================================================
# ROUTES: Skills tree page
# =============================================================================

@app.route('/skills')
@app.route('/skills-tree')
def skills_tree():
    conn = get_db_connection()
    user_id = session.get('user_id')

    all_skills = conn.execute(
        'SELECT * FROM skills WHERE user_id = ? ORDER BY level, name',
        (user_id,)
    ).fetchall()
    conn.close()

    tree = build_skill_tree(all_skills)
    return render_template('skills.html', tree=tree)


def build_skill_tree(skills, parent_id=None):
    """
    Build nested tree structure from flat list of skills.
    """
    tree = []
    for skill in skills:
        if skill['parent_id'] == parent_id:
            children = build_skill_tree(skills, parent_id=skill['id'])
            # ✅ Исправлено: передаём ВСЕ поля навыка в дерево
            tree.append({
                'id': skill['id'],
                'name': skill['name'],
                'level': skill['level'],
                'xp': skill['xp'],
                'xp_to_next': skill['xp_to_next'],
                'color': skill['color'],
                'icon': skill['icon'],
                'user_id': skill['user_id'],  # Добавили для безопасности
                'parent_id': skill['parent_id'],
                'children': children
            })
    return tree

# =============================================================================
# ROUTES: Tasks page
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
    user_id = session.get('user_id')

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
    import math
    return int(math.sqrt(xp / 10)) + 1


def add_xp_to_skill(skill_id, xp_amount):
    conn = get_db_connection()

    skill = conn.execute(
        'SELECT * FROM skills WHERE id = ?', (skill_id,)
    ).fetchone()

    if not skill:
        conn.close()
        return None

    new_xp = skill['xp'] + xp_amount
    conn.execute(
        'UPDATE skills SET xp = ? WHERE id = ?', (new_xp, skill_id)
    )

    old_level = skill['level']
    new_level = calculate_level(new_xp)

    if new_level > old_level:
        conn.execute(
            'UPDATE skills SET level = ? WHERE id = ?', (new_level, skill_id)
        )
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


@app.route('/search')
@app.route('/knowledge')  # Дублируем для удобства
def knowledge_base_page():
    """Страница локальной базы знаний (как Obsidian)"""
    conn = get_db_connection()
    user_id = session.get('user_id')

    # Пока просто получаем список папок и заметок (заглушка)
    folders = conn.execute(
        'SELECT * FROM note_folders WHERE user_id = ? AND parent_id IS NULL',
        (user_id,)
    ).fetchall()

    notes = conn.execute(
        'SELECT id, title, created_at FROM notes WHERE user_id = ? ORDER BY updated_at DESC LIMIT 10',
        (user_id,)
    ).fetchall()

    conn.close()

    return render_template('knowledge_base.html',
                           folders=rows_to_dicts(folders),
                           recent_notes=rows_to_dicts(notes))




# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/api/skills/<int:skill_id>/add-xp', methods=['POST'])
def add_xp(skill_id):
    data = request.json
    xp_amount = data.get('xp', 10)
    result = add_xp_to_skill(skill_id, xp_amount)
    return jsonify(result)


@app.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    from datetime import datetime

    conn = get_db_connection()
    task = conn.execute(
        'SELECT * FROM tasks WHERE id = ?', (task_id,)
    ).fetchone()

    if not task:
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    now = datetime.now()
    conn.execute('''
        UPDATE tasks 
        SET is_completed = 1, is_archived = 1, completed_at = ?
        WHERE id = ?
    ''', (now, task_id))

    if task['skill_id']:
        add_xp_to_skill(task['skill_id'], task['xp_reward'])

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'xp_reward': task['xp_reward']})

# =============================================================================
# BACKGROUND TASKS: Recurring task reset
# =============================================================================

def reset_recurring_tasks():
    from datetime import datetime, time
    import pytz

    conn = get_db_connection()
    yekaterinburg_tz = pytz.timezone('Asia/Yekaterinburg')
    now = datetime.now(yekaterinburg_tz)
    current_time = now.time()
    current_date = now.date()

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
    init_db()
    add_test_data()
    reset_recurring_tasks()
    print('🚀 Server starting: http://127.0.0.1:5000')
    app.run(debug=True)