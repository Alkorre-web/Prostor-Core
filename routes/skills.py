"""
Маршруты: Дерево навыков и API для навыков
"""

from flask import Blueprint, render_template, request, jsonify, session
from database import get_db_connection
from models.xp_system import add_xp_to_skill, calculate_level

bp = Blueprint('skills', __name__)


def build_skill_tree(skills, parent_id=None):
    """Построение дерева навыков из плоского списка"""
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


@bp.route('/skills')
@bp.route('/skills-tree')
def skills_tree():
    """Страница с деревом навыков"""
    conn = get_db_connection()
    user_id = session.get('user_id')

    all_skills = conn.execute(
        'SELECT * FROM skills WHERE user_id = ? ORDER BY level, name',
        (user_id,)
    ).fetchall()
    conn.close()

    tree = build_skill_tree(list(all_skills))
    return render_template('skills.html', tree=tree)


@bp.route('/test-skills')
def test_skills():
    """Отладочная страница дерева навыков"""
    conn = get_db_connection()
    user_id = session.get('user_id')

    all_skills = conn.execute(
        'SELECT * FROM skills WHERE user_id = ? ORDER BY id',
        (user_id,)
    ).fetchall()
    conn.close()

    tree = build_skill_tree(list(all_skills))
    return render_template('test_skills.html', tree=tree)


@bp.route('/api/skills/<int:skill_id>/add-xp', methods=['POST'])
def add_xp(skill_id):
    """API: Начислить XP навыку"""
    data = request.json
    xp_amount = data.get('xp', 10)

    result = add_xp_to_skill(skill_id, xp_amount)
    return jsonify(result)