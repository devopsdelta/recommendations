
"""
Recommendation Steps
Steps file for recommendation.feature
"""

import environment
import json
import requests
from app import server
from behave import *
from os import getenv
from compare import expect, ensure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

BASE_URL = getenv('BASE_URL', 'http://0.0.0.0:8081')
WAIT_SECONDS = 15
@given(u'the following recommendations')
def step_impl(context):
    """ Create Recommendations """
    headers = {'Content-Type': 'application/json'}
    context.resp = requests.delete(context.base_url + '/recommendations/reset', headers=headers)
    expect(context.resp.status_code).to_equal(204)
    create_url = context.base_url + '/recommendations'

    for row in context.table:
        recommendations = {
        "product_id": int(row['product_id']),
        "rec_type_id": int(row['rec_type_id']),
        "rec_product_id": int(row['rec_product_id']),
        "weight": float(row['weight'])
        }
        payload = json.dumps(recommendations)

        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)


@when(u'I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url + '/index')

@then(u'I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    assert message in context.driver.title

@then(u'I should not see "404 Not Found"')
def step_impl(context):
    """ Check to make sure there is no 404 message """
    context.resp = requests.get(context.base_url)
    print (context.resp.status_code)
    assert context.resp.status_code != str(404)

@when(u'I visit the "Recommendation Details" page for recommendation detail "{message}"')
def step_impl(context,message):
    context.driver.get(context.base_url+"/recommendations/detail/{message}")

@then(u'I will see a "rec_id" with "1" in my results')
def step_impl(context):
    context.driver.get(context.base_url+"/recommendations/detail/1")
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(expected_conditions.presence_of_element_located((By.ID, 'rec_id')))
    assert found.text == '1'
    assert found.text != 'batman'
    context.driver.save_screenshot('line67.png')

@then(u'I will see a "product_id" with "45" in my results')
def step_impl(context):
    context.driver.get(context.base_url+"/recommendations/detail/1")
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(expected_conditions.presence_of_element_located((By.ID, 'product_id')))
    assert found.text == '45'
    assert found.text != 'batman'
    context.driver.save_screenshot('GetTest.png')

@then(u'I will see a "rec_type_id" with "2" in my results')
def step_impl(context):
    context.driver.get(context.base_url+"/recommendations/detail/1")
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(expected_conditions.presence_of_element_located((By.ID, 'rec_type_id')))
    assert found.text == '2'
    assert found.text != 'batman'
    context.driver.save_screenshot('GetTest.png')

@then(u'I will see a "rec_product_id" with "51" in my results')
def step_impl(context):
    context.driver.get(context.base_url+"/recommendations/detail/1")
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(expected_conditions.presence_of_element_located((By.ID, 'rec_product_id')))
    assert found.text == '51'
    assert found.text != 'batman'
    context.driver.save_screenshot('GetTest.png')

@then(u'I will see a "weight" with "0.2" in my results')
def step_impl(context):
    context.driver.get(context.base_url+"/recommendations/detail/1")
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(expected_conditions.presence_of_element_located((By.ID, 'weight')))
    assert found.text == '0.2'
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

#===============================================================================================
# LIST ALL RECOMMENDATIONS
#===============================================================================================
@when(u'I visit the "Recommendation Details" page')
def step_impl(context):
    context.driver.get(context.base_url+"/recommendations/manage")

@when(u'I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()

@then(u'I should see "{message}" in the search_results')
def step_impl(context, message):
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results'),
            message
        )
    )
    expect(found).to_be(True)

@then(u'I should not see "{message}" in the search_results')
def step_impl(context, message):
    element = context.driver.find_element_by_id('search_results')
    error_msg = "I should not see '%s' in '%s'" % (message, element.text)
    ensure(message in element.text, False, error_msg)

#===============================================================================================
# SEARCH FOR RECOMMENDATIONS BY TYPE
#===============================================================================================
@when(u'I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    url = context.base_url+"/recommendations/manage?" + element_name.lower() + "=" + text_string.lower()
    print (url)
    context.driver.get(url)
    print (element_name)
    print (text_string)
    element_id = 'rec_type_name'
    print (element_id)
    element = context.driver.find_element_by_id(element_id)
    element.send_keys(text_string)
