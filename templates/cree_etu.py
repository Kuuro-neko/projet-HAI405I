import csv
import json

with open('csv_etudiants.csv', 'r') as f:
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
        data.append(row)

with open('etudiants.json', 'w') as f:
    json.dump(data, f, indent=4)