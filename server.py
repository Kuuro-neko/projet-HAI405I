from fonctions import *
from flask import Flask, render_template, redirect, url_for, request, session
from flask_socketio import SocketIO
import os

app = Flask(__name__)
app.secret_key = "super secret key"
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app)

host = '0.0.0.0'
port = 8888

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
        return render_template("questions.html", name=name, questions=questions, length=len(questions), message=request.args.get('message') or "")
    return render_template("index.html", name=None)


@app.route("/del_question/<int:id_question>")
def del_question(id_question):
    if 'user' in session:
        name = session['user']
        data = get_data()
        user_id = get_prof_id(name)
        data[user_id]['questions'].pop(id_question)
        write_data(data)
        return redirect(url_for('questions', message="Question supprimée avec succès"))
    return render_template("index.html", name=None)


@app.route("/traiter_type", methods = ['POST', 'GET'])
def traiter_type():
   if request.method == 'POST':
      type = request.form['type']
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
      type_question = request.form['type']
      question_id = create_unique_id(len(get_questions(session['user'])), session['user'])
      try:
         etiquettes = json.loads(request.form['etiquettes'])
      except:
         etiquettes = []
      if type_question == "ChoixMultiple":
         try:
            answers = json.loads(request.form['answers_json'])
         except:
            answers = []
      elif type_question == "Alphanumerique" :
         try:
            answers = request.form['rep']
         except:
            answers = ""
      user = session['user']
      question = {
         "type" : type_question,
         "text": text,
         "etiquettes" : etiquettes,
         "answers": answers,
         "titre": titre,
         "id": question_id
      }
      data[get_prof_id(user)]['questions'].append(question)
      majListeEtiquettes(etiquettes)
      write_data(data)
      return redirect(url_for('questions', message="Question créée avec succès"))
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
            type_question = request.form['type']
            if type_question == "ChoixMultiple":
                try:
                    answers = json.loads(request.form['answers_json'])
                except:
                    answers = []
            elif type_question == "Alphanumerique":
                try:
                    answers = request.form['rep']
                except:
                    answers = ""

            user = session['user']
            user_id = get_prof_id(user)
            id_question = int(request.form['id_question'])
            id_question_unique = request.form['id_question_unique']
            question = {
                "type": type_question,
                "text": text,
                "etiquettes": etiquettes,
                "answers": answers,
                "titre": titre,
                "id" : id_question_unique
            }

            data[user_id]['questions'][id_question] = question
            write_data(data)
            majListeEtiquettes(etiquettes)
            return redirect(url_for('questions', message="Question modifiée avec succès"))
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
            return render_template("changePass.html", error = "Vous avez la mémoire courte dis donc ! Veuillez réessayer.")
      else:
         return render_template("changePass.html")  


@app.route("/wait", methods = ['POST', 'GET'])
def wait():
   if 'etudiant' in session:
      etudiant = json.loads(session['etudiant'])
      return render_template("wait.html", etudiant = etudiant)
   return redirect(url_for('index'))

################################################ SOCKET ################################################
sequencesCourantes = []
"""
@app.route('/creer-sequence', methods=['POST'])
def creer_sequence():
    if 'user' in session:
        if request.method == 'POST':
            sequence = json.loads(request.form['sequence_json'])
            sequence = traiter_sequence(sequence)
            sequencesCourantes.append(sequence)
            return render_template("visualiser.html", question=sequence)
        else:

    return render_template("index.html", name=None)

@app.route('/sequence/<int:id_sequence>')
def sequence(id_sequence):
    if 'etudiant' in session:
        # affichage pour etudiant
        pass
    elif 'user' in session:
        # affichage pour prof
        pass
    return redirect(url_for('index'))

"""
if __name__ == '__main__':
  # Fonctions pour mettre à jour les bases de données qui n'ont pas suivi les màj du code
  generer_id_question()
  update_type_question()
  # Lancement du serveur
  socketio.run(app, host=host, port=port, debug=True)