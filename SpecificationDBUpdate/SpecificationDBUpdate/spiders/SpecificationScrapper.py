import re
import json
import datetime
import json,os
from scrapy.selector import Selector
import DBOperations
import getpass
import traceback
try:
	from scrapy.spider import Spider
except:
	from scrapy.spider import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.contrib.spiders import CrawlSpider
from scrapy.http.request import Request
from websites import FlipKartScrapper
from websites import SnapDealScrapper
from websites import AmazonScrapper
import os.path
import csv
import requests
import logging
class SpecificationScrapper():
	specificationClient = DBOperations.getMongoDBClient("ProductSpecification")
	
	ProductMasterDBName = "Productmaster"
	SpecificationCollection = "allproducts"
	ProductMasterFilePath = "/home/" + getpass.getuser() + "/BazaarfundaSrapperFiles/ProductMaster/MasterFile_Overall.csv"
	
	def start_requests(self):
		AppProducts = self.getURLS()
		allCategory = [category[4] for category in AppProducts]

		allCategory = list(set(allCategory))

		snapDealSpecificationMatchDict = {}
		amazonSpecificationMatchDict = {}

		for cat in allCategory:
			if cat != "Category" and cat != '':
				snapDealSpecificationMatchDict[cat] = self.createMatchDict('./SpecificationMatch/' + cat + '/SpecificationMatchSnapDeal.csv')
				amazonSpecificationMatchDict[cat] = self.createMatchDict('./SpecificationMatch/' + cat + '/SpecificationMatchAmazon.csv')
		
		for items in AppProducts:
			product_id = items[0]
			brand = items[1]
			productName = items[2]
			url = items[3]
			category = items[4]
			try:
				snapDealMatch = snapDealSpecificationMatchDict[category]
				amazonMatch = amazonSpecificationMatchDict[category]
				# outputFilePath = self.outputFilePath + productName.replace("/","") + ".json"
				outputFilePath = ""
				print product_id
				if not DBOperations.isIdPresent(self.specificationClient, self.SpecificationCollection, "product_id", product_id):
					try:
						response = requests.get(url, timeout=5)
						self.parse(response,url, brand, productName, product_id, snapDealMatch, amazonMatch)
					except Exception, err:
						print(traceback.format_exc()), "Error", url, items
					# self.parse( meta = {'outputFilePath': outputFilePath,'brand':brand,'productName':productName,'product_id':product_id, 'snapDealMatch':snapDealMatch, 'amazonMatch':amazonMatch})
			except Exception, err:
				print  (traceback.format_exc())

	def parse(self,response,url, brand, productName, product_id, snapDealMatch, amazonMatch):
		productJSON = {}
		if ("flipkart" in url):
			flipKartScrapper = FlipKartScrapper()
			productJSON = flipKartScrapper.downloadProductDetails(response.content, productName, brand)
		if ("snapdeal" in url):
			snapdealScrapper = SnapDealScrapper()
			productJSON = snapdealScrapper.downloadProductDetails(response.content, productName, brand, snapDealMatch)
		if ("amazon" in url):
			amazonScrapper = AmazonScrapper()
			productJSON = amazonScrapper.downloadProductDetails(response.content, productName, brand, amazonMatch)
		
		# self.saveOutPut(productJSON, outputFilePath)
		productJSON['product_id'] = product_id
		productJSON['spec_url'] = response.url
		# print productJSON
		DBOperations.mongoSaveDocument(productJSON,self.SpecificationCollection, self.specificationClient, "product_id", False) 

	def getURLS(self):
		inputFile = self.ProductMasterFilePath
		fileObj = open(inputFile)
		ProductList = []
		reader = csv.reader(fileObj)
		DBMasterClient = DBOperations.getMongoDBClient(self.ProductMasterDBName)
		masterCursor = DBOperations.getCollectionCursorObject(DBMasterClient, "allproducts")
		for items in masterCursor:
			product_id = items['product_id']
			brand = items['brand']
			category = items['category']
			product_name = items['product_name']
			product_urlList = items['product_urlList']
			url = self.__getOrderedURL(product_urlList)
			ProductList.append([product_id,brand,product_name, url, category])		
		return ProductList

	def __getOrderedURL(self, url_list):
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

	def saveOutPut(self,productJSON, filePath):
		if not os.path.exists(os.path.dirname(filePath)):
			os.makedirs(os.path.dirname(filePath))
		with open(filePath, 'a+') as fManager:
			json.dump(productJSON, fManager, sort_keys = True, indent = 4, ensure_ascii=False)

	def createMatchDict(self, fileName):
		fileObj = open(fileName)
		ProductList = []
		MatchDict = {}
		reader = csv.reader(fileObj)
		for row in reader:
			if row[2]:
				try:
					MatchDict[row[0]] = [row[1],row[2]]
				except:
					print "error in matching with Flipkart Specification"
					print row[0]
		return MatchDict

if __name__ == '__main__':
	scrapper = SpecificationScrapper()
	scrapper.start_requests()

