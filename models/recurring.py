"""
Бизнес-логика: Сброс повторяющихся задач
"""

from datetime import datetime, time
import pytz
from database import get_db_connection


def reset_recurring_tasks():
    """
    Сброс повторяющихся задач в 03:00 по Екатеринбургу.
    Вызывается при запуске приложения или по расписанию.
    """
    conn = get_db_connection()

    yekaterinburg_tz = pytz.timezone('Asia/Yekaterinburg')
    now = datetime.now(yekaterinburg_tz)
    current_time = now.time()
    current_date = now.date()

    # Находим архивированные повторяющиеся задачи для сброса
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