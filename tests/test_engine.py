import unittest
from engine import Engine
class EngineTestCase(unittest.TestCase):
    def setUp(self):
        self.rec_engine_1 = Engine('{"id":"1","name":"socks","category":"footwear","price":"4.50"}', 1)
        self.rec_engine_2 = Engine('{"id":"1","name":"cookies","category":"food","price":"2.50"}', 174)
        self.other_prod_1 = '{"id":"2","name":"shoes","category":"footwear","price":"8.50"}'
        self.other_prod_2 = '{"id":"4","name":"flipflops","category":"swimwear","price":"8.50"}'
        self.other_prod_3 = '{"id":"3","name":"cheapsocks","category":"footwear","price":"1.50"}'
        self.other_prod_4 = '{"id":"2","name":"broccoli","category":"vegetables","price":".50"}'
        self.other_prod_5 = '{"id":"2","name":"broccoli","category":"vegetables","price":"somethingwrong"}'


    def tearDown(self):
        self.rec_engine_1 = None
        self.rec_engine_2 = None

    
    # def test_instantiation(self):
    #     self.assertRaises(Exception, self.rec_engine_missing_rec_type = Engine(''))
    #     self.assertRaises(Exception, self.rec_engine_missing_rec_type = Engine())

    def test_parseMetaData(self):
        """Testing Parsing of Product Metadata"""
        #nothing to parse
        self.assertEquals(self.rec_engine_1.parseMetaData(""), "Missing metadata for one or both products!" )
        #invalid json
        self.assertRaises(Exception, self.rec_engine_1.parseMetaData('"id":"1","name":"socks","adf":"footwear"4.50"}'))
        

        #getting valid product metadata
        p1, p2 = self.rec_engine_1.parseMetaData(self.other_prod_1)
        
        #valid product_1_metadata
        self.assertEquals(p1,{"id":"1","name":"socks","category":"footwear","price":"4.50"})
        #valid product_2_metadata
        self.assertEquals(p2,{"id":"2","name":"shoes","category":"footwear","price":"8.50"})

    def test_badRecType(self):
        """Testing Bad Recommendation Types"""
        self.assertEquals(self.rec_engine_2.getWeight(self.other_prod_1),"Invalid rec_type_id")

    def test_badMetadata(self):
        """Testing Bad Metadata"""
        self.assertEquals(self.rec_engine_1.getWeight(self.other_prod_5),"Invalid metadata! Confirm you entered an id, category, and price. Also, confirm that price is a numeric value!")

    def test_getWeight(self):
        """Testing Correct Weights"""

        #upsell algo test          
        self.assertEquals(self.rec_engine_1.getWeight(self.other_prod_1),2) 
        self.assertEquals(self.rec_engine_1.getWeight(self.other_prod_2),1) 
        self.assertEquals(self.rec_engine_1.getWeight(self.other_prod_3),1)
        self.assertEquals(self.rec_engine_1.getWeight(self.other_prod_4),0)

   
if __name__ == '__main__':
    unittest.main()

