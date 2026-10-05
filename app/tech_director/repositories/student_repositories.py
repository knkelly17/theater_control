'''Repository (DB) handling'''
import logging

from app.tech_director.repositories.tech_director_repositories import (
    ASSIGNMENT_TABLES,
    VALID_ASSIGNMENT_FIELDS
)

from app.functions_db import (
    check_row_exists,
    insert_db,
    update_db,
    query_db
)

log = logging.getLogger(__name__)

class StudentRepository:
    '''Functions used for interacting with show db tables'''

    @staticmethod
    def check_for_student(index_id):
        '''Check if a row exists for this student'''
        return check_row_exists("students", "index_id", index_id)

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
            "all":"students.index_id as index_id, students.*",
            "full_name": "students.index_id, CONCAT(first_name,' ',last_name) AS full_name"
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
            "avclub": ["LEFT JOIN student2avclub ON students.index_id = student2avclub.student_id"]
        }

        fields = field_mappings.get(data_needed, "students.index_id as index_id, students.*")
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
                    "column": "index_id",
                    "operator": "=",
                    "value": student_id
                }
            ],
        }
        joins = None
        fields = "students.index_id as student_id, " \
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
        '''Update student table'''
        allowed_fields = {
            "first_name": "first_name",
            "last_name": "last_name",
            "email": "email",
            "graduation_year": "graduation_year",
            "status_id": "status_id",
            "student_num": "student_num",
            "parent_name": "parent_name",
            "parent_email": "parent_email",
            "preferred_pronouns": "preferred_pronouns",
            "notes":"notes",
            "school":"school"
        }

        index_id = data.pop("index_id", None)
        data_values = {}

        for key, value in data.items():
            column = allowed_fields.get(key)
            if column is None:
                raise ValueError(f"Invalid student field: {data['field']}")
            data_values[column] = value

        log.warning(data_values)

        return update_db(
            "students", 
            index_id,
            data_values
        )

    @staticmethod
    def add_assignment(data, assignment_group):
        '''Insert student to the club/group/show table'''
        data_values = {}
        for field in data:
            column = VALID_ASSIGNMENT_FIELDS[assignment_group].get(field)
            if column is None:
                raise ValueError(f"Invalid data field: {data['field']}")
            data_values[field] = data[field]
        inserted_id = insert_db(
            ASSIGNMENT_TABLES[assignment_group],
            data_values
        )
        return inserted_id

    @staticmethod
    def update_membership_info(data, assignment_group):
        '''Send updates regarding membership to the db'''

        column = VALID_ASSIGNMENT_FIELDS[assignment_group].get(data['field'])
        if column is None:
            raise ValueError(f"Invalid {assignment_group} field: {data['field']}")

        data_values = {
            column: data['value']
        }

        return update_db(
            ASSIGNMENT_TABLES[assignment_group],
            data['index_id'],
            data_values
        )
