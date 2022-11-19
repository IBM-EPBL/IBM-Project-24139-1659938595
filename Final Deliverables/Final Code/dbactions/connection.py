import ibm_db
import os
from dotenv import load_dotenv

def getConnection():
    conn = False
    try:
        conn = ibm_db.connect(os.getenv('DB2_CREDENTIALS'), '', '')
    except Exception as e:
        print("Exception while opening connection :",e)
        print(ibm_db.conn_errormsg())
    return(conn)

def closeConnection(conn):
    try:
        ibm_db.close(conn)
        return(True)
    except Exception as e:
        print("Exception while closing connection :",e)
        return(False)