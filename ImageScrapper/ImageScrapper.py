from os import listdir
from os.path import isfile, join
import getpass, csv, datetime
import requests, os, traceback
from websites import FlipKartScrapper
from websites import SnapDealScrapper
from websites import AmazonScrapper
import DBOperations
update_time = datetime.datetime.now().strftime('%Y-%m-%d')
outputFolderAll  = "/home/" + getpass.getuser() + "/BazaarfundaSrapperFiles/ProductImages/Allimages/"
outputFolderInc  = "/home/" + getpass.getuser() + "/BazaarfundaSrapperFiles/ProductImages/" + update_time + "/"
# os.makedirs(os.path.dirname(outputFolderAll))
if not os.path.exists(os.path.dirname(outputFolderInc)):
	os.makedirs(os.path.dirname(outputFolderInc))
ProductMasterFilePath = "/home/" + getpass.getuser() + "/BazaarfundaSrapperFiles/ProductMaster/MasterFile_Overall.csv"
ProductMasterDBName = "Productmaster"
PriceCollection = "allProducts"	
def start_requests():
		AppProducts = getURLS()
		for items in AppProducts:
			product_id = items[0]
			url = items[1]
			print product_id, url
			imageFileAll = outputFolderAll +  product_id + ".jpg"
			imageFileInc = outputFolderInc +  product_id + ".jpg"
			if not os.path.isfile(imageFileAll):
				try:
					response = requests.get(url,timeout=5)
					download_img(url,response, imageFileAll, imageFileInc)
				except Exception, err:
					print(traceback.format_exc()), "Error", 	
				

def download_img(url, response, imageFileAll, imageFileInc):

		#+ "/" + dateStr + "/" 
		if ("flipkart" in url):
			flipKartScrapper = FlipKartScrapper()
			flipKartScrapper.downloadProductList(response.content, imageFileInc, imageFileAll)
		if ("snapdeal" in url):
			snapdealScrapper = SnapDealScrapper()
			snapdealScrapper.downloadProductList(response.content, imageFileInc, imageFileAll)
		if ("amazon" in url):
			amazonScrapper = AmazonScrapper()
			amazonScrapper.downloadProductList(response.content, imageFileInc, imageFileAll)

def getURLS():
	productMasterClient = DBOperations.getMongoDBClient(ProductMasterDBName)
	cursor = productMasterClient.allproducts.find()
	ProductList = []
	for row in cursor:
		product_id = row['product_id']
		brand = row['brand']
		product_name = row['product_name']
		product_urlList = row['product_urlList']
		url = __getOrderedURL(product_urlList)
		ProductList.append([product_id,url])
	return ProductList
		
def __getOrderedURL(url_list):
		# print filter(lambda x: 'flipkart' in x, url_list)
		try:
			url = filter(lambda x: 'flipkart' in x, url_list)[0]
		except:
			try:
				url = filter(lambda x: 'snapdeal' in x, url_list)[0]
			except:
				try:
					url = filter(lambda x: 'amazon' in x, url_list)[0]
				except:
					url = None
		return url
if __name__ == '__main__':
	start_requests()