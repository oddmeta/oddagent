

from flask import Blueprint, render_template

from oddagent.modules.module_tool import load_skills

bp = Blueprint('oddbookmark', __name__, url_prefix='')

@bp.route('/bookmark')
def home():
    bookmark_list = load_skills()
    return render_template('bookmark.html', bookmark_list=bookmark_list)
