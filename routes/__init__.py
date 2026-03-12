from routes.index import bp as index_bp
from routes.rewards import bp as rewards_bp
from routes.settings import bp as settings_bp

def register_blueprints(app):
    """Регистрирует все blueprints в приложении"""
    app.register_blueprint(index_bp)
    app.register_blueprint(rewards_bp)
    app.register_blueprint(settings_bp)