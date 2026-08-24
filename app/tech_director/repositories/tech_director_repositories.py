'''Repository (DB) handling'''
import logging
from app.functions_db import (
    query_db,
    update_db,
    insert_db
)

log = logging.getLogger(__name__)

ASSIGNMENT_TABLES = {
    'avclub':'student2avclub',
    'show':'assignments_show',
    'inventory': 'assignments_inventory'
    }

VALID_ASSIGNMENT_FIELDS = {
    'avclub':{
       'status_id': 'status_id', 
       'notes':'notes',
       'student_id':'student_id'
    },
    'show':{
        'status_id': 'status_id', 
        'notes':'notes',
        'student_id':'student_id',
        'show_id':'show_id',
        'team_id':'team_id',
        'role_description':'role_description'
    },
    'inventory':{
        'status_id': 'status_id', 
        'notes':'notes',
        'student_id':'student_id',
        'show_id':'show_id',
        'inventory_id':'inventory_id',
        'assign_date':'assign_date',
        'due_date':'due_date',
        'returned_date':'returned_date'
    }
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

    @staticmethod
    def placeholder():
        '''Keeping pyling quiet (too few functions)'''
        message = 'keeping Pylint quiet for now'
        return message

class InventoryRepository:
    '''Repository for Inventory'''

    @staticmethod
    def add_inventory(data):
        '''Add to the inventory table'''
        return insert_db("inventory", data)

    @staticmethod
    def update_inventory(data):
        '''Update inventory field'''
        data_values = {
            data['field']:data['value']
        }
        return update_db(
            "inventory", 
            data['ID'],
            data_values
        )

    @staticmethod
    def list_inventory_assignments(status):
        '''Gets a list of assigned equipment'''

        # At some point we may need to rethink the status values.
        # What if there is inventory that is no longer active?
        # That can easily be managed with the same status argument

        fields = "a.ID as index_id, i.name, i.ID as inventory_id, " \
                "a.student_id, a.status_id, " \
                "DATE_FORMAT(a.assign_date, '%Y-%m-%d') as assign_date, " \
                "DATE_FORMAT(a.due_date, '%Y-%m-%d') as due_date, " \
                "DATE_FORMAT(a.returned_date, '%Y-%m-%d') as returned_date "

        sort = "i.name ASC"
        where_object = {
            "connector": "AND",
            "conditions": [
                {
                    "column": "i.status_id", 
                    "operator": "=", 
                    "value": 1
                },
                {
                    "column": "t.name", 
                    "operator": "=", 
                    "value": "Equipment"
                },
            ],
        }


        joins = [
            "LEFT JOIN inventory_types t on i.inventory_type_id = t.ID",
        ]

        if status == "active":
            joins.append(
                (   "LEFT JOIN assignments_inventory a "
                    "ON a.inventory_id = i.ID "
                    "AND a.status_id = 1"
                )
            )
        elif status == "all":
            joins.append("LEFT JOIN assignments_inventory a on a.inventory_id = i.ID")

        return query_db (
            fields,
            "inventory i", 
            where_object,
            sort,
            joins
        )

    @staticmethod
    def list_types(status):
        '''Gets a list of inventory type'''

        fields = "i.ID as index_id, i.name as name"
        sort = "i.name ASC"
        where_object = None

        if status == "active":
            where_object = {
                "connector": "AND",
                "conditions": [
                    {
                        "column": "i.status_id", 
                        "operator": "=", 
                        "value": 1
                    }
                ],
            }

        joins = None

        return query_db (
            fields,
            "inventory_types i", 
            where_object,
            sort,
            joins
        )



    @staticmethod
    def list_all(status):
        '''Fetches the list of inventory from the database.'''


        fields = "i.ID as index_id, " \
            "i.name, i.description, i.serial_num, " \
            "i.status_id, i.inventory_type_id"
        sort = "i.name ASC"

        where_object = None

        if status == "active":
            where_object = {
                "connector": "AND",
                "conditions": [
                    {
                        "column": "i.status_id", 
                        "operator": "=", 
                        "value": 1
                    }
                ],
            }

        joins = None

        return query_db (
            fields,
            "inventory i", 
            where_object,
            sort,
            joins
        )
