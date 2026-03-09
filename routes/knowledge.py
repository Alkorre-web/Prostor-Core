"""
Маршруты: Локальная база знаний (заметки)
"""

from flask import Blueprint, render_template, session
from database import get_db_connection

bp = Blueprint('knowledge', __name__)


@bp.route('/knowledge')
@bp.route('/search')
def knowledge_base_page():
    """Страница локальной базы знаний"""
    conn = get_db_connection()
    user_id = session.get('user_id')

    # Получаем папки верхнего уровня
    folders = conn.execute(
        'SELECT * FROM note_folders WHERE user_id = ? AND parent_id IS NULL',
        (user_id,)
    ).fetchall()

    # Получаем последние заметки
    notes = conn.execute(
        'SELECT id, title, created_at FROM notes WHERE user_id = ? ORDER BY updated_at DESC LIMIT 10',
        (user_id,)
    ).fetchall()

    conn.close()

    return render_template('knowledge_base.html',
                           folders=list(folders),
                           recent_notes=list(notes))