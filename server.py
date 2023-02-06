import io
from flask import Flask
from flask import render_template
from flask import request
from flask import make_response

from flask import redirect, url_for, request, session

from bs4 import BeautifulSoup

from hashlib import sha256

import markdown2
import json
import csv
import os

app = Flask(__name__)
app.secret_key = "super secret key"
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

host = '0.0.0.0'
port = 8888

################################## Fonctions ##################################

def create_unique_id(id, string):
    return sha256(str(id).encode() + string.encode()).hexdigest()[:8]


def get_data():
    """
    Retourne le contenu du fichier prof.json
    Out : data (dict)
    """
    with open('prof.json', 'r') as fp:
        data = json.load(fp)
    return data


def get_etudiants():
    """
    Retourne le contenu du fichier etudiants.json
    Out : data (dict)
    """
    with open('etudiants.json', 'r') as fp:
        data = json.load(fp)
    return data


def write_data(data):
    """
    Ecrit dans le fichier prof.json
    In : data (dict)
    """
    with open('prof.json', 'w') as fp:
        json.dump(data, fp, indent=4)

def write_data_etudiant(data):
   """
   Ecrit dans le fichier prof.json
   In : data (dict)
   """
   with open('etudiants.json', 'w') as fp:
      json.dump(data, fp, indent=4)

def get_prof_id(prof):
    """
    Retourne l'id de l'utilisateur dans le fichier prof.json
    In : prof (str)
    Out : id (int)
    """
    data = get_data()
    for i in range(len(data)):
        if data[i]['user'] == prof:
            return i
    return None


def get_questions(prof, filtre=None):
    """
    Retourne la liste des questions de l'utilisateur ayant une etiquette filtre
    In : prof (str)
    In : filtre (list (str)), optionnel : None par défaut
    Out : questions (list (dict)))
    """
    data = get_data()
    if filtre != None:
        questions = []
        for question in data[get_prof_id(prof)]['questions']:
            for etiquette in question['etiquettes']:
                if etiquette in filtre:
                    questions.append(question)
                    break
        return questions
    return data[get_prof_id(prof)]['questions']

# Retourne la liste des etiquettes utilisées dans des questions
# In : questions (list (dict)) (optionnel, si non renseigné, on prend toutes les etiquettes utilisées dans toutes les questions)
# Out : etiquettes (list)


def get_etiquettes(questions=None):
    """
    Retourne la liste des etiquettes utilisées dans des questions
    In : questions (list (dict)) (optionnel, si non renseigné, on prend toutes les etiquettes utilisées dans toutes les questions)
    Out : etiquettes (list)
    """
    if questions == None:
        with open('etiquettes.json', 'r') as fp:
            data = json.load(fp)
    else:
        data = []
        for question in questions:
            for etiquette in question['etiquettes']:
                if etiquette not in data:
                    data.append(etiquette)
    return data


def majListeEtiquettes(listeEtiquettes):
    """
    Met à jour la liste des etiquettes utilisées dans etiquettes.json
    """
    data = get_etiquettes()
    for etiquette in listeEtiquettes:
        if etiquette not in data:
            data.append(etiquette)
    with open('etiquettes.json', 'w') as fp:
        json.dump(data, fp, indent=4)


def clear_etiquettes_non_utilisees():
    """
    Supprime les etiquettes non utilisées dans etiquettes.json
    """
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


def traiter_texte(texte):
    """
    Traite une chaine de caractère pour la visualiser
    In : texte (str)
    Out : html (str)
    """
    # Markdown et code coloré
    html = markdown2.markdown(texte, extras=[
                              "fenced-code-blocks", "code-friendly", "mermaid"], safe_mode='escape')
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


def traiter_question(question):
    """
    Traite une question pour la visualiser
    In : question (dict)
    Out : question (dict)
    """
    question["text"] = traiter_texte(question["text"])
    for answer in question["answers"]:
        answer["text"] = traiter_texte(answer["text"])
    return question


def creer_comptes_etudiant(filename):
   with open((UPLOAD_FOLDER + "/" + filename), 'r') as f:
      reader = csv.DictReader(f)
      rows = list(reader)

   try:
      with open('etudiants.json', 'r') as f:
         data = json.load(f)
   except:
      data = []
      
   def get_all_num_etu(json_data):
      num_etu = []
      for etu in json_data:
         num_etu.append(etu['numero_etudiant'])
      return num_etu

   num_existants = get_all_num_etu(data)

   for row in rows:
      if row['numero_etudiant'] not in num_existants:
         row["password"] = ""
         row["prenom"] = row["prenom"].replace(" ", "_").replace("'", "_").lower()
         row["nom"] = row["nom"].replace(" ", "_").replace("'", "_").lower()
         data.append(row)

   with open('etudiants.json', 'w') as f:
      json.dump(data, f, indent=4)
      
def try_login_etudiant(login, password, etudiant):
   if etudiant['nom'] + "." + etudiant['prenom'] == login:
      if etudiant['password'] == "":
         if password == etudiant['numero_etudiant']:
            return True
      else:
         if password == etudiant['password']:
            return True
   return False
      
############################################### ROUTES ###############################################

@app.route("/")
@app.route("/index")
def index():
    if 'user' in session:
        name = session['user']
        return render_template("index.html", name=name)
    return render_template("index.html", name=None)


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
        return render_template("login.html", error="Login ou mot de passe incorrect")
    else:
        return render_template("login.html")






@app.route("/inscription", methods=['POST', 'GET'])
def inscription():
    if request.method == 'POST':
        data = get_data()
        login = request.form['login']
        password = request.form['password']
        for users in data:
            if users['user'] == login:
                return render_template("inscription.html", error="Login déjà utilisé")
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
        try:
            questions = get_questions(name)
        except:
            session.pop('user', None)
            return redirect(url_for('index'))
        return render_template("questions.html", name=name, questions=questions, length=len(questions))
    return render_template("index.html", name=None)


@app.route("/del_question/<int:id_question>")
def del_question(id_question):
    if 'user' in session:
        name = session['user']
        data = get_data()
        user_id = get_prof_id(name)
        data[user_id]['questions'].pop(id_question)
        write_data(data)
        return redirect(url_for('questions'))
    return render_template("index.html", name=None)


@app.route("/traiter_type", methods = ['POST', 'GET'])
def traiter_type():
   if request.method == 'POST':
      type = request.form['types']
      etiquettes_existantes = get_etiquettes()
      return render_template("add_question.html", etiquettes_existantes = etiquettes_existantes, type = type)
   else: 
      return render_template("choixType.html")
      
@app.route("/add_question", methods = ['POST', 'GET'])
def add_question():
   if request.method == 'POST':
      data = get_data()
      text = request.form['text']
      titre = request.form['titre']
      type = request.form['types']
      question_id = create_unique_id(get_questions(session['user']).length(), session['user'])
      try:
         etiquettes = json.loads(request.form['etiquettes'])
      except:
         etiquettes = []
      if type == "ChoixMultiple":
         try:
            answers = json.loads(request.form['answers_json'])
         except:
            answers = []
      elif type == "Alphanumerique" :
         try:
            answers = request.form['rep']
         except:
            answers = ""
      user = session['user']
      question = {
         "type" : type,
         "id": question_id,
         "text": text,
         "etiquettes" : etiquettes,
         "answers": answers,
         "titre": titre
      }
      data[get_prof_id(user)]['questions'].append(question)
      majListeEtiquettes(etiquettes)
      write_data(data)
      return redirect(url_for('questions'))
   else:
      etiquettes_existantes = get_etiquettes()
      return render_template("add_question.html", etiquettes_existantes = etiquettes_existantes)

@app.route("/edit_question/<int:id_question>", methods=['POST', 'GET'])
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
            user_id = get_prof_id(user)
            id_question = int(request.form['id_question'])
            question = {
                "type": "QCM",
                "text": text,
                "etiquettes": etiquettes,
                "answers": answers,
                "titre": titre
            }

            data[user_id]['questions'][id_question] = question
            write_data(data)
            majListeEtiquettes(etiquettes)
            return redirect(url_for('questions'))
        else:
            name = session['user']
            questions = get_questions(name)
            etiquettes_existantes = get_etiquettes()
            return render_template("edit_question.html", name=name, question=questions[id_question], id_question=id_question, etiquettes_existantes=etiquettes_existantes)
    return render_template("index.html", name=None)


@app.route("/visualiser/<int:id_question>")
def visualiser(id_question, question=None):
    if 'user' in session:
        name = session['user']
        if question == None:
            question = get_questions(name)[id_question]
            question = traiter_question(question)
        return render_template("visualiser.html", question=question)
    return render_template("index.html", name=None)


@app.route("/visualiser_temp", methods=['POST'])
def visualiser_temp():
    if 'user' in session and request.method == 'POST':
        name = session['user']
        question = json.loads(request.form['question_json'])
        question = traiter_question(question)
        return render_template("visualiser.html", question=question)
    return render_template("index.html", name=None)


@app.route('/generation', methods=['GET', 'POST'])
def generation():
    if 'user' in session:
        name = session['user']
        all_questions = get_questions(name)
        if request.method == 'POST':
            filtres = request.form.getlist('filtres')
            questions = get_questions(name, filtres)
        else:
            filtres = []
            questions = all_questions
        liste_filtre = get_etiquettes(all_questions)
        for filtre_applique in filtres:
            liste_filtre.remove(filtre_applique)
        return render_template('generation.html', name=name, questions=questions, filtres=filtres, liste_filtre=liste_filtre)
    return render_template("index.html", name=None)


@app.route('/show', methods=['POST'])
def show():
    if 'user' in session:
        name = session['user']
        questions = get_questions(name)
        if request.method == 'POST':
            tabChoix = request.form.getlist('choisi')
            questions_a_generer = []
            for id in tabChoix:
                new_question = questions[int(id)]
                new_question = traiter_question(new_question)
                questions_a_generer.append(new_question)
        return render_template("SHOW.html", name=name, questions=questions_a_generer)
    return render_template("index.html", name=None)


@app.route('/creation-comptes-etudiants', methods=['GET', 'POST'])
def creation_comptes_etudiants():
   if 'user' in session:
      if request.method == 'POST':
         print(request.files)
         csv_file = request.files['csv_file']
         if csv_file.filename == '':
            return redirect(request.url)
         filename = csv_file.filename
         if filename.rsplit('.', 1)[1].lower() != 'csv':
            return redirect(request.url)
         csv_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
         creer_comptes_etudiant(filename)
         return redirect(url_for('index'))
      return render_template('creation_comptes_etudiants.html')
   return render_template("index.html", name = None)


################################################ ELEVES ################################################


@app.route("/login-etudiant", methods = ['POST', 'GET'])
def login_etudiant():
   if request.method == 'POST':
      data = get_etudiants()
      login = request.form['login']
      password = request.form['password']
      for etudiant in data:
         if try_login_etudiant(login, password, etudiant):
            session['etudiant'] = json.dumps(etudiant)
            print(session['etudiant'])
            return redirect(url_for('wait'))
      return render_template("login_etudiant.html", error = "Login ou mot de passe incorrect")
   else:
      return render_template("login_etudiant.html")
   
@app.route("/logoutEtd")
def logoutEtd():
   session.pop('etudiant', None)
   return redirect(url_for('index'))
   

@app.route("/changePass", methods = ['POST', 'GET'])
def changePass():
   if 'etudiant' in session:
      if request.method == 'POST':
         etudiant = json.loads(session['etudiant'])
         nouveau = request.form['nouveau']
         confirmer = request.form['confirmer']
         if nouveau == confirmer:
            data = get_etudiants()
            for etd in data:
               if etd['nom'] + "." + etd['prenom'] == etudiant['nom'] + "." + etudiant['prenom']:
                  etd['password'] = nouveau
                  write_data_etudiant(data) 
                  return redirect(url_for('wait'))
         else: 
            return render_template("changePass.html", newConfirmErr = 0) # tester cote client si newConfirmErr n'est pas none et pas 0
      else:
         return render_template("changePass.html")  


@app.route("/wait", methods = ['POST', 'GET'])
def wait():
   if 'etudiant' in session:
      etudiant = json.loads(session['etudiant'])
      return render_template("wait.html", etudiant = etudiant)
   return redirect(url_for('index'))



if __name__ == '__main__':
  app.run(host=host, port=port, debug=True)
