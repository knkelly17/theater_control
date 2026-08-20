'''Serices for processing Admin Items'''
import logging
from werkzeug.security import generate_password_hash
from app.admin.repositories.admin_repositories import (
    UserRepository,
    GroupRepository,
    SettingRepository
)

log = logging.getLogger(__name__)

class UserService:
    '''Processing Users'''

    @staticmethod
    def list_all(status):
        '''Fetches the list of users from the database.'''
        return UserRepository.list_all(
            status
        )

    @staticmethod
    def add_user(data):
        '''Add a new user'''
        new_user_id = UserRepository.add_user(data)
        return {'index_id':new_user_id}

    @staticmethod
    def update_user(data):
        '''Update user info'''
        return UserRepository.update_user(data)

    @staticmethod
    def change_user_password(data):
        '''change a user's password'''

        new_password = data["new_password"]
        hashed_password = generate_password_hash(new_password)
        password_data = {
            'ID': data['index_id'],
            'field': 'password_hash',
            'value': hashed_password
        }
        return UserRepository.change_user_password(password_data)

    @staticmethod
    def get_user_group_matrix():
        '''build a matrix of users and groups'''
        users = UserRepository.list_all('all')
        groups = GroupRepository.list_all('all')
        links = UserRepository.get_user_group_matrix()

        link_set = {(l["user_id"], l["group_id"]) for l in links}

        rows = []
        for u in users:
            row = {"user_id": u["index_id"], "username": u["username"]}
            for g in groups:
                row[f"g_{g['index_id']}"] = (u["index_id"], g["index_id"]) in link_set
            rows.append(row)

        return {"rows": rows, "groups": groups}

    @staticmethod
    def update_user_group(data):
        '''Updates the groups that a user belongs to'''
        return UserRepository.update_user_group(data)



class GroupService:
    '''Processing Groups'''

    @staticmethod
    def list_all(status):
        '''Fetches the list of groups from the database.'''
        return GroupRepository.list_all(
            status
        )

    @staticmethod
    def add_group(data):
        '''Add a new user'''
        new_user_id = GroupRepository.add_group(data)
        return {'index_id':new_user_id}

    @staticmethod
    def update_group(data):
        '''Update user info'''
        return GroupRepository.update_group(data)


class SettingService:
    '''Processing Settings'''

    @staticmethod
    def list_all(status):
        '''Fetches the list of settings from the database.'''
        return SettingRepository.list_all(
            status
        )

    @staticmethod
    def add_setting(data):
        '''Add a new setting'''
        new_setting_id = SettingRepository.add_setting(data)
        return {'index_id':new_setting_id}

    @staticmethod
    def update_setting(data):
        '''Update user info'''
        return SettingRepository.update_setting(data)

    @staticmethod
    def get_setting(key):
        '''Get the value of a specific setting'''
        return SettingRepository.get_setting(key)

    @staticmethod
    def get_last_setting_update():
        '''Get the last time the settings were updated'''
        return SettingRepository.get_last_setting_update()
