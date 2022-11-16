from dbactions.connection import getConnection,closeConnection
import ibm_db

def add_product(mail_id,warehouse_id,product_name,count,threshold):
    response = get_warehouse_ids_and_product_names(mail_id)
    if response['status']:
        warehouse_ids = response['warehouse_ids']
        product_names = response['product_names']
        if warehouse_id in warehouse_ids:
            if product_name.lower() in product_names:
                return { 'status' : False, 'reason' : 'Product name already exists' }
            else:
                response = add_new_product(warehouse_id,product_name,count,threshold)
                return(response)
        else:
            return { 'status' : False, 'reason' : "Warehouse ID doesn't exists"  }
    return response

def edit_product_count(inventory_id,product_id,count,action):
    response = get_product_count_and_threshold_count(product_id)
    if response['status']:
        count = count if action == 'add' else -1*count
        threshold_count = response['threshold_count']
        new_count = response['product_count'] + count
        if new_count >= 0:
            response = change_product_count(product_id,new_count)
            if response['status']:
                #send_alert_mail(inventory_id,new_count,threshold_count)
                return({ 'status':True,'reason':'','new_count':new_count })
            return(response)
        else:
            return { 'status':False,'reason':"Invalid quantity" }
    return(response)
    
def get_warehouse_ids_and_product_names(mail_id):
    conn = getConnection()
    warehouse_ids = []
    product_names = []
    if conn:
        try:
            query = "SELECT WAREHOUSES.WAREHOUSE_ID,PRODUCTS.PRODUCT_NAME,USERS.MAIL_ID FROM  USERS INNER JOIN INVENTORIES ON USERS.USER_ID = INVENTORIES.RETAILER_ID INNER JOIN WAREHOUSES ON INVENTORIES.INVENTORY_ID = WAREHOUSES.INVENTORY_ID LEFT JOIN PRODUCTS ON WAREHOUSES.WAREHOUSE_ID = PRODUCTS.WAREHOUSE_ID WHERE USERS.MAIL_ID = ?"
            statement = ibm_db.prepare(conn,query)
            ibm_db.bind_param(statement,1,mail_id)
            ibm_db.execute(statement)
            result = ibm_db.fetch_both(statement)
            while(result):
                warehouse_ids.append(result[0])
                if result[1]:
                    product_names.append(result[1].lower()) 
                result = ibm_db.fetch_both(statement)
        except Exception as e:
            print("Exception while getting warehouse ids and product names from DB : ",e)
            return{ 'status' : False, 'reason' : "Something went wrong",'warehouse_ids':warehouse_ids,"product_names":product_names }
        finally:
            closeConnection(conn)
        return{ 'status' : True, 'reason' : "",'warehouse_ids':warehouse_ids,"product_names":product_names }
    else:
        return{ 'status' : False, 'reason' : "Couldn't connect to DB",'warehouse_ids':warehouse_ids,"product_names":product_names}

def add_new_product(warehouse_id,product_name,count,threshold):
    conn = getConnection()
    if conn:
        try:
            query = "INSERT INTO PRODUCTS (WAREHOUSE_ID,PRODUCT_NAME,PRODUCT_COUNT,THRESHOLD_COUNT) VALUES(?,?,?,?)"
            statement = ibm_db.prepare(conn,query)
            ibm_db.bind_param(statement, 1,warehouse_id)
            ibm_db.bind_param(statement, 2,product_name)
            ibm_db.bind_param(statement, 3,count)
            ibm_db.bind_param(statement, 4,threshold)
            ibm_db.execute(statement)
            if ibm_db.num_rows(statement) != 1:
                return{ 'status' : False, 'reason' : "Something went wrong" }
        except Exception as e:
            print("Exception while adding new products : ",e)
            return{ 'status' : False, 'reason' : "Something went wrong" }
        finally:
            closeConnection(conn)
        return{ 'status' : True, 'reason' : "" }
    else:
        return{ 'status' : False, 'reason' : "Couldn't connect to DB"}


def get_product_count_and_threshold_count(product_id):
    conn = getConnection()
    product_count = ''
    threshold_count = ''
    if conn:
        try:
            query = "SELECT PRODUCT_COUNT,THRESHOLD_COUNT FROM PRODUCTS WHERE PRODUCT_ID = ?"
            statement = ibm_db.prepare(conn,query)
            ibm_db.bind_param(statement, 1,product_id)
            ibm_db.execute(statement)
            result = ibm_db.fetch_both(statement)
            while result:
                product_count = result[0]
                threshold_count = result[1]
                result = ibm_db.fetch_both(statement)
        except Exception as e:
            print("Exception while getting products count : ",e)
            return{ 'status' : False, 'reason' : "Something went wrong" , 'product_count':product_count, 'threshold_count':threshold_count }
        finally:
            closeConnection(conn)
        return{ 'status' : True, 'reason' : "" ,'product_count':product_count, 'threshold_count':threshold_count}
    else:
        return{ 'status' : False, 'reason' : "Couldn't connect to DB" , 'product_count':product_count , 'threshold_count':threshold_count}

def change_product_count(product_id,new_count):
    conn = getConnection()
    if conn:
        try:
            query = "UPDATE PRODUCTS SET PRODUCT_COUNT = ? WHERE PRODUCT_ID = ?"
            statement = ibm_db.prepare(conn,query)
            ibm_db.bind_param(statement, 1,new_count)
            ibm_db.bind_param(statement, 2,product_id)
            ibm_db.execute(statement)
        except Exception as e:
            print("Exception while getting products count : ",e)
            return{ 'status' : False, 'reason' : "Something went wrong"  }
        finally:
            closeConnection(conn)
        return{ 'status' : True, 'reason' : "" }
    else:
        return{ 'status' : False, 'reason' : "Couldn't connect to DB"  }

def send_alert_mail(inventory_id,current_count,threshold_count):
    pass