from flask import Flask
from flask import render_template
from flask import request
from flask import make_response

from flask import Flask, redirect, url_for, request

import json


app = Flask(__name__)

host = '0.0.0.0'
port = 8888

@app.route("/")
@app.route("/index")
def index():
   return render_template("index.html")

@app.route("/login", methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      with open('data.json', 'r') as fp:
         data = json.load(fp)
      login = request.form['login']
      password = request.form['password']
      for users in data:
         if users['user'] == login and users['password'] == password:
            resp = make_response(render_template("index.html", user = login))
            resp.set_cookie('user', login)
            return resp
      return render_template("login.html", error = "Login ou mot de passe incorrect")
   else:
      return render_template("login.html")

@app.route('/hello')
def hello_world():
   return "hello world"

if __name__ == '__main__':
  #app.run(host=host, port=port)
  app.run(host=host, port=port, debug=True)