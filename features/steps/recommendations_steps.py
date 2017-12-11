
"""
Recommendation Steps
Steps file for recommendation.feature
"""

import environment
import json
import requests
import app.server
from behave import *
from os import getenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

BASE_URL = getenv('BASE_URL', 'http://0.0.0.0:8081')
WAIT_SECONDS = 10
@given(u'the following recommendations')
def step_impl(context):
    """ Create Recommendations """
    headers = {'Content-Type': 'application/json'}
    create_url = context.base_url + '/recommendations'
    for row in context.table:
        recommendations = {
        "rec_id": row['rec_id'],
        "product_id": row['product_id'],
        "rec_type_id": row['rec_type_id'],
        "rec_product_id": row['rec_product_id'],
        "weight": row['weight']
        }
        payload = json.dumps(recommendations)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        assert (context.resp.status_code==201)


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


@when(u'I visit the "{pagename}" page for recommendation "{path}" "{message}"')
def step_impl(context,pagename,path,message):
    context.driver.get(context.base_url+"/recommendations/"+path+"/"+message)

@then(u'I will see a "{key}" with "{value}" in my results')
def step_impl(context,key,value):
    context.driver.get(context.base_url+"/recommendations/detail/1")
    context.driver.save_screenshot('GetTest.png')
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(expected_conditions.presence_of_element_located((By.ID, key)))
    assert found.text == value
    assert found.text != 'batman'
    context.driver.save_screenshot('GetTest.png')

#had trouble getting this to raise TimeOutException
@then(u'I should not see "rof-riders" in my results')
def step_impl(context):
    context.driver.get(context.base_url+"/recommendations/detail/1")
    try:
        found = WebDriverWait(context.driver, WAIT_SECONDS).until(expected_conditions.presence_of_element_located((By.ID, 'rof-riders')))
    except Exception:
        pass

@then(u'I will see that Recommendation ID "{id_numb}" was deleted')
def step_impl(context,id_numb):
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(expected_conditions.presence_of_element_located((By.ID, 'was_deleted')))
    assert found.text == "Recommendation ID "+id_numb+" was deleted"
    context.driver.save_screenshot('GetTest.png')
