

from flask import send_file, Blueprint

bp = Blueprint('oddfront', __name__, url_prefix='')

@bp.route('/', methods=['GET'])
def index():
    """主页"""
    return send_file('./templates/index.html')

