from flask import Blueprint, render_template, render_template_string

bp = Blueprint('settings', __name__, url_prefix='/settings')

@bp.route('/')
def setting_page():
    return render_template('settings.html')
