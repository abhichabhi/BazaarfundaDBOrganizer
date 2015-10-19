from scrapy.selector import HtmlXPathSelector
from decimal import Decimal
import urllib, traceback

class AmazonScrapper:
	def getPrice(self,response):
		hxs = HtmlXPathSelector(text=response)
		stock = 1
		price =0
		priceText = hxs.select('//span[@id="priceblock_ourprice"]/text()').extract()
		stockDiv = hxs.select('//div[@id="availability"]/span/text()').extract()

		if not priceText:
			priceText = hxs.select('//span[@class="a-color-price"]/text()').extract()
		try:
			priceText = priceText[0]

			priceText = priceText.strip()
			priceText = priceText.replace(",","")

			priceText = priceText.replace("Rs ","")

			price = Decimal(priceText)
			price = int(price)

			
		except:
			priceText = hxs.select('//span[@id="priceblock_saleprice"]/text()').extract()
			try:
				priceText = priceText[0]

				priceText = priceText.strip()
				priceText = priceText.replace(",","")

				priceText = priceText.replace("Rs ","")

				price = Decimal(priceText)
				price = int(price)
			except:
				price= 0
				stock = 0

		try:
			stockDiv = stockDiv[0].strip()
			
		except:
			stockDiv = ''

		if "Currently unavailable" in stockDiv:
			stock = 0
		if "Out" in stockDiv:
			stock = 0
		try:
			discount = hxs.select('//tr[contains(@id,"regularprice_savings")]/td/text()').extract()
			discount = "".join(discount).strip()
			discount = self.__extract_between(discount,"(",")",1)
			discount = discount.replace("%","")
			discount = int(discount)
		except:
			discount = 0

		try:
			rating = hxs.select('//span[@id="acrPopover"]/@title').extract()[0]
			
			rating = rating.replace(' out of 5 stars','')
			rating = float(rating)
		except:
			rating = None

		try:
			shippingCharges = hxs.select('//span[contains(@id,"dealprice_shippingmessage")]/span/b/text()').extract()
			if not shippingCharges:
				shippingCharges = hxs.select('//span[contains(@id,"ourprice_shippingmessage")]/span/b/text()').extract()
			shippingCharges = "".join(shippingCharges)
			if 'FREE' in shippingCharges:
				shippingCharges = 0

		except Exception, err:
			print(traceback.format_exc()), "Error"
			if price > 499 or price == 0:
				shippingCharges = 0
			else:
				shippingCharges = 40
		# print price,stock, discount, rating, shippingCharges
		return price,stock, discount, rating, shippingCharges

	def __extract_between(self, text, sub1, sub2, nth=1):
		"""
		extract a substring from text between two given substrings
		sub1 (nth occurrence) and sub2 (nth occurrence)
		arguments are case sensitive
		"""
		# prevent sub2 from being ignored if it's not there
		if sub2 not in text.split(sub1, nth)[-1]:
			return None
		return text.split(sub1, nth)[-1].split(sub2, nth)[0]