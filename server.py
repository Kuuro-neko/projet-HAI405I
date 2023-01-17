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

def get_user_id(user):
   with open('data.json', 'r') as fp:
      data = json.load(fp)
   
   for i in range(len(data)):
      if data[i]['user'] == user:
         return i
   return None

def get_questions(user):
   with open('data.json', 'r') as fp:
      data = json.load(fp)
   user_id = get_user_id(user)
   return data[user_id]['questions']

def majListeEtiquettes(listeEtiquettes):
   with open('etiquettes.json', 'r') as fp:
      data = json.load(fp)
   for etiquette in listeEtiquettes:
      if etiquette not in data:
         data.append(etiquette)
   with open('etiquettes.json', 'w') as fp:
      json.dump(data, fp, indent=4)

def get_etiquettes():
   with open('etiquettes.json', 'r') as fp:
      data = json.load(fp)
   return data

def clear_etiquettes_non_utilisees():
   with open('etiquettes.json', 'r') as fp:
      data = json.load(fp)
   with open('data.json', 'r') as fp:
      data2 = json.load(fp)
      
   # Pour chaque etiquette, si on la trouve dans une question, on la garde sinon on la supprime
   for etiquette in data:
      found = False
      for user in data2:
         if found:
            break
         for question in user['questions']:
            if etiquette in question['etiquettes']:
               found = True
               break
      if not found:
         data.remove(etiquette)
   
   with open('etiquettes.json', 'w') as fp:
      json.dump(data, fp, indent=4)

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
            return redirect(url_for('index'))
      return render_template("login.html", error = "Login ou mot de passe incorrect")
   else:
      return render_template("login.html")

@app.route("/inscription", methods = ['POST', 'GET'])
def inscription():
   if request.method == 'POST':
      with open('data.json', 'r') as fp:
         data = json.load(fp)
      login = request.form['login']
      password = request.form['password']
      for users in data:
         if users['user'] == login:
            return render_template("inscription.html", error = "Login déjà utilisé")
      data.append({
         "user": login,
         "password": password,
         "questions": []
      })
      with open('data.json', 'w') as fp:
         json.dump(data, fp, indent=4)
      return redirect(url_for('login'))
   else:
      return render_template("inscription.html")

@app.route("/questions")
def questions():
   if 'user' in session:
      name = session['user']
      questions = get_questions(name)
      return render_template("questions.html", name = name, questions = questions, length = len(questions))
   return render_template("index.html", name = None)

@app.route("/del_question/<int:id_question>")
def del_question(id_question):
   if 'user' in session:
      name = session['user']
      with open('data.json', 'r') as fp:
         data = json.load(fp)
      user_id = get_user_id(name)
      data[user_id]['questions'].pop(id_question)
      with open('data.json', 'w') as fp:
         json.dump(data, fp, indent=4)
      return redirect(url_for('questions'))
   return render_template("index.html", name = None)

@app.route("/add_question", methods = ['POST', 'GET'])
def add_question():
   if request.method == 'POST':
      with open('data.json', 'r') as fp:
         data = json.load(fp)
      
      text = request.form['text']
      etiquettes = json.loads(request.form['etiquettes'])
      majListeEtiquettes(etiquettes)
      user = session['user']
      user_id = get_user_id(user)

      nbAnswers = request.form['nbAnswers']
      answers = []
      for i in range(int(nbAnswers)):
         answers.append({
            "text": request.form['text' + str(i)],
            "isCorrect": request.form.get('correct' + str(i)) != None
         })

      question = {
         "type" : "QCM",
         "text": text,
         "etiquettes" : etiquettes,
         "answers": answers
      }
      data[user_id]['questions'].append(question)
      with open('data.json', 'w') as fp:
         json.dump(data, fp, indent=4)
      
      return redirect(url_for('questions'))
   else:
      etiquettes_existantes = get_etiquettes()
      return render_template("add_question.html", etiquettes_existantes = etiquettes_existantes)

@app.route("/edit_question/<int:id_question>", methods = ['POST', 'GET'])
def edit_question(id_question):
   
   if 'user' in session:
      if request.method == 'POST':
         with open('data.json', 'r') as fp:
            data = json.load(fp)
         
         text = request.form['text']
         etiquettes = json.loads(request.form['etiquettes'])
         majListeEtiquettes(etiquettes)
         user = session['user']
         user_id = get_user_id(user)
         id_question = int(request.form['id_question'])

         nbAnswers = request.form['nbAnswers']
         answers = []
         for i in range(int(nbAnswers)):
            answers.append({
               "text": request.form['text' + str(i)],
               "isCorrect": request.form.get('correct' + str(i)) != None
            })

         question = {
            "type" : "QCM",
            "text": text,
            "etiquettes" : etiquettes,
            "answers": answers
         }

         data[user_id]['questions'][id_question] = question

         with open('data.json', 'w') as fp:
            json.dump(data, fp, indent=4)
         
         return redirect(url_for('questions'))
      else:
         name = session['user']
         questions = get_questions(name)
         nbAnswers = len(questions[id_question]['answers'])
         etiquettes_existantes = get_etiquettes()
         return render_template("edit_question.html", name = name, question = questions[id_question], id_question = id_question, nbAnswers = nbAnswers, etiquettes_existantes = etiquettes_existantes)
   return render_template("index.html", name = None)

if __name__ == '__main__':
  #app.run(host=host, port=port)
  app.run(host=host, port=port, debug=True)

