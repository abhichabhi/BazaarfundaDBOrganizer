from scrapy.selector import HtmlXPathSelector
import urllib, traceback

class SnapDealScrapper:
	def getPrice(self,response):
		hxs = HtmlXPathSelector(text=response)
		status = 1 
		discount = 0
		stockStatus = hxs.select("//div[@class='notifyMe-soldout']/text()").extract()
		if not stockStatus:
			stockStatus = hxs.select("//div[@class='soldleftImg btn']/span/text()").extract()
		if stockStatus:
			status = 0
		if not status:
			stockStatus = hxs.select("//span[@class='discontImage']")
			if stockStatus:
				status = 0
		priceText = hxs.select('//span[@id="selling-price-id"]/text()').extract()
		if not priceText:
			priceText = hxs.select('//span[@itemprop="price"]/text()').extract()
		try:
			priceText = priceText[0]
			priceText = priceText.strip()
			priceText = priceText.replace(",","")
			priceText = priceText.replace("Rs. ","")
			price = int(priceText)
		except:
			price = 0

		try:
			discount = hxs.select('//span[contains(@class,"pdp-e-i-MRP-r-dis")]/text()').extract()[0]
			discount = int(discount)

		except:
			discount = 0

		try:
			rating = hxs.select('//span[contains(@itemprop, "ratingValue")]/text()').extract()[0]
			
			rating = float(rating)
		except:
			rating = None

		try:
			shippingCharges = hxs.select('//span[contains(@class,"freeDeliveryChargeCls")]/text()').extract()[0]
			print shippingCharges
			shippingCharges = shippingCharges.replace("+","")
			shippingCharges = shippingCharges.replace("Rs","")
			shippingCharges = shippingCharges.replace("Delivery","")
			shippingCharges = shippingCharges.replace(":","")
			shippingCharges = shippingCharges.replace("Charges","")
			shippingCharges = shippingCharges.replace(",","")
			shippingCharges = shippingCharges.replace("-","")
			shippingCharges = shippingCharges.strip()
			
			shippingCharges = int(shippingCharges)
		except Exception, err:
			
			shippingCharges = 0

		# print price, status, discount, rating, shippingCharges
		return price, status, discount, rating, shippingCharges

	