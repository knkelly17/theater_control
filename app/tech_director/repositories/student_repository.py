'''Repository (DB) handling'''
import logging
from app.functions_db import (
    check_row_exists,
    insert_db,
    update_db,
    query_db
)

log = logging.getLogger(__name__)

ASSIGNMENT_TABLES = {
    'avclub':'student2avclub',
    'show':'assignments_show'
    }

class StudentRepository:
    '''Functions used for interacting with show db tables'''

    @staticmethod
    def check_for_student(email):
        '''Check if a row exists for this student'''
        return check_row_exists("students", "email", email)

    @staticmethod
    def get_students_all_db():
        '''Fetches the list of all students from the database.'''
        where_object = None
        return query_db(
            "*", 
            "students", 
            where_object,
            "first_name ASC"
        )

    @staticmethod
    def get_students(active, start_of_current_year, data_needed, sort_by, exclude_items):
        '''Fetches the list of active students from the database.'''

        field_mappings = {
            "all":"students.ID as index_id, students.*",
            "full_name": "students.ID, CONCAT(first_name,' ',last_name) AS full_name"
        }

        sort_mappings = {
            "full_name": "full_name ASC",
            "grade": "students.graduation_year ASC"
        }

        exclude_conditions_map = {
            "avclub": {
                "column": "student2avclub.student_id",
                "operator": "IS",
                "value": None
            }
        }

        exclude_joins_map = {
            "avclub": ["LEFT JOIN student2avclub ON students.ID = student2avclub.student_id"]
        }

        fields = field_mappings.get(data_needed, "students.ID as index_id, students.*")
        sort = sort_mappings.get(sort_by, "students.graduation_year ASC")
        exclude_conditions = exclude_conditions_map.get(exclude_items, None)
        joins = exclude_joins_map.get(exclude_items, None)

        where_object = None

        if active == "active":
            where_object = {
                "connector": "AND",
                "conditions": [
                    {
                        "column": "graduation_year",
                        "operator": ">=",
                        "value": start_of_current_year + 1
                    },
                    {
                        "column": "students.status_id", 
                        "operator": "=", 
                        "value": 1
                    }
                ],
            }

        if exclude_conditions:
            where_object['conditions'].append(exclude_conditions)

        return query_db (
            fields,
            "students", 
            where_object,
            sort,
            joins
        )

    @staticmethod
    def add_student(data):
        '''Add student to the student table'''
        return insert_db("students", data)

    @staticmethod
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
        fields = "students.ID as student_id, " \
            "CONCAT(students.first_name,' ',students.last_name) AS full_name, " \
            "students.graduation_year, students.notes, students.email, " \
            "students.status_id, students.parent_name, students.parent_email"
        order = None
        return query_db (
            fields,
            "students", 
            where_object,
            order,
            joins
        )

    @staticmethod
    def update_student(data):
        '''Add student to the student table'''
        log.warning(data)
        data_values = {
            data['field']:data['value']
        }
        return update_db(
            "students", 
            data['ID'],
            data_values
        )

    @staticmethod
    def add_assignment(data, assignment_group):
        '''Insert student to the club/group/show table'''
        inserted_id = insert_db(
            ASSIGNMENT_TABLES[assignment_group],
            data
        )
        return inserted_id

    @staticmethod
    def update_membership_info(data, assignment_group):
        '''Send updates regarding membership to the db'''
        data_values = {
            data['field']:data['value']
        }
        return update_db(
            ASSIGNMENT_TABLES[assignment_group],
            data['ID'],
            data_values
        )
