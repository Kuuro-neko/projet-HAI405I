import copy
import json
from random import randint

with open('test.json') as f:
    data = json.load(f)

nb_controles = 88
settings = {"Java" :5 , "PHP" : 3, "Python" : 3}
questions_dispo = {"Java" :[], "PHP" : [], "Python" : []}

for etiquette in settings:
    for question in data:
        if etiquette in question['etiquettes']:
            questions_dispo[etiquette].append(question)

print(f"Creation de controles avec Java: {settings['Java']}, PHP: {settings['PHP']}, Python: {settings['Python']}\n")

def generer_controle(settings, questions):
    try:
        controle = []
        questions_dispo = dict(questions)

        for etiquette in settings:
            while settings[etiquette] > 0:
                index = randint(0, len(questions_dispo[etiquette])-1)
                if questions_dispo[etiquette][index] not in controle:
                    controle.append(questions_dispo[etiquette][index])
                    questions_dispo[etiquette].pop(index)
                    settings[etiquette] -= 1
        
        # Tri des controles par titre
        controle.sort(key=lambda x: x['titre'])

        return controle
    except ValueError as exc:
        raise ValueError("Pas assez de questions pour créer un controle") from exc

tous_controles = []
for i in range(0, nb_controles):

    
    controle = generer_controle(settings.copy(), copy.deepcopy(questions_dispo))
    #Vérification que le nouveau controle ne contient pas les mêmes questions que les autres
    for controle_exist in tous_controles:
        if controle_exist == controle:
            print("Controle déjà existant")
            controle = generer_controle(settings.copy(), copy.deepcopy(questions_dispo))
    tous_controles.append(controle)
    
    print(f"Controle {i+1}", end=" : {")
    for question in controle:
        print(question['text'], end="; ")
    print("}\n")




