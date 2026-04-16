from app import app
import mysql.connector

# --- DATABASE CONNECTION ---
def get_db(dbconnection=app.dbconnection):
    return mysql.connector.connect(
        host=dbconnection['dbhost'],
        user=dbconnection['dbuser'],
        password=dbconnection['dbpassword'],
        database=dbconnection['dbdatabase']
    )

def get_site_settings():
    with get_db(dbconnection=app.dbconnection) as db:
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM settings"
        cursor.execute(query)
        settings_data = cursor.fetchall()
        output = {}
        for setting in settings_data:
            output[setting['name']] = setting['value']
        return output
    
def update_db(table_name, thisID, data_values):
    with get_db(dbconnection=app.dbconnection) as db:
        cursor = db.cursor(dictionary=True)
        query = "UPDATE " + table_name + " SET "
        update_list = []
        for field in data_values:
            update_list.append(field + " = '" + str(data_values[field]) + "'" )
        update_string = ', '.join(update_list)
        query = query + update_string + " WHERE ID = " + str(thisID)
        cursor.execute(query)
        db.commit()
        return cursor.rowcount
    
def insert_db(table_name, data_values):
    with get_db(dbconnection=app.dbconnection) as db:
        cursor = db.cursor(dictionary=True)
        field_list = []
        values_list = []
        for field in data_values:
            field_list.append(str(field))
            values_list.append("'"+str(data_values[field])+"'")
        field_string = ", ".join(field_list)
        values_string = ", ".join(values_list)
        query = "INSERT INTO " + table_name + "(" + field_string + ")"
        query = query + " VALUES (" + values_string + ")"
        print (query)
        cursor.execute(query)
        db.commit()
        inserted_id = cursor.lastrowid
        return inserted_id