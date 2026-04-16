"""Routes for the Flask web application handling lighting and QLab control via OSC."""
import datetime
from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from pythonosc.udp_client import SimpleUDPClient
from werkzeug.security import generate_password_hash, check_password_hash
# import mysql.connector
from app import app
from .admin_forms import AdminForm
from . import admin_bp
from systems import qlab_ip, qlab_port
from app.functions import get_db, update_db, get_site_settings, insert_db


app.secret_key = app.config['SECRET_KEY']
app.dbconnection = app.config['DBCONNECTION']


currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")


@admin_bp.route('/', methods=['GET', 'POST'])
@login_required
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
def get_users():
    users = get_users_db()
    return users

def get_users_db():
    with get_db(dbconnection=app.dbconnection) as db:
        cursor = db.cursor(dictionary=True)
        user_fields = "ID, username, userType, first_name, last_name, email, active"
        query = "SELECT " + user_fields + " FROM users ORDER BY ID"
        cursor.execute(query)
        settings_data = cursor.fetchall()
        return settings_data

@admin_bp.route('/admin_groups', methods=['POST', 'GET'])
@login_required
def admin_groups():
    """Admin Groups page route."""
    contents = "Admin Groups"
    return render_template(
        'admin/admin.html', 
        title='Admin Groups', 
        version=ver, 
        main_menu='admin', 
        base='admin_groups',
        page_content=contents
    )

    
@admin_bp.route('/admin_settings', methods=['POST', 'GET'])
@login_required
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
def get_settings():
    settings = get_settings_db()
    return settings



