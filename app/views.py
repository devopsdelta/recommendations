from server import app
from flask import render_template, request
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound
from models import Recommendation, init_db, db, RecommendationType

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
    type_name = request.args.get('type')
    rec_type = None

    if type_name:
        rec_type = RecommendationType.find_by_name(type_name)
        if not rec_type:
            raise NotFound("Recommendations with type '{}' was not found.".format(type_name))

    if rec_type:
        recs = Recommendation.find_by_type(rec_type)
    else:
        recs = Recommendation.all()

    results = [rec.serialize() for rec in recs if rec is not None]
    return render_template('manage.html', name="Manage", result=results), status.HTTP_200_OK

@app.route('/recommendations/docs')
def view_documentation():
    """ Manage Documentation View """
    return render_template('docs.html', name="Documentation"), status.HTTP_200_OK

@app.route('/recommendations/detail/<int:recommendation_id>')
def rec_detail(recommendation_id):
    """ Manage Recommendation Detail"""
    rec = Recommendation.find_by_id(recommendation_id)
    recJSON = rec.serialize()
    return render_template('manage/detail.html',
                            detail_id = recJSON["id"],
                            product_id=recJSON["product_id"] ,
                            rec_type = recJSON["rec_type"]["id"],
                            rec_product_id = recJSON["rec_product_id"],
                            weight = recJSON["weight"],
                            status = recJSON["rec_type"]["is_active"]),status.HTTP_200_OK

@app.route('/recommendations/manage/<int:recommendation_id>')
def create_recommendations(recommendation_id):
    """ Create Recommendation View """
    data = request.get_json()
    rec = Recommendation()
    rec.deserialize(data)
    rec.save()
    message = rec.serialize()

    return render_template('manage.html', name="Manage", result=message), status.HTTP_201_CREATED
