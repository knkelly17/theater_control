'''Repository (DB) handling'''
import logging
from flask import current_app
from app.functions import (
    check_row_exists,
    insert_db
)

log = logging.getLogger(__name__)

def check_for_student(email):
    '''Check if a row exists for this student'''
    return check_row_exists(current_app.config, "students", "email", email)

def add_student(data_values):
    '''Add student to the student table'''
    return insert_db(current_app.config, "students", data_values)

