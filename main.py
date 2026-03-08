from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('prostor_core.db')
    conn.row_factory = sqlite3.Row
    return conn


# ========================================
# ЗАГЛУШКИ (УБРАЛИ /goals отсюда!)
# ========================================
@app.route('/')
@app.route('/tasks')
@app.route('/api')
@app.route('/search')
@app.route('/settings')
@app.route('/help')
def placeholder():
    return render_template('placeholder.html')


# ========================================
# СТРАНИЦА ЦЕЛИ (две панели)
# ========================================
@app.route('/goals')
def goals_page():
    conn = get_db_connection()

    # Все навыки (для левой панели)
    skills = conn.execute('SELECT * FROM skills ORDER BY id').fetchall()

    # Все основные цели
    goals = conn.execute('SELECT * FROM goals').fetchall()

    # Все подцели
    subgoals = conn.execute('SELECT * FROM subgoals ORDER BY goal_id, position').fetchall()

    conn.close()

    print(f"📊 Навыков: {len(skills)}, Целей: {len(goals)}, Подцелей: {len(subgoals)}")

    return render_template('goals.html',
                           skills=skills,
                           goals=goals,
                           subgoals=subgoals)


@app.route('/api/goals/skill/<int:skill_id>')
def get_goal_for_skill(skill_id):
    conn = get_db_connection()

    # Получаем навык
    skill = conn.execute('SELECT * FROM skills WHERE id = ?', (skill_id,)).fetchone()

    # Получаем цель (если есть)
    goal = conn.execute('SELECT * FROM goals WHERE skill_id = ?', (skill_id,)).fetchone()

    # Получаем подцели
    subgoals = conn.execute('''
        SELECT * FROM subgoals 
        WHERE goal_id = (SELECT id FROM goals WHERE skill_id = ?)
        ORDER BY position
    ''', (skill_id,)).fetchall()

    conn.close()

    return jsonify({
        'skill_id': skill['id'],
        'skill_name': f"{skill['icon']} {skill['name']}",
        'goal': dict(goal) if goal else None,
        'subgoals': [dict(sg) for sg in subgoals]
    })




# ========================================
# СТРАНИЦА ДЕРЕВО НАВЫКОВ
# ========================================
@app.route('/skills')
def skills_tree():
    conn = get_db_connection()
    all_skills = conn.execute('SELECT * FROM skills ORDER BY id').fetchall()
    conn.close()

    print(f"📊 Найдено навыков: {len(all_skills)}")

    tree = build_skill_tree(all_skills)

    print(f"🌳 Корней в дереве: {len(tree)}")

    return render_template('skills.html', tree=tree)


def build_skill_tree(skills, parent_id=None):
    tree = []
    for skill in skills:
        if skill['parent_id'] == parent_id:
            children = build_skill_tree(skills, parent_id=skill['id'])
            tree.append({
                'id': skill['id'],
                'name': skill['name'],
                'level': skill['level'],
                'xp': skill['xp'],
                'xp_to_next': skill['xp_to_next'],
                'color': skill['color'],
                'icon': skill['icon'],
                'children': children
            })
    return tree


@app.route('/test-skills')
def test_skills():
    conn = get_db_connection()
    all_skills = conn.execute('SELECT * FROM skills ORDER BY id').fetchall()
    conn.close()
    tree = build_skill_tree(all_skills)
    return render_template('test_skills.html', tree=tree)


# ========================================
# ФУНКЦИИ XP
# ========================================
def add_xp_to_skill(skill_id, xp_amount):
    conn = get_db_connection()
    skill = conn.execute('SELECT * FROM skills WHERE id = ?', (skill_id,)).fetchone()

    if not skill:
        conn.close()
        return

    new_xp = skill['xp'] + xp_amount
    conn.execute('UPDATE skills SET xp = ? WHERE id = ?', (new_xp, skill_id))

    old_level = skill['level']
    new_level = calculate_level(new_xp)

    if new_level > old_level:
        conn.execute('UPDATE skills SET level = ? WHERE id = ?', (new_level, skill_id))

        if skill['parent_id']:
            parent_xp_bonus = new_level * 50
            add_xp_to_skill(skill['parent_id'], parent_xp_bonus)

    conn.commit()
    conn.close()

    return {
        'skill_id': skill_id,
        'new_xp': new_xp,
        'new_level': new_level,
        'leveled_up': new_level > old_level
    }


def calculate_level(xp):
    import math
    return int(math.sqrt(xp / 10)) + 1


# ========================================
# API МАРШРУТЫ
# ========================================
@app.route('/api/skills/<int:skill_id>/add-xp', methods=['POST'])
def add_xp(skill_id):
    data = request.json
    xp_amount = data.get('xp', 10)
    result = add_xp_to_skill(skill_id, xp_amount)
    return jsonify(result)


@app.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()

    if not task:
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    from datetime import datetime
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


# ========================================
# СБРОС RECURRING ЗАДАЧ
# ========================================
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
                SET is_completed = 0, is_archived = 0, completed_at = NULL, last_reset_date = ?
                WHERE id = ?
            ''', (current_date, task['id']))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    print('🚀 Запуск: http://127.0.0.1:5000')
    app.run(debug=True)