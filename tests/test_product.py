import unittest
from product import Product
class ProductTestCase(unittest.TestCase):
    def setUp(self):
        self.prod = Product('{"id":"1","name":"socks","category":"footwear","price":"4.50"}')
        self.other_prod_1 = Product('{"id":"2","name":"shoes","category":"footwear","price":"8.50"}')
        self.other_prod_2 = Product('{"id":"4","name":"flipflops","category":"swimwear","price":"8.50"}')
        self.other_prod_3 = Product('{"id":"3","name":"shoes3","category":"footwear","price":"8.50"}')
        self.other_prod_4 = Product('{"id":"2","name":"shoes","category":"footwear","price":"8.50"}')

    def tearDown(self):
        self.prod = None

    def test_parseMetaData(self):
        """Testing ID, Name, Category, and other Attributes"""
        self.assertEqual(self.prod.id , "1")
        self.assertEqual(self.prod.name , "socks")
        self.assertEqual(self.prod.category , "footwear")
        self.assertNotEqual(self.prod.weight , "footwear")
        self.assertEqual(self.prod.price , float("4.50"))
        self.assertRaises(Exception, self.prod.parseMetaData(""))
        self.assertRaises(Exception, self.prod.parseMetaData(None))
        self.assertRaises(Exception, self.prod.parseMetaData('{"irrd":"1","name":"socks","category":"footwear"}'))
        self.assertRaises(Exception, self.prod.parseMetaData(1))
        self.assertEqual(str(self.prod),'1')

    def test_addToRecommendations(self):

        """Testing 1 Product Added"""
        self.prod.addToRecommendations(self.other_prod_1)
        self.assertEqual(len(self.prod.recommendations),1)

        """Testing 2 Products Added"""
        self.prod.addToRecommendations(self.other_prod_2)
        self.assertEqual(len(self.prod.recommendations),2)

        """Testing 3 Products Added"""
        self.prod.addToRecommendations(self.other_prod_3)
        self.assertEqual(len(self.prod.recommendations),3)

        """Testing Weight of First Product"""
        self.assertEqual(self.prod.recommendations['2'].weight,2)

        """Testing Product Exists"""
        self.assertEqual(self.prod.addToRecommendations(self.other_prod_4),"Product exists! Refer to Update API!")

    def test_deleteFromRecommendations(self):
        self.prod.addToRecommendations(self.other_prod_1)
        self.prod.addToRecommendations(self.other_prod_2)
        self.prod.addToRecommendations(self.other_prod_3)
        self.prod.deleteFromRecommendations(self.other_prod_3)

        """Testing Existing Product Removed"""
        self.assertEqual(len(self.prod.recommendations),2)

        """Testing Nonexistant Product Cannot Be Removed"""
        self.assertEqual(self.prod.deleteFromRecommendations(self.other_prod_3),"Product not found!")
    def test_cmpkey(self):
        self.assertEqual(self.prod.weight , self.prod._cmpkey())

    def test_compare(self):
        apple = []
        self.other_prod_1 = Product('{"id":"2","name":"shoes","category":"footwear","price":"8.50"}')
        self.other_prod_2 = Product('{"id":"3","name":"flipflops","category":"swimwear","price":"8.50"}')

        """Testing Type Error Comparisons"""
        self.assertRaises(TypeError, self.prod._compare(self.prod, apple))

        self.other_prod_1.weight=5
        self.other_prod_2.weight= 3
        self.other_prod_3.weight= 3

        """Testing Weight Comparisons"""
        self.assertTrue(self.other_prod_1 > self.other_prod_2)
        self.assertTrue(self.other_prod_2 < self.other_prod_1)
        self.assertTrue(self.other_prod_2 <= self.other_prod_3)
        self.assertTrue(self.other_prod_2 >= self.other_prod_3)
        self.assertTrue(self.other_prod_2 == self.other_prod_3)
        self.assertTrue(self.other_prod_1 != self.other_prod_3)

    def test_getSortedRecommendations(self):
        """Testing getSortedRecommendations Returns Sorted List"""
        self.prod.addToRecommendations(self.other_prod_1)
        self.prod.addToRecommendations(self.other_prod_2)
        self.prod.addToRecommendations(self.other_prod_3)
        self.assertEqual(self.prod.getSortedRecommendations(),[self.other_prod_1,self.other_prod_3,self.other_prod_2])
        self.prod.recommendations = {}
        self.assertEqual(self.prod.getSortedRecommendations(),[])

if __name__ == '__main__':
    unittest.main()
