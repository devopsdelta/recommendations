
"""
Recommendation Steps
Steps file for recommendation.feature
"""

from os import getenv
import json
import requests
from behave import *
import server
import environment

BASE_URL = getenv('BASE_URL', 'http://0.0.0.0:8081')

@given(u'the following recommendations')
def step_impl(context):
    """ Create Recommendations """
    # for rows in context.table:
        # model.create(name=row['name'], department=row['department']))
    #TODO: MAKE THE CREATE
    pass

@when(u'I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)

@then(u'I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    assert message in context.driver.title

@then(u'I should not see "404 Not Found"')
def step_impl(context):
    """ Check to make sure there is no 404 message """
    context.resp = requests.get(context.base_url)
    assert context.resp.status_code !=404

@when(u'I visit the "Recommendation Details" page for recommendation detail "{message}"')
def step_impl(context,message):
    context.driver.get(context.base_url+"/recommendations/detail/{message}")

@then(u'I will see a "product_id" with "3512" in my results')
def step_impl(context):
    context.driver.find_element_by_id("product_id")

@then(u'I will see a "type_id" with "up-sell" in my results')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I will see a "type_id" with "up-sell" in my results')

@then(u'I will see a "rec_product_id" with "6783" in my results')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I will see a "rec_product_id" with "6783" in my results')

@then(u'I will see a "weight" with ".52" in my results')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I will see a "weight" with ".52" in my results')

@then(u'I should not see "rof-riders" in my results')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I should not see "rof-riders" in my results')
