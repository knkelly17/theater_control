'''Repository (DB) handling'''
import logging
from flask import current_app
from app.functions_db import (
    check_row_exists,
    insert_db,
    update_db,
    query_db
)

log = logging.getLogger(__name__)

def check_for_student(email):
    '''Check if a row exists for this student'''
    return check_row_exists(current_app.config, "students", "email", email)

def get_students_all_db():
    '''Fetches the list of all students from the database.'''
    where_object = None
    return query_db(
        current_app.config,
        "*", 
        "students", 
        where_object,
        "firstName ASC"
    )

def get_students(active, start_of_current_year, data_needed, sort_by, exclude_items):
    '''Fetches the list of active students from the database.'''

    field_mappings = {
        "all":"students.ID as indexId, students.*",
        "fullName": "students.ID, CONCAT(firstName,' ',lastName) AS fullName"
    }

    sort_mappings = {
        "fullName": "fullName ASC",
        "grade": "students.graduationYear ASC"
    }

    exclude_conditions_map = {
        "avClub": {
            "column": "user2avclub.studentId",
            "operator": "IS",
            "value": None
        }
    }

    exclude_joins = {
        "avClub": ["LEFT JOIN user2avclub ON students.ID = user2avclub.studentId"]
    }

    fields = field_mappings.get(data_needed, "students.ID as indexId, students.*")
    sort = sort_mappings.get(sort_by, "students.graduationYear ASC")
    exclude_conditions = exclude_conditions_map.get(exclude_items, None)
    joins = exclude_joins.get(exclude_items, None)

    where_object = None

    if active == "Active":
        where_object = {
            "connector": "AND",
            "conditions": [
                {
                    "column": "graduationYear",
                    "operator": ">=",
                    "value": start_of_current_year + 1
                },
                {
                    "column": "students.active", 
                    "operator": "=", 
                    "value": 1
                }
            ],
        }

    if exclude_conditions:
        where_object['conditions'].append(exclude_conditions)

    return query_db (
        current_app.config,
        fields,
        "students", 
        where_object,
        sort,
        joins
    )

def get_av_club_members_db(active, start_of_current_year):
    '''Fetches AV Club Members from DB'''

    where_object = None

    if active == "Active":
        where_object = {
                "connector": "AND",
                "conditions": [
                    {
                        "column": "students.graduationYear",
                        "operator": ">=",
                        "value": start_of_current_year + 1
                    },
                    {
                        "column": "students.active",
                        "operator": "=",
                        "value": 1
                    },
                    {
                        "column": "user2avclub.active", 
                        "operator": "=", 
                        "value": 1
                    },
                ],
            }

    joins = [
        "LEFT JOIN students ON user2avclub.studentId = students.ID"
        ]

    fields = "user2avclub.ID as indexId, " \
    "students.Id as studentId, " \
    "CONCAT(students.firstName,' ',students.lastName) AS fullName, " \
    "students.graduationYear, user2avclub.notes, students.email, " \
    "user2avclub.active, students.parentName, students.parentEmail"

    return query_db (
            current_app.config,
            fields,
            "user2avclub", 
            where_object,
            "students.graduationYear ASC",
            joins
        )

def add_club_member_db(data):
    '''Insert student to the av club table'''
    inserted_id = insert_db(current_app.config, "user2avclub", data)
    return inserted_id

def add_student(data):
    '''Add student to the student table'''
    return insert_db(current_app.config, "students", data)

def get_student_details(student_id):
    '''Get student details from student table'''
    where_object = {
        "conditions": [
            {
                "column": "ID",
                "operator": "=",
                "value": student_id
            }
        ],
    }
    joins = None
    fields = "students.ID as studentId, " \
        "CONCAT(students.firstName,' ',students.lastName) AS fullName, " \
        "students.graduationYear, students.notes, students.email, " \
        "students.active, students.parentName, students.parentEmail"
    order = None
    return query_db (
        current_app.config,
        fields,
        "students", 
        where_object,
        order,
        joins
    )

def update_member_info_db(data):
    '''Send update to db'''
    data_values = {
        data['field']:data['value']
    }
    return update_db(
        current_app.config,
        "user2avclub", 
        data['ID'],
        data_values
    )

def update_student(data):
    '''Add student to the student table'''
    data_values = {
        data['field']:data['value']
    }
    return update_db(
        current_app.config,
        "students", 
        data['ID'],
        data_values
    )
