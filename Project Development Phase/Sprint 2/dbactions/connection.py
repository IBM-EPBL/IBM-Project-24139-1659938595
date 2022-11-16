import ibm_db

def getConnection():
    conn = False
    try:
        conn = ibm_db.connect('DATABASE=YOURDATABASE;HOSTNAME=YOURHOSTNAME;PORT=YOURPORT;SECURITY=YOURSECURITYL;SSLServerCertificate=YOURCERTIFICATE, '', '')
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