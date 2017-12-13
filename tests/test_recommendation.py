# Test cases can be run with:
# nosetests
# coverage report -m

""" Test cases for Recommendation Model """
from ctypes import ArgumentError
import json
import os
import unittest
from psycopg2 import OperationalError
from mock import patch
from app.models import Recommendation, RecommendationType
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from app import app
from app.models import db, DataValidationError, seed_db, init_db

VCAP_SERVICES = {
    'elephantsql': [
        {'credentials': {
            'uri': 'postgres://postgres:password@localhost:5432/test',
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
        APP_SETTING = os.getenv('APP_SETTING', 'DevelopmentConfig')
        app.config.from_object('config.%s' % str(APP_SETTING))
        db.drop_all()
        db.create_all()
        seed_db()

    def tearDown(self):
        """ Ensures that the database is emptied for next unit test """
        try:
            db.session.remove()
            db.drop_all()
        except Exception as e:
            pass

    def test_create_a_recommendation(self):
        """ Create a recommendation and assert that it exists """
        data = { "product_id": 54, "rec_type_id": 1, "rec_product_id": 45, "weight": .5 }
        rec = Recommendation()
        rec.deserialize(data)
        rec.save()

        self.assertTrue(rec != None)
        self.assertEqual(Recommendation.count(), 1)

    def test_update_a_recommendation(self):
        """ Update a Recommendation """
        data = { "product_id": 23, "rec_type_id": 1, "rec_product_id": 45, "weight": .5 }
        rec = Recommendation()
        rec.deserialize(data)
        rec.save()
        # self.assertEqual(rec.id, 1)

        # Change and save it
        rec.product_id = 54
        rec.save()
        self.assertEqual(rec.product_id, 54)

        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        rec = Recommendation.find_by_id(1)
        self.assertEqual(rec.product_id, 54)

    def test_delete_a_recommendation(self):
        """ Delete a Recommendation """
        data = { "product_id": 54, "rec_type_id": 1, "rec_product_id": 45, "weight": .5 }
        rec = Recommendation()
        rec.deserialize(data)
        rec.save()

        self.assertEqual(Recommendation.count(), 1)

        # delete the recommendation and make sure it isn't in the database
        rec.delete()
        self.assertEqual(Recommendation.count(), 0)

    def test_serialize_a_recommendation(self):
        """ Test serialization of a Recommendation """

        input_data = {"product_id": 23, \
                      "id": 1, \
                      "rec_type_id": 1, \
                      "rec_product_id": 45, \
                      "weight": .5}
        rec = Recommendation()
        rec.deserialize(input_data)
        rec.save()

        data = rec.serialize()

        self.assertNotEqual(data, None)
        self.assertIn('product_id', data)
        self.assertEqual(data['product_id'], 23)
        self.assertIn('id', data["rec_type"])
        self.assertEqual(data["rec_type"]["id"], 1)
        self.assertIn('rec_product_id', data)
        self.assertEqual(data['rec_product_id'], 45)
        self.assertIn('weight', data)
        self.assertEqual(data['weight'], .5)

    def test_deserialize_a_recommendation(self):
        """ Test deserialization of a Recommendation """
        data = { "product_id": 54, "rec_type_id": 1, "rec_product_id": 45, "weight": .5 }
        rec = Recommendation()
        rec.deserialize(data)
        self.assertNotEqual(rec, None)
        self.assertEqual(rec.product_id, 54)
        self.assertEqual(rec.rec_type_id, 1)
        self.assertEqual(rec.rec_product_id, 45)
        self.assertEqual(rec.weight, .5)

    def test_deserialize_with_no_product(self):
        """ Deserialize a Recommendation without a product """
        rec = Recommendation()
        data = { "rec_type_id": 1, "rec_product_id": 45, "weight": .5 }
        self.assertRaises(DataValidationError, rec.deserialize, data)

    def test_deserialize_with_no_type(self):
        """ Deserialize a Recommendation with no Recommendation Type """
        rec = Recommendation()
        data = { "product_id": 1, "rec_product_id": 45, "weight": .5 }
        self.assertRaises(DataValidationError, rec.deserialize, data)

    def test_deserialize_with_no_data(self):
        """ Deserialize a Recommendation with no data """
        rec = Recommendation()
        self.assertRaises(DataValidationError, rec.deserialize, None)

    def test_deserialize_with_bad_data_type(self):
        """ Deserailize a Recommendation with bad data type """
        rec = Recommendation()
        self.assertRaises(DataValidationError, rec.deserialize, "data")

    def test_find_recommendation(self):
        """ Find a Recommendation by ID """
        data_one = { "product_id": 54, "rec_type_id": 1, "rec_product_id": 45, "weight": .5 }
        rec = Recommendation()
        rec.deserialize(data_one)
        rec.save()

        data_two = { "product_id": 87, "rec_type_id": 1, "rec_product_id": 51, "weight": .5 }
        rec = Recommendation()
        rec.deserialize(data_two)
        rec.save()

        rec = Recommendation.find_by_id(2)
        self.assertIsNot(rec, None)
        self.assertEqual(rec.product_id, 87)
        self.assertEqual(rec.rec_type_id, 1)
        self.assertEqual(rec.rec_product_id, 51)
        self.assertEqual(rec.weight, .5)

    def test_finding_recommendations_by_type(self):
        """ List all recommendations for a particular recommendation type """

        data_one = { "product_id": 23, "rec_type_id": 1, "rec_product_id": 45, "weight": .5 }
        rec = Recommendation()
        rec.deserialize(data_one)
        rec.save()

        data_two = { "product_id": 87, "rec_type_id": 2, "rec_product_id": 51, "weight": .5 }
        rec = Recommendation()
        rec.deserialize(data_two)
        rec.save()

        # Assuming the client will provide a product id and category as a String
        rec_type = RecommendationType.find_by_id(1)
        rec = Recommendation.find_by_type(rec_type)[0]

        self.assertIsNot(rec, None)
        self.assertEqual(rec.product_id, 23)
        self.assertEqual(rec.rec_type_id, 1)
        self.assertEqual(rec.rec_product_id, 45)
        self.assertEqual(rec.weight, .5)

    def test_finding_recommendations_by_product_id_and_type(self):
        """ List all recommendations for a particular product id and recommendation type """

        data_one = { "product_id": 23, "rec_type_id": 1, "rec_product_id": 45, "weight": .5 }
        rec = Recommendation()
        rec.deserialize(data_one)
        rec.save()

        data_two = { "product_id": 87, "rec_type_id": 2, "rec_product_id": 51, "weight": .5 }
        rec = Recommendation()
        rec.deserialize(data_two)
        rec.save()

        # Assuming the client will provide a product id and category as a String
        rec_type = RecommendationType.find_by_id(1)
        rec = Recommendation.find_by_product_id_and_type(23, rec_type)[0]

        self.assertIsNot(rec, None)
        self.assertEqual(rec.product_id, 23)
        self.assertEqual(rec.rec_type_id, 1)
        self.assertEqual(rec.rec_product_id, 45)
        self.assertEqual(rec.weight, .5)

    def test_finding_recommendations_by_product_id(self):
        """ List all recommendations for a particular product id """

        data_one = { "product_id": 23, "rec_type_id": 1, "rec_product_id": 45, "weight": .5 }
        rec = Recommendation()
        rec.deserialize(data_one)
        rec.save()

        data_two = { "product_id": 87, "rec_type_id": 2, "rec_product_id": 51, "weight": .5 }
        rec = Recommendation()
        rec.deserialize(data_two)
        rec.save()

        # Assuming the client will provide a product id and category as a String
        rec = Recommendation.find_by_product_id(87)[0]

        self.assertIsNot(rec, None)
        self.assertEqual(rec.product_id, 87)
        self.assertEqual(rec.rec_type_id, 2)
        self.assertEqual(rec.rec_product_id, 51)
        self.assertEqual(rec.weight, .5)

    def test_find_with_no_recommendation_data(self):
        """ Find a Recommendation with no Recommendations """
        rec = Recommendation.find_by_id(1)
        self.assertIs(rec, None)

    def test_recommendation_not_found_with_data(self):
        """ Test for a Recommendation that doesn't exist """
        data_one = { "product_id": 23, "rec_type_id": 1, "rec_product_id": 45, "weight": .5 }
        rec = Recommendation()
        rec.deserialize(data_one)
        rec = Recommendation.find_by_id(2)
        self.assertIs(rec, None)

    def test_good_database_connection(self):
        """ Pass in a good db connection """
        test_app = Flask(__name__)
        test_app.config.from_object('config.TestingConfig')
        self.assertIsNotNone(db)

    def test_incorrect_database_connection(self):
        """ Pass in the connection with incorrect info """
        
        bad_connection = 'postgres://recommendations:password@localhost:9999/recommendations'
        app.config["SQLALCHEMY_DATABASE_URI"] = bad_connection
        self.assertRaises(OperationalError, init_db)

    def test_passing_bad_connection_string(self):
        """ Pass in a bad connection string """

        app.config["SQLALCHEMY_DATABASE_URI"] = 'Bad Connection'

        self.assertRaises(OperationalError, init_db)

    @patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(VCAP_SERVICES)})
    def test_vcap_services(self):
        """ Test if VCAP_SERVICES works """
        app.config.from_object('config.ProductionConfig')
        init_db
        self.assertIsNotNone(db)

    @patch('app.models.db.session.commit')
    def test_db_error_on_save(self, db_error_mock):
        """ Test Rollback on save """
        current_rec_count = len(Recommendation.all())
        db_error_mock.side_effect = OperationalError()
        data = { 'product_id': 23, 'rec_type_id': "up-sell", 'rec_product_id': 45, 'weight': .5 }
        rec = Recommendation()
        rec.deserialize(data)
        new_rec_count = len(Recommendation.all())
        self.assertEqual(current_rec_count, new_rec_count)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestRecommendations)
    # unittest.TextTestRunner(verbosity=2).run(suite)
