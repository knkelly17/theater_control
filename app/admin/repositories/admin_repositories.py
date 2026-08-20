'''Admin Repository (DB) handling'''
import logging
from app.functions_db import (
    insert_db,
    update_db,
    query_db,
    delete_db,
)

# from .tech_director_repository import ASSIGNMENT_TABLES # pylint: disable=relative-beyond-top-level

log = logging.getLogger(__name__)

class UserRepository:
    '''Processing Users'''

    @staticmethod
    def add_user(data):
        '''Add show to the users table'''
        return insert_db("users", data)

    @staticmethod
    def update_user(data):
        '''Update user field'''
        data_values = {
            data['field']:data['value']
        }
        return update_db(
            "users", 
            data['ID'],
            data_values
        )

    @staticmethod
    def change_user_password(data):
        '''Update user field'''
        data_values = {
            data['field']:data['value']
        }
        return update_db(
            "users", 
            data['ID'],
            data_values
        )

    @staticmethod
    def get_user_group_matrix():
        '''Get users assigned to user groups'''
        fields = 'ID as index_id, user_id, group_id'
        sort = None
        where_object = None
        joins = None
        return query_db (
            fields,
            "user2group", 
            where_object,
            sort,
            joins
        )

    @staticmethod
    def update_user_group(data):
        '''Updates the groups a user belongs to in the db'''
        user_id = data["user_id"]
        group_id = data["group_id"]
        assigned = data.pop("assigned", None)
        table_name = 'user2group'
        where_object = {
            "connector": "AND",
            "conditions": [
                {
                    "column": "user2group.user_id", 
                    "operator": "=", 
                    "value": user_id
                },
                {
                    "column": "user2group.group_id", 
                    "operator": "=", 
                    "value": group_id
                }
            ],
        }

        if assigned:
            insert_db(table_name, data)
        else:
            delete_db(table_name, where_object)

        return {"status": "ok"}


    @staticmethod
    def list_all(status):
        '''Fetches the list of users from the database.'''


        fields = 'ID as index_id, username, first_name, last_name, email, status_id'
        sort = "first_name ASC"

        where_object = None

        if status == "active":
            where_object = {
                "connector": "AND",
                "conditions": [
                    {
                        "column": "users.status_id", 
                        "operator": "=", 
                        "value": 1
                    }
                ],
            }

        joins = None

        return query_db (
            fields,
            "users", 
            where_object,
            sort,
            joins
        )

class GroupRepository:
    '''Processing Groups (in DB)'''

    @staticmethod
    def add_group(data):
        '''Add show to the users table'''
        return insert_db("user_groups", data)

    @staticmethod
    def update_group(data):
        '''Update group field'''
        data_values = {
            data['field']:data['value']
        }
        return update_db(
            "user_groups", 
            data['ID'],
            data_values
        )


    @staticmethod
    def list_all(status):
        '''Fetches the list of groups from the database.'''


        fields = 'ID as index_id, name, description, status_id'
        sort = "name ASC"

        where_object = None

        if status == "active":
            where_object = {
                "connector": "AND",
                "conditions": [
                    {
                        "column": "user_groups.status_id", 
                        "operator": "=", 
                        "value": 1
                    }
                ],
            }

        joins = None

        return query_db (
            fields,
            "user_groups", 
            where_object,
            sort,
            joins
        )

class SettingRepository:
    '''Processing Groups (in DB)'''

    @staticmethod
    def add_setting(data):
        '''Add setting to the settomgs table'''
        return insert_db("settings", data)

    @staticmethod
    def update_setting(data):
        '''Update setting field'''
        data_values = {
            data['field']:data['value']
        }
        return update_db(
            "settings", 
            data['ID'],
            data_values
        )

    @staticmethod
    def get_setting(key):
        '''Get a specific setting value from the settings table.'''
        fields = 'value'
        sort = None
        where_object = {
            "conditions": [
                {
                    "column": "settings.name", 
                    "operator": "=", 
                    "value": key
                }
            ],
        }
        joins = None
        result = query_db (
            fields,
            "settings", 
            where_object,
            sort,
            joins
        )
        return result[0].get('value')

    @staticmethod
    def list_all(status):
        '''Fetches the list of settings from the database.'''


        fields = 'ID as index_id, name, description, value, the_order, status_id'
        sort = "the_order ASC"

        where_object = None

        if status == "active":
            where_object = {
                "conditions": [
                    {
                        "column": "settings.status_id", 
                        "operator": "=", 
                        "value": 1
                    }
                ],
            }

        joins = None

        return query_db (
            fields,
            "settings", 
            where_object,
            sort,
            joins
        )

    @staticmethod
    def get_last_setting_update():
        '''Get the most recent time that settings were updated'''
        last_update = query_db(
            "DATE_FORMAT(MAX(timestamp), '%Y-%m-%d %h:%i:%s %p') as last_update",
            "settings")
        return last_update[0].get('last_update')
