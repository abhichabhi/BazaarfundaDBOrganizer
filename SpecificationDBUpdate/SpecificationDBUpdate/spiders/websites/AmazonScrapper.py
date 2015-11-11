from scrapy.selector import HtmlXPathSelector
import urllib

class AmazonScrapper:
	def downloadProductDetails(self,response, productName, brand, amazonMatch):
		hxs = HtmlXPathSelector(text=response)
		SpecTableDIV = hxs.select("//div[@class='pdTab']/table/tbody/tr").extract()
		specDict = {}
		specDictVal = {}
		for specs in SpecTableDIV:
			specs = HtmlXPathSelector(text = specs)
			field = specs.select("//td/text()").extract()
			keyVal = field

			keyValDict = {}

			if keyVal:
				key = keyVal[0]
				key = key.strip()
				value = keyVal[1]
				value = value.strip()
				print key, value
				try:
					snapDealVal = amazonMatch[key]
					print key, snapDealVal
				except:
					snapDealVal = []
				if snapDealVal:
					try:
						specDictVal = specDict[snapDealVal[0]]	
					except:
						specDictVal = {}
					if specDictVal:
						snapDealDictKey = snapDealVal[1]
						specDictVal[snapDealDictKey] = value
						specDict[snapDealVal[0]] = specDictVal
					else:
						specDictVal = {}
						snapDealDictKey = snapDealVal[1]
						specDictVal[snapDealDictKey] = value
						specDict[snapDealVal[0]] = specDictVal
		print specDict
		
		specificationDict = {}
		for specs in specDict:			
			specificationDict[specs] = specDict[specs]
			
		allSpecification = {}
		
		# generalSpecFlag = 0
		# try:
		# 	generalSpec = specs["GENERAL FEATURES"]
		# 	generalSpec["Brand"] = brand
		# 	generalSpec["Model Name"] = productName
		# 	specs["GENERAL FEATURES"] = generalSpec
		# 	generalSpecFlag = 1
		# except:
		# 	pass
		# 	# specDictVal = {}
		# 	# specDictVal["Brand"] = brand
		# 	# specDictVal["Model Name"] = productName
		# 	# specs["GENERAL FEATURES"] = specDictVal
		# 	# break
			
		# if generalSpecFlag == 0:
		# 	specificationDict = {}
		# 	generalSpec = {}
		# 	generalSpec["Brand"] = brand
		# 	generalSpec["Model Name"] = productName
		# 	specificationDict["GENERAL FEATURES"] = generalSpec
			

		allSpecification['specification'] = specificationDict
		return allSpecification


			
		#/img[contains(@class,"current")]/@src