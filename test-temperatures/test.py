import json

a = {
    'name': 'Christophe',
    'age': 26
}
b = {
    'name': 'Ben',
    'age': 26
}

people = [a, b]

with open('test.json', 'w', encoding='utf-8') as outfile:
    outfile.write(json.dumps(people))
