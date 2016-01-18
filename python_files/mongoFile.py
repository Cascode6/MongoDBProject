#!/usr/bin/env python

# referenced:
#https://docs.mongodb.org/getting-started/python/introduction/
#https://docs.mongodb.org/getting-started/python/client/
#https://docs.mongodb.org/getting-started/python/remove/
# https://docs.mongodb.org/manual/reference/method/db.collection.findAndModify/#db.collection.
# https://docs.mongodb.org/manual/reference/operator/update/#id1


import json


JSONFILE = 'buffalogrove.osm.json'

###MongoDB upload and queries



#upload
def import_to_mongo(data, db):
    db.buffalogrove.insert(data)
    return db

if __name__ == "__main__":

    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.buffalogrove
    result = db.buffalogrove.delete_many({})
    with open(JSONFILE, 'r') as f:
        data = json.load(f)
        import_to_mongo(data, db)
        print(db.buffalogrove.find().count())
        
    
   
        