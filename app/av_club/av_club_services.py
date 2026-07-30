'''Serices for processing AV Club Items'''
import logging
from app.google_drive_user import (
    get_credentials,
    read_sheet
)

from app.functions import (
    get_current_academic_year_start
)

from .av_club_repository import(
    check_for_student,
    add_student,
    get_students_all_db,
    get_students_active_db
)

log = logging.getLogger(__name__)

def upload_student_gsheet(spreadsheet_id, range_name):
    '''upload sheet and insert into db'''
    creds = get_credentials()
    student_data = read_sheet(creds, spreadsheet_id, range_name)
    columns = student_data[0]
    for student in student_data[1:]:
        email = student[columns.index("email")]
        student_exists = check_for_student(email)
        data_values = {
            "ID": student[columns.index("indexId")],
            "studentId": student[columns.index("studentId")],
            "firstName": student[columns.index("firstName")],
            "lastName":student[columns.index("lastName")],
            "graduationYear": student[columns.index("graduationYear")],
            "parentName": student[columns.index("parentName")],
            "parentEmail": student[columns.index("parentEmail")],
            "email": student[columns.index("email")]
        }
        if student_exists:
            log.warning("record for %s is  %s", email, student_exists)
        else:
            this_id = add_student(data_values)
            log.warning("insert %s with ID %s", email, this_id)

    return columns

def get_students_all():
    '''Fetches the list of actors from the database.'''
    return get_students_all_db()

def get_students_active():
    '''Fetches the list of actors from the database.'''
    return get_students_active_db(get_current_academic_year_start())
