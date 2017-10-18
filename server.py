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
from flask import Flask, jsonify, request, url_for, make_response
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound
from models import Recommendation, DataValidationError

# Create Flask application
app = Flask(__name__)

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '8080')

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
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    return jsonify(name='Recommendation Demo REST API Service',
                   version='1.0',
                   paths=url_for('list_recommendations', _external=True)
                  ), status.HTTP_200_OK

######################################################################
# LIST ALL RECOMMENDATIONS
######################################################################
@app.route('/recommendations', methods=['GET'])
def list_recommendations():
    """ Returns all of the Recommendations """
    category = request.args.get('category')
    recommendations = []
    results = []

    if category:
        recommendations = Recommendation.find_by_category(category)
    else:
        recommendations = Recommendation.all()

    if recommendations:
        results = [recommendation.serialize() for recommendation in recommendations]
        return make_response(jsonify(results), status.HTTP_200_OK)

    raise NotFound("No Recommendations found.")

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

    This endpoint will create a Recommendations based the data in the body that is posted
    """
    recommendation = Recommendation()
    recommendation.deserialize(request.get_json())
    recommendation.save()

    message = recommendation.serialize()
    location_url = url_for('get_recommendations', recommendation_id=recommendation.id, _external=True)

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

    if recommendation:
        recommendation.delete()

    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# ACTION 2 ON RECOMMENDATION
######################################################################
@app.route('/recommendations/rating', methods=['GET'])
def rating_recommendation():
    """
    Rate the Recommendation app

    This endpoint will return the overall rating of Recommendation app
    """
    recommendations = []

    recommendations = Recommendation.all()
    overall_rating = 0
    count = 0

    for recommendation in recommendations:
        rating = recommendation.recommendation['rating']
        overall_rating = int(overall_rating) + int(rating)
        count += 1

    rate = float(overall_rating) / float(count)

    return make_response(str(rate), status.HTTP_200_OK)

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


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    print "Recommendation Service Starting..."
    initialize_logging(logging.INFO)
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
