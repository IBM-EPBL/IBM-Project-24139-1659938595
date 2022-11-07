from dbactions.connection import getConnection,closeConnection
import ibm_db

def create_retailer_account(name,mail_id,password,inventory_name):
    response = create_account(name,mail_id,password,1)
    if response['status']:
        retailer_id = response['user_id']
        response = create_inventory(inventory_name,retailer_id)
        if response['status']:
            inventory_id = response['inventory_id']
            response = update_account(retailer_id,inventory_id)
            return(response)
    return(response)
    
   

def create_user_account(name,mail_id,password,inventory_id):
    response = create_account(name,mail_id,password,2)
    if response['status']:
        user_id = response['user_id']
        response = update_account(user_id,inventory_id)
        return(response)
    return(response)

def create_inventory(name,retailer_id):
    conn = getConnection()
    inventory_id = ""
    if conn:
        try:
            query = "INSERT INTO INVENTORIES (NAME,RETAILER_ID) VALUES(?,?)"
            statement = ibm_db.prepare(conn,query)
            ibm_db.bind_param(statement, 1,name)
            ibm_db.bind_param(statement, 2,retailer_id)
            ibm_db.execute(statement)
            if ibm_db.num_rows(statement) != 1:
                return{ 'status' : False, 'reason' : "Something went wrong" , 'inventory_id' : inventory_id }
            else:
                query = "SELECT INVENTORY_ID FROM INVENTORIES WHERE NAME = ?"
                statement = ibm_db.prepare(conn,query)
                ibm_db.bind_param(statement, 1,name)
                ibm_db.execute(statement)
                result = ibm_db.fetch_both(statement)
                while result:
                    inventory_id = result[0]
                    result = ibm_db.fetch_both(statement)
        except Exception as e:
            print("Exception while creating inventory : ",e)
            return{ 'status' : False, 'reason' : "Something went wrong" , 'inventory_id' : inventory_id }
        finally:
            closeConnection(conn)
        return{ 'status' : True, 'reason' : "" , 'inventory_id' : inventory_id }
    else:
        return{ 'status' : False, 'reason' : "Couldn't connect to DB" , 'inventory_id' : inventory_id }

def create_account(name,mail_id,password,role_id):
    conn = getConnection()
    user_id = ""
    if conn:
        try:
            query = "INSERT INTO USERS (NAME,MAIL_ID,PASSWORD,ROLE_ID) VALUES(?,?,?,?)"
            statement = ibm_db.prepare(conn,query)
            ibm_db.bind_param(statement, 1,name)
            ibm_db.bind_param(statement, 2,mail_id)
            ibm_db.bind_param(statement, 3,password)
            ibm_db.bind_param(statement, 4,role_id)
            ibm_db.execute(statement)
            if ibm_db.num_rows(statement) != 1:
                return{ 'status' : False, 'reason' : "Something went wrong" , 'user_id' : user_id }
            else:
                query = "SELECT user_id FROM USERS WHERE name = ?"
                statement = ibm_db.prepare(conn,query)
                ibm_db.bind_param(statement, 1,name)
                ibm_db.execute(statement)
                result = ibm_db.fetch_both(statement)
                user_id = result[0]
        except Exception as e:
            print("Exception while creating account : ",e)
            return{ 'status' : False, 'reason' : "Something went wrong" , 'user_id' : user_id }
        finally:
            closeConnection(conn)
        return{ 'status' : True, 'reason' : "" , 'user_id' : user_id }
    else:
        return{ 'status' : False, 'reason' : "Couldn't connect to DB" , 'user_id' : user_id }
    

def update_account(user_id,inventory_id):
    conn = getConnection()
    if conn:
        try:
            query = "UPDATE USERS SET INVENTORY_ID = ? WHERE USER_ID = ?"
            statement = ibm_db.prepare(conn,query)
            ibm_db.bind_param(statement, 1,inventory_id)
            ibm_db.bind_param(statement, 2,user_id)
            ibm_db.execute(statement)
        except Exception as e:
            print("Exception while adding inventory id in user account : ",e)
            return{ 'status' : False, 'reason' : "Something went wrong" }
        finally:
            closeConnection(conn)
        return{ 'status' : True, 'reason' : "" }
    else:
        return{ 'status' : False, 'reason' : "Couldn't connect to DB"}


