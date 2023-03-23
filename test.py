from hashlib import sha512
import json

with open('etudiants.json', 'r') as f:
    prof = json.load(f)

for p in prof:
    if p['password'] != '':
        p['password'] = sha512(p['password'].encode()).hexdigest()

with open('etudiants.json', 'w') as f:
    json.dump(prof, f, indent=4)