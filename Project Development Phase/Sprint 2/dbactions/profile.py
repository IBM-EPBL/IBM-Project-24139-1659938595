from dbactions.connection import getConnection,closeConnection
from dbactions.signup import is_mail_id_unique
import ibm_db

def get_user_profile_details(mail_id):
    response = get_user_info(mail_id)
    if response['status']:
        del response['user_info']['password']
    return(response)

def update_profile(mail_id,data):
    response = get_user_info(mail_id)
    dynamic_params = ""
    dynamic_values = []
    new_inventory_name = ''
    if response['status']:
        user_info = response['user_info']
        if data.get('name') and data.get('name') != user_info['person_name']:
            dynamic_params = "NAME = ?"
            dynamic_values.append(data.get('name'))
        if data.get('mail_id') and data.get('mail_id') != user_info['mail_id']:
            response = is_mail_id_unique(data.get('mail_id'))
            if not response['status']:
                return response
            dynamic_params += ", MAIL_ID = ?" if dynamic_params != "" else "" + "MAIL_ID = ?"
            dynamic_values.append(data.get('mail_id'))
        if data.get('password') and data.get('password') != user_info['password']:
            dynamic_params += ", PASSWORD = ?" if dynamic_params != "" else "" + "PASSWORD = ?"
            dynamic_values.append(data.get('password'))
        if user_info['role'] == "retailer" and data.get('inventory_name') and data.get('inventory_name') != user_info['inventory_name']:
            new_inventory_name = data.get('inventory_name')
        if dynamic_params == "" and new_inventory_name == "":
            return { 'status' : False, 'reason' : "No changes found" }
        if dynamic_params != "":
            response = update_user_details(mail_id,dynamic_params,dynamic_values)
            if response['status'] and new_inventory_name != "":
                response = update_inventory_details(user_info['inventory_id'],data.get('inventory_name'))
        else:
            response = update_inventory_details(user_info['inventory_id'],data.get('inventory_name'))
    return response

def get_user_info(mail_id):
    conn = getConnection()
    user_info = {}
    if conn:
        try:
            query = "SELECT USERS.USER_ID,USERS.NAME,USERS.MAIL_ID,USERS.ROLE_ID,USERS.INVENTORY_ID,INVENTORIES.NAME, USERS.PASSWORD FROM USERS INNER JOIN INVENTORIES ON USERS.INVENTORY_ID = INVENTORIES.INVENTORY_ID WHERE USERS.MAIL_ID = ?"
            statement = ibm_db.prepare(conn,query)
            ibm_db.bind_param(statement, 1,mail_id)
            ibm_db.execute(statement)
            result = ibm_db.fetch_both(statement)
            user_info['person_id'] = result[0]
            user_info['person_name'] = result[1]
            user_info['mail_id'] = result[2]
            user_info['role'] = "retailer" if result[3] == 1 else "user"
            user_info['inventory_id'] = result[4]
            user_info['inventory_name'] = result[5]
            user_info['password'] = result[6]
        except Exception as e:
            print("Exception while getting info of user : ",e)
            return{ 'status' : False, 'reason' : "Something went wrong" , 'user_info' : user_info }
        finally:
            closeConnection(conn)
        return{ 'status' : True, 'reason' : "" , 'user_info' : user_info }
    else:
        return{ 'status' : False, 'reason' : "Couldn't connect to DB" , 'user_info' : user_info }

def update_user_details(mail_id,dynamic_params,dynamic_values):
    conn = getConnection()
    if conn:
        try:
            query = "UPDATE USERS SET {} WHERE MAIL_ID = ?".format(dynamic_params)
            statement = ibm_db.prepare(conn,query)
            mail_id_index = 1
            for i in range(1,len(dynamic_values) + 1):
                ibm_db.bind_param(statement, i,dynamic_values[i - 1])
                mail_id_index += 1
            ibm_db.bind_param(statement, mail_id_index,mail_id)
            ibm_db.execute(statement)
        except Exception as e:
            print("Exception while updating user details : ",e)
            return{ 'status' : False, 'reason' : "Something went wrong" }
        finally:
            closeConnection(conn)
        return{ 'status' : True, 'reason' : "" }
    else:
        return{ 'status' : False, 'reason' : "Couldn't connect to DB"}

def update_inventory_details(inventory_id,new_inventory_name):
    conn = getConnection()
    if conn:
        try:
            query = "UPDATE INVENTORIES SET NAME = ? WHERE INVENTORY_ID = ?"
            statement = ibm_db.prepare(conn,query)
            ibm_db.bind_param(statement, 1,new_inventory_name)
            ibm_db.bind_param(statement, 2,inventory_id)
            ibm_db.execute(statement)
        except Exception as e:
            print("Exception while updating inventory details : ",e)
            return{ 'status' : False, 'reason' : "Something went wrong" }
        finally:
            closeConnection(conn)
        return{ 'status' : True, 'reason' : "" }
    else:
        return{ 'status' : False, 'reason' : "Couldn't connect to DB"}
