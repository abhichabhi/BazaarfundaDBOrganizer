from scrapy.selector import HtmlXPathSelector
import urllib, traceback

class FlipKartScrapper:
	def getPrice(self,response):
		hxs = HtmlXPathSelector(text=response)
		stockStatus = hxs.select('//div[@class="out-of-stock"]').extract()
		status = 1
		if stockStatus:
			status =  0
		priceText = hxs.select('//span[contains(@class,"selling-price")]/text()').extract()
		try:
			priceText = priceText[0]
			priceText = priceText.strip()
			priceText = priceText.replace(",","")
			priceText = priceText.replace("Rs. ","")
			price = int(priceText)
		except:
			price = 0
		try:
			discount = hxs.select('//span[contains(@class,"discount")]/text()').extract()
			discount = discount[0]
			discount = discount.replace("%","")
			discount = discount.replace("OFF","")
			discount = discount.strip()
			discount = int(discount)
		except:
			discount = 0
		try:
			rating = hxs.select('//div[@class="bigStar"]/text()').extract()[0]
			
			rating = float(rating)
			
		except:
			rating = None
		shippingCharges = 0

		try:
			shippingCharges = hxs.select('//div[contains(@class,"default-shipping-charge")]/text()').extract()[0]
			shippingCharges = shippingCharges.replace("+","")
			shippingCharges = shippingCharges.replace("Rs","")
			shippingCharges = shippingCharges.replace("Delivery","")
			shippingCharges = shippingCharges.strip()
			shippingCharges = int(shippingCharges)
		except Exception, err:
			print(traceback.format_exc()), "Error"
			shippingCharges = 0
		print price, status, discount,rating, shippingCharges
		
		return price, status, discount,rating, shippingCharges
		