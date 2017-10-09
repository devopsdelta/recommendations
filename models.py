# Copyright 2016, 2017 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Models for Product Demo Service

All of the models are stored in this module

Models
------
Product - A Product used in the Product Store

Attributes:
-----------
name (string) - the name of the product
category (string) - the category the product belongs to (i.e., dog, cat)

"""
import threading

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Product(object):
    """
    Class that represents a Product

    This version uses an in-memory collection of products for testing
    """
    lock = threading.Lock()
    data = []
    index = 0

    def __init__(self, id=0, name='', category=''):
        """ Initialize a Product """
        self.id = id
        self.name = name
        self.category = category

    def save(self):
        """
        Saves a Product to the data store
        """
        if self.id == 0:
            self.id = self.__next_index()
            Product.data.append(self)
        else:
            for i in range(len(Product.data)):
                if Product.data[i].id == self.id:
                    Product.data[i] = self
                    break

    def delete(self):
        """ Removes a Product from the data store """
        Product.data.remove(self)

    def serialize(self):
        """ Serializes a Product into a dictionary """
        return {"id": self.id, "name": self.name, "category": self.category}

    def deserialize(self, data):
        """
        Deserializes a Product from a dictionary

        Args:
            data (dict): A dictionary containing the Product data
        """
        if not isinstance(data, dict):
            raise DataValidationError('Invalid product: body of request contained bad or no data')
        if data.has_key('id'):
            self.id = data['id']
        try:
            self.name = data['name']
            self.category = data['category']
        except KeyError as err:
            raise DataValidationError('Invalid product: missing ' + err.args[0])
        return

    @staticmethod
    def __next_index():
        """ Generates the next index in a continual sequence """
        with Product.lock:
            Product.index += 1
        return Product.index

    @staticmethod
    def all():
        """ Returns all of the Products in the database """
        return [product for product in Product.data]

    @staticmethod
    def remove_all():
        """ Removes all of the Products from the database """
        del Product.data[:]
        Product.index = 0
        return Product.data

    @staticmethod
    def find(product_id):
        """ Finds a Product by it's ID """
        if not Product.data:
            return None
        products = [product for product in Product.data if product.id == product_id]
        if products:
            return products[0]
        return None

    @staticmethod
    def find_by_category(category):
        """ Returns all of the Products in a category

        Args:
            category (string): the category of the Products you want to match
        """
        return [product for product in Product.data if product.category == category]

    @staticmethod
    def find_by_name(name):
        """ Returns all Products with the given name

        Args:
            name (string): the name of the Products you want to match
        """
        return [product for product in Product.data if product.name == name]
