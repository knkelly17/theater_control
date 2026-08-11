'''Repository (DB) handling'''
import logging
from app.functions_db import (
    insert_db,
    update_db,
    query_db
)

# from .tech_director_repository import ASSIGNMENT_TABLES # pylint: disable=relative-beyond-top-level

log = logging.getLogger(__name__)

class ShowRepository:
    '''Functions used for interacting with show db tables'''

    @staticmethod
    def add_show(data):
        '''Add show to the shows table'''
        return insert_db("shows", data)

    @staticmethod
    def update_show(data):
        '''Update show field'''
        data_values = {
            data['field']:data['value']
        }
        return update_db(
            "shows", 
            data['ID'],
            data_values
        )

    @staticmethod
    def list_show_members(show_id):
        '''Fetches students assigned to a show'''

        where_object = {
                "conditions": [
                    {
                        "column": "assignments_show.show_id",
                        "operator": "=",
                        "value": show_id
                    },
                ],
            }

        joins = [
            "LEFT JOIN students ON assignments_show.student_id = students.ID",
            "LEFT JOIN teams ON assignments_show.team_id = teams.ID"
            ]

        fields = "assignments_show.ID as index_id, " \
        "students.Id as student_id, " \
        "CONCAT(students.first_name,' ',students.last_name) AS full_name, " \
        "students.first_name, students.last_name, " \
        "teams.name as teamName, assignments_show.team_id, " \
        "students.graduation_year, assignments_show.notes, students.email, " \
        "assignments_show.role_description, assignments_show.status_id, " \
        "students.parent_name, students.parent_email"

        return query_db (
                fields,
                "assignments_show",
                where_object,
                "full_name ASC",
                joins
            )

    @staticmethod
    def list_all(status):
        '''Fetches the list of shows from the database.'''


        fields = "shows.ID as index_id, " \
            "shows.name, " \
            "DATE_FORMAT(opening_date, '%Y-%m-%d') as opening_date, " \
            "shows.status_id"
        sort = "shows.opening_date ASC"

        where_object = None

        if status == "active":
            where_object = {
                "connector": "AND",
                "conditions": [
                    {
                        "column": "shows.status_id", 
                        "operator": "=", 
                        "value": 1
                    }
                ],
            }

        joins = None

        return query_db (
            fields,
            "shows", 
            where_object,
            sort,
            joins
        )

class TeamRepository:
    '''Used to get team information from the db'''
    @staticmethod
    def list_all(status):
        '''Fetches the list of teams from the database.'''

        fields = "teams.ID as index_id, " \
            "teams.name, " \
            "teams.description, " \
            "teams.the_order, " \
            "teams.status_id"
        sort = "teams.the_order ASC"

        joins = None

        where_object = None

        if status == "active":
            where_object = {
                "connector": "AND",
                "conditions": [
                    {
                        "column": "teams.status_id", 
                        "operator": "=", 
                        "value": 1
                    }
                ],
            }

        return query_db (
            fields,
            "teams", 
            where_object,
            sort,
            joins
        )

    @staticmethod
    def place_holder():
        '''placeholder'''
        message = 'keeping pylint happy'
        return message
