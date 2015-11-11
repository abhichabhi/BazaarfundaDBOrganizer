import DBOperations
from os import listdir
from os.path import isfile, join
import getpass, csv, datetime


ProductRecommendationDBName = "ProductRecommendation"
ProductRecommendationPath = "/home/" + getpass.getuser() + "/BazaarfundaSrapperFiles/Recommendation/allComp/"

def upDateProductRecommendation():
	ProductRecommendationClient = DBOperations.getMongoDBClient(ProductRecommendationDBName)
	fileList = getProductRecommendationFile(ProductRecommendationPath)
	for file in fileList:
		for row in __getListFromCSV(file):
			itemDict = {}
			product_id, category, recommendedProducts = getProductElementsFromMasterFileRow(row)
			itemDict['product_id'] = product_id
			itemDict['category'] = category
			itemDict['recommendedProducts'] = recommendedProducts
			if recommendedProducts != []:
				DBOperations.mongoSaveDocument(itemDict,"allComp", ProductRecommendationClient, 'product_id', False)

def getProductElementsFromMasterFileRow(row):
	product_id = row[0]
	category = row[1]
	recommendedProducts = row[2:]
	return product_id, category, recommendedProducts

def prepareSurl(category, product_name):
	surl = category.strip() + " " + product_name.strip()
	surl = surl.strip()
	surl = surl.replace(" ","_")
	surl = surl.replace(".","")
	surl = surl.replace("(","_")
	surl = surl.replace(")","")
	surl = surl.replace("/","_")
	surl = surl.replace("&","_")
	return surl

def getProductRecommendationFile(filePath):
	onlyfiles = [ f for f in listdir(filePath) if isfile(join(filePath,f)) ]
	fileList = []
	for file in onlyfiles:
		if "readme" in file.lower():
			pass
		else:
			fileList.append(filePath + file)
	return fileList

def __getListFromCSV(filename):
    profileLinks = []
    with open(filename, 'r') as f:
        readColumns = (csv.reader(f, delimiter=','))
        iter = 0
        for row in readColumns:
            profileLinks.append(row)
        return profileLinks

if __name__ == '__main__':
	upDateProductRecommendation()