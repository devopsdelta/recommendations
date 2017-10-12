import json

class Product:

	def __init__(self,item_meta_data):
		self.id = None
		self.name = None
		self.category = None
		self.weight = 0
		self.price = 0
		self.recommendations = {}
		self.parseMetaData(item_meta_data)


	#assumes that we recieve JSON Data in this Manner
	#'[{'id':'1'},{'name':'socks'},{'category':'footwear'}]'
	def parseMetaData(self,item_meta_data):
		try:
			if (item_meta_data!= ""):
				json_meta_data = json.loads(item_meta_data)
				self.id = json_meta_data['id']
				self.name = json_meta_data['name']
				self.category = json_meta_data['category']
				self.price = float(json_meta_data['price'])
			else:
				return ("No meta data provided!")

		#down the road, we will need to test specific type errors
		except Exception as exception:
			return (str(type(exception)))

	#weight is the relation of another product to this product
	def __getWeight__(self,product):
		weight = 0
		if self.category == product.category:
			weight +=1
		if (abs(self.price-product.price)<=5.00):
			weight +=1
		#... conditions
		return weight

	#we create a recommendation hash table keyed by ID
	#{id#:product_object}
	def addToRecommendations(self,product):
		if product.id not in self.recommendations:
			weight = self.__getWeight__(product)
			product.weight = weight
			self.recommendations[product.id]=product
		else:
			return "Product exists! Refer to Update API!"

	#we sort product recommendations by weight
	def getSortedRecommendations(self):
		if bool(self.recommendations):
			keyList = self.recommendations.keys()
			keyList = sorted(keyList)
			sortedRecs = []
			for key in keyList:
				sortedRecs += [self.recommendations[key]]
			return sortedRecs
		else:
			return []

	#pop item from recommendations hash
	def deleteFromRecommendations(self,product):
		if product.id in self.recommendations:
			del self.recommendations[product.id]
		else:
			return "Product not found!"

	#Comprable equivalent below
	#borrowed from https://stackoverflow.com/questions/6907323/comparable-classes-in-python-3
	def _cmpkey(self):
	   return (self.weight)

	#toString Equivalent
	def __repr__(self):
	   return "%s" % (self.id)

	def _compare(self, other, method):
	    try:
	        return method(self._cmpkey(), other._cmpkey())
	    except (AttributeError, TypeError):
	        # _cmpkey not implemented, or return different type,
	        # so I can't compare with "other".
	        return NotImplemented

	#less than
	def __lt__(self, other):
	    return self._compare(other, lambda s, o: s < o)

	#less than or equal
	def __le__(self, other):
	    return self._compare(other, lambda s, o: s <= o)

	def __eq__(self, other):
	    return self._compare(other, lambda s, o: s == o)

	def __ge__(self, other):
	    return self._compare(other, lambda s, o: s >= o)

	def __gt__(self, other):
	    return self._compare(other, lambda s, o: s > o)

	def __ne__(self, other):
	    return self._compare(other, lambda s, o: s != o)
