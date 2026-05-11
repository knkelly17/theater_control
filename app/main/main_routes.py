'''Main route for the site'''
import logging
import datetime
from flask import render_template, current_app
from flask_login import login_required
from app.functions import get_setting
from . import main_bp #pylint: disable=cyclic-import

log = logging.getLogger(__name__)

currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")

@main_bp.route("/")
@main_bp.route("/index")
@login_required
def index():
    """Home page route."""

    log.warning("any different")
    return render_template(
        'index.html', 
        title='Home',
        version=ver,
        site_name=get_setting(current_app.config, 'name'),
        main_menu='index')
