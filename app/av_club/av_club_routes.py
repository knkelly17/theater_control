"""Routes for the Flask web application handling AV Club Administration."""
import logging
import datetime
from flask import (
    render_template,
    request,
    jsonify,
    current_app)
from flask_login import login_required, current_user
from pythonosc.udp_client import SimpleUDPClient

from app.functions import (
    get_setting,
    group_required,
    upload_file
)

from app.functions_db import (
    get_db,
    update_db,
    insert_db
)

from app.google_drive_user import (
    get_credentials,
    run_gas_api
)

from .av_club_services import (
    upload_student_gsheet,
    get_students_active
)

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
def get_students():
    '''Fetches the list of students from the database and returns it as JSON.'''
    all_students =  get_students_active()
    return jsonify(all_students)


@av_club_bp.route('/upload_students', methods=['POST', 'GET'])
@login_required
@group_required("av_club_admin")
@group_required("admin")
def upload_students():
    '''Upload students from Google Sheet'''
    form = AVClubForm()
    response = "Waiting for data"

    if request.form:
        student_data = upload_student_gsheet(
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