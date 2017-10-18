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
