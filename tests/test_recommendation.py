# Test cases can be run with:
# nosetests
# coverage report -m

""" Test cases for Recommendation Model """

import unittest
import json
from psycopg2 import OperationalError
from mock import patch
import os
from models import Recommendation, RecommendationType, RecommendationDetail
from models import init_db, db, DataValidationError
from flask import Flask, jsonify

LOCAL_HOST_URI = 'postgres://recommendations:password@localhost:5433/recommendations'
BAD_DATABASE_CREDS = 'postgres://recommendations:password@localhost:5400/recommendations'

VCAP_SERVICES = {
    'elephantsql': [
        {'credentials': {
            'uri': LOCAL_HOST_URI,
            'max_conns': '5'
            }
        }
    ]
}

######################################################################
#  T E S T   C A S E S
######################################################################
class TestRecommendations(unittest.TestCase):
    """ Test Cases for Recommendations """

    def setUp(self):
        """ Creates a new database for the unit test to use """
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        init_db(self.app, LOCAL_HOST_URI)

    def tearDown(self):
        """ Ensures that the database is emptied for next unit test """
        try:
            db.session.remove()
            db.drop_all()
        except Exception as e:
            pass

    def test_create_a_recommendation(self):
        """ Create a recommendation and assert that it exists """
        rec_type = RecommendationType.find_by_id(1)
        rec = Recommendation(23, rec_type)
        rec.save()

        self.assertTrue(rec != None)
        self.assertEqual(Recommendation.count(), 1)

    def test_update_a_recommendation(self):
        """ Update a Recommendation """
        rec_type = RecommendationType.find_by_id(1)
        rec = Recommendation(23, rec_type)
        rec.save()
        self.assertEqual(rec.id, 1)

        # Change it an save it
        rec.product_id = 54
        rec.save()
        self.assertEqual(rec.product_id, 54)

        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        rec = Recommendation.find_by_id(1)
        self.assertEqual(rec.product_id, 54)

    def test_delete_a_recommendation(self):
        """ Delete a Recommendation """
        rec_type = RecommendationType.find_by_id(1)
        rec = Recommendation(23, rec_type)
        rec.save()
        self.assertEqual(Recommendation.count(), 1)

        # delete the recommendation and make sure it isn't in the database
        rec.delete()
        self.assertEqual(Recommendation.count(), 0)

    def test_serialize_a_recommendation(self):
        """ Test serialization of a Recommendation """

        rec_type = RecommendationType.find_by_id(1)
        rec = Recommendation(23, rec_type)
        rec.save()
        data = rec.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], 1)
        self.assertIn('product_id', data)
        self.assertEqual(data['product_id'], 23)

    def test_deserialize_a_recommendation(self):
        """ Test deserialization of a Recommendation """
        data = { 'product_id': 54, 'type': 'up-sell' }
        rec_type = RecommendationType.find_by_id(1)
        rec = Recommendation()
        rec.deserialize(data)
        self.assertNotEqual(rec, None)
        self.assertEqual(rec.product_id, 54)

    def test_deserialize_with_no_product(self):
        """ Deserialize a Recommendation without a product """
        rec = Recommendation()
        data = { "id": 3, "rec_type_id": 1 }
        self.assertRaises(DataValidationError, rec.deserialize, data)

    def test_deserialize_with_no_type(self):
        """ Deserialize a Recommendation with no Recommendation Type """
        rec = Recommendation()
        data = { "id": 3, "product_id": 1 }
        self.assertRaises(DataValidationError, rec.deserialize, data)

    def test_deserialize_with_no_data(self):
        """ Deserialize a Recommendation with no data """
        rec = Recommendation()
        self.assertRaises(DataValidationError, rec.deserialize, None)

    def test_deserialize_with_bad_data_type(self):
        """ Deserailize a Recommendation with bad data type """
        rec = Recommendation()
        self.assertRaises(DataValidationError, rec.deserialize, "data")

    def test_adding_a_recommendation(self):
        """ Add a recommendation to a Recommendation record """
        rec_type = RecommendationType.find_by_id(1)
        rec = Recommendation(23, rec_type)
        rec.save()

        self.assertTrue(rec != None)
        self.assertEqual(Recommendation.count(), 1)
        self.assertEqual(len(rec.recommendations), 0)

        rec_detail = RecommendationDetail(45, .5)
        rec.recommendations.append(rec_detail)
        rec.save()

        self.assertEqual(len(rec.recommendations), 1)

    def test_update_a_recommendation_detail(self):
        """ Update a Recommendation Detail Record """
        rec_type = RecommendationType.find_by_id(1)
        rec = Recommendation(23, rec_type)
        rec_detail = RecommendationDetail(45, .5)
        rec.recommendations.append(rec_detail)
        rec.save()
        self.assertEqual(rec.id, 1)

        # Change it an save it
        rec.recommendations[0].weight = .2
        rec.save()
        self.assertEqual(rec.recommendations[0].weight, .2)

        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        rec = Recommendation.find_by_id(1)
        self.assertEqual(rec.recommendations[0].weight, .2)

    def test_find_recommendation(self):
        """ Find a Recommendation by ID """
        rec_type = RecommendationType.find_by_id(1)
        Recommendation(4, rec_type).save()
        Recommendation(87, rec_type).save()
        rec = Recommendation.find_by_id(2)
        self.assertIsNot(rec, None)
        self.assertEqual(rec.product_id, 87)
        self.assertEqual(rec.rec_type, rec_type)

    def test_finding_recommendations_by_type(self):
        """ List all recommendations for a particular recommendation type """

        rec_type = RecommendationType.find_by_id(1)
        rec = Recommendation(23, rec_type)
        rec_detail1 = RecommendationDetail(10, .9)
        rec_detail2 = RecommendationDetail(20, .8)
        rec_detail3 = RecommendationDetail(30, .8)
        rec_detail4 = RecommendationDetail(40, .5)
        rec.recommendations.append(rec_detail1)
        rec.recommendations.append(rec_detail2)
        rec.recommendations.append(rec_detail3)
        rec.recommendations.append(rec_detail4)
        rec.save()

        rec_type = RecommendationType.find_by_id(2)
        rec = Recommendation(23, rec_type)
        rec_detail1 = RecommendationDetail(50, .1)
        rec_detail2 = RecommendationDetail(60, .2)
        rec_detail3 = RecommendationDetail(70, .3)
        rec.recommendations.append(rec_detail1)
        rec.recommendations.append(rec_detail2)
        rec.recommendations.append(rec_detail3)
        rec.save()

        # Assuming the client will provide a product id and category as a String
        rec_type = RecommendationType.find_by_id(1)
        rec = Recommendation.find_by_type(rec_type)[0]
        print rec.serialize()
        self.assertIsNot(rec, None)
        self.assertEqual(len(rec.recommendations), 4)
        self.assertEqual(rec.product_id, 23)
        self.assertEqual(rec.rec_type, rec_type)

    def test_find_with_no_recommendation_data(self):
        """ Find a Recommendation with no Recommendations """
        rec = Recommendation.find_by_id(1)
        self.assertIs(rec, None)

    def test_find_by_rec_id_and_product_id(self):
        """ Find a Recommendation with no Recommendations """
        rec_type = RecommendationType.find_by_id(1)
        rec = Recommendation(23, rec_type)
        rec_detail1 = RecommendationDetail(10, .9)
        rec_detail2 = RecommendationDetail(20, .8)
        rec_detail3 = RecommendationDetail(30, .8)
        rec_detail4 = RecommendationDetail(40, .5)
        rec.recommendations.append(rec_detail1)
        rec.recommendations.append(rec_detail2)
        rec.recommendations.append(rec_detail3)
        rec.recommendations.append(rec_detail4)
        rec.save()

        recs = RecommendationDetail.find_by_rec_id_and_product_id(1, 20)
        self.assertIsNotNone(recs)
        self.assertEqual(recs.rec_product_id, 20)

    def test_recommendation_not_found_with_data(self):
        """ Test for a Recommendation that doesn't exist """
        rec_type = RecommendationType.find_by_id(2)
        rec = Recommendation(23, rec_type).save()
        rec = Recommendation.find_by_id(2)
        self.assertIs(rec, None)

    def test_good_database_connection(self):
        """ Pass in a good db connection """
        self.test_app = Flask(__name__)
        init_db(self.test_app, LOCAL_HOST_URI)
        self.assertIsNotNone(db)

    def test_incorrect_database_connection(self):
        """ Pass in the connection with incorrect info """
        self.test_app = Flask(__name__)
        self.assertRaises(OperationalError, init_db, self.test_app, BAD_DATABASE_CREDS)

    def test_passing_bad_connection(self):
        """ Pass in a bad connection string """
        self.test_app = Flask(__name__)
        self.assertRaises(OperationalError, init_db, self.test_app, "Bad Connection")

    @patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(VCAP_SERVICES)})
    def test_vcap_services(self):
        """ Test if VCAP_SERVICES works """
        self.test_app = Flask(__name__)
        init_db(self.test_app)
        self.assertIsNotNone(db)

    @patch('models.db.session.commit')
    def test_db_error_on_save(self, db_error_mock):
        """ Test Rollback on save """
        current_rec_count = len(Recommendation.all())
        db_error_mock.side_effect = OperationalError()
        rec_type = RecommendationType.find_by_name("up-sell")
        Recommendation(1, rec_type).save()
        new_rec_count = len(Recommendation.all())
        self.assertEqual(current_rec_count, new_rec_count)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestRecommendations)
    # unittest.TextTestRunner(verbosity=2).run(suite)
