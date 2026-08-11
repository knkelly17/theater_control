'''Repository (DB) handling'''
import logging
from app.functions_db import (
    insert_db,
    update_db,
    query_db
)

log = logging.getLogger(__name__)

ASSIGNMENT_TABLES = {
    'avclub':'student2avclub',
    'show':'assignments_show'
    }



def get_group_members(assignment_group, active, start_of_current_year):
    '''Fetches AV Club Members from DB'''

    assignment_table = ASSIGNMENT_TABLES[assignment_group]

    where_object = None

    if active == "active":
        where_object = {
                "connector": "AND",
                "conditions": [
                    {
                        "column": "students.graduation_year",
                        "operator": ">=",
                        "value": start_of_current_year + 1
                    },
                    {
                        "column": "students.status_id",
                        "operator": "=",
                        "value": 1
                    },
                    {
                        "column": f"{assignment_table}.status_id", 
                        "operator": "=", 
                        "value": 1
                    },
                ],
            }

    joins = [
        f"LEFT JOIN students ON {assignment_table}.student_id = students.ID"
        ]

    fields = f"{assignment_table}.ID as index_id, " \
    "students.Id as student_id, " \
    "CONCAT(students.first_name,' ',students.last_name) AS full_name, " \
    "students.first_name, students.last_name, " \
    "students.graduation_year, student2avclub.notes, students.email, " \
    "student2avclub.status_id, students.parent_name, students.parent_email"

    return query_db (
            fields,
            assignment_table,
            where_object,
            "students.graduation_year ASC",
            joins
        )

def add_club_member_db(data):
    '''Insert student to the av club table'''
    inserted_id = insert_db("student2avclub", data)
    return inserted_id

def update_membership_info(data, assignment_group):
    '''Send update to db'''
    data_values = {
        data['field']:data['value']
    }
    return update_db(
        ASSIGNMENT_TABLES[assignment_group],
        data['ID'],
        data_values
    )
