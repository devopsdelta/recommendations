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
from werkzeug.exceptions import NotFound
from models import Recommendation, RecommendationType, init_db, DataValidationError
from engine import Engine
# Create Flask application
app = Flask(__name__)
app.config.from_object('config')

DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '8081')

@app.template_global()
def static_include(filename):
    fullpath = os.path.join(app.static_folder, filename)
    with open(fullpath, 'r') as f:
        return f.read()

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(400)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=400, error='Bad Request', message=message), 400

@app.errorhandler(ValueError)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=400, error='Bad Request', message=message), 400

@app.errorhandler(404)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=404, error='Not Found', message=message), 404

@app.errorhandler(405)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=405, error='Method not Allowed', message=message), 405

@app.errorhandler(500)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=500, error='Internal Server Error', message=message), 500

######################################################################
# Views
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    return render_template('index.html', name='Recommendation Demo REST API Service',
                   version='1.0',
                   paths=url_for('list_recommendations', _external=True)), status.HTTP_200_OK

@app.route('/recommendations/metadata')
def metadata():
    """ Metadata View """
    return render_template('metadata.html', name='Manage Recommendation Meta Data'), status.HTTP_200_OK

@app.route('/recommendations/docs')
def docs():
    """ Documentation View """
    return render_template('docs.html', name='Documentation'), status.HTTP_200_OK

@app.route('/recommendations/manage')
def manage_recommendations():
    """ Manage Recommendation View """
    return render_template('recommendations.html'), status.HTTP_200_OK

######################################################################
# LIST ALL RECOMMENDATIONS
######################################################################
@app.route('/recommendations', methods=['GET'])
def list_recommendations():
    """ Returns all of the Recommendations """
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

    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# RETRIEVE A RECOMMENDATION
######################################################################
@app.route('/recommendations/<int:recommendation_id>', methods=['GET'])
def get_recommendations(recommendation_id):
    """
    Retrieve a single Recommendation

    This endpoint will return a Recommendations based on it's id
    """
    recommendation = Recommendation.find_by_id(recommendation_id)

    if not recommendation:
        raise NotFound("Recommendations with id '{}' was not found.".format(recommendation_id))

    return make_response(jsonify(recommendation.serialize()), status.HTTP_200_OK)


######################################################################
# ADD A NEW RECOMMENDATION
######################################################################
@app.route('/recommendations', methods=['POST'])
def create_recommendations():
    """
    Creates a Recommendation

    This endpoint will create a Recommendations based the data in the body that is posted.
    We assume when a user ask for a recommendation they will provide a Product Id
    And a Type in the following format:
        { 'product_id': <int>, 'type': '<[up-sell|accessory|cross-sell]>' }
    """
    data = request.get_json()
    rec = Recommendation()
    rec.deserialize(data)


    #recs = Recommendation.find_by_product_id_and_type(rec.product_id, rec.rec_type)

    # TODO: Based on our session, we decided that in the event a previous recommendation
    #       Is found we should we delete the previous recommendation and rerun the engine

    # if not recs:
        # TODO: Determine what products will be recommended based on product id and
        #       Recommendation type

        # TODO: Place a GET call to the Product API to get the product details for the
        #       Product we need to make a recommendation for

        # TODO: Make a GET call to the Product API query method to get products
        #       That will be used to make our recommendations. Loop through each
        #       Products that is returned and run it through our engine.

        # TODO: Place our 'Canned' recommendations here. In other words, if for
        #       Any reason our engine is unable to make recommendations
        #       (i.e. the Product service is down) return a standard set of
        #       Products (for isinstance, most popular)
        # rec_detail1 = RecommendationDetail(10, .6)
        # rec_detail2 = RecommendationDetail(20, .7)
        # rec_detail3 = RecommendationDetail(30, .67)
        # rec.recommendations.append(rec_detail1)
        # rec.recommendations.append(rec_detail2)
        # rec.recommendations.append(rec_detail3)
    rec.save()

    message = rec.serialize()
    location_url = url_for('get_recommendations', recommendation_id=rec.id, _external=True)

    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             'Location': location_url
                         })

######################################################################
# UPDATE AN EXISTING RECOMMENDATION
######################################################################
@app.route('/recommendations/<int:recommendation_id>', methods=['PUT'])
def update_recommendations(recommendation_id):
    """
    Update a Recommendation

    This endpoint will update a Recommendations based the body that is posted
    """
    recommendation = Recommendation.find_by_id(recommendation_id)

    if not recommendation:
        raise NotFound("Recommendation with id '{}' was not found.".format(recommendation_id))


    recommendation.deserialize(request.get_json())
    recommendation.id = recommendation_id
    recommendation.save()

    return make_response(jsonify(recommendation.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE A RECOMMENDATION
######################################################################
@app.route('/recommendations/<int:recommendation_id>', methods=['DELETE'])
def delete_recommendations(recommendation_id):
    """
    Delete a Recommendation

    This endpoint will delete a Recommendation based the id specified in the path
    """
    recommendation = Recommendation.find_by_id(recommendation_id)

    if not recommendation:
        raise NotFound("Recommendation with id '{}' was not found.".format(recommendation_id))

    recommendation.delete()

    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def initialize_logging(log_level):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print 'Setting up logging...'

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

def initialize_db():
    init_db(app)

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    print "Recommendation Service Starting..."
    initialize_logging(logging.INFO)
    initialize_db()
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG, use_reloader=False)
