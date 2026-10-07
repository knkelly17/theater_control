'''Repository (DB) handling'''
import logging
from app.functions_db import (
    query_db,
    update_db,
    insert_db,
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
        'index_id': 'index_id',
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
            "LEFT JOIN students ON student2avclub.student_id = students.index_id"
            ]

        fields = "student2avclub.index_id as index_id, " \
        "students.index_id as student_id, " \
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

class SkillsRepository:
    '''Repository for Skills'''

    @staticmethod
    def add_skill(data):
        '''Add to the skills table'''
        return insert_db("skills", data)

    @staticmethod
    def update_skill(data):
        '''Update skills field'''
        data_values = {
            data['field']:data['value']
        }
        return update_db(
            "skills", 
            data['index_id'],
            data_values
        )

    @staticmethod
    def list_all(status):
        '''Fetches the list of skills from the database.'''


        fields = "s.index_id as index_id, " \
            "s.name, s.team_id, s.status_id, s.in_grid"
        sort = "s.name ASC"

        where_object = None

        if status == "active":
            where_object = {
                "connector": "AND",
                "conditions": [
                    {
                        "column": "s.status_id", 
                        "operator": "=", 
                        "value": 1
                    }
                ],
            }

        joins = None

        return query_db (
            fields,
            "skills s", 
            where_object,
            sort,
            joins
        )

    @staticmethod
    def list_all_skill_levels():
        '''Fetches the list of skill levels from the database.'''


        fields = "l.index_id as index_id, l.name as name"
        sort = "l.name ASC"

        where_object = None
        joins = None

        return query_db (
            fields,
            "skill_levels l", 
            where_object,
            sort,
            joins
        )

    @staticmethod
    def get_students_skills_grid():
        '''Get students assigned to skills'''
        fields = "index_id as index_id, student_id, skill_id, level_id, " \
        "assessed_by, notes, " \
        "DATE_FORMAT(achieved_date, '%Y-%m-%d') as achieved_date "
        sort = None
        where_object = None
        joins = None
        return query_db (
            fields,
            "students_skills", 
            where_object,
            sort,
            joins
        )

    @staticmethod
    def update_student_skill(update_data):
        '''Update student skill record'''
        table_name = "students_skills"
        field = 'index_id'
        where_object = {
            "connector": "AND",
            "conditions": [
                {
                    "column": "student_id", 
                    "operator": "=", 
                    "value": update_data['student_id']
                },
                {
                    "column": "skill_id", 
                    "operator": "=", 
                    "value": update_data['skill_id']
                }
            ],
        }
        sort = None
        joins = None
        row_exists = query_db (
            field,
            table_name,
            where_object,
            sort,
            joins
        )
        log.warning(row_exists)

        #if row_exists == 0:
        #    insert_db(table_name, update_data)
        if row_exists:
            return update_db(table_name, row_exists[0]['index_id'], update_data)
        else:
            return insert_db(table_name, update_data)


class TeamRepository:
    '''Used to get team information from the db'''
    @staticmethod
    def list_all(status):
        '''Fetches the list of teams from the database.'''

        fields = "teams.index_id as index_id, " \
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
    def list_all_tech_teams(status):
        '''Fetches the list of tech teams from the database.'''

        fields = "t.index_id as index_id, " \
            "t.name, " \
            "t.description, " \
            "t.the_order, " \
            "t.status_id"
        sort = "t.the_order ASC"

        joins = None

        where_object = None

        if status == "active":
            where_object = {
                "connector": "AND",
                "conditions": [
                    {
                        "column": "t.status_id", 
                        "operator": "=", 
                        "value": 1
                    }
                ],
            }

        return query_db (
            fields,
            "tech_teams t", 
            where_object,
            sort,
            joins
        )

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
            data['index_id'],
            data_values
        )

    @staticmethod
    def list_inventory_assignments(status):
        '''Gets a list of assigned equipment'''

        # At some point we may need to rethink the status values.
        # What if there is inventory that is no longer active?
        # That can easily be managed with the same status argument

        fields = "a.index_id as index_id, i.name, i.index_id as inventory_id, " \
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
            "LEFT JOIN inventory_types t on i.inventory_type_id = t.index_id",
        ]

        if status == "active":
            joins.append(
                (   "LEFT JOIN assignments_inventory a "
                    "ON a.inventory_id = i.index_id "
                    "AND a.status_id = 1"
                )
            )
        elif status == "all":
            joins.append("LEFT JOIN assignments_inventory a on a.inventory_id = i.index_id")

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

        fields = "i.index_id as index_id, i.name as name"
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


        fields = "i.index_id as index_id, " \
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
