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
    jsonify
    )
from flask_login import login_required

from app.functions import (
    get_setting,
    group_required,
)

from .services import tech_director_services
from .services.student_services import StudentService
from .services.tech_director_services import AVClubService

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
    """Tech Director Main page route."""

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
    form = TechDirectorForm()
    exclude = "avclub"
    form.student_id.choices = StudentService.get_students_active_names_options(exclude)
    return render_template(
        'tech_director/av_club_members.html', 
        site_name=get_setting('name'),
        form=form,
        version=ver,
        main_menu='tech_director',
        base='av_club_members',
        assignment_group='avclub',
        sub_base='assign_student'
    )

@tech_director_bp.route(
        '/api/assign_student_avclub/<string:state>/',
        methods=['POST', 'PUT']
    )
@login_required
@group_required("tech_director_admin")
def assign_student_avclub(state):
    '''Assign a student (new or existing) to the AV Club.'''

    if state not in VALID_STATES:
        return jsonify({
            "message": "State (new/existing) is missing or invalid."
        }), 422

    try:
        add_response = AVClubService.assign_student_avclub(
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


@tech_director_bp.route(
        '/api/list_avclub_students/<string:state>',
        methods=['GET']
    )
@login_required
@group_required("tech_director_admin")
def list_avclub_students(state):
    '''Fetches the list of students in the AV Club.'''
    if state not in VALID_STATES:
        return jsonify({
            "message": "State (all/active) is missing or invalid."
        }), 422
    all_students =  AVClubService.list_avclub_students(state)
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
