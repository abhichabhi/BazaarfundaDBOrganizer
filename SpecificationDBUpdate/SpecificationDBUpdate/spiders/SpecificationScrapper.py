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
import urllib2, urllib
import logging
class SpecificationScrapper():
	specificationClient = DBOperations.getMongoDBClient("ProductSpecification")
	name = "SpecificationScrapper"
	ProductMasterDBName = "Productmaster"
	SpecificationCollection = "allProducts"
	ProductMasterFilePath = "/home/" + getpass.getuser() + "/BazaarfundaSrapperFiles/ProductMaster/MasterFile_Overall.csv"
	
	snapDealMatchFileName = "SpecificationMatchSnapDeal.csv"
	amazonMatchFileName = "SpecificationMatchAmazon.csv"
	def start_requests(self):
		AppProducts = self.getURLS()
		snapDealMatch = self.createMatchDict(self.snapDealMatchFileName)
		amazonMatch = self.createMatchDict(self.amazonMatchFileName)
		#start_urls = ["http://www.snapdeal.com/product/blackberry-q10/1368483"]
		for items in AppProducts:
			product_id = items[0]
			brand = items[1]
			productName = items[2]
			url = items[3]

			# outputFilePath = self.outputFilePath + productName.replace("/","") + ".json"
			outputFilePath = ""
			if not DBOperations.isIdPresent(self.specificationClient, self.SpecificationCollection, "product_id", product_id):
				try:
					request = urllib2.Request(url)
					response = urllib.urlopen(url)
					# response = urllib2.urlopen(url)
					self.parse(response,url, brand, productName, product_id, snapDealMatch, amazonMatch)
				except Exception, err:
					print(traceback.format_exc()), "Error", url
				# self.parse( meta = {'outputFilePath': outputFilePath,'brand':brand,'productName':productName,'product_id':product_id, 'snapDealMatch':snapDealMatch, 'amazonMatch':amazonMatch})

	def parse(self,response,url, brand, productName, product_id, snapDealMatch, amazonMatch):
		productJSON = {}
		
		
		if ("flipkart" in url):
			flipKartScrapper = FlipKartScrapper()
			productJSON = flipKartScrapper.downloadProductDetails(response.read(), productName, brand)
		if ("snapdeal" in url):
			snapdealScrapper = SnapDealScrapper()
			productJSON = snapdealScrapper.downloadProductDetails(response.read(), productName, brand, snapDealMatch)
		if ("amazon" in url):
			amazonScrapper = AmazonScrapper()
			productJSON = amazonScrapper.downloadProductDetails(response.read(), productName, brand, amazonMatch)
		
		# self.saveOutPut(productJSON, outputFilePath)
		productJSON['product_id'] = product_id
		productJSON['spec_url'] = response.url
		DBOperations.mongoSaveDocument(productJSON,"allProducts", self.specificationClient, "product_id", False) 

	def getURLS(self):
		inputFile = self.ProductMasterFilePath
		fileObj = open(inputFile)
		ProductList = []
		reader = csv.reader(fileObj)

		for row in reader:
			product_id = row[0]
			brand = row[2]
			product_name = row[3]
			product_urlList = row[4:]
			product_urlList = list(set(product_urlList))
			try:
				product_urlList.remove("")
			except:
				pass
			url = self.__getOrderedURL(product_urlList)
			ProductList.append([product_id,brand,product_name, url])
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

