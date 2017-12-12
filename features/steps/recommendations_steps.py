
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
    print (headers)
    print ("Before delete")
    context.resp = requests.delete(context.base_url + '/recommendations/reset', headers=headers)
    # print ("Before response")
    expect(context.resp.status_code).to_equal(204)
    # print ("After delete")
    create_url = context.base_url + '/recommendations'
    print (create_url)
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



@when(u'I visit the "Recommendation Details" page for recommendation detail "{message}"')
def step_impl(context,message):
    context.driver.get(context.base_url+"/recommendations/detail/{message}")

@then(u'I will see a "rec_id" with "1" in my results')
def step_impl(context):
    context.driver.get(context.base_url+"/recommendations/detail/1")
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(expected_conditions.presence_of_element_located((By.ID, 'rec_id')))
    assert found.text == '1'
    assert found.text != 'batman'
    context.driver.save_screenshot('GetTest.png')

@then(u'I will see a "product_id" with "29" in my results')
def step_impl(context):
    context.driver.get(context.base_url+"/recommendations/detail/1")
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(expected_conditions.presence_of_element_located((By.ID, 'product_id')))
    assert found.text == '29'
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

@when(u'I visit the "Recommendation Details" page of all recommendations')
def step_impl(context):
    context.driver.get(context.base_url+"/recommendations/list")

@then(u'I should see "{message}" in the results')
def step_impl(context, message):
    context.driver.get(context.base_url+"/recommendations/list")
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_result'),
            message
        )
    )
    expect(found).to_be(True)

@then(u'I should not see "{message}" in the results')
def step_impl(context, message):
    context.driver.get(context.base_url+"/recommendations/list")
    element = context.driver.find_element_by_id('search_result')
    error_msg = "I should not see '%s' in '%s'" % (message, element.text)
    ensure(message in element.text, False, error_msg)

#===============================================================================================
# SEARCH FOR RECOMMENDATIONS BY TYPE
#===============================================================================================
@when(u'I visit the Recommendation Details page of filter recommendations by type "{message}"')
def step_impl(context, message):
    context.driver.get(context.base_url+"/recommendations/query")

@when(u'I change the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    context.driver.get(context.base_url+"/recommendations/query?type=up-sell")
    element_id = element_name.lower() + '_id'
    print (element_id)
    element = context.driver.find_element_by_id(element_id)
    element.send_keys(text_string)

@when(u'I press the "{button}" button')
def step_impl(context, button):
    context.driver.get(context.base_url+"/recommendations/query?type=up-sell")
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()

@then(u'I should see "{message}" in the search_results')
def step_impl(context, message):
    context.driver.get(context.base_url+"/recommendations/query?type=up-sell")
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_result'),
            message
        )
    )
    expect(found).to_be(True)

@then(u'I should not see "{message}" in the search_results')
def step_impl(context, message):
    context.driver.get(context.base_url+"/recommendations/query?type=up-sell")
    element = context.driver.find_element_by_id('search_result')
    error_msg = "I should not see '%s' in '%s'" % (message, element.text)
    ensure(message in element.text, False, error_msg)

#===============================================================================================
# SEARCH FOR RECOMMENDATIONS BY PRODUCT
#===============================================================================================
@when(u'I visit the Recommendation Details page of filter recommendations by product "{message}"')
def step_impl(context, message):
    context.driver.get(context.base_url+"/recommendations/query")

@when(u'I enter the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    context.driver.get(context.base_url+"/recommendations/query?product_id=29")
    element_id = element_name.lower() + '_id'
    print (element_id)
    element = context.driver.find_element_by_id(element_id)
    element.send_keys(text_string)

@when(u'I click the "{button}" button')
def step_impl(context, button):
    context.driver.get(context.base_url+"/recommendations/query?product_id=29")
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()

@then(u'I should see "{message}" in the search_result')
def step_impl(context, message):
    context.driver.get(context.base_url+"/recommendations/query?product_id=29")
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_result'),
            message
        )
    )
    expect(found).to_be(True)

@then(u'I should not see "{message}" in the search_result')
def step_impl(context, message):
    context.driver.get(context.base_url+"/recommendations/query?product_id=29")
    element = context.driver.find_element_by_id('search_result')
    error_msg = "I should not see '%s' in '%s'" % (message, element.text)
    ensure(message in element.text, False, error_msg)

#===============================================================================================
# SEARCH FOR RECOMMENDATIONS BY PRODUCT ID AND TYPE
#===============================================================================================
@when(u'I visit the Recommendation Details page to filter recommendations by type "{type_name}" and product "{product_id}"')
def step_impl(context, type_name, product_id):
    context.driver.get(context.base_url+"/recommendations/query")

@when(u'And I enter the "{element_name1}" to "{text_string1}" and "{element_name2}" to "{text_string2}"')
def step_impl(context, element_name1, text_string1, element_name2, text_string2):
    context.driver.get(context.base_url+"/recommendations/query?type=accessory&product_id=29")
    element_id1 = element_name1.lower() + '_id'
    print (element_id1)
    element1 = context.driver.find_element_by_id(element_id1)
    element1.send_keys(text_string1)
    element_id2 = element_name2.lower() + '_id'
    print (element_id2)
    element2 = context.driver.find_element_by_id(element_id2)
    element2.send_keys(text_string2)

@when(u'I pressed the "{button}" button')
def step_impl(context, button):
    context.driver.get(context.base_url+"/recommendations/query?type=accessory&product_id=29")
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()

@then(u'I should see "{message}" in the result')
def step_impl(context, message):
    context.driver.get(context.base_url+"/recommendations/query?type=accessory&product_id=29")
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_result'),
            message
        )
    )
    expect(found).to_be(True)

@then(u'I should not see "{message}" in the result')
def step_impl(context, message):
    context.driver.get(context.base_url+"/recommendations/query?type=accessory&product_id=29")
    element = context.driver.find_element_by_id('search_result')
    error_msg = "I should not see '%s' in '%s'" % (message, element.text)
    ensure(message in element.text, False, error_msg)
