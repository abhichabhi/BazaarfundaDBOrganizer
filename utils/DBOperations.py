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
    		if collectionOriginal.find_one({identifier:document[identifier]}):
    			pass
    		else:
			collectionOriginal.insert(document)

