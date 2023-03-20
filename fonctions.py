import csv
import json
import markdown2
from bs4 import BeautifulSoup
from hashlib import sha256
from server import UPLOAD_FOLDER
import re

################################## Fonctions ##################################

class SequenceDeQuestions:
    nb_max_alphanumerique = 2

    def __init__(self, prof, questions):
        if type(questions) != list:
            self.questions = [].append(questions)
        else:
            self.questions = questions
        if len(questions) == 1:
            self.id_unique = questions[0]["id"]
        else:
            id_string = ""
            for question in self.questions:
                id_string += question["id"]
            self.id_unique = create_unique_id(get_prof_id(prof), id_string)
        self.prof = prof
        self.etudiants = []
        self.etudiants_qui_ont_repondu = []
        self.etat = 0
        self.reponsesOuvertes = True
        self.reponses = {}
        for question in questions:
            self.reponses[question["id"]] = {}
            if question["type"] == "ChoixMultiple":
                for reponse in question["answers"]:
                    self.reponses[question["id"]][reponse["text"]] = []
        
    
    def questionSuivante(self):
        print(f"Question suivante :\n Actuelle : {self.etat} / {len(self.questions)}, Suivante : {self.etat + 1} / {len(self.questions)}")
        if self.etat == len(self.questions) - 1:
            self.etat = -2
            self.archiverSequence()
            print("Sequence archivée")
            return False
        self.etudiants_qui_ont_repondu = []
        self.etat += 1
        self.ouvrirReponses()
        print(f"Passé à la question {self.etat}")
        return True

    def fermerReponses(self):
        self.reponsesOuvertes = False
    
    def ouvrirReponses(self):
        self.reponsesOuvertes = True

    def getQuestionCourante(self):
        return {"question" : self.questions[self.etat], "position" : self.etat + 1, "total" : len(self.questions)}
    
    def getAllQuestions(self):
        return self.questions
    
    def ajouterReponse(self, num_etu, reponse):
        if not self.reponsesOuvertes:
            raise Exception("Les réponses sont fermées.")
        if reponse == []:
            raise Exception("Aucune réponse n'a été donnée.")
        if num_etu in self.etudiants_qui_ont_repondu:
            raise Exception("Vous avez déjà répondu.")
        
        if self.questions[self.etat]["type"] == "ChoixMultiple":
            for i, reponse_possible in enumerate(self.questions[self.etat]["answers"]):
                if str(i) in reponse and num_etu not in self.reponses[self.questions[self.etat]["id"]][reponse_possible["text"]]:
                    self.reponses[self.questions[self.etat]["id"]][reponse_possible["text"]].append(num_etu)
            self.etudiants_qui_ont_repondu.append(num_etu)
            return True
        
        elif self.questions[self.etat]["type"] == "Alphanumerique":
            reponse = reponse[0]
            if "," in reponse:
                reponse = reponse.replace(",", ".")
            if reponse != "" and not re.match("^[0-9]+(\.[0-9]{0,2})?$", reponse):
                raise Exception("La réponse n'est pas un nombre avec au plus deux chiffres après la virgule.")
            
            if str(reponse) not in self.reponses[self.questions[self.etat]["id"]].keys():
                self.reponses[self.questions[self.etat]["id"]][str(reponse)] = []
                self.reponses[self.questions[self.etat]["id"]][str(reponse)].append(num_etu)
                self.etudiants_qui_ont_repondu.append(num_etu)
                return True
            elif num_etu not in self.reponses[self.questions[self.etat]["id"]][reponse]:
                self.reponses[self.questions[self.etat]["id"]][str(reponse)].append(num_etu)
                self.etudiants_qui_ont_repondu.append(num_etu)
                return True
        return False
    
    def getReponsesCourantes(self):
        return self.reponses[self.etat]
    
    def getNbReponsesCourantes(self):
        reponses = dict(self.reponses[self.questions[self.etat]["id"]])
        retour = {}
        retour["answers"] = {}
        total = 0
        if self.questions[self.etat]["type"] == "ChoixMultiple":
            
            for i, reponse in enumerate(reponses):
                retour["answers"][i] = len(reponses[reponse])
                total += len(reponses[reponse])
            retour["type"] = "ChoixMultiple"
        
        if self.questions[self.etat]["type"] == "Alphanumerique":
            alphanumerique = {}
            nb_rep_diff = len(reponses)
            for reponse in reponses:
                alphanumerique[reponse] = len(reponses[reponse])
                total += len(reponses[reponse])
            if nb_rep_diff > self.nb_max_alphanumerique:
                alphanumerique = dict(sorted(alphanumerique.items(), key=lambda item: item[1], reverse=True)[:self.nb_max_alphanumerique])
                alphanumerique["Autres"] = total - sum(alphanumerique.values())
            retour["type"] = "Alphanumerique"
            retour["answers"] = alphanumerique
        
        retour["total"] = total
        retour["rep_count"] = len(self.etudiants_qui_ont_repondu)
        print(retour)
        return retour
    
    def getCorrectionCourante(self):
        print("Correction : " + str(self.questions[self.etat]["answers"]))
        return self.questions[self.etat]["answers"]

    def getAllReponses(self):
        return self.reponses

    def setReponseEtudiant(self, etudiant, reponse):
        if re.match("^[a-zA-Z0-9]{8}$", etudiant) and self.reponsesOuvertes:
            self.reponses[self.questions[self.etat]["id"]][etudiant] = reponse
    
    def ajouterEtudiant(self, etudiant):
        print("Ajout de l'étudiant " + etudiant)
        print("Etudiants : " + str(self.etudiants))
        if etudiant not in self.etudiants:
            self.etudiants.append(etudiant)
        print("Etudiants : " + str(self.etudiants))

    def supprimerEtudiant(self, etudiant):
        self.etudiants.remove(etudiant)

    def getEtudiants(self):
        return self.etudiants

    def archiverSequence(self):
        with open("archive.json", "r") as fp:
            data = json.load(fp)
        try:
            archive_prof = data[self.prof]
        except KeyError:
            data[self.prof] = {}
            archive_prof = {}
        archive_prof[self.id_unique] = self.reponses
        data[self.prof] = archive_prof
        with open("archive.json", "w") as fp:
            json.dump(data, fp, indent=4)

    def __str__(self) -> str:
        return "SequenceDeQuestions de " + self.prof + " avec " + str(len(self.questions)) + " questions"

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
    html = markdown2.markdown(texte, extras=["newline", "fenced-code-blocks", "code-friendly", "mermaid"], safe_mode='escape')
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

def get_all_num_etu(json_data):
      num_etu = []
      for etu in json_data:
         num_etu.append(etu['numero_etudiant'])
      return num_etu

def creer_comptes_etudiant(filename):
   with open((UPLOAD_FOLDER + "/" + filename), 'r') as f:
      reader = csv.DictReader(f)
      rows = list(reader)

   try:
      with open('etudiants.json', 'r') as f:
         data = json.load(f)
   except:
      data = []

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

def get_archives(prof, id_sequence=None):
   """
   Retourne les séquences archivées d'un prof
   In : prof (str)
   In : id_sequence (str) (optionnel)
   Out : sequences (list (dict))
   """
   with open('archive.json', 'r') as fp:
      data = json.load(fp)
   try:
      if id_sequence == None:
        return data[prof]
      else:
        return data[prof][id_sequence]
   except:
      return []