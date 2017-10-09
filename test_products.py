# Test cases can be run with:
# nosetests
# coverage report -m

""" Test cases for Product Model """

import unittest
from models import Product, DataValidationError

######################################################################
#  T E S T   C A S E S
######################################################################
class TestProducts(unittest.TestCase):
    """ Test Cases for Products """

    def setUp(self):
        Product.remove_all()

    def test_create_a_product(self):
        """ Create a product and assert that it exists """
        product = Product(0, "fido", "dog")
        self.assertTrue(product != None)
        self.assertEqual(product.id, 0)
        self.assertEqual(product.name, "fido")
        self.assertEqual(product.category, "dog")

    def test_add_a_product(self):
        """ Create a product and add it to the database """
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(0, "fido", "dog")
        self.assertTrue(product != None)
        self.assertEqual(product.id, 0)
        product.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(product.id, 1)
        products = Product.all()
        self.assertEqual(len(products), 1)

    def test_update_a_product(self):
        """ Update a Product """
        product = Product(0, "fido", "dog")
        product.save()
        self.assertEqual(product.id, 1)
        # Change it an save it
        product.category = "k9"
        product.save()
        self.assertEqual(product.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].category, "k9")

    def test_delete_a_product(self):
        """ Delete a Product """
        product = Product(0, "fido", "dog")
        product.save()
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_serialize_a_product(self):
        """ Test serialization of a Product """
        product = Product(0, "fido", "dog")
        data = product.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], 0)
        self.assertIn('name', data)
        self.assertEqual(data['name'], "fido")
        self.assertIn('category', data)
        self.assertEqual(data['category'], "dog")

    def test_deserialize_a_product(self):
        """ Test deserialization of a Product """
        data = {"id": 1, "name": "kitty", "category": "cat"}
        product = Product()
        product.deserialize(data)
        self.assertNotEqual(product, None)
        self.assertEqual(product.id, 1)
        self.assertEqual(product.name, "kitty")
        self.assertEqual(product.category, "cat")

    def test_deserialize_with_no_name(self):
        """ Deserialize a Product without a name """
        product = Product()
        data = {"id":0, "category": "cat"}
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_with_no_data(self):
        """ Deserialize a Product with no data """
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, None)

    def test_deserialize_with_bad_data(self):
        """ Deserailize a Product with bad data """
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, "data")

    def test_find_product(self):
        """ Find a Product by ID """
        Product(0, "fido", "dog").save()
        Product(0, "kitty", "cat").save()
        product = Product.find(2)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, 2)
        self.assertEqual(product.name, "kitty")

    def test_find_with_no_products(self):
        """ Find a Product with no Products """
        product = Product.find(1)
        self.assertIs(product, None)

    def test_product_not_found(self):
        """ Test for a Product that doesn't exist """
        Product(0, "fido", "dog").save()
        product = Product.find(2)
        self.assertIs(product, None)

    def test_find_by_category(self):
        """ Find Products by Category """
        Product(0, "fido", "dog").save()
        Product(0, "kitty", "cat").save()
        products = Product.find_by_category("cat")
        self.assertNotEqual(len(products), 0)
        self.assertEqual(products[0].category, "cat")
        self.assertEqual(products[0].name, "kitty")

    def test_find_by_name(self):
        """ Find a Product by Name """
        Product(0, "fido", "dog").save()
        Product(0, "kitty", "cat").save()
        products = Product.find_by_name("kitty")
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].category, "cat")
        self.assertEqual(products[0].name, "kitty")


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestProducts)
    # unittest.TextTestRunner(verbosity=2).run(suite)
