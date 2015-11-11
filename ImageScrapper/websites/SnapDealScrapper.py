from scrapy.selector import HtmlXPathSelector
import urllib, traceback, shutil

class SnapDealScrapper:
	def downloadProductList(self,response, imageFileInc, imageFileAll):
		hxs = HtmlXPathSelector(text=response)
		imageURL = hxs.select('//p[@class="tileImages"]/img/@src').extract()
		if not imageURL:
			print "not found"
			imageURL = hxs.select('//div[@class="cloudzoom-lens"]/img/@src').extract()
		if not imageURL:
			print "not found2"
			# class="jqzoom zoomPad cloudzoom"
			imageURL = hxs.select('//img[@class="jqzoom zoomPad cloudzoom"]/@src').extract()
		try:
			print imageURL
			imageURL = imageURL[0]
			urllib.urlretrieve(imageURL,imageFileInc)
			# shutil.copy2(imageFileInc, imageFileAll)
		except Exception, err:
			print(traceback.format_exc()), "Error",
			print "image could not be found for " + imageFileInc