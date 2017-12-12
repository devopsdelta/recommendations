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
  rec_prod_id  (int)     - The id of the product being recommended
  weight       (float)   - Weight determined by our algorithm

"""
import threading
import os
import json
import urlparse
import logging
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, DateTime
from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.orm import relationship, backref, sessionmaker
from flask_sqlalchemy import Model, SQLAlchemy
from psycopg2 import OperationalError
from app.connection import get_database_uri

""" Base DB Model """
class BaseModel(Model):
    __abstract__ = True

    @classmethod
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

    def delete(self):
        try:
            db.session.delete(self)
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
    # PK | Name      | Is Active | Product Query
    # --------------------------------------------------------
    # 1  | "up-sell" | 1         | "?category=shoes&price>0"
    #
    __tablename__ = 'recommendation_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True, nullable=False)
    is_active = Column(Boolean, nullable=False)
    product_query = Column(String(255), nullable=False)
    # Category="originalproductCategory", Price > current Product Price + 1


    def __init__(self, Name=None, active=True, query=None):
        self.name = Name
        self.is_active = active
        self.product_query = query

    def __repr__(self):
        return '{ "type_id": %i, "name": "%s" }' % (self.id, self.name)

    def serialize(self):
        """ Serializes a Recommendation Type into a dictionary """
        return { 'id': self.id, \
                'name': self.name, \
                'is_active': self.is_active}

    @classmethod
    def find_by_name(cls, rec_name):
        """ Find a Recommendation Type By Name """
        return (cls.query.filter_by(name=str(rec_name.lower()))
                .filter_by(is_active=True)).first()

# PK | PRODUCT_ID   | TYPE
# 1  | 2 (Converse) | 1 (up-sell)
# 2  | 2 (Converse) | 2 (accessory)

""" Recommendation per category """
class Recommendation(db.Model):
    """ Class that represents a Recommendation """
    # PK | Product Id | Type Id | Recommendation Prod Id | Weight
    # ------------------------------------------------------------
    # 1  | 23         | 1       | 32                    | .6
    # 2  | 23         | 2       | 34                    | .6
    # 3  | 33         | 1       | 45                    | .6


    __tablename__ = 'recommendation'
    id = Column(Integer, primary_key = True)
    product_id = Column(Integer, unique=False)
    rec_type_id = Column(Integer, ForeignKey('recommendation_type.id'), nullable=False)
    rec_product_id = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)

    rec_type = relationship('RecommendationType')

    def __repr__(self):
        return '{ "id": %s, "product_id": %s, "rec_type_id": %s, "rec_product_id": %s, "weight": %s}' % (self.id, self.product_id, self.rec_type_id, self.rec_product_id, self.weight)

    def serialize(self):
        """ Serializes a Recommendation into a dictionary """
        return {'id': self.id, \
                'product_id': self.product_id, \
                'rec_type': self.rec_type.serialize(), \
                'rec_product_id': self.rec_product_id, \
                'weight': self.weight}

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary
        Args:
            data (dict): A dictionary containing the Recommendation data
        """

        if not isinstance(data, dict):
            raise DataValidationError('Invalid recommendation: body of request contained bad or no data')

        try:
            self.product_id = data['product_id']
            self.rec_type_id = data['rec_type_id']
            self.rec_product_id = data['rec_product_id']
            self.weight = float(data['weight'])
        except KeyError as err:
            raise DataValidationError('Invalid recommendation: missing ' + err.args[0])
        return

    @classmethod
    def find_by_product_id(cls, prod_id):
        """ Find all Recommendations by Product Id """
        return (cls.query.filter_by(product_id=int(prod_id))
                .filter(cls.rec_type.has(RecommendationType.is_active == True))).all()

    @classmethod
    def find_by_type(cls, rec_type):
        """ Find all Recommendations by Recommenation Type """
        return (cls.query.filter_by(rec_type_id = rec_type.id)
                .filter(cls.rec_type.has(RecommendationType.is_active == True))).all()

    @classmethod
    def find_by_product_id_and_type(cls, prod_id, rec_type):
        """ Find all Recommendations by Product Id and Type """
        return (cls.query
                .filter_by(product_id=int(prod_id))
                .filter(cls.rec_type.has(RecommendationType.id == rec_type.id))
                .filter(cls.rec_type.has(RecommendationType.is_active == True))).all()

#################################################################################
#  E L E P H A N T S Q L   D A T A B A S E   C O N N E C T I O N   M E T H O D S
#################################################################################

def init_db(app):
    """
    Initialized database connection

    Exception:
    ----------
      OperationalError - if connect() fails
    """

    try:
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
    RecommendationType(Name='up-sell', active=True, query='category=values').save()
    RecommendationType(Name='accessory', active=True, query='category=values').save()
    RecommendationType(Name='cross-sell', active=False, query='category=values').save()
