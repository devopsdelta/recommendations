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
    index = 0

    def __init__(self, id=0, pid=0):
        """ Initialize a Recommendation """
        self.id = id
        self.product_id = pid

    def save(self):
        """
        Saves a Recommendation to the data store
        """
        if self.id == 0:
            self.id = self.__next_index()
            Recommendation.data.append(self)
        else:
            for i in range(len(Recommendation.data)):
                if Recommendation.data[i].id == self.id:
                    Recommendation.data[i] = self
                    break

    def delete(self):
        """ Removes a Recommendation from the data store """
        Recommendation.data.remove(self)

    def serialize(self):
        """ Serializes a Recommendation into a dictionary """
        return {"id": self.id, "product_id": self.product_id}

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
            self.product_id = data['product_id']
        except KeyError as err:
            raise DataValidationError('Invalid product: missing ' + err.args[0])
        return

    @staticmethod
    def __next_index():
        """ Generates the next index in a continual sequence """
        with Recommendation.lock:
            Recommendation.index += 1
        return Recommendation.index

    @staticmethod
    def all():
        """ Returns all of the Products in the database """
        return [recommendation for recommendation in Recommendation.data]

    @staticmethod
    def remove_all():
        """ Removes all of the Recommendation from the database """
        del Recommendation.data[:]
        Recommendation.index = 0
        return Recommendation.data

    @staticmethod
    def find(recommendation_id):
        """ Finds a Recommendation by it's ID """
        if not Recommendation.data:
            return None

        recommendations = [recommendation for recommendation in Recommendation.data if recommendation.id == recommendation_id]

        if recommendations:
            return recommendations[0]

        return None