'''Serices for processing AV Club Items'''
import logging
from app.google_drive_user import (
    get_credentials,
    read_sheet
)

from app.functions import (
    get_current_academic_year_start
)

from app.tech_director.repositories.tech_director_repositories import AVClubRepository
from app.tech_director.repositories.student_repositories import StudentRepository

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
    def list_avclub_students(active):
        '''Fetches the list of av club members'''
        return AVClubRepository.list_avclub_students(
            active,
            get_current_academic_year_start()
        )

def upload_student_gsheet(spreadsheet_id, range_name):
    '''upload sheet and insert into db'''
    creds = get_credentials()
    student_data = read_sheet(creds, spreadsheet_id, range_name)
    columns = student_data[0]
    for student in student_data[1:]:
        email = student[columns.index("email")]
        student_exists = StudentRepository.check_for_student(email)
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
            this_id = StudentRepository.add_student(data_values)
            log.warning("insert %s with ID %s", email, this_id)

    return columns
