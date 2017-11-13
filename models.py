"""
Models for Recommendation Service

All of the models are stored in this module

Models
------
Base Model          - Represents columns that are used for all tables
Recommendation      - A recommendation based on a product with similar attributes
Recommendations     - Each product and it's weight
Recommendation Type - A lookup table for the type of recommendations (i.e. up-sell, cross-sell, accessory, etc)

Attributes:
-----------
Base Model
  __abstract__           - Indicates that this object must be inherited
  _created    (DateTime) - The DateTime that this record was created
  _updated    (DateTime) - The DateTime that this record was last _updated

Recommendation_type
  rec_type_id  (int)      - Auto incrimented id (PK)
  name         (char)     - The Name of this type (i.e. up-sell, cross-sell, accessory, etc)
  is_active    (boolean)  - Determines if this recommendation type can be used
  product_query(char)     - Store query that should be used against the product
                            API to get a list of potiential recommendations and then apply weight to

Recommendation
  rec_id      (int)      - Auto incrimented id (PK)
  product_id  (int)      - the id of the product that will be used to get recommendations for
  rec_type_id  (int)     - The type of recommendation

RecommendationDetail
  prod_rec_id  (int)     - Auto incrimented id (PK)
  rec_id       (int)     - foreign key to Recommendation table
  weight       (float)   - Weight determined by our algorithm
  rec_prod_id  (int)     - The id of the product being recommended
  dislike_count(int)     - Was the provided disliked

"""
import threading
import os
import json
import urlparse
import logging
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, DateTime
from sqlalchemy import Index
from sqlalchemy.orm import relationship, backref, sessionmaker
from flask_sqlalchemy import Model, SQLAlchemy
from psycopg2 import OperationalError

LOCAL_HOST_URI = u'postgres://recommendations:password@localhost:5432/recommendations'

""" Base DB Model """
class BaseModel(Model):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    created = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.utcnow, default=datetime.utcnow)

    def save(self):
        try:
            if not self.id:
                db.session.add(self)

            db.session.commit()
        except:
            db.session.rollback()

    @classmethod
    def all(cls):
        """ Returns all records from the database """
        return cls.query.all()

    @classmethod
    def count(cls):
        """ Return the total number of records in table """
        return cls.query.count()

    @classmethod
    def remove_all(cls):
        """ Removes all records from the database for a particular Recommendation """
        cls.query.delete()

    @classmethod
    def find_by_id(cls, id):
        """ Find a Record by primary key """
        return cls.query.get(id)

db = SQLAlchemy(model_class=BaseModel)

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class RecommendationType(db.Model):
    """ Lookup table to store the Recommendation Types """

    __tablename__ = 'recommendation_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True, nullable=False)
    is_active = Column(Boolean, nullable=False)
    # TODO: Store the query that will be used to call the Product service
    # product_query = Column(String(255), nullable=False) Category="originalproductCategory", Price > current Product Price + 1

    def __init__(self, Name=None, active=True):
        self.name = Name
        self.is_active = active

    def __repr__(self):
        return '{ "type_id": %i, "name": "%s" }' % (self.id, self.name)

    def serialize(self):
        """ Serializes a Recommendation Type into a dictionary """
        return { 'id': self.id,
                'name': self.name,
                'is_active': self.is_active}

    @classmethod
    def find_by_name(cls, rec_name):
        """ Find a Recommendation Type By Name """
        return cls.query.filter_by(name=str(rec_name.lower())).first()

""" Recommendation per category """
class Recommendation(db.Model):
    """
    Class that represents a Recommendation
    """
    __tablename__ = 'recommendation'
    id = Column(Integer, primary_key = True)
    product_id = Column(Integer, unique=False)
    rec_type_id = Column(Integer, ForeignKey('recommendation_type.id'), nullable=False)
    dislike_count = Column(Integer, nullable=False, default=0)

    rec_type = relationship('RecommendationType')
    recommendations = relationship('RecommendationDetail', backref="recommendation")

    def __init__(self, prod_id=-1, rec_type=None):
        self.product_id = prod_id
        if rec_type:
            self.rec_type = RecommendationType.find_by_id(rec_type.id)
        else:
            self.rec_type = RecommendationType.find_by_id(1)

    def __repr__(self):
        return '{ "id": %i, "product_id": %i, "type_id": %i, "rec_type": "%s", "dislike_count": %i }' % (self.id, self.product_id, self.rec_type_id, self.rec_type.name, self.dislike_count)

    def serialize(self):
        """ Serializes a Recommendation into a dictionary """
        return { 'id': self.id,
                'product_id': self.product_id,
                'rec_type_id': self.rec_type_id,
                'rec_type': self.rec_type.serialize(),
                'recommendations': [rec.serialize() for rec in self.recommendations],
                'dislike_count': self.dislike_count}

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary
        Args:
            data (dict): A dictionary containing the Recommendation data
        """

        if not isinstance(data, dict):
            raise DataValidationError('Invalid recommendation: body of request contained bad or no data')

        try:
            r_type = RecommendationType.find_by_name(data['type'])

            self.product_id = data['product_id']
            self.rec_type_id = r_type.id
        except KeyError as err:
            raise DataValidationError('Invalid recommendation: missing ' + err.args[0])
        return

    def delete(self):
        try:
            for rec in self.recommendations:
                rec.delete()

            db.session.delete(self)
            db.session.commit()
        except:
            db.session.rollback()

    @classmethod
    def find_by_product_id(cls, prod_id):
        """ Find all Recommendations by Product Id """
        return cls.query.filter_by(product_id=int(prod_id)).all()

    @classmethod
    def find_by_type(cls, rec_type):
        """ Find all Recommendations by Recommenation Type """
        return cls.query.filter_by(rec_type_id = rec_type.id).all()

    @classmethod
    def find_by_product_id_and_type(cls, prod_id, rec_type):
        """ Find all Recommendations by Product Id and Type """
        return (cls.query
                .filter_by(product_id=int(prod_id))
                .filter(cls.rec_type.has(RecommendationType.id == rec_type.id))).all()

class RecommendationDetail(db.Model):
    """ Represents the details of a recommendation """
    __tablename__ = 'recommendation_detail'
    id = Column(Integer, primary_key = True)
    rec_id = Column(Integer, ForeignKey('recommendation.id'), nullable=False)
    rec_product_id = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    dislike_count = Column(Integer, nullable=False, default=0)

    def __init__(self, recommended_prod_id, fweight):
        self.rec_product_id = recommended_prod_id
        self.weight = fweight

    def __repr__(self):
        return '{ "id": %i, "rec_id": %i, "rec_product_id": %i, "weight": %f, "dislike_count": %i }' % \
            (self.id, self.rec_id, self.rec_product_id, self.weight, self.dislike_count)

    def serialize(self):
        """ Serializes a Recommendation into a dictionary """
        return { 'id': self.id,
                'rec_id': self.rec_id,
                'rec_product_id': self.rec_product_id,
                'weight': self.weight,
                'dislike_count': self.dislike_count }

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            db.session.rollback()

    @classmethod
    def find_by_recommendation_id(cls, recommendation_id):
        """ Find all Recommendations by Product Id """
        return cls.query.filter_by(rec_id=recommendation_id).all()

    @classmethod
    def find_by_rec_id_and_product_id(cls, recommendation_id, product_id):
        """ Find all Recommendation Details by Recommendation Id and Product Id """
        return (cls.query
                .filter_by(rec_id=recommendation_id)
                .filter_by(rec_product_id=product_id)).first()

#################################################################################
#  E L E P H A N T S Q L   D A T A B A S E   C O N N E C T I O N   M E T H O D S
#################################################################################

def init_db(app, conn=None):
    """
    Initialized ElephantSQL database connection

    This method will work in the following conditions:
      1) In Bluemix with ElephantSQL bound through VCAP_SERVICES
      2) With ElephantSQL running on the local server as with Travis CI
      3) With PostgresSQL --link in a Docker container called 'postgres'
      4) Passing in your own ElephantSQL connection object

    Exception:
    ----------
      OperationalError - if connect() fails
    """

    if conn:
        logging.info("Using client connection...")
        app.config['SQLALCHEMY_DATABASE_URI'] = conn
    elif 'VCAP_SERVICES' in os.environ:
        # Get the credentials from the Bluemix environment
        logging.info("Using VCAP_SERVICES...")
        vcap_services = os.environ['VCAP_SERVICES']
        services = json.loads(vcap_services)
        creds = services['elephantsql'][0]['credentials']
        uri = creds['uri']
        urlparse.uses_netloc.append("postgres")
        url = urlparse.urlparse(uri)
        logging.info("Conecting to ElephantSQL on host %s port %s", url.hostname, url.port)
        app.config['SQLALCHEMY_DATABASE_URI'] = uri
    else:
        logging.info("VCAP_SERVICES not found, checking localhost for ElephantSQL")
        app.config['SQLALCHEMY_DATABASE_URI'] = LOCAL_HOST_URI

    try:
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        app.app_context().push()
        db.create_all()

        if len(RecommendationType.all()) == 0:
            seed_db()

    except Exception as e:
        logging.fatal(e.message)
        raise OperationalError(e.message)

def seed_db():
    logging.info("Seeding database tables")
    RecommendationType(Name='up-sell').save()
    RecommendationType(Name='accessory').save()
    RecommendationType(Name='cross-sell').save()
