

from flask import send_file, Blueprint, render_template

from modules.module_tool import load_skills

bp = Blueprint('oddfront', __name__, url_prefix='')

@bp.route('/old', methods=['GET'])
def index():
    """主页"""
    return send_file('./templates/index.html')

@bp.route('/')
def home():
    skill_list = load_skills()
    return render_template('index.html', skills=skill_list)
