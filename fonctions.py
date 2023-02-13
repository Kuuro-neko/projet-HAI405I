import csv
import json
import markdown2
from bs4 import BeautifulSoup
from hashlib import sha256
from server import UPLOAD_FOLDER

################################## Fonctions ##################################

class SequenceDeQuestions:
    def __init__(self, prof, questions):
        if type(questions) != list:
            self.questions = [].append(questions)
        else:
            self.questions = questions
        id_string = ""
        for question in self.questions:
            id_string += question["id"]
        self.id_unique = create_unique_id(get_prof_id(prof), id_string)
        self.prof = prof
        self.etudiants = []
        self.estTerminee = False
    
    def terminerSequence(self):
        self.estTerminee = True

    def ajouterEtudiant(self, etudiant):
        self.etudiants.append(etudiant)

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


def generer_id_question():
    """
    Genere un ID à toutes les questions de tous les utilisateurs si elles n'en ont pas
    A supprimer quand les ID fonctionneront parfaitement à la création et modification des questions et que toutes les questions auront un ID
    """
    data = get_data()
    for i in range(len(data)):
        for j in range(len(data[i]['questions'])):
            data[i]['questions'][j]['id'] = create_unique_id(j, data[i]["user"])
    write_data(data)


def update_type_question():
    # Met à jour le type des questions. Si c'est QCM Rempalcer par ChoixMultiple
    data = get_data()
    for i in range(len(data)):
        for j in range(len(data[i]['questions'])):
            if data[i]['questions'][j]['type'] == "QCM":
                data[i]['questions'][j]['type'] = "ChoixMultiple"
    write_data(data)

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
    if question["type"] == "ChoixMultiple":
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
      