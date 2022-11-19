from dbactions.connection import getConnection,closeConnection
import ibm_db
import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask_mail import Message

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

def edit_product_count(inventory_id,product_id,count,action,flask_mail_object):
    response = get_product_count_and_threshold_count(product_id)
    if response['status']:
        count = count if action == 'add' else -1*count
        threshold_count = response['threshold_count']
        new_count = response['product_count'] + count
        if new_count >= 0:
            response = change_product_count(product_id,new_count)
            if response['status']:
                if new_count < threshold_count:
                    send_alert_mail(inventory_id,new_count,threshold_count,product_id,flask_mail_object)
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

def send_alert_mail(inventory_id,current_count,threshold_count,product_id,flask_mail_object):
    response = get_receiver_mail_ids(inventory_id)
    if response['status']:
        receiver_mail_ids = response['receiver_mail_ids']
        response = get_product_details(product_id)
        if response['status']:
            send_notification_via_flaskmail(receiver_mail_ids,current_count,threshold_count,response['product_name'],response['warehouse_name'],flask_mail_object)
            send_notification_via_sendgrid(receiver_mail_ids,current_count,threshold_count,response['product_name'],response['warehouse_name'])
    return(response)
    

def get_receiver_mail_ids(inventory_id):
    conn = getConnection()
    receiver_mail_ids = []
    if conn:
        try:
            query = "SELECT MAIL_ID FROM USERS WHERE INVENTORY_ID = ?"
            statement = ibm_db.prepare(conn,query)
            ibm_db.bind_param(statement, 1,inventory_id)
            ibm_db.execute(statement)
            result = ibm_db.fetch_both(statement)
            while result:
                receiver_mail_ids.append(result[0])
                result = ibm_db.fetch_both(statement)
        except Exception as e:
            print("Exception while getting receiver mail ids for notification : ",e)
            return{ 'status' : False, 'reason' : "Something went wrong" , 'receiver_mail_ids':receiver_mail_ids }
        finally:
            closeConnection(conn)
        return{ 'status' : True, 'reason' : "" ,'receiver_mail_ids':receiver_mail_ids}
    else:
        return{ 'status' : False, 'reason' : "Couldn't connect to DB" , 'receiver_mail_ids':receiver_mail_ids}

def get_product_details(product_id):
    conn = getConnection()
    product_name = ""
    warehouse_name = ""
    if conn:
        try:
            query = "SELECT WAREHOUSES.WAREHOUSE_NAME,PRODUCTS.PRODUCT_NAME FROM PRODUCTS INNER JOIN WAREHOUSES ON WAREHOUSES.WAREHOUSE_ID = PRODUCTS.WAREHOUSE_ID WHERE PRODUCT_ID = ?"
            statement = ibm_db.prepare(conn,query)
            ibm_db.bind_param(statement, 1,product_id)
            ibm_db.execute(statement)
            result = ibm_db.fetch_both(statement)
            while result:
                warehouse_name = result[0]
                product_name = result[1]
                result = ibm_db.fetch_both(statement)
        except Exception as e:
            print("Exception while getting product details for sending mail : ",e)
            return{ 'status' : False, 'reason' : "Something went wrong" , 'product_name':product_name,'warehouse_name':warehouse_name }
        finally:
            closeConnection(conn)
        return{ 'status' : True, 'reason' : "" , 'product_name':product_name,'warehouse_name':warehouse_name}
    else:
        return{ 'status' : False, 'reason' : "Couldn't connect to DB" , 'product_name':product_name,'warehouse_name':warehouse_name}


def send_notification_via_sendgrid(receiver_mail_ids,current_count,threshold_count,product_name,warehouse_name):
    message = Mail(
    from_email=os.getenv('SENDER_MAIL_ID'), # sender mail ID
    #to_emails=[receiver_mail_ids],
    to_emails=receiver_mail_ids,
    subject='Test Mail sendgrid',
    html_content='<strong>Test Content</strong>')
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        sg.send(message)
    except Exception as e:
        print("Exception while sending alert mail via sendgrid : ",e)

def send_notification_via_flaskmail(receiver_mail_ids,current_count,threshold_count,product_name,warehouse_name,flask_mail_object):
    msg = Message(
                'Inventory Management - Notification Mail',
                sender =os.getenv('SENDER_MAIL_ID'),
                recipients = receiver_mail_ids
               )
    msg.body = "Hello , This is to notify that a product count has decreased below the threshold limit . Kindly note it down.\n1. Warehouse Name : {}\n2. Product Name : {}\n3. Product's Current Count : {}\n4. Threshold Count : {}".format(warehouse_name,product_name,current_count,threshold_count)
    flask_mail_object.send(msg)
    return 'Sent'

