from flask import Blueprint, render_template
import database as db

bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    conn = db.get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as count FROM goals')
    goals_count = cursor.fetchone()['count']

    conn.close()

    return render_template('index.html', goals_count=goals_count)