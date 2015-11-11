import sys, traceback, os, csv
from pymongo import MongoClient
from DBOperations import *
scoreClient = getMongoDBClient("Productratings")
scoreCollection = "scores"

def calculateScore(category):
	destFile = "/home/stratdecider/AdminRandomFiles/AllScores/"+ category +"_AllScore.csv"
	mongoPrice = MongoClient('localhost', 27017)["ProductPrice"]
	mongoProdmaster = MongoClient('localhost', 27017)["Productmaster"]
	mongoRating = MongoClient('localhost', 27017)["Productratings"]['keywords']
	mongoCategory = MongoClient('localhost', 27017)["categoryDB"]['catType'].find_one({'type':category})
	allCatProducts = mongoProdmaster.allproducts.find({'category':category})
	csvRow =  ["product_id", "min_price", "price_factor", "overallRating", 'overallBuzz', "overallFinalRating"]
	writeToFile(csvRow,destFile)
	buzzDict = mongoCategory['buzzFactor']
	defaultKeyWeight = mongoCategory['defaultKeyWeight']

	for product in allCatProducts:
		product_id  = product['product_id']
		try:			
			price_factor, min_price = getProductPricefactor(product_id,category, mongoPrice, mongoCategory['priceFactor'])			
		except Exception, err:
			price_factor, min_price = 1, None
			print(traceback.format_exc()), "Error", "error with product ", product_id
		try:			
			allKeywordsBuzz = getBuzzFactorForAllKeywords(buzzDict,mongoRating, product_id, category, defaultKeyWeight)			
		except Exception, err:
			overallRating, overallBuzz, overallCount, afterKeywordScore = None, None, None, None
			print(traceback.format_exc()), "Error", "error with product ", product_id

		
		for key in allKeywordsBuzz:
			rating_score = allKeywordsBuzz[key]['score']*14 + allKeywordsBuzz[key]['buzzScore'] + price_factor
			allKeywordsBuzz[key]['finalRating'] = rating_score
		allKeywordsBuzz['product_id'] = product_id
		allKeywordsBuzz['category'] = category
		print product_id, min_price, price_factor, allKeywordsBuzz['overall']
		scoreDict = {}
		scoreDict['score'] = allKeywordsBuzz
		scoreDict['product_id'] = product_id
		scoreDict['category'] = category
		mongoSaveDocument(scoreDict,scoreCollection, scoreClient, 'product_id', False)
		csvRow = [product_id, min_price, price_factor, allKeywordsBuzz['overall']['score'], allKeywordsBuzz['overall']['buzzScore'],allKeywordsBuzz['overall']['finalRating']]
		writeToFile(csvRow,destFile)
		

def getBuzzFactorForAllKeywords(buzzDict,mongoRating, product_id, category, defaultKeyWeight):
	allKeywords = mongoRating.find({'product_id':product_id})
	overallRating = 0
	overallBuzz = 0
	overallCount = 0
	allKeywordScore = 0
	afterKeywordScore = 0
	allKeywordsBuzz = {}
	for keywordDict in allKeywords:
		keywordBuzzDict = {}
		try:
			keyword = keywordDict['keyword']
			if keyword != 'overall':
				keywordScore = defaultKeyWeight[keyword]
				afterKeywordScore = afterKeywordScore + keywordScore*float(keywordDict['rating'])
				print keyword, keywordScore, keywordDict['rating']
				keywordBuzzDict['score'] = float(keywordDict['rating'])

				keywordBuzzDict['buzzScore'] = getFactor(float(keywordDict['rating']), buzzDict[keyword])
			allKeywordsBuzz[keyword] = keywordBuzzDict
		except:
			keywordBuzzDict['score'] = 0.0

			keywordBuzzDict['buzzScore'] = 0.0
	afterKeywordScoreBuzz = getFactor(afterKeywordScore, buzzDict['overall'])
	allKeywordsBuzz['overall'] = {'score':afterKeywordScore, 'buzzScore': afterKeywordScoreBuzz }
	print "######################"
	print afterKeywordScore, buzzDict['overall']
	print allKeywordsBuzz
	return allKeywordsBuzz

	# buzzKeywordDict = {}
	# for keywordDict in allKeywords:
	# 	keyword = keywordDict['keyword']
	# 	try:
	# 		buzzVal = buzzDict[keyword]
	# 		try:
	# 			pos = float(keywordDict['positive'])
	# 		except:
	# 			pos= 0.0
	# 		try:
	# 			neg = float(keywordDict['negative'])
	# 		except:
	# 			neg= 0.0
	# 		try:
	# 			rating = float(keywordDict['rating'])
	# 		except:
	# 			rating = .5
	# 		# print float(keywordDict['positive']) + float(keywordDict['negative'])
	# 		buzzFactor = (pos + neg)*0.5*rating/buzzVal
	# 		buzzFactor = buzzFactor + .5
	# 		if keyword == 'overall':
	# 			print buzzFactor, rating, pos, neg
	# 	except Exception, err:
	# 		print(traceback.format_exc()), "Error", "error with product ", product_id, keyword
	# 		buzzFactor = 0.5
	# 	buzzKeywordDict[keyword] = buzzFactor
	# return buzzKeywordDict

def getProductPricefactor(product_id,category, mongoPrice,priceFactor):
	try:
		product_price = mongoPrice.allProducts.find_one({'product_id':product_id})
		priceList = product_price['priceList']
	except:
		priceList = []
	
	min_priceDict = {}
	if priceList:
		min_price = 100000000		
		for price in priceList:
			if price['price'] < min_price:
				min_priceDict = price			
	min_price = min_priceDict['price']
	if min_price:
		return getFactor(min_price, priceFactor), min_price
	return 1, min_price

def getFactor(value, type_dict):

	for factor in type_dict:
		fRange = factor['range']
		if 	fRange[0] < value < fRange[1]:
			return factor['factor']
	return 1

def writeToFile(row,destFile):
		if not os.path.exists(os.path.dirname(destFile)):
			os.makedirs(os.path.dirname(destFile))
			# with open(destFile, 'a') as outcsv:
			# 	writer = csv.writer(outcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
			# 	writer.writerow(self.header)
            #configure writer to write standart csv file
                
		with open(destFile, 'a') as outcsv:
			
			writer = csv.writer(outcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
			writer.writerow(row)
            # with open(filename, 'a') as outcsv:
            # #configure writer to write standart csv file
            #     writer = csv.writer(outcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')           
            #     writer.writerow(self.amazon_HeadingList)



if __name__ == '__main__':
	category = None
	try:
		category = sys.argv[1]								
	except :
		print "Listen you dumb fuck. The command is : python PullSpecificationFilter.py mobile"	
	if category:
		calculateScore(category)
