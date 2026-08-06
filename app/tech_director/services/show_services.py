'''Serices for processing Show Items'''
import logging

from ..repositories.show_repository import ShowRepository # pylint: disable=relative-beyond-top-level

log = logging.getLogger(__name__)

class ShowService:
    '''Class for processing show requests'''

    @staticmethod
    def list_all(active):
        '''Fetches the list of students from the database.'''
        exclude = None
        return ShowRepository.list_all(
            active,
            exclude
        )

    @staticmethod
    def add_show(data):
        '''Add a new student'''
        new_student_id = ShowRepository.add_show(data)
        return {'indexId':new_student_id}

    # @staticmethod
    # def update_member_info(data):
    #    '''Update membership info'''
    #    return tech_director_repository.update_member_info_db(data)

    @staticmethod
    def update_show(data):
        '''Update membership info'''
        return ShowRepository.update_show(data)
