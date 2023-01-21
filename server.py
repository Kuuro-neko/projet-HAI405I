from flask import Flask
from flask import render_template
from flask import request
from flask import make_response

from flask import redirect, url_for, request, session

from bs4 import BeautifulSoup

import mermaid as mmd
import markdown
import markdown2
import json


app = Flask(__name__)
app.secret_key = "super secret key"

host = '0.0.0.0'
port = 8888

# Retourne le contenu du fichier data.json
# Out : data (dict)
def get_data():
   with open('data.json', 'r') as fp:
      data = json.load(fp)
   return data

# Ecrit dans le fichier data.json
# In : data (dict)
def write_data(data):
   with open('data.json', 'w') as fp:
      json.dump(data, fp, indent=4)

# Retourne l'id de l'utilisateur dans le fichier data.json
# In : user (str)
# Out : id (int)
def get_user_id(user):
   data = get_data()
   for i in range(len(data)):
      if data[i]['user'] == user:
         return i
   return None

# Retourne la liste des questions de l'utilisateur
# In : user (str)
# Out : questions (list)
def get_questions(user):
   data = get_data()
   return data[get_user_id(user)]['questions']

# Retourne la liste des etiquettes utilisées
# Out : etiquettes (list)
def get_etiquettes():
   with open('etiquettes.json', 'r') as fp:
      data = json.load(fp)
   return data

# Met à jour la liste des etiquettes utilisées
def majListeEtiquettes(listeEtiquettes):
   data = get_etiquettes()
   for etiquette in listeEtiquettes:
      if etiquette not in data:
         data.append(etiquette)
   with open('etiquettes.json', 'w') as fp:
      json.dump(data, fp, indent=4)

# Supprime les etiquettes non utilisées
def clear_etiquettes_non_utilisees():
   data = get_etiquettes()
   data2 = get_data()
      
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
      data = get_data()
      login = request.form['login']
      password = request.form['password']
      for users in data:
         if users['user'] == login and users['password'] == password:
            session['user'] = login
            return redirect(url_for('questions'))
      return render_template("login.html", error = "Login ou mot de passe incorrect")
   else:
      return render_template("login.html")

@app.route("/inscription", methods = ['POST', 'GET'])
def inscription():
   if request.method == 'POST':
      data = get_data()
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
      write_data(data)
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
      data = get_data()
      user_id = get_user_id(name)
      data[user_id]['questions'].pop(id_question)
      write_data(data)
      return redirect(url_for('questions'))
   return render_template("index.html", name = None)

@app.route("/add_question", methods = ['POST', 'GET'])
def add_question():
   if request.method == 'POST':
      data = get_data()
      
      text = request.form['text']
      titre = request.form['titre']
      try:
         etiquettes = json.loads(request.form['etiquettes'])
      except:
         etiquettes = []
      try:
         answers = json.loads(request.form['answers_json'])
      except:
         answers = []
      user = session['user']
      question = {
         "type" : "QCM",
         "text": text,
         "etiquettes" : etiquettes,
         "answers": answers,
         "titre": titre
      }
      data[get_user_id(user)]['questions'].append(question)
      majListeEtiquettes(etiquettes)
      write_data(data)
      return redirect(url_for('questions'))
   else:
      etiquettes_existantes = get_etiquettes()
      return render_template("add_question.html", etiquettes_existantes = etiquettes_existantes)

@app.route("/edit_question/<int:id_question>", methods = ['POST', 'GET'])
def edit_question(id_question):
   
   if 'user' in session:
      if request.method == 'POST':
         data = get_data()
         
         text = request.form['text']
         titre = request.form['titre']
         try:
            etiquettes = json.loads(request.form['etiquettes'])
         except:
            etiquettes = []
         try:
            answers = json.loads(request.form['answers_json'])
         except:
            answers = []
         
         user = session['user']
         user_id = get_user_id(user)
         id_question = int(request.form['id_question'])
         question = {
            "type" : "QCM",
            "text": text,
            "etiquettes" : etiquettes,
            "answers": answers,
            "titre" : titre
         }

         data[user_id]['questions'][id_question] = question
         write_data(data)
         majListeEtiquettes(etiquettes)
         return redirect(url_for('questions'))
      else:
         name = session['user']
         questions = get_questions(name)
         etiquettes_existantes = get_etiquettes()
         return render_template("edit_question.html", name = name, question = questions[id_question], id_question = id_question, etiquettes_existantes = etiquettes_existantes)
   return render_template("index.html", name = None)

def traitement_visualiser(texte):
   # Markdown et code coloré
   html = markdown2.markdown(texte, extras=["fenced-code-blocks", "code-friendly", "mermaid"], safe_mode='escape')
   # Mermaid
   soup = BeautifulSoup(html, 'html.parser')
   for code_block in soup.find_all('code'):
      if "class" not in code_block.parent.parent.attrs:
         new_div = soup.new_tag("div")
         new_div['class'] = "mermaid"
         for line in code_block.contents:
            new_div.append(line)
         code_block.replace_with(new_div)
   return soup.prettify()


@app.route("/visualiser/<int:id_question>")
def visualiser(id_question):
   if 'user' in session:
      name = session['user']
      question = get_questions(name)[id_question]
      question['text'] = traitement_visualiser(question['text'])

      for answer in question['answers']:
         answer['text'] = traitement_visualiser(answer['text'])
      return render_template("visualiser.html", question = question)
   return render_template("index.html", name = None)

@app.route('/generation', methods=['GET'])
def generation():
    if 'user' in session:
      name = session['user']
      questions = get_questions(name)
      return render_template('generation.html', name=name, questions=questions, length = len(questions))
    return render_template("index.html", name = None)



@app.route('/show', methods=['POST'])
def show():
   if 'user' in session:
      name = session['user']
      questions = get_questions(name)
      if request.method == 'POST':
         tabChoix = request.form.getlist('choisi')
         questions_a_generer = []
         htmlTraite = []
         for id in tabChoix :
            questions_a_generer.append(questions[int(id)]) 
            texte_a_traiter = questions[int(id)]['text']
            html = traitement_visualiser(texte_a_traiter)
            htmlTraite.append(html) 

      print(htmlTraite)
      return render_template("SHOW.html",name=name, questions_a_generer = questions_a_generer, length = len(questions_a_generer), htmlTraite = htmlTraite)
   return render_template("index.html", name = None)



if __name__ == '__main__':
  #app.run(host=host, port=port)
  app.run(host=host, port=port, debug=True)

