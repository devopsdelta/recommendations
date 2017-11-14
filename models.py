"""
Models for Recommendation Service

All of the models are stored in this module

Models
------
Recommendation - A recommendation based on a product with similar attributes

Attributes:
-----------
productId (int) - the id of the product that will be used to get recommendations for

"""
import threading
import os
import json
import psycopg2
import urlparse
import logging

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Recommendation(object):
    """
    Class that represents a Recommendation

    This version uses an in-memory collection of recommendations for testing
    """
    lock = threading.Lock()
    data = []

    def __init__(self, pid=0, rec=""):
        """ Initialize a Recommendation """
        self.id = pid
        self.recommendation = rec

    def save(self):
        """
        Saves a Recommendation to the data store
        """

        index = 0

        for i in range(len(Recommendation.data)):
            if (Recommendation.data[i].id != self.id):
                continue
            index = i

        if index == 0:
            Recommendation.data.append(self)
        else:
            Recommendation.data[index] = self

    def delete(self):
        """ Removes a Recommendation from the data store """
        Recommendation.data.remove(self)

    def serialize(self):
        """ Serializes a Recommendation into a dictionary """
        return {"id": self.id, "recommendation": self.recommendation}

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the Recommendation data
        """
        if not isinstance(data, dict):
            raise DataValidationError('Invalid product: body of request contained bad or no data')

        if data.has_key('id'):
            self.id = data['id']

        try:
            self.recommendation = data['recommendation']
        except KeyError as err:
            raise DataValidationError('Invalid product: missing ' + err.args[0])
        return

    @staticmethod
    def all():
        """ Returns all of the Products in the database """
        return [recommendation for recommendation in Recommendation.data]

    @staticmethod
    def remove_all():
        """ Removes all of the Recommendation from the database """
        del Recommendation.data[:]
        return Recommendation.data

    @staticmethod
    def find_by_id(id):
        """ Finds a Recommendation by it's ID """
        if not Recommendation.data:
            return None

        recommendations = [recommendation for recommendation in Recommendation.data if recommendation.id == id]

        if recommendations:
            return recommendations[0]

        return None

    @staticmethod
    def find_by_category(value):
        """ Finds a Recommendation by it's Category """

        if not Recommendation.data:
            return None

        search_criteria = value.lower()
        results = []

        for recommendation in Recommendation.data:
            if search_criteria in recommendation.recommendation['category']:
                results.append(recommendation)
                
        return results

#################################################################################
#  E L E P H A N T S Q L   D A T A B A S E   C O N N E C T I O N   M E T H O D S
#################################################################################

    @staticmethod
    def connect_to_elephantsql(database, user, password, host, port):
        """ Connects to ElephantSQL and tests the connection """
        logging.info("Testing Connection to: %s:%s", host, port)
        try:
            conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
            logging.info("Connection established")
            Recommendation.conn = conn
        except:
            logging.info("Connection Error from: %s:%s", host, port)
            Recommendation.conn = None
        return Recommendation.conn

    @staticmethod
    def init_db(conn=None):
        """
        Initialized ElephantSQL database connection

        This method will work in the following conditions:
          1) In Bluemix with ElephantSQL bound through VCAP_SERVICES
          2) With ElephantSQL running on the local server as with Travis CI
          3) With PostgresSQL --link in a Docker container called 'postgres'
          4) Passing in your own ElephantSQL connection object

        Exception:
        ----------
          psycopg2.OperationalError - if connect() fails
        """
        if conn:
            logging.info("Using client connection...")
            Recommendation.conn = conn
            try:
                #status = Recommendation.conn.poll()
                cur = conn.cursor()
                cur.execute('SELECT 1')
            except:
                logging.error("Client Connection Error!")
                Recommendation.conn = None
                raise psycopg2.OperationalError("Could not connect to the ElephantSQL Service")
            return
        # Get the credentials from the Bluemix environment
        if 'VCAP_SERVICES' in os.environ:
            logging.info("Using VCAP_SERVICES...")
            vcap_services = os.environ['VCAP_SERVICES']
            services = json.loads(vcap_services)
            creds = services['elephantsql'][0]['credentials']
            uri = creds['uri']
            urlparse.uses_netloc.append("postgres")
            url = urlparse.urlparse(uri)
            logging.info("Conecting to ElephantSQL on host %s port %s",url.hostname, url.port)
            Recommendation.connect_to_elephantsql(url.path[1:], url.username, url.password, url.hostname, url.port)
        else:
            logging.info("VCAP_SERVICES not found, checking localhost for ElephantSQL")
            Recommendation.connect_to_elephantsql('postgres', '', '', '127.0.0.1', 5432)
            if not Recommendation.conn:
                logging.info("No ElephantSQL on localhost")
        if not Recommendation.conn:
            # if you end up here, postgres instance is down.
            logging.fatal('*** FATAL ERROR: Could not connect to the ElephantSQL Service')
