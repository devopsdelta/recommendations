# Test cases can be run with:
# nosetests
# coverage report -m

""" Test cases for Recommendation Model """

import unittest
import json
from models import Recommendation, DataValidationError

######################################################################
#  T E S T   C A S E S
######################################################################
class TestRecommendations(unittest.TestCase):
    """ Test Cases for Recommendations """

    def setUp(self):
        Recommendation.remove_all()

    def test_create_a_recommendation(self):
        """ Create a recommendation and assert that it exists """
        recommendation = Recommendation(23, "Recommendation Object")
        self.assertTrue(recommendation != None)
        self.assertEqual(recommendation.id, 23)
        self.assertEqual(recommendation.recommendation, "Recommendation Object")

    def test_add_a_recommendation(self):
        """ Create a recommendation and add it to the database """
        recommendations = Recommendation.all()
        self.assertEqual(recommendations, [])
        recommendation = Recommendation(3, "rec object")
        self.assertTrue(recommendation != None)
        self.assertEqual(recommendation.id, 3)
        recommendation.save()

        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(recommendation.id, 3)
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)

    def test_update_a_recommendation(self):
        """ Update a Recommendation """
        recommendation = Recommendation(5, "rec object")
        recommendation.save()
        self.assertEqual(recommendation.id, 5)

        # Change it an save it
        recommendation.recommendation = "updated object"
        recommendation.save()
        self.assertEqual(recommendation.id, 5)

        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        recommendation = Recommendation.find_by_id(5)
        self.assertEqual(recommendation.recommendation, "updated object")

    def test_delete_a_recommendation(self):
        """ Delete a Recommendation """
        recommendation = Recommendation(0, "rec object")
        recommendation.save()
        self.assertEqual(len(Recommendation.all()), 1)

        # delete the recommendation and make sure it isn't in the database
        recommendation.delete()
        self.assertEqual(len(Recommendation.all()), 0)

    def test_serialize_a_recommendation(self):
        """ Test serialization of a Recommendation """
        recommendation = Recommendation(6, "rec object")
        data = recommendation.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], 6)
        self.assertIn('recommendation', data)
        self.assertEqual(data['recommendation'], "rec object")

    def test_deserialize_a_recommendation(self):
        """ Test deserialization of a Recommendation """
        data = {"id": 1, "recommendation": "rec"}
        recommendation = Recommendation()
        recommendation.deserialize(data)
        self.assertNotEqual(recommendation, None)
        self.assertEqual(recommendation.id, 1)
        self.assertEqual(recommendation.recommendation, "rec")

    def test_deserialize_with_no_name(self):
        """ Deserialize a Recommendation without a recommendation """
        recommendation = Recommendation()
        data = {"id":3}
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_with_no_data(self):
        """ Deserialize a Recommendation with no data """
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, None)

    def test_deserialize_with_bad_data(self):
        """ Deserailize a Recommendation with bad data """
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, "data")

    def test_find_recommendation(self):
        """ Find a Recommendation by ID """
        Recommendation(4, "rec obj 1").save()
        Recommendation(87, "rec obj 2").save()
        recommendation = Recommendation.find_by_id(87)
        self.assertIsNot(recommendation, None)
        self.assertEqual(recommendation.id, 87)
        self.assertEqual(recommendation.recommendation, "rec obj 2")

    def test_find_with_no_recommendation(self):
        """ Find a Recommendation with no Recommendations """
        recommendation = Recommendation.find_by_id(1)
        self.assertIs(recommendation, None)

    def test_recommendation_not_found(self):
        """ Test for a Recommendation that doesn't exist """
        Recommendation(4, "rec obj").save()
        recommendation = Recommendation.find_by_id(2)
        self.assertIs(recommendation, None)

    def test_find_by_category(self):
        """ Find Recommendations by Category """
        Recommendation(10, "{ 'id': 10, 'recommendation': { 'name': 'Product 1': 'category': 'software'}}").save()
        Recommendation(20, "{ 'id': 20, 'recommendation': { 'name': 'Product 2': 'category': 'software'}}").save()
        recommendations = Recommendation.find_by_category("software")
        data = recommendations[0].recommendation
        self.assertNotEqual(len(recommendations), 0)
        self.assertTrue('Product 1' in data)
        self.assertTrue('software' in data)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestRecommendations)
    # unittest.TextTestRunner(verbosity=2).run(suite)
