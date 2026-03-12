from flask import Blueprint, render_template

bp = Blueprint('rewards', __name__, url_prefix='/rewards')

@bp.route('/')
def rewards_list():
    return render_template('rewards.html')