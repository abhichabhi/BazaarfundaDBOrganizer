from pymongo import MongoClient
def getMongoDBClient(dbName):
	mongo = MongoClient('localhost', 27017)[dbName]
	return mongo
def mongoSaveDocument(document,collection, client, identifier, versionControl=False):
	# print identifier
	collectionOriginal = client[collection]
	if versionControl==True:
		versioned_collection = collection + "v_1_0"
		collection_1_0 = client[versioned_collection]
		collection_1_0.remove()
		for record in collectionOriginal.find():
			collection_1_0.insert(record)
    	        mongoSaveDocument(document,collection, client, identifier, False)
        else:
    		collectionOriginal = client[collection]
    		priceDoc = collectionOriginal.find_one({identifier:document[identifier]})
    		if priceDoc:
    			document["_id"] = priceDoc["_id"]
    			collectionOriginal.save(document)
    		else:
    			collectionOriginal.insert(document)
    			

def getCollectionCursorObject(client, collection):
	return client[collection].find()

def isIdPresent(client, collection, idKey, idval):
	val = client[collection].find_one({idKey:idval})
	if val:
		return True
	return False

