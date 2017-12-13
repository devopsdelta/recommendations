from server import app
from flask import render_template
from flask_api import status    # HTTP Status Codes
from models import Recommendation

######################################################################
# Views
######################################################################
@app.route('/index')
def index():
    """ Root URL response """
    return render_template('index.html', name='Recommendation Demo REST API Service',
                   version='1.0'), status.HTTP_200_OK

@app.route('/recommendations/metadata')
def metadata():
    """ Metadata View """
    return render_template('metadata.html', name='Manage Recommendation Meta Data'), status.HTTP_200_OK

@app.route('/recommendations/manage')
def manage_recommendations():
    """ Manage Recommendation View """
    return render_template('recommendations.html', name="Manage"), status.HTTP_200_OK

@app.route('/recommendations/docs')
def view_documentation():
    """ Manage Documentation View """
    return render_template('docs.html', name="Documentation"), status.HTTP_200_OK

@app.route('/recommendations/detail/<int:recommendation_id>')
def rec_detail(recommendation_id):
    """ Manage Recommendation Detail"""
    rec = Recommendation.find_by_id(recommendation_id)
    recJSON = rec.serialize()
    return render_template('recommendation.html',
                            detail_id = recJSON["id"],
                            product_id=recJSON["product_id"] ,
                            rec_type = recJSON["rec_type"]["id"],
                            rec_product_id = recJSON["rec_product_id"],
                            weight = recJSON["weight"],
                            status = recJSON["rec_type"]["is_active"]),status.HTTP_200_OK