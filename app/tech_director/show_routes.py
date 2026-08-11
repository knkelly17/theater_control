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
    jsonify)
from flask_login import login_required

from app.functions import (
    get_setting,
    group_required,
)

from .services.show_services import ShowService, TeamService
from .services.student_services import StudentService

from .tech_director_forms import TechDirectorForm


from .tech_director_routes import (
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
        site_name=get_setting('name'),
        form=form,
        version=ver,
        main_menu='tech_director',
        base='shows',
        sub_base='list_show'
    )

@tech_director_bp.route('/students_shows', methods=['GET'])
@login_required
@group_required("tech_director_admin")
def students_shows():
    """List Show Assignment"""
    form = TechDirectorForm()
    active = "active"
    exclude = None
    form.show_id.choices = ShowService.list_show_names_options(active)
    form.student_id.choices = StudentService.get_students_active_names_options(exclude)
    return render_template(
        'tech_director/students_shows.html', 
        site_name=get_setting('name'),
        form=form,
        version=ver,
        main_menu='tech_director',
        base='shows',
        sub_base='assign_students_shows',
        assignment_group='show',
    )


@tech_director_bp.route('/api/list_teams_options/', methods=['GET'])
@login_required
@group_required("tech_director_admin")
def list_teams_options():
    '''get a list of teams for drop down selction'''
    all_teams =  TeamService.list_all('active')
    return jsonify(all_teams)

# /tech_director/api/get_show_assigments/${show_id}

@tech_director_bp.route('/api/list_shows/<string:status>', methods=['GET'])
@login_required
@group_required("tech_director_admin")
def list_shows(status):
    '''List all Shows'''
    if status not in (['all', 'active']):
        return jsonify({
            "message": "State (all/active) is missing or invalid."
        }), 422
    all_shows =  ShowService.list_all(status)
    return jsonify(all_shows)

@tech_director_bp.route('/api/update_show', methods=['PUT', 'POST'])
@login_required
@group_required("tech_director_admin")
def update_show():
    '''Update show details'''
    update_response =  ShowService.update_show(request.get_json())
    return jsonify(update_response)

@tech_director_bp.route('/api/add_show', methods=['POST'])
@login_required
@group_required("tech_director_admin")
def add_show():
    '''Add a show'''
    add_response =  ShowService.add_show(request.get_json())
    return jsonify(add_response)

@tech_director_bp.route(
        '/api/list_show_students/<int:show_id>',
        # <string:assignment_group>/<string:state> -- maybe we'll need this!
        methods=['GET']
    )
@login_required
@group_required("tech_director_admin")
def get_show_members(show_id):
    '''Fetches the list of students assigned to show and returns it as JSON.'''
    all_students =  ShowService.list_show_members(show_id)
    return jsonify(all_students)

@tech_director_bp.route(
        '/api/assign_student_show/<string:state>/',
        methods=['POST', 'PUT']
    )
@login_required
@group_required("tech_director_admin")
def assign_student_show(state):
    '''Assign a student (new or existing) to a show.'''

    if state not in VALID_STATES:
        return jsonify({
            "message": "State (new/existing) is missing or invalid."
        }), 422

    try:
        add_response = ShowService.assign_student_show(
            request.get_json(),
            state
        )
    except IntegrityError as error:
        if error.errno == errorcode.ER_DUP_ENTRY:
            # this contains the actual message: error.msg
            message = "Error completing task.  Contact Administrator."
            if 'email' in error.msg:
                message = "A student with that email address already exists."
            return jsonify({
                "message": message,
                "field": "email",
            }), 409

        log.exception("Database integrity error while creating student")
        return jsonify({
            "message": "The student could not be saved."
        }), 500

    return jsonify(add_response)
