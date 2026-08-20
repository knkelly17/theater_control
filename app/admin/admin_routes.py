"""Routes for the Flask web application handling lighting and QLab control via OSC."""
import logging
from datetime import datetime
from mysql.connector import (
    errorcode,
    IntegrityError,
)
from flask import render_template, request, jsonify
from flask_login import login_required
from app.functions import (
    group_required,
)

from app.forms import SiteForm

from app.services.device_service import get_devices
from app.settings_cache import get_cache_last_loaded

from .services.admin_services import(
    UserService,
    GroupService,
    SettingService,
)


from .admin_forms import AdminForm
from . import admin_bp # pylint: disable=cyclic-import


log = logging.getLogger(__name__)

currentDT = datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")

@admin_bp.route('/', methods=['GET', 'POST'])
@login_required
@group_required("admin")
def admin_tasks():
    """Admin Tasks page route."""
    return render_template(
        'admin/admin.html', 
        title='Admin Tasks',
        sub_title='Admin Menu',
        version=ver,
        main_menu='admin')

#USERS

@admin_bp.route('/admin_users', methods=['POST', 'GET'])
@login_required
@group_required("admin")
def admin_users():
    """Admin Users page route."""
    return render_template(
        'admin/users.html', 
        title='Admin Tasks',
        sub_title='Users',
        form=AdminForm(),
        site_form = SiteForm(),
        version=ver,
        main_menu='admin',
        base='admin_users',
    )


@admin_bp.route('/api/list_users/<string:status>', methods=['GET'])
@login_required
@group_required("admin")
def list_users(status):
    '''Fetches the list of users from the database and returns it as JSON.'''
    users = UserService.list_all(status)
    return users

@admin_bp.route('/api/update_user', methods=['PUT'])
@login_required
@group_required("admin")
def update_user():
    '''Update user details'''
    update_response =  UserService.update_user(request.get_json())
    return jsonify(update_response)

@admin_bp.route('/api/add_user', methods=['POST'])
@login_required
@group_required("admin")
def add_user():
    '''Add a user'''
    add_response =  UserService.add_user(request.get_json())
    return jsonify(add_response)

@admin_bp.route("/api/change_user_password", methods=['PUT'])
@login_required
@group_required("admin")
def change_user_password():
    '''Allows an admin to change a user's password. 
    Expects a JSON payload with the new password and user ID.'''
    form = AdminForm()

    if not form.validate_on_submit():
        # return validation errors
        return jsonify({
            "login_result": 0,
            "errors": form.errors
        }), 400

    change_response = UserService.change_user_password(request.get_json())
    return jsonify(change_response)

#GROUPS

@admin_bp.route('/admin_groups', methods=['GET'])
@login_required
@group_required("admin")
def admin_groups():
    """Admin Groups page route."""
    return render_template(
        'admin/groups.html', 
        title='Admin Tasks',
        sub_title='Groups',
        form=AdminForm(),
        site_form = SiteForm(),
        version=ver,
        main_menu='admin',
        base='admin_groups'
    )

@admin_bp.route('/api/list_groups/<string:status>', methods=['GET'])
@login_required
def get_groups(status):
    '''Fetches the list of user groups from the database and returns it as JSON.'''
    groups = GroupService.list_all(status)
    return groups

@admin_bp.route('/api/update_group', methods=['PUT'])
@login_required
@group_required("admin")
def update_group():
    '''Update group details'''
    update_response =  GroupService.update_group(request.get_json())
    return jsonify(update_response)

@admin_bp.route('/api/add_group', methods=['POST'])
@login_required
@group_required("admin")
def add_group():
    '''Add a group'''
    add_response =  GroupService.add_group(request.get_json())
    return jsonify(add_response)

#USER2GROUPS
@admin_bp.route('/admin_user2group', methods=['GET'])
@login_required
@group_required("admin")
def admin_user2group():
    """Admin User2Group page route."""
    return render_template(
        'admin/user2group.html', 
        title='Admin Tasks',
        sub_title='Users to Groups',
        form=AdminForm(),
        site_form = SiteForm(),
        version=ver,
        main_menu='admin',
        base='admin_user2group'
    )

@admin_bp.route("/api/permissions_matrix")
@login_required
@group_required("admin")
def permissions_matrix():
    '''Admin Permissions Matrix page route.'''
    user_group_matrix = UserService.get_user_group_matrix()
    return user_group_matrix

@admin_bp.route("/api/update_user_group", methods=["POST"])
@login_required
@group_required("admin")
def update_user_group():
    '''Update the user's group assignment based on the provided data.'''
    return UserService.update_user_group(request.get_json())

#SETTINGS

@admin_bp.route('/admin_settings', methods=['GET'])
@login_required
@group_required("admin")
def admin_settings():
    """Admin Settings page route."""
    return render_template(
        'admin/settings.html', 
        form=AdminForm(),
        site_form = SiteForm(),
        title='Admin Tasks',
        sub_title='Settings',
        version=ver,
        main_menu='admin',
        base='admin_settings'
    )

@admin_bp.route('/api/list_settings/<string:status>', methods=['GET'])
@login_required
@group_required("admin")
def get_settings(status):
    '''Fetches the list of settings from the database and returns it as JSON.'''
    settings = SettingService.list_all(status)
    return settings

@admin_bp.route('/api/update_setting', methods=['PUT'])
@login_required
@group_required("admin")
def update_setting():
    '''Update setting details'''
    try:
        update_response =  SettingService.update_setting(request.get_json())
    except IntegrityError as error:
        if error.errno == errorcode.ER_DUP_ENTRY:
            # this contains the actual message: error.msg
            message = "Error completing task.  Contact Administrator."
            if 'settings.name' in error.msg:
                message = "A setting with that name already exists."
            return jsonify({
                "message": message,
                "field": "name",
            }), 409
    return jsonify(update_response)

@admin_bp.route('/api/add_setting', methods=['POST'])
@login_required
@group_required("admin")
def add_setting():
    '''Add a setting'''
    try:
        add_response =  SettingService.add_setting(request.get_json())
    except IntegrityError as error:
        if error.errno == errorcode.ER_DUP_ENTRY:
            # this contains the actual message: error.msg
            message = "Error completing task.  Contact Administrator."
            if 'settings.name' in error.msg:
                message = "A setting with that name already exists."
            return jsonify({
                "message": message,
                "field": "name",
            }), 409

    return jsonify(add_response)


##########Status page routes##########

@admin_bp.route("/admin_status")
@login_required
@group_required("admin")
def admin_status():
    '''Admin Status page route.'''
    return render_template(
        "admin/status.html",
        settings_last_updated=SettingService.get_last_setting_update(),
        cache_last_loaded = get_cache_last_loaded(),
        devices=get_devices(),
        title='Admin Tasks',
        sub_title='System Status',
        version=ver,
        main_menu='admin',
        base='admin_status'
    )

@admin_bp.route('/api/get_settings', methods=['GET'])
@login_required
@group_required("admin")
def get_settings_status():
    '''Fetches the list of settings from the database and returns it as JSON.'''
    status = 'all'
    settings = SettingService.list_all(status)
    return settings

########## END Status page routes##########
