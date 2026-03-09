"""
Бизнес-логика: Система опыта и уровней
"""

import math
from database import get_db_connection


def calculate_level(xp):
    """
    Расчёт уровня навыка от общего XP.
    Формула: level = sqrt(xp / 10) + 1
    """
    return int(math.sqrt(xp / 10)) + 1


def add_xp_to_skill(skill_id, xp_amount):
    """
    Добавить XP к навыку и распространить на родительские навыки при повышении уровня.

    Args:
        skill_id: ID навыка для обновления
        xp_amount: Количество XP для добавления

    Returns:
        Dict с новым XP, уровнем и статусом повышения
    """
    conn = get_db_connection()

    skill = conn.execute(
        'SELECT * FROM skills WHERE id = ?', (skill_id,)
    ).fetchone()

    if not skill:
        conn.close()
        return None

    # Обновляем XP
    new_xp = skill['xp'] + xp_amount
    conn.execute(
        'UPDATE skills SET xp = ? WHERE id = ?', (new_xp, skill_id)
    )

    # Проверяем повышение уровня
    old_level = skill['level']
    new_level = calculate_level(new_xp)

    if new_level > old_level:
        conn.execute(
            'UPDATE skills SET level = ? WHERE id = ?', (new_level, skill_id)
        )

        # Передаём бонусный XP родительскому навыку
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