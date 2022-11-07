from dbactions.connection import getConnection,closeConnection
import ibm_db


def validate_user(mail_id,password):
    response = get_user_id(mail_id,password) 
    if response['status']:
        if response['user_id'] == '':
            return({ 'status' : False, 'reason' : "Invalid credentials" })
    return(response)

def get_user_id(mail_id,password):
    conn = getConnection()
    user_id = ''
    if conn:
        try:
            query = "SELECT MAIL_ID,PASSWORD,USER_ID FROM USERS WHERE MAIL_ID = ? AND PASSWORD = ?"
            statement = ibm_db.prepare(conn,query)
            ibm_db.bind_param(statement, 1,mail_id)
            ibm_db.bind_param(statement, 2,password)
            ibm_db.execute(statement)
            result = ibm_db.fetch_both(statement)
            while result:
                user_id = result[2]
                result = ibm_db.fetch_both(statement)
        except Exception as e:
            print("Exception while checking mail id and password of user : ",e)
            return{ 'status' : False, 'reason' : "Something went wrong" , 'user_id' : user_id }
        finally:
            closeConnection(conn)
        return{ 'status' : True, 'reason' : "" , 'user_id' : user_id }
    else:
        return{ 'status' : False, 'reason' : "Couldn't connect to DB" , 'user_id' : user_id }

    
    