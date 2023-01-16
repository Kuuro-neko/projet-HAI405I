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

@app.route('/product/<name>')
def get_product(name):
  return "The product is " + str(name)

@app.route('/sale/<transaction_id>')
def get_sale(transaction_id=0):
  return "The transaction is "+str(transaction_id)

@app.route('/create/<first_name>/<last_name>')
def create(first_name=None, last_name=None):
  return 'Hello ' + first_name + ', ' + last_name

@app.route('/dashboard/<name>')
def dashboard(name):
   return 'welcome %s' % name


@app.route('/ajouter',methods = ['POST', 'GET'])
def ajouter():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        prix = request.form['prix']
        quantite = request.form['quantite']
        if (name == "" or prix == "" or quantite == ""):
            return redirect(url_for("ajouter"))
        if (name.find("---") != -1 or description.find("---") != -1 or prix.find("---") != -1 or quantite.find("---") != -1):
            return redirect(url_for("ajouter"))
        f = open("static/stock.txt", "a")
        f.write(name + "---" + description + "---" + prix + "---" + quantite + "\n")
        f.close()
        return redirect(url_for("index"))
    else:
        return render_template('ajouter.html')

@app.route('/stock')
def stock():
    f = open("static/stock.txt", "r")
    lines = f.readlines()
    f.close()
    stock = []
    for item in lines:
        item = item.split("---")
        stock.append(item)
    stock.sort()
    return render_template('stock.html', stock=stock)

if __name__ == '__main__':
   app.run(debug = True)