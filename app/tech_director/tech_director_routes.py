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

from .services import tech_director_services

from .tech_director_forms import TechDirectorForm
from . import tech_director_bp # pylint: disable=cyclic-import

log = logging.getLogger(__name__)

currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")

VALID_ASSIGNMENTS = {'avclub', 'show', 'all'}
VALID_STATES = {'new', 'existing', 'all', 'active'}

# Main page

@tech_director_bp.route('/', methods=['GET', 'POST'])
@login_required
@group_required("tech_director_admin")
def tech_director_admin():
    """AV Club Control page route."""

    form = TechDirectorForm()
    return render_template(
        'tech_director/tech_director.html', 
        title='AV Club Amdin',
        site_name=get_setting('name'),
        form=form,
        version=ver,
        main_menu='tech_director'
    )

@tech_director_bp.route('/av_club_members', methods=['POST', 'GET'])
@login_required
@group_required("tech_director_admin")
def av_club_members():
    """List AV Club Members"""
    contents = "AV Club Groups"
    form = TechDirectorForm()
    exclude = "avclub"
    form.studentId.choices = tech_director_services.get_students_active_names_options(exclude)
    return render_template(
        'tech_director/av_club_members.html', 
        # title='List AV Club Members',
        # sub_title='AV Club Members',
        site_name=get_setting('name'),
        form=form,
        version=ver,
        main_menu='tech_director',
        base='av_club_members',
        assignment_group='avclub',
        page_content=contents
    )

#STUDENTS

@tech_director_bp.route('/students', methods=['POST', 'GET'])
@login_required
@group_required("tech_director_admin")
def students():
    """List Students"""
    contents = "AV Club Groups"
    form = TechDirectorForm()
    return render_template(
        'tech_director/students.html', 
        title='List Students',
        sub_title='Students',
        site_name=get_setting('name'),
        form=form,
        version=ver,
        main_menu='tech_director',
        base='students',
        page_content=contents
    )

### Helper routes

@tech_director_bp.route('/get_list_of_students/<string:assignment_group>', methods=['POST', 'GET'])
@login_required
@group_required("tech_director_admin")
def get_list_of_students(assignment_group):
    """Get an options list of students for drop downs"""
    if assignment_group not in VALID_ASSIGNMENTS:
        return jsonify({
            "message": "Assignment type is missing or invalid."
        }), 422
    exclude = assignment_group
    return tech_director_services.get_students_active_names_options(exclude)


@tech_director_bp.route(
        '/get_group_members/<string:assignment_group>/<string:state>',
        methods=['POST', 'GET']
    )
@login_required
@group_required("tech_director_admin")
def get_group_members(assignment_group, state):
    '''Fetches the list of students from the database and returns it as JSON.'''
    if assignment_group not in VALID_ASSIGNMENTS:
        return jsonify({
            "message": "Assignment type is missing or invalid."
        }), 422
    if state not in VALID_STATES:
        return jsonify({
            "message": "State (all/active) is missing or invalid."
        }), 422

    # active = request.args.get('active', default='Active')
    all_students =  tech_director_services.get_group_members(assignment_group, state)
    return jsonify(all_students)

@tech_director_bp.route('/add_existing_student', methods=['POST', 'GET'])
@login_required
@group_required("tech_director_admin")
def add_existing_student():
    '''Add an existing student to the AV Club'''
    add_response =  tech_director_services.add_existing_student(request.get_json())
    # log.warning(add_response)
    return jsonify(add_response)

@tech_director_bp.route(
        '/assign_student/<string:state>/<string:assignment_group>',
        methods=['POST']
    )
@login_required
@group_required("tech_director_admin")
def assign_new_student(state, assignment_group):
    '''Assign a student (new or existing) to a group.'''
    if assignment_group not in VALID_ASSIGNMENTS:
        return jsonify({
            "message": "Assignment type is missing or invalid."
        }), 422

    if state not in VALID_STATES:
        return jsonify({
            "message": "State (new/existing) is missing or invalid."
        }), 422

    try:
        add_response = tech_director_services.assign_student(
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


@tech_director_bp.route('/add_student', methods=['POST', 'GET'])
@login_required
@group_required("tech_director_admin")
def add_student():
    '''Add an existing student to the AV Club'''
    add_response =  tech_director_services.add_student(request.get_json())
    return jsonify(add_response)

@tech_director_bp.route('/update_student', methods=['POST', 'GET'])
@login_required
@group_required("tech_director_admin")
def update_student():
    '''Update student information'''
    log.warning(request.get_json())
    update_response =  tech_director_services.update_student(request.get_json())
    # log.warning(add_response)
    return jsonify(update_response)

@tech_director_bp.route('/update_member_info', methods=['POST', 'GET'])
@login_required
@group_required("tech_director_admin")
def update_membe_info():
    '''Update basic info for av club member'''
    log.warning(request.get_json())
    update_response =  tech_director_services.update_member_info(request.get_json())
    # log.warning(add_response)
    return jsonify(update_response)

@tech_director_bp.route('/get_students/<string:state>', methods=['POST', 'GET'])
@login_required
@group_required("tech_director_admin")
def get_students(state):
    '''Fetches the list of students from the database and returns it as JSON.'''
    if state not in (['all', 'active']):
        return jsonify({
            "message": "State (all/active) is missing or invalid."
        }), 422
    all_students =  tech_director_services.get_students(state)
    return jsonify(all_students)

@tech_director_bp.route('/get_students_active', methods=['POST', 'GET'])
@login_required
@group_required("tech_director_admin")
@group_required("tech_director_admin")
def get_students_active():
    '''Fetches the list of active students from the database and returns it as JSON.'''
    all_students =  tech_director_services.get_students_active()
    return jsonify(all_students)

@tech_director_bp.route('/get_active_student_names', methods=['POST', 'GET'])
@login_required
@group_required("tech_director_admin")
@group_required("tech_director_admin")
def get_students_active_names():
    '''Fetches the list of students from the database and returns it as JSON.'''
    all_students =  tech_director_services.get_students_active_names()
    return jsonify(all_students)


@tech_director_bp.route('/upload_students', methods=['POST', 'GET'])
@login_required
@group_required("tech_director_admin")
@group_required("admin")
def upload_students_gsheet():
    '''Upload students from Google Sheet'''
    form = TechDirectorForm()
    response = "Waiting for data"

    if request.form:
        student_data = tech_director_services.upload_student_gsheet(
            request.form['google_sheet_id'],
            request.form['google_sheet_range']
            )
        response = student_data


    return render_template(
        'tech_director/upload_students.html', 
        form=form,
        title='AV Club Student Upload',
        sub_title='Upload Students From Google Sheet',
        site_name=get_setting('name'),
        version=ver,
        main_menu='tech_director',
        base='upload_students',
        upload_response=response

    )
