

from flask import send_file, Blueprint, render_template, send_from_directory, send_file
import platform
import os

from oddagent.modules.module_tool import load_skills
from oddagent.odd_agent_logger import logger

bp = Blueprint('oddfront', __name__, url_prefix='')

@bp.route('/old', methods=['GET'])
def index():
    """主页"""
    return send_file('./templates/index.html')

@bp.route('/')
def home():
    skill_list = load_skills()
    return render_template('index.html', skills=skill_list)


@bp.route('/download/<filename>', methods=['GET'])
def download(filename):
    name = filename.split('\\')[-1]
    basepath = os.getcwd()
    if platform.system() != "Windows":
        if filename in ("敏感词模板.xls", "热词模板.xls"):
            path = os.path.join(basepath, 'static/templates')
        else:
            path = os.path.join(basepath, 'static/auth_cert')
    else:
        path = os.path.join(basepath, '.\\docs')
    logger.info(f"path:{path}")
    if not os.path.exists(path):
        os.makedirs(path)
    templates_path = os.path.join(path, filename)
    logger.info(f"templates_path:{templates_path}")
    return send_from_directory(path, name, as_attachment=True)
