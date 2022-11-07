import ibm_db

def getConnection():
    conn = False
    try:
        conn = ibm_db.connect('DATABASE=bludb;HOSTNAME=8e359033-a1c9-4643-82ef-8ac06f5107eb.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30120;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=jnq67868;PWD=JbJrbPr9U44SqIgx', '', '')
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