from dbactions.connection import getConnection,closeConnection
import ibm_db

def get_dashboard_details(inventory_id):
    response =  get_warehouses_info(inventory_id)
    print(response['warehouses_info'])
    return(response)
    

def get_warehouses_info(inventory_id):
    conn = getConnection()
    warehouses_info = {}
    if conn:
        try:
            query =  '''SELECT 
                            INVENTORIES.INVENTORY_ID,
                            WAREHOUSES.WAREHOUSE_ID,
                            WAREHOUSES.WAREHOUSE_NAME,
                            WAREHOUSES.WAREHOUSE_LOCATION,
                            WAREHOUSES.DESCRIPTION,
                            PRODUCTS.PRODUCT_ID,
                            PRODUCTS.PRODUCT_NAME,
                            PRODUCTS.PRODUCT_COUNT,
                            PRODUCTS.THRESHOLD_COUNT
                        FROM 
                            INVENTORIES INNER JOIN WAREHOUSES 
                                ON INVENTORIES.INVENTORY_ID = WAREHOUSES.INVENTORY_ID 
                                    LEFT JOIN PRODUCTS
                                        ON WAREHOUSES.WAREHOUSE_ID = PRODUCTS.WAREHOUSE_ID
                        WHERE INVENTORIES.INVENTORY_ID = ?
                        '''
            statement = ibm_db.prepare(conn,query)
            ibm_db.bind_param(statement, 1,inventory_id)
            ibm_db.execute(statement)
            result = ibm_db.fetch_both(statement)
            while result:
                if warehouses_info.get(result[1]):
                    warehouses_info[result[1]]['products'].update({
                        result[5]:{
                                'product_id': result[5],
                                'product_name': result[6],
                                'product_count': result[7],
                                'threshold_count': result[8],
                        }
                    })
                else:
                    warehouses_info[result[1]] = {
                        'warehouse_id':result[1],
                        'warehouse_name' : result[2],
                        'location' : result[3],
                        'description' : result[4],
                        'products':{

                            }
                        }
                    if result[5]:
                        warehouses_info[result[1]]['products'] = {
                            result[5]:{
                                'product_id': result[5],
                                'product_name': result[6],
                                'product_count': result[7],
                                'threshold_count': result[8],
                            }
                        }
                     
                result = ibm_db.fetch_both(statement)
        except Exception as e:
            print("Exception while getting dashboard details : ",e)
            return{ 'status' : False, 'reason' : "Something went wrong" }
        finally:
            closeConnection(conn)
        return{ 'status' : True, 'reason' : "" ,'warehouses_info':warehouses_info}
    else:
        return{ 'status' : False, 'reason' : "Couldn't connect to DB"}

