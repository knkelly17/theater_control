'''Utility functions for the app.'''
import os
from functools import wraps
from datetime import datetime
from flask import current_app, request, render_template
from flask_login import current_user
from werkzeug.utils import secure_filename
from app.functions_db import (
    get_db_value,
    query_single_table_db
)

def group_required(*group_names):
    '''Get groups for a user'''
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return {"error": "Unauthorized"}, 401
                return render_template(
                    'index.html',
                    title='Unauthorized',
                    page_content='Unauthorized'
                ), 401
            if not any(current_user.has_group(g) for g in group_names):
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return {"error": "Forbidden"}, 403
                return render_template(
                    'index.html',
                    title='Forbidden',
                    page_content='Forbidden'
                ), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


def get_site_settings(config):
    '''Get all settings from the DB'''
    where_object = {
        'where_colume': "active",
        'target_value': " = 'Y'"
    }
    query_single_table_db(config, "name, value", 'settings', where_object, None)


def get_setting(config, key):
    '''Get a specific setting value from the settings table.'''
    return get_db_value(config, 'value', 'settings', ' name = ' + key)



def upload_file(file):
    '''Upload a file for temporary action'''
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)

    file.save(file_path)
    return file_path

def get_current_academic_year_start():
    '''Get the current academic year'''
    today = datetime.now()
    # Python uses 1-indexed months (January is 1, June is 6, July is 7)
    return today.year - 1 if today.month < 7 else today.year

def check_if_current_student(graduation_year):
    '''Check if student is still active'''
    return graduation_year >= get_current_academic_year_start() + 1
