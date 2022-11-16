
from flask import *
import re
from dbactions.signup import create_retailer_account,create_user_account 
from dbactions.signin import validate_user
from dbactions.profile import get_user_profile_details, update_profile
app = Flask(__name__)  


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
                  user_info_response = get_user_profile_details(mail_id)
                  if user_info_response.get('status'):
                        user_info = user_info_response['user_info']
                  return render_template("dashboard.html",user_info=user_info,mail_id=user_info['mail_id'])
                  
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