"""
Recommendation Service

Paths:
------
GET /recommendations - Returns a list all of previously created recommendations
GET /recommendations/{id} - Returns the Recommendations with a given id number
POST /recommendations - creates a new Recommendation record in the database
PUT /recommendations/{id} - updates an existing Recommendations record in the database
DELETE /recommendations/{id} - deletes a Recommendations record in the database
"""

import os
import sys
import logging
import requests
from flask import Flask, jsonify, request, url_for, make_response, json, render_template
from flask_api import status    # HTTP Status Codes
from flask_restplus import Resource
from werkzeug.exceptions import NotFound
from models import Recommendation, RecommendationType, init_db, DataValidationError, db
from engine import Engine
from . import app
from swagger import api, ns, recommendation_model, expected_create_model

@app.template_global()
def static_include(filename):
    fullpath = os.path.join(app.static_folder, filename)
    with open(fullpath, 'r') as f:
        return f.read()

@app.before_first_request
def initialize_db():
    """ Initialize the model """
    init_db()

@ns.route('/<int:recommendation_id>')
@ns.param('recommendation_id', 'The Recommendation identifier')
class RecommendationResource(Resource):
    ######################################################################
    # RETRIEVE A RECOMMENDATION
    ######################################################################
    @ns.doc('get_recommendations')
    @ns.response(404, 'Recommendation not found')
    @ns.marshal_with(recommendation_model)
    def get(self, recommendation_id):
        """ Retrieve a single Recommendation

        This endpoint will return a Recommendations based on it's id
        """
        recommendation = Recommendation.find_by_id(recommendation_id)

        recJSON = ""
        if not recommendation:
            raise NotFound("Recommendations with id '{}' was not found.".format(recommendation_id))
        else:
            recJSON = recommendation.serialize()

        return recJSON, status.HTTP_200_OK

    ######################################################################
    # UPDATE AN EXISTING RECOMMENDATION
    ######################################################################
    @ns.doc('update_recommendation')
    @ns.response(404, 'Recommendation not found')
    @ns.response(400, 'The posted Recommendation data was not valid')
    @ns.expect(expected_create_model)
    @ns.marshal_with(recommendation_model)
    def put(self, recommendation_id):
        """ Update a Recommendation

        This endpoint will update a Recommendations based the body that is posted
        """
        recommendation = Recommendation.find_by_id(recommendation_id)

        if not recommendation:
            raise NotFound("Recommendation with id '{}' was not found.".format(recommendation_id))

        recommendation.deserialize(request.get_json())
        recommendation.id = recommendation_id
        recommendation.save()

        return recommendation.serialize(), status.HTTP_200_OK


    ######################################################################
    # DELETE A RECOMMENDATION
    ######################################################################
    @ns.doc('delete_recommendation')
    @ns.response(204, 'Recommendation deleted')
    def delete(self, recommendation_id):
        """ Delete a Recommendation

        This endpoint will delete a Recommendation based the id specified in the path
        """
        recommendation = Recommendation.find_by_id(recommendation_id)

        if not recommendation:
            raise NotFound("Recommendation with id '{}' was not found.".format(recommendation_id))

        recommendation.delete()

        return '', status.HTTP_204_NO_CONTENT

@ns.route('/', strict_slashes=False)
class RecommendationCollection(Resource):
    ######################################################################
    # LIST ALL RECOMMENDATIONS
    ######################################################################
    @ns.doc('list_recs')
    @ns.param('type', 'Get Recommendation By Type (i.e. up-sell, accessory, cross-sell, etc)')
    @ns.param('product_id', 'Get Recommendation By Product Id')
    @ns.response(500, 'There was an issue resolving your request')
    @ns.marshal_list_with(recommendation_model)
    def get(self):
        """ Returns all Recommendations """

        type_name = request.args.get('type')
        product_id = request.args.get('product_id')
        results = []
        rec_type = None

        if type_name:
            rec_type = RecommendationType.find_by_name(type_name)
            if not rec_type:
                raise NotFound("Recommendations with type '{}' was not found.".format(type_name))

        if rec_type and product_id:
            recs = Recommendation.find_by_product_id_and_type(product_id, rec_type)
        elif rec_type:
            recs = Recommendation.find_by_type(rec_type)
        elif product_id:
            recs = Recommendation.find_by_product_id(product_id)
        else:
            recs = Recommendation.all()

        results = [rec.serialize() for rec in recs if rec is not None]

        return results, status.HTTP_200_OK

    @ns.doc('create_recommendation')
    @ns.expect(expected_create_model)
    @ns.response(400, 'The posted data was not valid')
    @ns.response(201, 'Recommendation created successfully')
    @ns.marshal_with(recommendation_model, code=201)
    def post(self):
        """ Creates a Recommendation

        This endpoint will create a Recommendations based the data in the body that is posted.
        We assume when a user ask for a recommendation they will provide a Product Id
        And a Type in the following format:
            { 'product_id': <int>, 'type': '<[up-sell|accessory|cross-sell]>' }
        """

        #data = request.get_json()
        rec = Recommendation()
        rec.deserialize(api.payload)
        rec.save()

        location_url = api.url_for(RecommendationResource, recommendation_id=rec.id, _external=True)

        return rec.serialize(), status.HTTP_201_CREATED, {'Location': location_url}

@ns.route('/activate/<int:type_id>')
@ns.param('type_id', 'The Recommendation activate action')
class ActivateResource(Resource):

    ######################################################################
    #  ACTION 1: ACTIVATE A RECOMMENDATION TYPE
    ######################################################################
    @ns.doc('activate_recommendation')
    @ns.response(404, 'Recommendation not found')
    @ns.response(409, 'The Recommendation is not available to activate')
    def put(self, type_id):
        """ Activate a Recommendation Type

        This endpoint will activate a Recommendation type based the type specified in the path
        """

        rec_type = RecommendationType.find_by_id(type_id)

        if not rec_type:
            raise NotFound("Recommendations with type '{}' was not found.".format(type_id))

        rec_type.is_active = True
        rec_type.save()

        return rec_type.serialize(), status.HTTP_200_OK

@ns.route('/deactivate/<int:type_id>')
@ns.param('type_id', 'The Recommendation deactivate action')
class DeactivateResource(Resource):
    ######################################################################
    #  ACTION 2: DEACTIVATE A RECOMMENDATION TYPE
    ######################################################################
    @ns.doc('deactivate_recommendation')
    @ns.response(404, 'Recommendation not found')
    @ns.response(409, 'The Recommendation is not available to deactivate')
    def put(self, type_id):
        """ Deactivate a Recommendation Type

        This endpoint will deactivate a Recommendation type based the type specified in the path
        """
        rec_type = RecommendationType.find_by_id(type_id)

        if not rec_type:
            raise NotFound("Recommendations with type '{}' was not found.".format(type_id))

        rec_type.is_active = False
        rec_type.save()

        return 'Recommendation Type {} is deactivated.\n'.format(type), status.HTTP_200_OK

######################################################################
# DELETE ALL RECOMMENDATION DATA (for testing only)
######################################################################
@app.route('/recommendations/reset', methods=['DELETE'])
def reset_recommendations():
    """ Removes all recommendations from the database """
    db.session.remove()
    db.drop_all()
    init_db()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def initialize_logging():
    """ Initialized the default logging to STDOUT """

    print 'Setting up logging...'

    log_level = app.config['LOGGING_LEVEL']
    # Set up default logging for submodules to use STDOUT
    # datefmt='%m/%d/%Y %I:%M:%S %p'
    fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)

    # Make a new log handler that uses STDOUT
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt))
    handler.setLevel(log_level)

    # Remove the Flask default handlers and use our own
    handler_list = list(app.logger.handlers)

    for log_handler in handler_list:
        app.logger.removeHandler(log_handler)

    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)
    app.logger.info('Logging handler established')
