'''Serices for processing AV Club Items'''
import logging
from app.google_drive_user import (
    get_credentials,
    read_sheet
)

from app.functions import (
    get_current_academic_year_start
)

from app.tech_director.repositories import tech_director_repository
from app.tech_director.repositories.student_repository import StudentRepository

log = logging.getLogger(__name__)

class AVClubService:
    '''Services for AVClub'''
    @staticmethod
    def assign_student_avclub(data, state):
        '''Assign a student to a group (assignment_type)'''
        assignment_group = "avclub"
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
    def place_holder():
        '''placeholder'''
        message = 'keeping pylint happy'
        return message

def upload_student_gsheet(spreadsheet_id, range_name):
    '''upload sheet and insert into db'''
    creds = get_credentials()
    student_data = read_sheet(creds, spreadsheet_id, range_name)
    columns = student_data[0]
    for student in student_data[1:]:
        email = student[columns.index("email")]
        student_exists = tech_director_repository.check_for_student(email)
        data_values = {
            "ID": student[columns.index("indexId")],
            "student_id": student[columns.index("studentId")],
            "first_name": student[columns.index("firstName")],
            "last_name":student[columns.index("lastName")],
            "graduation_year": student[columns.index("graduationYear")],
            "parent_name": student[columns.index("parentName")],
            "parent_email": student[columns.index("parentEmail")],
            "email": student[columns.index("email")],
            "archived": student[columns.index("archived")]
        }
        if student_exists:
            # Need to decide if we want updates to come from the google sheet
            # output = update_student(data_values['ID'], data_values)
            log.warning("Update for %s is  %s", email, student_exists)
        else:
            this_id = tech_director_repository.add_student(data_values)
            log.warning("insert %s with ID %s", email, this_id)

    return columns



def get_group_members(assignment_group, active):
    '''Fetches the list of av club members'''
    return tech_director_repository.get_group_members(
        assignment_group,
        active,
        get_current_academic_year_start()
    )


def add_existing_student(data):
    '''Add an existing student to the AV Club'''
    insert_data = {
        'student_id':data['student_id']
    }
    inserted_id = tech_director_repository.add_club_member_db(insert_data)
    student_details = tech_director_repository.get_student_details(data['student_id'])
    student_details[0]['index_id'] = inserted_id
    return student_details[0]


def update_membership_info(data, assignment_group):
    '''Update membership info'''
    return tech_director_repository.update_membership_info(data, assignment_group)
