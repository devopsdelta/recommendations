"""
Microservice module
This module contains the microservice code for
    engine
    models
    server
    swagger
    views
"""
import os
from flask import Flask

APP_SETTING = os.getenv('APP_SETTING', 'DevelopmentConfig')

# Create the Flask aoo
app = Flask(__name__)
app.config.from_object('config.%s' % str(APP_SETTING))

# Service needs app so must be placed after app is created
import engine
import models
import server
import swagger
import views