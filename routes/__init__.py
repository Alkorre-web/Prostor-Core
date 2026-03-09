"""
Регистрация всех Blueprint'ов
"""

from . import profile, tasks, skills, goals, knowledge, help


def register_blueprints(app):
    """Регистрирует все маршруты в приложении"""
    app.register_blueprint(profile.bp)
    app.register_blueprint(tasks.bp)
    app.register_blueprint(skills.bp)
    app.register_blueprint(goals.bp)
    app.register_blueprint(knowledge.bp)
    app.register_blueprint(help.bp)