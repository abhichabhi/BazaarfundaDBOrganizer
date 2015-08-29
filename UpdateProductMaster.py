from utils import DBOperations
from os import listdir
from os.path import isfile, join
import getpass, csv


ProductMasterDBName = "Productmaster"
ProductMasterFilePath = "/home/" + getpass.getuser() + "/BazaarfundaSrapperFiles/ProductMaster/"
def upDateProductmaster():
	ProductMasterClient = DBOperations.getMongoDBClient("Productmaster")
	fileList = getProductMasterFile(ProductMasterFilePath)
	for file in fileList:
		for row in __getListFromCSV(file):
			itemDict = {}
			product_id, category,brand,product_name, product_urlList, surl = getProductElementsFromMasterFileRow(row)
			itemDict['product_id'] = product_id
			itemDict['category'] = category
			itemDict['brand'] = brand
			itemDict['product_name'] = product_name
			itemDict['product_urlList'] = product_urlList
			itemDict['surl'] = surl
			DBOperations.mongoSaveDocument(itemDict,"allproducts", ProductMasterClient, 'product_id', True)

def getProductElementsFromMasterFileRow(row):
	product_id = row[0]
	category = row[1]
	brand = row[2]
	product_name = row[3]
	product_urlList = row[4:]
	product_urlList = list(set(product_urlList))
	try:
		product_urlList.remove("")
	except:
		pass
	surl = prepareSurl(category, product_name)
	return product_id, category,brand,product_name, product_urlList, surl

def prepareSurl(category, product_name):
	surl = category.strip() + " " + product_name.strip()
	surl = surl.strip()
	surl = surl.replace(" ","_")
	surl = surl.replace(".","")
	surl = surl.replace("(","_")
	surl = surl.replace(")","")
	surl = surl.replace("/","_")
	return surl

def getProductMasterFile(filePath):
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
	upDateProductmaster()