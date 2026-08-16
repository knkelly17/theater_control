'''Admin Repository (DB) handling'''
import logging
from app.functions_db import (
    insert_db,
    update_db,
    query_db
)

log = logging.getLogger(__name__)

# query = "SELECT * FROM qlab_commands WHERE name = %s and active = 'Y'"
# cursor.execute(query, (command_name,))

class ETCConnectRepository:
    '''Processing Users'''

    @staticmethod
    def get_etc_api_command(command):
        '''Get specific command information'''
        fields = 'name, parameter_1, parameter_2, parameter_3, status_id'
        sort = None

        where_object = {
            "connector": "AND",
            "conditions": [
                {
                    "column": "name", 
                    "operator": "=", 
                    "value": command
                }
            ],
        }

        joins = None

        result = query_db (
            fields,
            "etc_api_commands", 
            where_object,
            sort,
            joins
        )
        return result[0]

    @staticmethod
    def list_all():
        '''Fetches the list of ETC API commands from the database.'''

        fields = 'ID as index_id, name, description, ' \
        'parameter_1, parameter_2, parameter_3, status_id'
        sort = "name ASC"

        where_object = None

        joins = None

        return query_db (
            fields,
            "etc_api_commands", 
            where_object,
            sort,
            joins
        )

    @staticmethod
    def add_command(data):
        '''Add command to the etc_api_commands table'''
        return insert_db("etc_api_commands", data)

    @staticmethod
    def update_command(data):
        '''Update etc_api_commands field'''
        data_values = {
            data['field']:data['value']
        }
        return update_db(
            "etc_api_commands", 
            data['ID'],
            data_values
        )
