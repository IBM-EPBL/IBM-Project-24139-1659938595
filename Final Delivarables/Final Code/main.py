
from flask import *
import re
import os
from dbactions.signup import create_retailer_account,create_user_account 
from dbactions.signin import validate_user
from dbactions.profile import get_user_profile_details, update_profile
from dbactions.addwarehouse import add_new_warehouse
from dbactions.dashboard import get_dashboard_details
from dbactions.products import add_product,edit_product_count
from flask_mail import Mail
from dotenv import load_dotenv

app = Flask(__name__)  
mail = Mail(app)

load_dotenv()
app.config['MAIL_SERVER']= os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route('/signin',methods = ['POST', 'GET'])  
def sign_in():
      if request.method == 'GET':
            mail_id = request.cookies.get('mail_id')
            if mail_id != None:
                  return redirect("http://127.0.0.1:5000/dashboard",code=302)
            else:
                  return render_template('signin.html')
      elif  request.method == 'POST':
            response = validate_user(request.json['mail_id'],request.json['password'])
            resp = make_response(response)
            if response['status']:
                  resp.set_cookie("mail_id", request.json['mail_id'])
                  resp.set_cookie("role",'retailer' if response['role_id'] == 1 else 'user')
            return(resp)

@app.route('/signup',methods = ['POST', 'GET'])  
def sign_up():
      if request.method == 'GET':   
            mail_id = request.cookies.get('mail_id')
            if mail_id != None:
                  return redirect("http://127.0.0.1:5000/dashboard",code=302)
            else:
                  return render_template('signup.html')
      elif  request.method == 'POST':
            if request.json['role'] == 'retailer':
                  response = create_retailer_account(request.json['name'],request.json['mail_id'],request.json['password'],request.json['inventory_id_or_name'])
            else:
                  response = create_user_account(request.json['name'],request.json['mail_id'],request.json['password'],request.json['inventory_id_or_name'])
            resp = make_response(response)
            if response['status']:
                  resp.set_cookie("mail_id", request.json['mail_id'])
                  resp.set_cookie("role",request.json['role'])
            return(resp)


@app.route('/logout',methods = ['GET'])  
def logout():
      if request.method == 'GET':  
            resp = make_response(redirect("http://127.0.0.1:5000/signin",code=302))
            resp.set_cookie('mail_id', '', expires=0)
            return(resp)

@app.route('/dashboard',methods = ['GET'])  
def dashboard():
      if request.method == 'GET':  
            mail_id = request.cookies.get('mail_id')
            if mail_id != None:
                  user_info = {}
                  warehouses_info = {}
                  user_info_response = get_user_profile_details(mail_id)
                  warehouses_info_response = {}
                  if user_info_response.get('status'):
                        user_info = user_info_response['user_info']
                        warehouses_info_response = get_dashboard_details(user_info['inventory_id'])
                  if warehouses_info_response.get('status'):
                        warehouses_info = warehouses_info_response['warehouses_info']
                  return render_template("dashboard.html",user_info=user_info,mail_id=user_info['mail_id'],warehouses_info=warehouses_info)
                  
            else:
                  return redirect("http://127.0.0.1:5000/signin",code=302)

@app.route('/dashboard/addwarehouse',methods = ['GET','POST'])  
def add_new_warehouse():
      mail_id = request.cookies.get('mail_id')
      role = request.cookies.get('role')
      if mail_id != None:
            if role == 'retailer':
                  if request.method == 'GET':   
                        return render_template("addwarehouse.html")
                  elif  request.method == 'POST':
                        response = add_new_warehouse(mail_id,request.json['warehouse_name'],request.json['location'],request.json['description'])
                        return(response)    
            else:
                  return redirect("http://127.0.0.1:5000/dashboard",code=302)
      else:   
            return redirect("http://127.0.0.1:5000/signin",code=302)
      

@app.route('/dashboard/addproduct',methods = ['GET','POST'])  
def add_new_product():
      mail_id = request.cookies.get('mail_id')
      role = request.cookies.get('role')
      if mail_id != None:
            warehouse_id = request.args.get('warehouse_id')
            if role == 'retailer' :
                  if request.method == 'GET':
                        warehouse_id_regex = re.compile(r'\d+')
                        if  warehouse_id and warehouse_id_regex.search(warehouse_id) :   
                              return render_template("addProducts.html",warehouse_id=warehouse_id)
                        else:
                              return redirect("http://127.0.0.1:5000/dashboard",code=302)
                  elif  request.method == 'POST':
                        response = add_product(mail_id,int(request.json['warehouse_id']),request.json['product_name'],request.json['count'],request.json['threshold'])
                        return(response)    
            else:
                  return redirect("http://127.0.0.1:5000/dashboard",code=302)
      else:   
            return redirect("http://127.0.0.1:5000/signin",code=302)

@app.route('/dashboard/editproductdetails',methods = ['POST'])  
def edit_product_details():
      mail_id = request.cookies.get('mail_id')
      if mail_id != None:
            if request.method == 'POST':
                  response = edit_product_count(request.json['inventory_id'],request.json['product_id'],int(request.json['count']),request.json['action'],mail)
                  return(response)
            else:
                  return redirect("http://127.0.0.1:5000/dashboard",code=302)
      else:   
            return redirect("http://127.0.0.1:5000/signin",code=302)


@app.route('/dashboard/profile',methods = ['GET'])  
def profile():
      if request.method == 'GET':  
            mail_id = request.cookies.get('mail_id')
            if mail_id != None:
                  response = get_user_profile_details(mail_id)
                  return(render_template('profile.html',response=response['user_info'],reason=response['reason']))
            else:
                  return redirect("http://127.0.0.1:5000/signin",code=302)
      
@app.route('/dashboard/profile/editprofile',methods = ['GET','POST'])  
def edit_profile():
      mail_id = request.cookies.get('mail_id')
      
      if mail_id == None:
            return redirect("http://127.0.0.1:5000/signin",code=302)
      else:
            if request.method == 'GET':  
                  response = get_user_profile_details(mail_id)
                  return render_template('editprofile.html',response=response['user_info'],reason=response['reason'])           
            elif request.method == 'POST':
                  response = update_profile(request.json['current_mail_id'],request.json)
                  resp = make_response(response)
                  if request.json.get('mail_id'):
                        resp.set_cookie("mail_id", request.json.get('mail_id'))
                  return resp


if __name__ == '__main__':  
   app.run(debug = True)  