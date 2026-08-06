"""Routes for the Flask web application handling AV Club Administration."""
import logging
import datetime
from mysql.connector import (
    errorcode,
    IntegrityError,
)
from flask import (
    render_template,
    request,
    jsonify,
    current_app)
from flask_login import login_required

from app.functions import (
    get_setting,
    group_required,
)

from .services.show_services import ShowService

from .tech_director_forms import TechDirectorForm


from .tech_director_routes import (
    VALID_ASSIGNMENTS,
    VALID_STATES
)

from . import tech_director_bp # pylint: disable=cyclic-import

log = logging.getLogger(__name__)

currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")

@tech_director_bp.route('/shows', methods=['GET'])
@login_required
@group_required("tech_director_admin")
def shows():
    """List Shows"""
    form = TechDirectorForm()
    return render_template(
        'tech_director/shows.html', 
        title='List Shows',
        sub_title='Shows',
        site_name=get_setting('name'),
        form=form,
        version=ver,
        main_menu='tech_director',
        base='shows',
        sub_base='list'
    )

@tech_director_bp.route('/get_shows/<string:state>', methods=['POST', 'GET'])
@login_required
@group_required("tech_director_admin")
def get_shows(state):
    '''Fetches the list of shows from the database and returns it as JSON.'''
    if state not in VALID_STATES:
        return jsonify({
            "message": "State (all/active) is missing or invalid."
        }), 422
    all_shows =  ShowService.list_all(state)
    return jsonify(all_shows)

@tech_director_bp.route('/update_show', methods=['POST', 'GET'])
@login_required
@group_required("tech_director_admin")
def update_show():
    '''Update student information'''
    update_response =  ShowService.update_show(request.get_json())
    return jsonify(update_response)
