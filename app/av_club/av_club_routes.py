"""Routes for the Flask web application handling AV Club Administration."""
import logging
import datetime
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

from app.av_club import av_club_services

from .av_club_forms import AVClubForm
from . import av_club_bp # pylint: disable=cyclic-import

log = logging.getLogger(__name__)

currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")

@av_club_bp.route('/', methods=['GET', 'POST'])
@login_required
@group_required("av_club_admin")
def av_club_admin():
    """AV Club Control page route."""

    form = AVClubForm()
    return render_template(
        'av_club/av_club.html', 
        title='AV Club Amdin',
        site_name=get_setting(current_app.config, 'name'),
        form=form,
        version=ver,
        main_menu='av_club'
    )


@av_club_bp.route('/av_club_members', methods=['POST', 'GET'])
@login_required
@group_required("av_club_admin")
def av_club_members():
    """List AV Club Members"""
    contents = "AV Club Groups"
    form = AVClubForm()
    exclude = "avClub"
    form.choose_student.choices = av_club_services.get_students_active_names_options(exclude)
    return render_template(
        'av_club/av_club_members.html', 
        # title='List AV Club Members',
        # sub_title='AV Club Members',
        site_name=get_setting(current_app.config,'name'),
        form=form,
        version=ver,
        main_menu='av_club',
        base='av_club_members',
        page_content=contents
    )

@av_club_bp.route('/get_list_of_students', methods=['POST', 'GET'])
@login_required
@group_required("av_club_admin")
def get_list_of_students():
    """Get an options list of students for drop downs"""
    exclude = "avClub"
    return av_club_services.get_students_active_names_options(exclude)

@av_club_bp.route('/get_av_club_members', methods=['POST', 'GET'])
@login_required
@group_required("av_club_admin")
def get_av_club_members():
    '''Fetches the list of students from the database and returns it as JSON.'''
    active = request.args.get('active', default='Active')
    all_students =  av_club_services.get_av_club_members(active)
    return jsonify(all_students)

@av_club_bp.route('/add_existing_student', methods=['POST', 'GET'])
@login_required
@group_required("av_club_admin")
def add_existing_student():
    '''Add an existing student to the AV Club'''
    add_response =  av_club_services.add_existing_student(request.get_json())
    # log.warning(add_response)
    return jsonify(add_response)

@av_club_bp.route('/add_student', methods=['POST', 'GET'])
@login_required
@group_required("av_club_admin")
def add_student():
    '''Add an existing student to the AV Club'''
    add_response =  av_club_services.add_student(request.get_json())
    return jsonify(add_response)

@av_club_bp.route('/update_student', methods=['POST', 'GET'])
@login_required
@group_required("av_club_admin")
def update_student():
    '''Update student information'''
    log.warning(request.get_json())
    update_response =  av_club_services.update_student(request.get_json())
    # log.warning(add_response)
    return jsonify(update_response)

@av_club_bp.route('/update_member_info', methods=['POST', 'GET'])
@login_required
@group_required("av_club_admin")
def update_membe_info():
    '''Update basic info for av club member'''
    log.warning(request.get_json())
    update_response =  av_club_services.update_member_info(request.get_json())
    # log.warning(add_response)
    return jsonify(update_response)

@av_club_bp.route('/students', methods=['POST', 'GET'])
@login_required
@group_required("av_club_admin")
def students():
    """List Students"""
    contents = "AV Club Groups"
    form = AVClubForm()
    return render_template(
        'av_club/students.html', 
        title='List Students',
        sub_title='Students',
        site_name=get_setting(current_app.config,'name'),
        form=form,
        version=ver,
        main_menu='av_club',
        base='students',
        page_content=contents
    )

@av_club_bp.route('/get_students', methods=['POST', 'GET'])
@login_required
@group_required("av_club_admin")
def get_students():
    '''Fetches the list of students from the database and returns it as JSON.'''
    active = request.args.get('active', default='Active')
    all_students =  av_club_services.get_students(active)
    return jsonify(all_students)

@av_club_bp.route('/get_students_active', methods=['POST', 'GET'])
@login_required
@group_required("av_club_admin")
@group_required("av_club_admin")
def get_students_active():
    '''Fetches the list of active students from the database and returns it as JSON.'''
    all_students =  av_club_services.get_students_active()
    return jsonify(all_students)

@av_club_bp.route('/get_active_student_names', methods=['POST', 'GET'])
@login_required
@group_required("av_club_admin")
@group_required("av_club_admin")
def get_students_active_names():
    '''Fetches the list of students from the database and returns it as JSON.'''
    all_students =  av_club_services.get_students_active_names()
    return jsonify(all_students)


@av_club_bp.route('/upload_students', methods=['POST', 'GET'])
@login_required
@group_required("av_club_admin")
@group_required("admin")
def upload_students_gsheet():
    '''Upload students from Google Sheet'''
    form = AVClubForm()
    response = "Waiting for data"

    if request.form:
        student_data = av_club_services.upload_student_gsheet(
            request.form['google_sheet_id'],
            request.form['google_sheet_range']
            )
        response = student_data


    return render_template(
        'av_club/upload_students.html', 
        form=form,
        title='AV Club Student Upload',
        sub_title='Upload Students From Google Sheet',
        site_name=get_setting(current_app.config, 'name'),
        version=ver,
        main_menu='av_club',
        base='upload_students',
        upload_response=response

    )
