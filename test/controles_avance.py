import copy
import json
from random import randint

with open('test.json') as f:
    data = json.load(f)

nb_controles = 88
nb_questions = 10
settings = {"Java" : (3, 5), "PHP" : (3, 4), "Python" : (2, 4)}
questions_dispo = {"Java" :[], "PHP" : [], "Python" : []}

for etiquette in settings:
    for question in data:
        if etiquette in question['etiquettes']:
            questions_dispo[etiquette].append(question)

print(f"Creation de controles avec Java: {settings['Java']}, PHP: {settings['PHP']}, Python: {settings['Python']}\n")

def generer_repartition(settings, nb_questions):
    result = {}
    for key in settings:
        result[key] = 0

    # Assigner le minimum de questions de chaque etiquette
    for key in settings:
        result[key] = settings[key][0]
        nb_questions -= settings[key][0]
        settings[key] = (0, settings[key][1] - settings[key][0])

    #  Vérifier que les minimum ne sont pas supérieurs au nombre de questions demandées
    if nb_questions < 0:
        raise ValueError("Trop de questions choisies pour créer ce controle")
    
    # Vérifier que le nombre de questions demandées est supérieur au nombre de questions disponibles
    nb_questions_dispo = 0
    for key in settings:
        nb_questions_dispo += settings[key][1]
    if nb_questions > nb_questions_dispo:
        raise ValueError("Pas assez de questions pour créer ce controle")

    # Assigner ce qui reste
    while nb_questions > 0:
        e = list(settings.keys())[randint(0, len(settings)-1)]
        if settings[e][1] > 0:
            result[e] += 1
            settings[e] = (settings[e][0], settings[e][1] - 1)
            nb_questions -= 1

    return result

def generer_controle(settings, questions, nb_questions):
        controle = []
        questions_dispo = dict(questions)

        # Randomise le nombre de questions de chaque etiquettes entre les bornes (min, max) fournies dans settings
        repartition = generer_repartition(settings, nb_questions)

        # Ajoute les questions au controle
        for etiquette in repartition:
            while repartition[etiquette] > 0:
                try:
                    index = randint(0, len(questions_dispo[etiquette])-1)
                    if questions_dispo[etiquette][index] not in controle:
                        controle.append(questions_dispo[etiquette][index])
                        questions_dispo[etiquette].pop(index)
                        repartition[etiquette] -= 1
                except ValueError as exc:
                    raise ValueError("Pas assez de questions pour créer un controle") from exc
        
        # Tri des controles par titre (ordre alphabétique) pour éviter les doublons
        controle.sort(key=lambda x: x['titre'])

        return controle
    

tous_controles = []
for i in range(0, nb_controles):
    
    controle = generer_controle(copy.deepcopy(settings), copy.deepcopy(questions_dispo), nb_questions)
    #Vérification que le nouveau controle ne contient pas les mêmes questions que les autres
    for controle_exist in tous_controles:
        if controle_exist == controle:
            print("Controle déjà existant")
            controle = generer_controle(copy.deepcopy(settings), copy.deepcopy(questions_dispo), nb_questions)
    tous_controles.append(controle)

    print(f"Controle {i+1}", end=" : {")
    for question in controle:
        print(question['text'], end="; ")
    print("}\n")





