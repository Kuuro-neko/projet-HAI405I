import json

data = []
data.append()

with open('static/data.json', 'w') as fp:
    json.dump(data, fp, indent=4)

with open('static/data.json', 'r') as fp:
    data = json.load(fp)

print(data)