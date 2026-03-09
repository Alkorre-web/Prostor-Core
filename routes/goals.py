"""
Маршруты: Цели и подцели
"""

from flask import Blueprint, render_template, request, jsonify, session
from database import get_db_connection

bp = Blueprint('goals', __name__)


@bp.route('/goals')
def goals_page():
    """Страница целей (двухпанельный вид)"""
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
    return render_template('goals.html',
                         skills=list(skills),
                         goals=list(tasks),
                         subgoals=list(subgoals))


@bp.route('/api/goals/skill/<int:skill_id>')
def get_goal_for_skill(skill_id):
    """API: Получить цель для конкретного навыка"""
    conn = get_db_connection()
    user_id = session.get('user_id')

    # Проверяем, что навык принадлежит пользователю
    skill = conn.execute(
        'SELECT * FROM skills WHERE id = ? AND user_id = ?',
        (skill_id, user_id)
    ).fetchone()

    if not skill:
        conn.close()
        return jsonify({'error': 'Skill not found'}), 404

    # Получаем цель
    goal = conn.execute(
        'SELECT * FROM goals WHERE skill_id = ? AND user_id = ?',
        (skill_id, user_id)
    ).fetchone()

    # Получаем подцели
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