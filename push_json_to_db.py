# Save JSON data to MongoDB
import pymongo
import json

# json_file = "test.json"
client = pymongo.MongoClient("localhost", 27017)
testDB = client.testDB
testCollection = client.testCollection


with open('test.json') as json_str:
    temps = json.load(json_str, encoding='utf-8')
    for temp in temps:
        testDB.temperatures.insert(temp)
