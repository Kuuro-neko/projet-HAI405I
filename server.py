from fonctions import *
from flask import Flask, render_template, redirect, url_for, request, session
from flask_socketio import *

import os


app = Flask(__name__)
app.secret_key = "super secret key"
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app)

host = '127.0.0.1'
port = 8888
sequencesCourantes = {}

############################################### ROUTES ###############################################


@app.route("/")
@app.route("/index")
def index():
    try:
        name=None
        if session['user_type'] == "prof":
            name = session['user']
        elif session['user_type'] == "etudiant":
            jsonEtu = json.loads(session['user'])
            name = jsonEtu['nom'] + " " + jsonEtu['prenom']
        return render_template("index.html", name=name)
    except KeyError:
        return render_template("index.html", name=None)


@app.route("/logout")
def logout():
    session.pop('user', None)
    session.pop('user_type', None)
    return redirect(url_for('index'))


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = get_data()
        login = request.form['login']
        password = request.form['password']
        for users in data:
            if users['user'] == login and users['password'] == password:
                session['user'] = login
                session['user_type'] = "prof"
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
    try:
        if session['user_type'] == "prof":  
            name = session['user']
            try:
                questions = get_questions(name)
            except:
                session.pop('user', None)
                return redirect(url_for('index'))
            return render_template("questions.html", name=name, questions=questions, length=len(questions), message=request.args.get('message') or "")
        return render_template("index.html", name=None, error="Vous devez être connecté")
    except KeyError:
        return render_template("index.html", name=None, error="Vous devez être connecté")


@app.route("/del_question/<int:id_question>")
def del_question(id_question):
    try:
        if session['user_type'] == "prof":
            name = session['user']
            data = get_data()
            user_id = get_prof_id(name)
            data[user_id]['questions'].pop(id_question)
            write_data(data)
            return redirect(url_for('questions', message="Question supprimée avec succès"))
        return render_template("index.html", name=None, error="Vous devez être connecté")
    except KeyError:
        return render_template("index.html", name=None, error="Vous devez être connecté")


@app.route("/traiter_type", methods=['POST', 'GET'])
def traiter_type():
    if request.method == 'POST':
        type = request.form['type']
        etiquettes_existantes = get_etiquettes()
        return render_template("add_question.html", etiquettes_existantes=etiquettes_existantes, type=type)
    else:
        return render_template("choixType.html")


@app.route("/add_question", methods=['POST', 'GET'])
def add_question():
    try:
        if session['user_type'] == "prof":
            if request.method == 'POST':
                data = get_data()
                text = request.form['text']
                titre = request.form['titre']
                type_question = request.form['type']
                question_id = create_unique_id(
                    len(get_questions(session['user'])), session['user'])
                try:
                    etiquettes = json.loads(request.form['etiquettes'])
                except:
                    etiquettes = []
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
                question = {
                    "type": type_question,
                    "text": text,
                    "etiquettes": etiquettes,
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
                return render_template("add_question.html", etiquettes_existantes=etiquettes_existantes)
        else:
            return render_template("index.html", name=None, error="Vous devez être connecté")
    except KeyError:
        return render_template("index.html", name=None, error="Vous devez être connecté")


@app.route("/edit_question/<int:id_question>", methods=['POST', 'GET'])
def edit_question(id_question):
    try:
        if session['user_type'] == "prof":
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
                    "id": id_question_unique
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
        return render_template("index.html", name=None, error="Vous devez être connecté")
    except KeyError:
        return render_template("index.html", name=None, error="Vous devez être connecté")


@app.route("/visualiser/<int:id_question>")
def visualiser(id_question, question=None):
    try:
        if session['user_type'] == "prof":
            name = session['user']
            if question == None:
                question = get_questions(name)[id_question]
                question = traiter_question(question)
            return render_template("visualiser.html", question=question)
        return render_template("index.html", name=None, error="Vous devez être connecté")
    except KeyError:
        return render_template("index.html", name=None, error="Vous devez être connecté")


@app.route("/visualiser_temp", methods=['POST'])
def visualiser_temp():
    try:
        if session['user_type'] == "prof" and request.method == 'POST':
            question = json.loads(request.form['question_json'])
            question = traiter_question(question)
            return render_template("visualiser.html", question=question)
        return render_template("index.html", name=None, error="Vous devez être connecté")
    except KeyError:
        return render_template("index.html", name=None, error="Vous devez être connecté")


@app.route('/generation', methods=['GET', 'POST'])
def generation():
    try:
        if session['user_type'] == "prof":
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
        return render_template("index.html", name=None, error="Vous devez être connecté en tant que professeur")
    except KeyError:
        return render_template("index.html", name=None, error="Vous devez être connecté en tant que professeur")


@app.route('/show', methods=['POST'])
def show():
    try:
        if session['user_type'] == "prof":
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
        return render_template("index.html", name=None, error="Vous devez être connecté en tant que professeur")
    except KeyError:
        return render_template("index.html", name=None, error="Vous devez être connecté en tant que professeur")


@app.route('/creation-comptes-etudiants', methods=['GET', 'POST'])
def creation_comptes_etudiants():
    try:
        if session['user_type'] == "prof":
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
        return render_template("index.html", name=None, error="Vous devez être connecté en tant que professeur pour accéder à cette page")
    except KeyError:
        return render_template("index.html", name=None, error="Vous devez être connecté en tant que professeur pour accéder à cette page")


@app.route('/sequence', methods=['GET', 'POST'])
def sequence():
    try:
        print(session['user_type'])
        print(session['user'])
        if session['user_type'] == "prof":
            prof = session['user']
            questions = get_questions(prof)
            if request.method == 'POST':
                tabChoix = request.form.getlist('choisi')
                questions_sequence = []
                for id in tabChoix:
                    questions_sequence.append(traiter_question(questions[int(id)]))
                print(questions_sequence)
                sequence = SequenceDeQuestions(prof, questions_sequence)
                sequencesCourantes[sequence.id_unique] = sequence
                return redirect(url_for('live', id_sequence=sequence.id_unique))
            return render_template('diffusion.html', questions=questions)
        return render_template("index.html", name=None, error="Vous devez être connecté en tant que professeur pour accéder à cette page")
    except KeyError:
        return render_template("index.html", name=None, error="Vous devez être connecté en tant que professeur pour accéder à cette page 1")


################################################ ELEVES ################################################


@app.route("/login-etudiant", methods=['POST', 'GET'])
def login_etudiant():
    if request.method == 'POST':
        data = get_etudiants()
        login = request.form['login']
        password = request.form['password']
        for etudiant in data:
            if try_login_etudiant(login, password, etudiant):
                session['user'] = json.dumps(etudiant)
                session['user_type'] = "etudiant"
                return redirect(url_for('wait'))
        return render_template("login_etudiant.html", error="Login ou mot de passe incorrect")
    else:
        return render_template("login_etudiant.html")


@app.route("/logoutEtd")
def logoutEtd():
    session.pop('user_type', None)
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route("/changePass", methods=['POST', 'GET'])
def changePass():
    try:
        if session['user_type'] == "etudiant":
            if request.method == 'POST':
                etudiant = json.loads(session['user'])
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
                    return render_template("changePass.html", error="Vous avez la mémoire courte dis donc ! Veuillez réessayer.")
            else:
                return render_template("changePass.html")
        else:
            return render_template("index.html", name=None, error="Vous devez être connecté")
    except Exception:
        return render_template("index.html", name=None, error="Vous devez être connecté")


@app.route("/wait")
def wait():
    try:
        if session['user_type'] == "etudiant":
            print(json.loads(session['user']))
            return render_template("wait.html", etudiant=json.loads(session['user']))
        return render_template("index.html", name=None, error="Vous devez être connecté en tant qu'étudiant pour accéder à cette page")
    except Exception:
        return render_template("index.html", name=None, error="Vous devez être connecté en tant qu'étudiant pour accéder à cette page")

################################################ SOCKET ################################################


@app.route('/live/<string:id_sequence>', methods=['GET'])
def live(id_sequence):
    for sequence in sequencesCourantes.values():
        print(sequence)
    if id_sequence not in sequencesCourantes:
        return redirect(url_for('index', error="Cette séquence n'existe pas."))
    sequence = sequencesCourantes[id_sequence]
    print(len(sequence.getAllQuestions()))
    if session['user_type'] == "etudiant":
        etudiant = json.loads(session['user'])
        return render_template('live_etudiant.html', etudiant=etudiant, sequence=sequence)
    elif session['user_type'] == "prof":
        return render_template('live_prof.html', etudiant=False, sequence=sequence, questions=sequence.getAllQuestions(), length=len(sequence.getAllQuestions()))
    else :
        return render_template("index.html", name=None, error="Vous devez être connecté pour accéder à cette page")


@socketio.on('connect-prof')
def connect_prof(data):
    sid = data["sequence_id"]
    print(f"Prof connecté à la séquence {sid}")
    join_room(sid)
    emit('refresh-connects', {'connects': len(sequencesCourantes[sid].getEtudiants())}, room=sid)
    question = dict(sequencesCourantes[sid].getQuestionCourante())
    emit('display-question', question, room=sid) # Envoie la question courante au prof
    emit('refresh-answers', sequencesCourantes[sid].getNbReponsesCourantes(), room=sid) # Rafraichissement des stats pour le prof

@socketio.on('connect-etu')
def connect_etu(data):
    sid = data["sequence_id"]
    num = data["numero_etudiant"]
    sequencesCourantes[sid].ajouterEtudiant(num)
    print(f"Etudiant {num} connecté à la séquence {sid}")
    question = dict(sequencesCourantes[sid].getQuestionCourante())
    for answer in question["question"]["answers"]:
        answer["isCorrect"] = "Bien essayé :)"
    emit('display-question', question) # Envoie la question à l'étudiant
    emit('connect-etu', {'count': len(sequencesCourantes[sid].getEtudiants())}, room=sid) # Rafraichissement du nombre d'étudiants connectés côté prof

@socketio.on('send-answer')
def send_answer(data):
    print(data)
    print("Réponse reçue")
    sid = data["sequence_id"]
    num = data["numero_etudiant"]
    answer = data["answers"]
    confirm = sequencesCourantes[sid].ajouterReponse(num, answer)
    emit('confirm-answer', {'confirm': confirm}) # Message de confirmation pour le client
    emit('refresh-answers', sequencesCourantes[sid].getNbReponsesCourantes(), room=sid) # Rafraichissement des stats pour le prof


@socketio.on('stop-answers')
def stop_answers(data):
    sid = data["sequence_id"]
    sequencesCourantes[sid].fermerReponses()
    emit('stop-answers', broadcast=True)


@socketio.on('next-question')
def next_question(data):
    sid = data["sequence_id"]
    sequencesCourantes[sid].questionSuivante()
    question = dict(sequencesCourantes[sid].getQuestionCourante())
    print(question)
    emit('display-question', question, broadcast=True)

"""
Socket pour envoyer les stats à chaque réponse d'un étudiant
    - 1 socket emit côté eleve
    - 1 socket onmessage côté prof
    - 1 socket ici
Socket pour stopper les réponses + js côté client prof pour afficher la réponse + blocage des réponses côté client eleve :
   - 1 bouton + socket sur la page du prof pour stopper les réponses
   - 1 socket côté eleve pour bloquer les réponses
   - 1 socket ici pour bloquer les réponses au niveau de la classe
Socket pour passer à la question suivante + bouton côté client prof + rafraichir les lcients eleve
   - 1 socket onmessage côté eleve
   - 1 socket emit + bouton côté prof
   - 1 socket ici
Et tout le côté client (voir diapo)
"""

if __name__ == '__main__':
    # Fonctions pour mettre à jour les bases de données qui n'ont pas suivi les màj du code
    generer_id_question()
    update_type_question()
    # Lancement du serveur
    socketio.run(app, host=host, port=port, debug=True)