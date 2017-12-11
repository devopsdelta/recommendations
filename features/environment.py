"""
Environment for Behave Testing
"""
import os
from behave import *
from selenium import webdriver
os.environ['TEST'] = 'True'
BASE_URL = os.getenv('BASE_URL', 'http://0.0.0.0:8081')

def before_all(context):
    """ Executed once before all tests """
    context.driver = webdriver.PhantomJS()
    context.driver.set_window_size(1120, 550)
    context.base_url = BASE_URL
