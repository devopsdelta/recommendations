import json

class Engine:

	def __init__(self,product_1_metadata, rec_type_id):
		self.product_1_metadata = product_1_metadata
		self.rec_type_id = rec_type_id

	#assumes that we recieve JSON Data in this Manner	
	def parseMetaData(self, product_2_metadata):
		try:
			if (self.product_1_metadata!= "" and product_2_metadata!= ""):
				product_1 = json.loads(self.product_1_metadata)
				product_2 = json.loads(product_2_metadata)
				return product_1, product_2
			return ("Missing metadata for one or both products!")

		#down the road, we will need to test specific type errors
		except Exception as exception:
			return (str(type(exception)))

	def _getUpsellWeight(self, product_1, product_2):
			try:
				prod_1_id = product_1['id']
				prod_1_category = product_1['category']
				prod_1_price = float(product_1['price'])
				
				prod_2_id = product_2['id']
				prod_2_category = product_2['category']
				prod_2_price = float(product_2['price'])
			except:
				return "Invalid metadata! Confirm you entered an id, category, and price. Also, confirm that price is a numeric value!"

			weight = 0
			if prod_1_category == prod_2_category:
				weight +=1
			if prod_2_price > prod_1_price:
				weight +=1
			
			#... other conditions
			
			return weight


	#weight is the relation of another product to this product
	def getWeight (self, product_2_metadata):
		product_1, product_2 = self.parseMetaData(product_2_metadata)

		if (self.rec_type_id == 1):
			return self._getUpsellWeight(product_1, product_2)

		return "Invalid rec_type_id"

		#... more comparisons to come

	
	