#!/usr/bin/env python

# referenced:
# https://docs.mongodb.org/getting-started/python/query/
# https://docs.mongodb.org/manual/reference/operator/aggregation/sum/
# http://api.mongodb.org/python/current/tutorial.html
# https://docs.mongodb.org/manual/reference/operator/query/exists/
# https://docs.mongodb.org/manual/reference/method/js-collection/
# https://docs.mongodb.org/manual/reference/method/db.collection.update/#db.collection.update
# https://docs.mongodb.org/manual/reference/method/db.collection.update/#update-parameter

#queries


#basic info queries:

#returns the user who appears most:
def top_user():
    pipeline = [
        {"$group": {"_id":"$created.user", 
                    "count":{"$sum":1}}}, 
        {"$sort":{"count": -1}}, 
        {"$limit":1}
    ]
    return pipeline

#used in cleaning, would return all entries with name: Wheeling and a population field
def wheeling_pops():
    pipeline = [
        {'$match': {'name': 'Wheeling',
                   'population':{'$exists':1}}}
    ]
    return pipeline

#returns the total population of all townships represented in map dataset
def total_pop():
    pipeline = [
        {'$match': {'population':{'$exists': 1}}},
        {'$group': {'_id': '$name',
                    'total': {'$sum': '$population'}}},
        {'$group': {'_id': 'Total',
                    'totalpop': {'$sum': '$total'}}},
        ]
        
    return pipeline

#returns the township represented in map data with the highest population
def highest_pop():
    pipeline = [
        {'$match': {'population':{'$exists': 1}}},
        {'$group': {'_id': '$name', 
                    'total': {'$sum': '$population'}}},
        {'$sort': {'total': -1}},
        {'$limit':1}
    ]
    return pipeline
       
    
#returns number of documents with an address field
def has_address():
    pipeline = [
        {'$match': {'address': {'$exists': 1}}},
        
    ]    
    return pipeline
    
def multi_address():
    pipeline = [
        {'$match': {'address': {'$exists': 1}}},
        {}
    ]
    return pipeline

#runs .aggregate function on database collections
def aggregate(db, pipeline):
    result = [doc for doc in db.buffalogrove.aggregate(pipeline)]
    return result
    
if __name__ == "__main__":
    
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client.buffalogrove
    
    print("Total number of objects: ", db.buffalogrove.find().count())
    print("total number of nodes: ", db.buffalogrove.find({"type": "node"}).count())
    print("Total number of ways: ", db.buffalogrove.find({"type": "way"}).count())
    print("Number of schools: ", db.buffalogrove.find({"amenity":"school"}).count())
    
    with_address = db.buffalogrove.find({'address':{'$exists':True}})
    print('with address', with_address.count())
    
    with_street = db.buffalogrove.find({'address.street':{'$exists':True}})
    print("with street", with_street.count())
    
    street_housenum = db.buffalogrove.find({'$and': [
        {'address.street':{'$exists':True},
        'address.housenumber':{'$exists':True}}
        ]})
    print("with housenum", street_housenum.count())
    
    
    users = top_user()
    result_user = aggregate(db, users)
    print("Top user", result_user)
    
    pop_pipeline = highest_pop()
    result = aggregate(db, pop_pipeline)
    total_population = total_pop()
    resulttotal = aggregate(db, total_population)
    print("The township with the highest population is: ", result)
    print("The total population is: ", resulttotal)
    # wheelingresult = wheeling_pops()
    # print(aggregate(db, wheelingresult))
    
    
    