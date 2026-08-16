'''DB functions for the app.'''
import logging
import mysql.connector
from flask import current_app
from flask_login import current_user


log = logging.getLogger(__name__)


# --- DATABASE CONNECTION ---
def get_db():
    '''Get a database connection using the provided dbconnection configuration.'''

    return mysql.connector.connect(
        host=current_app.config["DB_HOST"],
        port=current_app.config["DB_PORT"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
        database=current_app.config["DB_NAME"],
    )


def get_db_value(field, table, where):
    '''Get a single value from the database based on 
    the provided field, table, and where clause.'''
    with get_db() as db:
        cursor = db.cursor(dictionary=True)
        query = f"SELECT {field} FROM {table} WHERE {where}"
        cursor.execute(query)
        output = cursor.fetchone()
        return output[field] if output else None

def check_row_exists(table, where_column, target_value):
    '''Check for a row in table based on field value'''
    with get_db() as db:
        cursor = db.cursor(dictionary=True)
        query = f"SELECT EXISTS(SELECT 1 FROM {table} WHERE {where_column} = %s) AS row_exists"
        cursor.execute(query, (target_value,))
        result = cursor.fetchone()
        return bool(result["row_exists"]) if result else False


def update_db(table_name, this_id, data_values):
    '''Update a record in the specified table with the provided data values.'''
    data_values['sessionid'] = current_user.sessionid
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
    data_values['sessionid'] = current_user.sessionid
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

def delete_db(
        table_name,
        where_object
    ):
    '''Delete a record from the 
    specified table with the provided data conditons.'''
    with get_db() as db:
        cursor = db.cursor(dictionary=True)

        query = f'DELETE FROM {table_name}'
        params = []

        where_clause, where_params = build_where_clause(where_object)
        query += where_clause
        params.extend(where_params)

        cursor.execute(query, params)
        db.commit()
        row_count = cursor.rowcount
        return row_count

def query_db(
    field_list,
    table,
    where_object=None,
    order=None,
    joins=None,
    ):
    '''Main DB Query'''
    with get_db() as db:
        cursor = db.cursor(dictionary=True)

        query = f"SELECT {field_list} FROM {table}"
        params = []

        if joins:
            for join in joins:
                query += f" {join}"

        if where_object and where_object.get("conditions"):
            where_clause, where_params = build_where_clause(where_object)
            query += where_clause
            params.extend(where_params)

        if order:
            query += f" ORDER BY {order}"

        cursor.execute(query, params)
        return cursor.fetchall()

def query_single_table_db(field_list, table, where_object, order):
    '''get values from a single DB table'''
    with get_db() as db:
        cursor = db.cursor(dictionary=True)

        query = f"SELECT {field_list} FROM {table}"
        params = []

        if where_object:
            where_column = where_object.get("where_column")
            target_value = where_object.get("target_value")
            operator = where_object.get("operator", "=")

            if where_column and target_value is not None:
                query += f" WHERE {where_column} {operator} %s"
                params.append(target_value)

        query += f" ORDER BY {order}"
        cursor.execute(query, params)
        return cursor.fetchall()


def build_where_clause(where_object):
    '''build out the where portion of a sql query'''
    if not where_object:
        return "", []

    conditions = where_object.get("conditions", [])
    if not conditions:
        return "", []

    clauses = []
    params = []

    for cond in conditions:
        column = cond["column"]
        operator = cond.get("operator", "=")
        value = cond["value"]

        if operator not in {"=", "!=", ">", "<", ">=", "<=", "LIKE", "IS"}:
            raise ValueError(f"Unsupported operator: {operator}")

        if operator == "IS" and value is None:
            clauses.append(f"{column} IS NULL")
        else:
            clauses.append(f"{column} {operator} %s")
            params.append(value)

    connector = where_object.get("connector", "AND").upper()
    if connector not in {"AND", "OR"}:
        raise ValueError(f"Unsupported connector: {connector}")

    sql = " WHERE " + f" {connector} ".join(clauses)
    return sql, params

###################################
#### Sample usage for query_db:
#### where_object = {
####     "connector": "AND",
####     "conditions": [
####         {"column": "name", "operator": "=", "value": "joe"},
####         {"column": "active", "operator": "=", "value": "Y"},
####     ],
#### }
####
#### joins = [
####     "JOIN other_table ON other_table.id = main_table.other_id"
#### ]
####
#### rows = query_db(
####     config,
####     "main_table.*",
####     "main_table",
####     where_object=where_object,
####     order="main_table.id",
####     joins=joins,
#### )
###################################
