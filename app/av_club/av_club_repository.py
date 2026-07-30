'''Repository (DB) handling'''
import logging
from flask import current_app
from app.functions_db import (
    check_row_exists,
    insert_db,
    query_single_table_db
)

log = logging.getLogger(__name__)

def check_for_student(email):
    '''Check if a row exists for this student'''
    return check_row_exists(current_app.config, "students", "email", email)

def add_student(data_values):
    '''Add student to the student table'''
    return insert_db(current_app.config, "students", data_values)

def get_students_all_db():
    '''Fetches the list of all students from the database.'''
    where_object = None
    return query_single_table_db(
        current_app.config,
        "*", 
        "students", 
        where_object,
        "firstName ASC"
    )

def get_students_active_db(start_of_current_year):
    '''Fetches the list of all students from the database.'''
    where_object = {
        'where_column':"graduationYear",
        'target_value': start_of_current_year + 1,
        'operator': ">="
    }
    return query_single_table_db(
        current_app.config,
        "*", 
        "students", 
        where_object,
        "firstName ASC"
    )
