
from flask import *
import ibm_db
from dbactions.signup import create_retailer_account,create_user_account 
from dbactions.signin import validate_user
app = Flask(__name__)  


@app.route('/signin',methods = ['POST', 'GET'])  
def sign_in():
      if request.method == 'GET':
            mail_id = request.cookies.get('mail_id')
            if mail_id != None:
                  return redirect("http://127.0.0.1:5000/dashboard",code=302)
            else:
                  return render_template('signin.html')
      else :
            response = validate_user(request.json['mail_id'],request.json['password'])
            if response['status']:
                  response['cookies'] = "mail_id = "+request.json['mail_id']
            else:
                  response['cookies'] = ""
            return(response)

@app.route('/signup',methods = ['POST', 'GET'])  
def sign_up():
      if request.method == 'GET':   
            mail_id = request.cookies.get('mail_id')
            if mail_id != None:
                  return redirect("http://127.0.0.1:5000/dashboard",code=302)
            else:
                  return render_template('signup.html')
      else:
            if request.json['role'] == 'retailer':
                  response = create_retailer_account(request.json['name'],request.json['mail_id'],request.json['password'],request.json['inventory_id_or_name'])
            else:
                  response = create_user_account(request.json['name'],request.json['mail_id'],request.json['password'],request.json['inventory_id_or_name'])
            if response['status']:
                  response['cookies'] = "mail_id = "+request.json['mail_id']
            else:
                  response['cookies'] = ""
            return(response)

@app.route('/dashboard',methods = ['GET'])  
def dashboard():
      if request.method == 'GET':  
            mail_id = request.cookies.get('mail_id')
            if mail_id != None:
                  return render_template("dashboard.html")
            else:
                  return redirect("http://127.0.0.1:5000/signin",code=302)

@app.route('/logout',methods = ['GET'])  
def logout():
      if request.method == 'GET':  
            resp = make_response(redirect("http://127.0.0.1:5000/signin",code=302))
            resp.set_cookie('mail_id', '', expires=0)
            return(resp)


if __name__ == '__main__':  
   app.run(debug = True)  