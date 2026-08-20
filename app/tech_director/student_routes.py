"""Routes for the Flask web application handling Student Administration."""
import logging
import datetime
from mysql.connector import (
    errorcode,
    IntegrityError,
)
from flask import (
    render_template,
    request,
    jsonify
    )
from flask_login import login_required

from app.functions import (
    get_setting,
    group_required,
)

from .services.student_services import StudentService

from .tech_director_forms import TechDirectorForm

from .tech_director_routes import(
    VALID_ASSIGNMENTS,
    VALID_STATES
)

from . import tech_director_bp # pylint: disable=cyclic-import

log = logging.getLogger(__name__)

currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")

# Main page

@tech_director_bp.route('/students', methods=['POST', 'GET'])
@login_required
@group_required("tech_director_admin")
def students():
    """List Students"""
    form = TechDirectorForm()
    return render_template(
        'tech_director/students.html', 
        title='List Students',
        sub_title='Students',
        site_name=get_setting('name'),
        form=form,
        version=ver,
        main_menu='tech_director',
        base='students'
    )

@tech_director_bp.route('/api/list_students/<string:state>', methods=['GET'])
@login_required
@group_required("tech_director_admin")
def list_students(state):
    '''Fetches the list of students from the database and returns it as JSON.'''
    if state not in (['all', 'active']):
        return jsonify({
            "message": "State (all/active) is missing or invalid."
        }), 422
    all_students =  StudentService.get_students(state)
    return jsonify(all_students)

@tech_director_bp.route(
        '/api/assign_student/<string:state>/<string:assignment_group>',
        methods=['POST', 'PUT']
    )
@login_required
@group_required("tech_director_admin")
def assign_new_student(state, assignment_group):
    '''Assign a student (new or existing) to a group/show/etc.'''
    if assignment_group not in VALID_ASSIGNMENTS:
        return jsonify({
            "message": "Assignment type is missing or invalid."
        }), 422

    if state not in VALID_STATES:
        return jsonify({
            "message": "State (new/existing) is missing or invalid."
        }), 422

    try:
        add_response = StudentService.assign_student(
            request.get_json(),
            state,
            assignment_group,
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


@tech_director_bp.route('/api/add_student', methods=['POST', 'GET'])
@login_required
@group_required("tech_director_admin")
def add_student():
    '''Add an existing student to the AV Club'''
    add_response =  StudentService.add_student(request.get_json())
    return jsonify(add_response)

@tech_director_bp.route('/api/update_student', methods=['PUT'])
@login_required
@group_required("tech_director_admin")
def update_student():
    '''Update student information'''
    try:
        update_response =  StudentService.update_student(request.get_json())
        return jsonify(update_response)
    except ValueError as exc:
        log.warning("Invalid student update: %s", exc)

        return jsonify({
            "message": "System Error.  Contact Administrator."
        }), 400


@tech_director_bp.route('/api/update_membership_info/<string:assignment_group>', methods=['PUT'])
@login_required
@group_required("tech_director_admin")
def update_membership_info(assignment_group):
    '''Update basic info for entity membership'''
    if assignment_group not in VALID_ASSIGNMENTS:
        return jsonify({
            "message": "Assignment type is missing or invalid."
        }), 422
    update_response =  StudentService.update_membership_info(
        request.get_json(), assignment_group
        )
    return jsonify(update_response)

@tech_director_bp.route('/api/get_list_of_students_name_options/<string:assignment_group>', methods=['GET'])
@login_required
@group_required("tech_director_admin")
def get_list_of_students_name_options(assignment_group):
    """Get an options list of students for drop downs"""
    if assignment_group not in VALID_ASSIGNMENTS:
        return jsonify({
            "message": "Assignment type is missing or invalid."
        }), 422
    exclude = assignment_group
    return StudentService.get_students_active_names_options(exclude)
