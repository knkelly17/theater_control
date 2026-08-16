'''Repository (DB) handling'''
import logging
from app.functions_db import (
    query_db
)

log = logging.getLogger(__name__)

ASSIGNMENT_TABLES = {
    'avclub':'student2avclub',
    'show':'assignments_show'
    }


class AVClubRepository:
    '''Repository for AV Club'''
    @staticmethod
    def list_avclub_students(active, start_of_current_year):
        '''Fetches AV Club Members from DB'''

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
                            "column": "student2avclub.status_id", 
                            "operator": "=", 
                            "value": 1
                        },
                    ],
                }

        joins = [
            "LEFT JOIN students ON student2avclub.student_id = students.ID"
            ]

        fields = "student2avclub.ID as index_id, " \
        "students.Id as student_id, " \
        "CONCAT(students.first_name,' ',students.last_name) AS full_name, " \
        "students.first_name, students.last_name, " \
        "students.graduation_year, student2avclub.notes, students.email, " \
        "student2avclub.status_id, students.parent_name, students.parent_email"

        return query_db (
                fields,
                "student2avclub",
                where_object,
                "students.graduation_year ASC",
                joins
            )
