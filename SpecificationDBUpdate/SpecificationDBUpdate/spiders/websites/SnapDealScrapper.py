from scrapy.selector import HtmlXPathSelector
import urllib

class SnapDealScrapper:
	def downloadProductDetails(self,response, productName, brand, snapDealMatch):
		hxs = HtmlXPathSelector(text=response)
		tempDiv = hxs.select("//div[@class='detailssubbox']/table/tr").extract()
		# print tempDiv
		SpecTableDIV = hxs.select("//div[@class='detailssubbox']/table/tr/td/table[@class='product-spec']").extract()
		# print SpecTableDIV
		specDict = {}
		specDictVal = {}
		for specs in SpecTableDIV:
			specs = HtmlXPathSelector(text = specs)
			fields = specs.select("//tr").extract()			
			keyValDict = {}
			for field in fields:
				field = HtmlXPathSelector(text = field)
				keyVal = field.select("//td/text()").extract()
				if keyVal:
					key = keyVal[0]
					value = keyVal[1]
					print key, value
					try:
						snapDealVal = snapDealMatch[key]
					except:
						snapDealVal = []						
					print snapDealVal
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

		# if generalSpecFlag == 0:
		# 	specificationDict = {}
		# 	generalSpec = {}
		# 	generalSpec["Brand"] = brand
		# 	generalSpec["Model Name"] = productName
		# 	specificationDict["GENERAL FEATURES"] = generalSpec

		allSpecification['specification'] = specificationDict
		print allSpecification, "#####"
		return allSpecification


			
		#/img[contains(@class,"current")]/@src