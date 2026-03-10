"""
Маршруты: Задачи и API для задач
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from database import get_db_connection
from models.xp_system import add_xp_to_skill
from datetime import datetime

bp = Blueprint('tasks', __name__)


@bp.route('/tasks')
def tasks_page():
    """Страница со списком задач"""
    conn = get_db_connection()
    user_id = session.get('user_id')

    # Получаем все задачи пользователя
    tasks = conn.execute('''
        SELECT t.*, s.name as skill_name, s.icon as skill_icon
        FROM tasks t
        LEFT JOIN skills s ON t.skill_id = s.id
        WHERE t.user_id = ? AND t.is_archived = 0
        ORDER BY t.priority, t.deadline
    ''', (user_id,)).fetchall()

    # Получаем навыки для выпадающего списка
    skills = conn.execute(
        'SELECT id, name, icon FROM skills WHERE user_id = ?',
        (user_id,)
    ).fetchall()

    conn.close()

    return render_template('tasks.html',
                         tasks=list(tasks),
                         skills=list(skills),
                         username=session.get('username'))


@bp.route('/tasks/create', methods=['POST'])
def create_task():
    """Создание новой задачи"""
    conn = get_db_connection()
    user_id = session.get('user_id')

    # Получаем данные из формы
    title = request.form.get('title')
    skill_id = request.form.get('skill_id') or None
    task_type = request.form.get('task_type', 'one_time')
    xp_reward = int(request.form.get('xp_reward', 10))
    priority = int(request.form.get('priority', 1))
    deadline = request.form.get('deadline') or None

    if not title:
        conn.close()
        return redirect(url_for('tasks.tasks_page'))

    # Вставляем в БД
    conn.execute('''
        INSERT INTO tasks (user_id, skill_id, title, task_type, xp_reward, priority, deadline)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, skill_id, title, task_type, xp_reward, priority, deadline))

    conn.commit()
    conn.close()

    return redirect(url_for('tasks.tasks_page'))


@bp.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """API: Отметить задачу как выполненную и начислить XP"""
    conn = get_db_connection()
    user_id = session.get('user_id')

    # Проверяем что задача принадлежит пользователю
    task = conn.execute(
        'SELECT * FROM tasks WHERE id = ? AND user_id = ?',
        (task_id, user_id)
    ).fetchone()

    if not task:
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    # Помечаем как выполненную и архивируем
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


@bp.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    """Редактирование задачи"""
    conn = get_db_connection()
    user_id = session.get('user_id')

    task = conn.execute(
        'SELECT * FROM tasks WHERE id = ? AND user_id = ?',
        (task_id, user_id)
    ).fetchone()

    if not task:
        conn.close()
        return redirect(url_for('tasks.tasks_page'))

    if request.method == 'POST':
        title = request.form.get('title')
        skill_id = request.form.get('skill_id') or None
        xp_reward = int(request.form.get('xp_reward', 10))
        priority = int(request.form.get('priority', 1))
        deadline = request.form.get('deadline') or None

        conn.execute('''
            UPDATE tasks 
            SET title = ?, skill_id = ?, xp_reward = ?, priority = ?, deadline = ?
            WHERE id = ?
        ''', (title, skill_id, xp_reward, priority, deadline, task_id))

        conn.commit()
        conn.close()

        return redirect(url_for('tasks.tasks_page'))

    skills = conn.execute(
        'SELECT id, name, icon FROM skills WHERE user_id = ?',
        (user_id,)
    ).fetchall()

    conn.close()

    return render_template('tasks_edit.html', task=task, skills=list(skills))


@bp.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Удаление задачи"""
    conn = get_db_connection()
    user_id = session.get('user_id')

    conn.execute(
        'DELETE FROM tasks WHERE id = ? AND user_id = ?',
        (task_id, user_id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('tasks.tasks_page'))