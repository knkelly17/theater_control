'''Serices for processing Show Items'''
import logging

from app.tech_director.repositories.student_repository import (
    StudentRepository
)

from app.functions import (
    get_current_academic_year_start
)

log = logging.getLogger(__name__)

class StudentService:
    '''Class for processing student requests'''

    @staticmethod
    def get_students(active):
        '''Fetches the list of students from the database.'''
        data_needed = "all"
        sorted_by = "graduation_year"
        exclude = None
        return StudentRepository.get_students(
            active,
            get_current_academic_year_start(),
            data_needed,
            sorted_by,
            exclude
        )

    @staticmethod
    def get_students_active():
        '''Fetches the list of students from the database.'''
        data_needed = "all"
        sorted_by = "grade"
        exclude = None
        return StudentRepository.get_students(
            "Active",
            get_current_academic_year_start(),
            data_needed,
            sorted_by,
            exclude
        )

    @staticmethod
    def get_students_active_names():
        '''Fetches the list of active student names and id's from the database.'''
        data_needed = "full_name"
        sorted_by = "full_name"
        exclude = None
        return StudentRepository.get_students(
            "Active",
            get_current_academic_year_start(),
            data_needed,
            sorted_by,
            exclude
        )

    @staticmethod
    def get_students_active_names_options(exclude):
        '''Generate a list of active students for a dropdown'''
        data_needed = "full_name"
        sorted_by = "full_name"
        student_object = StudentRepository.get_students(
            "active",
            get_current_academic_year_start(),
            data_needed,
            sorted_by,
            exclude
        )
        option_list = [('','')]
        for student in student_object:
            this_option = (student['ID'], student['full_name'])
            option_list.append(this_option)
        return option_list

    @staticmethod
    def add_student(data):
        '''Add a new student'''
        new_student_id = StudentRepository.add_student(data)
        return {'index_id':new_student_id}


    @staticmethod
    def update_student(data):
        '''Update membership info'''
        return StudentRepository.update_student(data)

    @staticmethod
    def assign_student(data, state, assignment_group):
        '''Assign a student to a group (assignment_type)'''
        if state == 'new':
            student_id = StudentRepository.add_student(data)
        else:
            student_id = data['student_id']

        insert_data = {
            'student_id':student_id
        }
        new_assignment_id = StudentRepository.add_assignment(insert_data, assignment_group)
        student_details = StudentRepository.get_student_details(student_id)
        student_details[0]['index_id'] = new_assignment_id
        return student_details[0]

    @staticmethod
    def update_membership_info(data, assignment_group):
        '''Update membership info'''
        return StudentRepository.update_membership_info(data, assignment_group)
