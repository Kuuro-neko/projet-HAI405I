from flask import Flask
from flask import render_template
from flask import request
from flask import make_response

from flask import redirect, url_for, request, session

import json


app = Flask(__name__)
app.secret_key = "super secret key"

host = '0.0.0.0'
port = 8888

@app.route("/")
@app.route("/index")
def index():
   if 'user' in session:
      name = session['user']
      return render_template("index.html", name = name)
   return render_template("index.html", name = None)

@app.route("/logout")
def logout():
   session.pop('user', None)
   return redirect(url_for('index'))

@app.route("/login", methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      with open('data.json', 'r') as fp:
         data = json.load(fp)
      login = request.form['login']
      password = request.form['password']
      for users in data:
         if users['user'] == login and users['password'] == password:
            session['user'] = login
            return render_template("index.html")
      return render_template("login.html", error = "Login ou mot de passe incorrect")
   else:
      return render_template("login.html")

@app.route('/hello')
def hello_world():
   return "hello world"

if __name__ == '__main__':
  #app.run(host=host, port=port)
  app.run(host=host, port=port, debug=True)