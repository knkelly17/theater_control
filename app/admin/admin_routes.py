"""Routes for the Flask web application handling lighting and QLab control via OSC."""
import logging
from datetime import datetime
from flask import current_app, render_template, request, jsonify
from flask_login import login_required, current_user
# from pythonosc.udp_client import SimpleUDPClient
from werkzeug.security import generate_password_hash
from app.functions import (
    get_db,
    get_db_value,
    get_setting,
    group_required,
    update_db,
    insert_db
)
from config import DBCONNECTION
from .admin_forms import AdminForm
from . import admin_bp


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
        site_name=get_setting('name'),
        version=ver,
        main_menu='admin')

@admin_bp.route('/admin_users', methods=['POST', 'GET'])
@login_required
@group_required("admin")
def admin_users():
    """Admin Users page route."""
    contents = "Admin Users"
    form = AdminForm()
    return render_template(
        'admin/users.html', 
        title='Admin Tasks',
        sub_title='Users',
        site_name=get_setting('name'),
        form=form,
        version=ver,
        main_menu='admin',
        base='admin_users',
        page_content=contents
    )


@admin_bp.route('/get_users', methods=['POST', 'GET'])
@login_required
@group_required("admin")
def get_users():
    '''Fetches the list of users from the database and returns it as JSON.'''
    users = get_users_db()
    return users

def get_users_db():
    '''Fetches the list of users from the database.'''
    with get_db(dbconnection=DBCONNECTION) as db:
        cursor = db.cursor(dictionary=True)
        user_fields = 'ID, username, first_name, last_name, email, active'
        query = "SELECT " + user_fields + " FROM users ORDER BY username"
        cursor.execute(query)
        settings_data = cursor.fetchall()
        return settings_data

@admin_bp.route("/change_password", methods=["GET", "POST"])
@login_required
@group_required("admin")
def change_password():
    '''Allows an admin to change a user's password. 
    Expects a JSON payload with the new password and user ID.'''
    form = AdminForm()

    edit_row = request.get_json()

    if form.validate_on_submit():
        new_password = edit_row["new_password"]
        user_id = edit_row["ID"]
        hashed_password = generate_password_hash(new_password)

        with get_db(dbconnection=DBCONNECTION) as db:
            cursor = db.cursor()
            cursor.execute("UPDATE users SET password_hash=%s WHERE ID=%s",
                           (hashed_password, user_id))
            db.commit()
            # do password update logic here
            return jsonify({
                "login_result": 1, 
                "message": "Password updated successfully. You may close this window."
            })

    if request.method == "POST":
        # return validation errors
        return jsonify({
            "login_result": 0,
            "errors": form.errors
        }), 400

    return render_template("admin/users.html", form=form)

@admin_bp.route('/admin_groups', methods=['POST', 'GET'])
@login_required
@group_required("admin")
def admin_groups():
    """Admin Groups page route."""
    contents = "Admin Groups"
    form = AdminForm()
    return render_template(
        'admin/groups.html', 
        title='Admin Tasks',
        sub_title='Groups',
        site_name=get_setting('name'),
        form=form,
        version=ver,
        main_menu='admin',
        base='admin_groups',
        page_content=contents
    )

@admin_bp.route('/get_groups', methods=['POST', 'GET'])
@login_required
def get_groups():
    '''Fetches the list of user groups from the database and returns it as JSON.'''
    groups = get_groups_db()
    return groups

def get_groups_db():
    '''Fetches the list of user groups from the database.'''
    with get_db(dbconnection=DBCONNECTION) as db:
        cursor = db.cursor(dictionary=True)
        group_fields = 'ID, name, description, active'
        query = "SELECT " + group_fields + " FROM user_groups ORDER BY name"
        print(query)
        cursor.execute(query)
        groups_data = cursor.fetchall()
        return groups_data

@admin_bp.route('/admin_user2group', methods=['POST', 'GET'])
@login_required
@group_required("admin")
def admin_user2group():
    """Admin User2Group page route."""
    contents = "Admin User2Group"
    form = AdminForm()
    return render_template(
        'admin/user2group.html', 
        title='Admin Tasks',
        sub_title='Users to Groups',
        site_name=get_setting('name'),
        form=form,
        version=ver,
        main_menu='admin',
        base='admin_user2group',
        page_content=contents
    )

@admin_bp.route("/get_user_groups")
@login_required
@group_required("admin")
def get_user_groups():
    '''Fetches all groups and the groups assigned to a specific user, 
    returning the data as JSON.'''

    user_id = request.args.get("user_id")

    with get_db(dbconnection=DBCONNECTION) as db:
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT ID, name FROM user_groups")
        all_groups = cursor.fetchall()

        cursor.execute("""
            SELECT g.ID, g.name
            FROM user_groups g
            JOIN user2group ug ON g.ID = ug.groupID
            WHERE ug.userID = %s
        """, (user_id,))
        user_groups = cursor.fetchall()

    return jsonify({
        "all_groups": all_groups,
        "user_groups": user_groups
    })

@admin_bp.route("/update_user_group", methods=["POST"])
@login_required
@group_required("admin")
def update_user_group():
    '''Update the user's group assignment based on the provided data.'''
    data = request.get_json()

    user_id = data["user_id"]
    group_id = data["group_id"]
    assigned = data["assigned"]

    with get_db(dbconnection=DBCONNECTION) as db:
        cursor = db.cursor()

        if assigned:
            cursor.execute("""
                INSERT IGNORE INTO user2group (userID, groupID)
                VALUES (%s, %s)
            """, (user_id, group_id))
        else:
            cursor.execute("""
                DELETE FROM user2group
                WHERE userID=%s AND groupID=%s
            """, (user_id, group_id))

        db.commit()

    return {"status": "ok"}

@admin_bp.route("/permissions_matrix")
@login_required
@group_required("admin")
def permissions_matrix():
    '''Admin Permissions Matrix page route.'''
    with get_db(dbconnection=DBCONNECTION) as db:
        cur = db.cursor(dictionary=True)

        cur.execute("SELECT id, username FROM users")
        users = cur.fetchall()

        cur.execute("SELECT id, name FROM user_groups")
        groups = cur.fetchall()

        cur.execute("SELECT userID, groupID FROM user2group")
        links = cur.fetchall()

    # build a lookup set for fast checks
    link_set = {(l["userID"], l["groupID"]) for l in links}

    # build rows like: {id, username, g_1: true/false, g_2: ...}
    rows = []
    for u in users:
        row = {"id": u["id"], "username": u["username"]}
        for g in groups:
            row[f"g_{g['id']}"] = (u["id"], g["id"]) in link_set
        rows.append(row)

    return {"rows": rows, "groups": groups}

@admin_bp.route('/admin_settings', methods=['POST', 'GET'])
@login_required
@group_required("admin")
def admin_settings():
    """Admin Settings page route."""
    settings = get_settings_db()
    form = AdminForm()
    return render_template(
        'admin/settings.html', 
        form=form,
        title='Admin Tasks',
        sub_title='Settings',
        site_name=get_setting('name'),
        version=ver,
        main_menu='admin',
        base='admin_settings',
        page_content=settings
    )

def get_settings_db():
    '''Fetches the list of settings from the database.'''
    with get_db(dbconnection=DBCONNECTION) as db:
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM settings ORDER BY the_order"
        cursor.execute(query)
        settings_data = cursor.fetchall()
        return settings_data

@admin_bp.route('/get_settings', methods=['POST', 'GET'])
@login_required
@group_required("admin")
def get_settings():
    '''Fetches the list of settings from the database and returns it as JSON.'''
    settings = get_settings_db()
    return settings


########### EXT QLAB COMMANDS##########

@admin_bp.route('/qlab_commands', methods=['POST', 'GET'])
@login_required
@group_required("admin")
def admin_qlab_commands():
    """Admin Settings page route."""
    qlab_commands = get_qlab_commands_db()
    form = AdminForm()
    return render_template(
        'admin/qlab_commands.html', 
        form=form,
        title='Admin Tasks',
        sub_title='QLAB Commands',
        site_name=get_setting('name'),
        version=ver,
        main_menu='admin',
        base='admin_qlab_commands',
        page_content=qlab_commands
    )


def get_qlab_commands_db():
    '''Fetches the list of QLab commands from the database.'''
    with get_db(dbconnection=DBCONNECTION) as db:
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM qlab_commands ORDER BY name"
        cursor.execute(query)
        qlab_commands_data = cursor.fetchall()
        return qlab_commands_data

@admin_bp.route('/get_qlab_commands', methods=['POST', 'GET'])
@login_required
@group_required("admin")
def get_qlab_commands():
    '''Fetches the list of QLab commands from the database and returns it as JSON.'''
    qlab_commands = get_qlab_commands_db()
    return qlab_commands

##########END EXT QLAB COMMANDS##########


@admin_bp.route('/update_db_field', methods=['POST'])
@login_required
@group_required("admin")
def update_field_db():
    '''Update a specific field in the specified table for the given ID. 
    The sessionid of the current user is automatically included in the update.'''
    edit_row = request.get_json()
    table = edit_row['table']
    update_fields = {
        edit_row['field']: edit_row['value'],
        'sessionid': current_user.sessionid
    }
    update_result = update_db(table, edit_row['ID'], update_fields)
    current_app.settings_last_loaded = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    return jsonify({
        "status": "ok",
        "value": update_result
    })

@admin_bp.route('/insert_db_row', methods=['POST'])
@login_required
@group_required("admin")
def insert_row_db():
    '''Insert a new row into the specified table 
    with the provided data. The sessionid of the current user 
    is automatically included in the inserted data.'''

    insert_values = request.get_json()
    insert_row = insert_values['rowData']
    table = insert_values['table']
    insert_row['sessionid'] = current_user.sessionid
    inserted_id = insert_db(table, insert_row)
    current_app.settings_last_loaded = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    return jsonify({
        "status": "ok",
        "value": inserted_id
    })


##########Status page routes##########
@admin_bp.route("/admin_status")
@login_required
@group_required("admin")
def admin_status():
    '''Admin Status page route.'''
    return render_template(
        "admin/status.html",
        last_loaded=get_db_value("MAX(timestamp)", "settings", "1"),
        devices=getattr(current_app, 'device_last_seen', []),
        title='Admin Tasks',
        sub_title='System Status',
        site_name=get_setting('name'),
        version=ver,
        main_menu='admin',
        base='admin_status'
    )
