from dbactions.connection import getConnection,closeConnection
from dbactions.profile import get_user_info
import ibm_db

def add_new_warehouse(mail_id,warehouse_name,location,description):
    response = get_user_info(mail_id)
    if response['status']:
        inventory_id = response['user_info']['inventory_id']
        conn = getConnection()
        if conn:
            try:
                query = "INSERT INTO WAREHOUSES (WAREHOUSE_NAME,WAREHOUSE_LOCATION,DESCRIPTION,INVENTORY_ID) VALUES(?,?,?,?)"
                statement = ibm_db.prepare(conn,query)
                ibm_db.bind_param(statement, 1,warehouse_name)
                ibm_db.bind_param(statement, 2,location)
                ibm_db.bind_param(statement, 3,description)
                ibm_db.bind_param(statement, 4,inventory_id)
                ibm_db.execute(statement)
                if ibm_db.num_rows(statement) != 1:
                    return{ 'status' : False, 'reason' : "Something went wrong" }
            except Exception as e:
                print("Exception while creating warehouse : ",e)
                return{ 'status' : False, 'reason' : "Something went wrong"}
            finally:
                closeConnection(conn)
            return{ 'status' : True, 'reason' : "" }
        else:
            return{ 'status' : False, 'reason' : "Couldn't connect to DB" }
    return response
