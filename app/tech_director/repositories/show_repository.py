'''Repository (DB) handling'''
import logging
from flask import current_app
from app.functions_db import (
    check_row_exists,
    insert_db,
    update_db,
    query_db
)

from .tech_director_repository import ASSIGNMENT_TABLES # pylint: disable=relative-beyond-top-level

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
    def list_all(active, exclude_items):
        '''Fetches the list of active students from the database.'''

        exclude_conditions_map = {
            "avclub": {
                "column": "student2avclub.studentId",
                "operator": "IS",
                "value": None
            }
        }

        exclude_joins_map = {
            "avclub": ["LEFT JOIN student2avclub ON students.ID = student2avclub.studentId"]
        }

        fields = "shows.ID as indexId, " \
            "shows.name, " \
            "DATE_FORMAT(openingDate, '%Y-%m-%d') as openingDate, " \
            "shows.active"
        sort = "shows.openingDate ASC"
        exclude_conditions = exclude_conditions_map.get(exclude_items, None)
        joins = exclude_joins_map.get(exclude_items, None)

        where_object = None

        if active == "active":
            where_object = {
                "connector": "AND",
                "conditions": [
                    {
                        "column": "shows.active", 
                        "operator": "=", 
                        "value": 1
                    }
                ],
            }

        if exclude_conditions:
            where_object['conditions'].append(exclude_conditions)

        return query_db (
            fields,
            "shows", 
            where_object,
            sort,
            joins
        )
