"""
Маршруты: Задачи и API для задач
"""

from flask import Blueprint, render_template, request, jsonify, session
from database import get_db_connection
from models.xp_system import add_xp_to_skill
from datetime import datetime

bp = Blueprint('tasks', __name__)


@bp.route('/tasks')
def tasks_page():
    """Страница со списком задач"""
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
    return render_template('tasks.html', tasks=list(tasks), username=session.get('username'))


@bp.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """API: Отметить задачу как выполненную и начислить XP"""
    conn = get_db_connection()
    task = conn.execute(
        'SELECT * FROM tasks WHERE id = ?', (task_id,)
    ).fetchone()

    if not task:
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    # Помечаем как выполненную
    now = datetime.now()
    conn.execute('''
        UPDATE tasks 
        SET is_completed = 1, is_archived = 1, completed_at = ?
        WHERE id = ?
    ''', (now, task_id))

    # Начисляем XP навыку
    if task['skill_id']:
        add_xp_to_skill(task['skill_id'], task['xp_reward'])

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'xp_reward': task['xp_reward']})