import re
import json
import datetime
import json,os
from scrapy.selector import Selector
import DBOperations
import getpass
import traceback
import datetime
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
import urllib2, urllib, requests
import logging

from celery import Celery
from celery import current_app
import time
from celery import signature
import ConfigParser
import requests

BROKER_URL = 'mongodb://localhost:27017/jobs'
celery = Celery('EOD_TASKS',broker=BROKER_URL)
#Loads settings for Backend to store results of jobs
celery.config_from_object('celeryconfig')

class PriceScrapper():
	priceClient = DBOperations.getMongoDBClient("ProductPrice")
	
	ProductMasterDBName = "Productmaster"
	PriceCollection = "allProducts"	
	def start_requests(self):
		AppProducts = self.getURLS()
		for items in AppProducts:
			allProductPriceDict = {}
			product_id = items[0]
			brand = items[1]
			productName = items[2]
			urlList = items[3]
			priceList = []
			update_time = datetime.datetime.now().strftime('%H:%M:%S')
			current_dict = DBOperations.getCollectionProduct( self.priceClient, self.PriceCollection, product_id)
			for url in urlList:
				# url = "http://www.amazon.in/dp/B00MPDR6PW"
				print url
				try:
					response = requests.get(url)
					priceDict = self.parse(response, current_dict)
					priceDict = self.checkForNonZeroPrice(priceDict, current_dict)
					priceList.append(priceDict)
				except Exception, err:
					print(traceback.format_exc()), "Error", url
				# self.parse( meta = {'outputFilePath': outputFilePath,'brand':brand,'productName':productName,'product_id':product_id, 'snapDealMatch':snapDealMatch, 'amazonMatch':amazonMatch})
			allProductPriceDict['product_id'] = product_id
			allProductPriceDict['brand'] = brand
			allProductPriceDict['productName'] = productName
			allProductPriceDict['priceList'] = priceList
			allProductPriceDict["update_time"] = update_time
			DBOperations.mongoSaveDocument(allProductPriceDict, self.PriceCollection, self.priceClient, 'product_id', False)

	def checkForNonZeroPrice(self, priceDict, current_dict):
		if priceDict['price'] == 0:
			print priceDict['price']
			for prices in current_dict['priceList']:
				if prices['website'] == priceDict['website']:
					priceDict['price'] = prices['price']					
					break
		return priceDict

	def parse(self,response,current_dict):
		discount = 0
		price = 0
		stock = 1
		priceDict = {}
		eComName = ""
		productUrl = response.url
		
		
		if ("flipkart" in response.url):
			flipKartScrapper = FlipKartScrapper()
			price, stock, discount, rating, shippingCharges = flipKartScrapper.getPrice(response.content)
			eComName = "flipkart"
			productUrl = response.url + "&affid=bazaarfun"
		if ("snapdeal" in response.url):
			snapdealScrapper = SnapDealScrapper()
			price, stock, discount, rating, shippingCharges = snapdealScrapper.getPrice(response.content)
			eComName = "snapdeal" 
			if '?' in response.url:
				productUrl = response.url + "&utm_source=aff_prog&utm_campaign=afts&offer_id=17&aff_id=50292"
			else:
				productUrl = response.url + "?utm_source=aff_prog&utm_campaign=afts&offer_id=17&aff_id=50292"
		if ("amazon" in response.url):
			amazonScrapper = AmazonScrapper()
			price, stock, discount,rating, shippingCharges = amazonScrapper.getPrice(response.content)
			eComName = "amazon"
			productUrl = response.url + "?tag=bazaarfunda-21"

		priceDict["price"] = price
		priceDict["productUrl"] = productUrl
		priceDict["stock"] = stock
		priceDict["discount"] = discount
		priceDict["rating"] = rating
		priceDict["shipping"] = shippingCharges
		priceDict["website"] = eComName
		return priceDict

	def getURLS(self):
		productMasterClient = DBOperations.getMongoDBClient(self.ProductMasterDBName)
		cursor = productMasterClient.allproducts.find()
		ProductList = []
		for row in cursor:
			product_id = row['product_id']
			brand = row['brand']
			product_name = row['product_name']
			product_urlList = row['product_urlList']
			ProductList.append([product_id,brand,product_name,product_urlList])
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
		
@celery.task
def celeryTask():
	scrapper = PriceScrapper()
	scrapper.start_requests()

if __name__ == '__main__':
	celeryTask()

