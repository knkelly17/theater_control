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

from .services.student_services import StudentService
from .services.tech_director_services import (
    AVClubService,
    UploadService,
    SkillsService,
    TeamService
)
from .services.show_services import ShowService

from .tech_director_forms import TechDirectorForm

from . import tech_director_bp # pylint: disable=cyclic-import

log = logging.getLogger(__name__)

currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")

VALID_ASSIGNMENTS = {'avclub', 'show', 'inventory', 'all'}
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

@tech_director_bp.route('/api/upload_google_sheets', methods=['POST'])
@login_required
@group_required("tech_director_admin")
@group_required("admin")
def api_upload_google_sheets():
    '''upload data from google'''
    payload = request.get_json()
    match payload['importProcess']:
        case 'student':
            response = UploadService.upload_student_gsheet(
                payload['sheetId'],payload['sheetRange']
            )
        case 'show_assign':
            response = UploadService.upload_show_assign_gsheet(
                payload['sheetId'],payload['sheetRange'],payload['showId']
            )
        case _:
            response = 'No action taken'
    return jsonify(response)

@tech_director_bp.route('/upload_google_sheets', methods=['GET'])
@login_required
@group_required("tech_director_admin")
@group_required("admin")
def upload_google_sheets():
    '''Upload students from Google Sheet'''
    form = TechDirectorForm()
    active = "active"
    form.show_id.choices = ShowService.list_show_names_options(active)
    return render_template(
        'tech_director/upload_google_sheets.html', 
        form=form,
        title='AV Club Student Upload',
        sub_title='Upload From Google Sheet',
        site_name=get_setting('name'),
        version=ver,
        main_menu='tech_director',
        base='upload_google_sheets'
    )

#### TEAMS ####

@tech_director_bp.route('/api/list_teams_options/', methods=['GET'])
@login_required
@group_required("tech_director_admin")
def list_teams_options():
    '''get a list of teams for drop down selction'''
    all_teams =  TeamService.list_all('active')
    return jsonify(all_teams)

@tech_director_bp.route('/api/list_tech_teams_options/', methods=['GET'])
@login_required
@group_required("tech_director_admin")
def list_tech_teams_options():
    '''get a list of teams for drop down selction'''
    all_teams =  TeamService.list_all_tech_team('active')
    return jsonify(all_teams)

#### SKILLS ####

@tech_director_bp.route('/skills', methods=['GET'])
@login_required
@group_required("tech_director_admin")
def skills():
    """List Skills"""
    form = TechDirectorForm()
    return render_template(
        'tech_director/skills.html', 
        site_name=get_setting('name'),
        form=form,
        version=ver,
        main_menu='tech_director',
        base='skills',
        sub_base='list_skills'
    )

@tech_director_bp.route('/students_skills', methods=['GET'])
@login_required
@group_required("tech_director_admin")
def students_skills():
    """List Skills Assignment"""
    form = TechDirectorForm()
    active = "active"
    exclude = None
    form.show_id.choices = ShowService.list_show_names_options(active)
    form.student_id.choices = StudentService.get_students_active_names_options(exclude)
    return render_template(
        'tech_director/students_skills.html', 
        site_name=get_setting('name'),
        form=form,
        version=ver,
        main_menu='tech_director',
        base='skills',
        sub_base='students_skills'
    )

@tech_director_bp.route('/api/list_skills/<string:status>', methods=['GET'])
@login_required
@group_required("tech_director_admin")
def list_skills(status):
    '''List all Skills'''
    if status not in (['all', 'active']):
        return jsonify({
            "message": "State (all/active) is missing or invalid."
        }), 422
    all_shows =  SkillsService.list_all(status)
    return jsonify(all_shows)

@tech_director_bp.route('/api/list_skill_levels/', methods=['GET'])
@login_required
@group_required("tech_director_admin")
def list_skill_levels():
    '''get a list of teams for drop down selction'''
    all_skill_levels =  SkillsService.list_all_skill_levels()
    return jsonify(all_skill_levels)

@tech_director_bp.route('/api/update_skill', methods=['PUT', 'POST'])
@login_required
@group_required("tech_director_admin")
def update_skill():
    '''Update skill details'''
    update_response =  SkillsService.update_skill(request.get_json())
    return jsonify(update_response)

@tech_director_bp.route('/api/add_skill', methods=['POST'])
@login_required
@group_required("tech_director_admin")
def add_skill():
    '''Add a show'''
    add_response =  SkillsService.add_skill(request.get_json())
    return jsonify(add_response)

@tech_director_bp.route(
        '/api/students_skills_grid',
        methods=['GET']
    )
@login_required
@group_required("tech_director_admin")
def get_students_skills_grid():
    '''Fetches the matrix of students skills and returns it as JSON.'''
    student_skills_grid =  SkillsService.get_student_skills_grid()
    return jsonify(student_skills_grid)


# ASSIGN STUDENT TO SKILLS
@tech_director_bp.route(
        '/api/assign_student_skill/',
        methods=['POST', 'PUT']
    )
@login_required
@group_required("tech_director_admin")
def assign_student_skill():
    '''Assign skill level to student.'''

    try:
        update_response = SkillsService.update_student_skill(request.get_json())
        return jsonify(update_response)
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
    except ValueError as exc:
        log.error("Invalid update: %s", exc)
        return jsonify({
            "message": "System Error.  Contact Administrator."
        }), 400
