from flask import Flask
from flask import render_template
from flask import request

from flask import Flask, redirect, url_for, request

app = Flask(__name__)

host = '0.0.0.0'
port = 8888

@app.route("/")
@app.route("/index")
def index():
   return render_template("index.html")

@app.route('/hello')
def hello_world():
   return "hello world"

if __name__ == '__main__':
  #app.run(host=host, port=port)
  app.run(host=host, port=port, debug=True)