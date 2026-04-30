'''Utility functions for the app.'''
from functools import wraps
from flask_login import current_user
import mysql.connector

# --- DATABASE CONNECTION ---
def get_db(dbconnection=None):
    '''Get a database connection using the provided dbconnection configuration.'''
    if dbconnection is None:
        from app import app # pylint: disable=import-outside-toplevel
        dbconnection = app.dbconnection

    return mysql.connector.connect(
        host=dbconnection['dbhost'],
        user=dbconnection['dbuser'],
        password=dbconnection['dbpassword'],
        database=dbconnection['dbdatabase']
    )

def group_required(*group_names):
    '''Get groups for a user'''
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return {"error": "Unauthorized"}, 401

            if not any(current_user.has_group(g) for g in group_names):
                return {"error": "Forbidden"}, 403

            return f(*args, **kwargs)
        return wrapper
    return decorator


def get_db_value(field, table, where):
    '''Get a single value from the database based on 
    the provided field, table, and where clause.'''
    with get_db() as db:
        cursor = db.cursor(dictionary=True)
        query = f"SELECT {field} FROM {table} WHERE {where}"
        cursor.execute(query)
        output = cursor.fetchone()
        return output[field] if output else None

def get_site_settings():
    '''Get all settings from the DB'''
    with get_db() as db:
        cursor = db.cursor(dictionary=True)
        query = "SELECT name, value FROM settings where active = 'Y'"
        cursor.execute(query)
        output = {
            row["name"]: row["value"]
            for row in cursor.fetchall()
        }
        return output

def get_setting(key, default=None):
    '''Get a specific setting value from the settings table.'''
    with get_db() as db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT value FROM settings WHERE name = %s AND active = 'Y'", (key,))
        row = cursor.fetchone()
        return row['value'] if row else default

def update_db(table_name, this_id, data_values):
    '''Update a record in the specified table with the provided data values.'''
    with get_db() as db:
        cursor = db.cursor(dictionary=True)
        query = "UPDATE " + table_name + " SET "
        update_list = []
        for field in data_values:
            update_list.append(field + " = '" + str(data_values[field]) + "'" )
        update_string = ', '.join(update_list)
        query = query + update_string + " WHERE ID = " + str(this_id)
        cursor.execute(query)
        db.commit()
        return cursor.rowcount

def insert_db(table_name, data_values):
    '''Insert a new record into the 
    specified table with the provided data values.'''
    with get_db() as db:
        cursor = db.cursor(dictionary=True)
        field_list = []
        values_list = []
        for field in data_values:
            field_list.append(str(field))
            values_list.append("'"+str(data_values[field])+"'")
        field_string = ", ".join(field_list)
        values_string = ", ".join(values_list)
        query = "INSERT INTO " + table_name + " (" + field_string + ")"
        query = query + " VALUES (" + values_string + ")"
        cursor.execute(query)
        db.commit()
        inserted_id = cursor.lastrowid
        return inserted_id
