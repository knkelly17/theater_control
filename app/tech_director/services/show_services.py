'''Serices for processing Show Items'''
import logging

from app.tech_director.repositories.show_repositories import (
    ShowRepository,
    TeamRepository
)

from app.tech_director.repositories.student_repositories import (
    StudentRepository
)

log = logging.getLogger(__name__)

class ShowService:
    '''Class for processing show requests'''

    @staticmethod
    def list_all(status):
        '''Fetches the list of students from the database.'''
        return ShowRepository.list_all(
            status
        )

    @staticmethod
    def add_show(data):
        '''Add a new show'''
        new_show_id = ShowRepository.add_show(data)
        return {'index_id':new_show_id}

    @staticmethod
    def update_show(data):
        '''Update show info'''
        return ShowRepository.update_show(data)

    @staticmethod
    def list_show_members(show_id):
        '''Fetches the list of av club members'''
        return ShowRepository.list_show_members(show_id)

    @staticmethod
    def list_show_names_options(status):
        '''Generate a list of active students for a dropdown'''
        show_list =  ShowRepository.list_all(
            status,
        )
        log.warning(show_list)
        option_list = [('','')]
        for show in show_list:
            this_option = (show['index_id'], show['name'])
            option_list.append(this_option)
        return option_list

    @staticmethod
    def assign_student_show(data, state):
        '''Assign a student to a group (assignment_type)'''
        assignment_group = "show"
        show_id = data.pop("show_id", None)
        if state == 'new':
            student_id = StudentRepository.add_student(data)
        else:
            student_id = data['student_id']

        insert_data = {
            'student_id':student_id,
            'show_id':show_id
        }
        new_assignment_id = StudentRepository.add_assignment(insert_data, assignment_group)
        student_details = StudentRepository.get_student_details(student_id)
        student_details[0]['index_id'] = new_assignment_id
        return student_details[0]

class TeamService:
    '''Class for specific team items'''
    @staticmethod
    def list_all(active):
        '''Fetches the list of students from the database.'''
        return TeamRepository.list_all(
            active
        )

    @staticmethod
    def place_holder():
        '''placeholder'''
        message = 'keeping pylint happy'
        return message
