"""Routes for the Flask web application handling lighting and QLab control via OSC."""
import datetime
from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from pythonosc.udp_client import SimpleUDPClient
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
from .admin_forms import AdminForm
from . import admin_bp
from app.functions import get_db, group_required, update_db, get_site_settings, insert_db


app.secret_key = app.config['SECRET_KEY']
app.dbconnection = app.config['DBCONNECTION']


currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")


@admin_bp.route('/', methods=['GET', 'POST'])
@login_required
@group_required("admin")
def admin_tasks():
    """Admin Tasks page route."""
    return render_template(
        'admin/admin.html', 
        title='Admin Tasks',
        site_name=app.site_name,  
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
        title='Admin Users', 
        site_name=app.site_name,
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
    users = get_users_db()
    return users

def get_users_db():
    with get_db(dbconnection=app.dbconnection) as db:
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
    form = AdminForm()

    editRow = request.get_json()

    if form.validate_on_submit():
        new_password = editRow["new_password"]
        user_id = editRow["ID"]
        hashed_password = generate_password_hash(new_password)

        with get_db(dbconnection=app.dbconnection) as db:
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
        title='Admin Groups', 
        site_name=app.site_name,
        form=form,
        version=ver, 
        main_menu='admin', 
        base='admin_groups',
        page_content=contents
    )

@admin_bp.route('/get_groups', methods=['POST', 'GET'])
@login_required
def get_groups():
    groups = get_groups_db()
    return groups

def get_groups_db():
    with get_db(dbconnection=app.dbconnection) as db:
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
        title='Admin Users to Groups', 
        site_name=app.site_name,
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
    user_id = request.args.get("user_id")

    with get_db(dbconnection=app.dbconnection) as db:
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
    data = request.get_json()

    user_id = data["user_id"]
    group_id = data["group_id"]
    assigned = data["assigned"]

    with get_db(dbconnection=app.dbconnection) as db:
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
    with get_db(dbconnection=app.dbconnection) as db:
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
        title='Admin Settings',
        site_name=app.site_name, 
        version=ver, 
        main_menu='admin', 
        base='admin_settings',
        page_content=settings
    )

def get_settings_db():
    with get_db(dbconnection=app.dbconnection) as db:
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM settings ORDER BY the_order"
        cursor.execute(query)
        settings_data = cursor.fetchall()
        return settings_data

@admin_bp.route('/get_settings', methods=['POST', 'GET'])
@login_required
@group_required("admin")
def get_settings():
    settings = get_settings_db()
    return settings


@admin_bp.route('/update_db_field', methods=['POST'])
@login_required
@group_required("admin")
def update_field_db():
    editRow = request.get_json()
    table = editRow['table']
    updateFields = {
        editRow['field']: editRow['value'],
        'sessionid': current_user.sessionid
    }
    updateResult = update_db(table, editRow['ID'], updateFields)
    app.site_settings = get_site_settings()
    app.site_name=app.site_settings['name']
    return jsonify({
        "status": "ok",
        "value": updateResult
    })

@admin_bp.route('/insert_db_row', methods=['POST'])
@login_required
@group_required("admin")
def insert_row_db():
    insertValues = request.get_json()
    insertRow = insertValues['rowData']
    table = insertValues['table']
    insertRow['sessionid'] = current_user.sessionid
    inserted_id = insert_db(table, insertRow)
    return jsonify({
        "status": "ok",
        "value": inserted_id
    })




