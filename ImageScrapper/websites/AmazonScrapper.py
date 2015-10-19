from scrapy.selector import HtmlXPathSelector
import urllib, traceback, shutil

class AmazonScrapper:
	def downloadProductList(self,response, imageFileInc, imageFileAll):
		hxs = HtmlXPathSelector(text=response)
		imageURL = hxs.select('//img[@id="landingImage"]/@src').extract()
		try:
			print imageURL
			imageURL = imageURL[0]
			urllib.urlretrieve(imageURL,imageFileInc)
			# shutil.copy2(imageFileInc, imageFileAll)
		except Exception, err:
			print(traceback.format_exc()), "Error",
			print "image could not be found for " + imageFileInc