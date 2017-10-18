# Test cases can be run with:
# nosetests
# coverage report -m

""" Test cases for the Recommendation Service """

import logging
import unittest
import json
from mock import MagicMock, patch
from flask_api import status    # HTTP Status Codes
import server
import mock

######################################################################
#  T E S T   C A S E S
######################################################################
class TestRecommendationServer(unittest.TestCase):
    """ Recommendation Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        server.app.debug = False
        server.initialize_logging(logging.ERROR)

    def setUp(self):
        """ Runs before each test """
        server.Recommendation.remove_all()
        server.Recommendation(1, {'name': 'Product 1', 'category': 'shoes'}).save()
        server.Recommendation(2, {'name': 'Product 2', 'category': 'belts'}).save()
        self.app = server.app.test_client()

    def tearDown(self):
        """ Runs after each test """
        server.Recommendation.remove_all()

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'Recommendation Demo REST API Service')

    def test_get_recommendation_list(self):
        """ Get a list of Recommendation """
        resp = self.app.get('/recommendations')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)

    def test_get_recommendation(self):
        """ Get one Recommendation """
        resp = self.app.get('/recommendations/2')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['recommendation'], {'name': 'Product 2', 'category': 'belts'})

    def test_get_recommendation_not_found(self):
        """ Get a Recommendation thats not found """
        resp = self.app.get('/recommendations/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_recommendation_when_no_data_exist(self):
        """ Get a Recommendation thats not found """
        server.Recommendation.remove_all()
        resp = self.app.get('/recommendations/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_rating_recommendation(self):
        """ Rating of Recommendation """
        resp = self.app.get('/recommendations/rating')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, '2.5')

    def test_create_recommendation(self):
        """ Create a Recommendation """
        # save the current number of recommendations for later comparrison
        recommendation_count = self.get_recommendation_count()

        # add a new recommendation
        new_recommendation = {'id': 87, 'recommendation': {'name': 'Product 3', 'category': 'computers'}}
        data = json.dumps(new_recommendation)
        resp = self.app.post('/recommendations', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['recommendation']['name'], 'Product 3')

        # check that count has gone up and includes sammy
        resp = self.app.get('/recommendations')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), recommendation_count + 1)
        self.assertIn(new_json, data)

    def test_update_recommendation(self):
        """ Update a Recommendation """
        new_recommendation = {'id': 52, 'recommendation': {'name': 'Product 4', 'category': 'software'}}
        data = json.dumps(new_recommendation)
        resp = self.app.put('/recommendations/2', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get('/recommendations/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['recommendation']['category'], 'software')

    def test_update_recommendation_not_found(self):
        """ Update a Recommendation that can't be found """
        new_recommendation = {'id': 98, 'recommendation': {'name': 'Product 5', 'category': 'glassware'}}
        data = json.dumps(new_recommendation)
        resp = self.app.put('/recommendations/0', data=data, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_recommendation(self):
        """ Delete a Recommendation that exists """
        # save the current number of recommendations for later comparrison
        recommendation_count = self.get_recommendation_count()

        # delete a recommendation
        resp = self.app.delete('/recommendations/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_recommendation_count()
        self.assertEqual(new_count, recommendation_count - 1)

    def test_get_nonexisting_recommendation(self):
        """ Get a Recommendation that doesn't exist """
        resp = self.app.get('/recommendations/5')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_query_recommendation_by_category(self):
        """ Query Recommendation by Category """
        resp = self.app.get('/recommendations', query_string='category=shoes')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        data = json.loads(resp.data)[0]
        self.assertTrue('Product 1' in data['recommendation']['name'])
        self.assertFalse('Product 2' in data['recommendation']['name'])
        self.assertTrue('shoes' in data['recommendation']['category'])

    def test_get_query_recommendation_not_found_by_category(self):
        """ Get a Recommendation that doesn't exist by Category """
        resp = self.app.get('/recommendations', query_string='category=milk')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_query_recommendation_when_no_data_exist(self):
        """ Get a Recommendation thats not found """
        server.Recommendation.remove_all()
        resp = self.app.get('/recommendations', query_string='category=milk')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_not_allowed(self):
        """ Call a Method thats not Allowed """
        resp = self.app.post('/recommendations/0')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @patch('server.Recommendation.find_by_category')
    def test_bad_request(self, bad_request_mock):
        """ Test a Bad Request error from Find By Category """
        bad_request_mock.side_effect = ValueError()
        resp = self.app.get('/recommendations', query_string='category=milk')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bad_request(self):
        """ Test a Validation error when performing a POST """
        new_recommendation = {'id': 87}
        data = json.dumps(new_recommendation)
        resp = self.app.post('/recommendations', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('server.Recommendation.find_by_category')
    def test_search_bad_data(self, recommendation_find_mock):
        """ Test a search that returns bad data """
        recommendation_find_mock.return_value = 4
        resp = self.app.get('/recommendations', query_string='category=foo')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

######################################################################
# Utility functions
######################################################################

    def get_recommendation_count(self):
        """ save the current number of recommendations """
        resp = self.app.get('/recommendations')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
