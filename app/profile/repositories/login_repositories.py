import logging
from app.functions_db import (
    check_row_exists,
    insert_db,
    update_db,
    query_db
)

log = logging.getLogger(__name__)

class LoginRepository:
    '''DB services for app login'''

    @staticmethod
    
