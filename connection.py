import os
import json
import logging

def get_database_uri():
    """
    Initialized ElephantSQL database connection

    This method will work in the following conditions:
      1) In Bluemix with ElephantSQL bound through VCAP_SERVICES
      2) With ElephantSQL running on the local server as with Travis CI
      3) With PostgresSQL --link in a Docker container called 'postgres'
      4) Passing in your own ElephantSQL connection object

    Exception:
    ----------
      OperationalError - if connect() fails
    """

    if 'VCAP_SERVICES' in os.environ:
        # Get the credentials from the Bluemix environment
        logging.info("Using VCAP_SERVICES...")
        vcap_services = os.environ['VCAP_SERVICES']
        services = json.loads(vcap_services)
        creds = services['elephantsql'][0]['credentials']
        uri = creds["uri"]

     else:
        logging.info("Using localhost database...")
        name = 'postgres'
        
        if 'TEST' in os.environ:
            name = 'test'
        else:
            name = 'development'
        uri = 'postgres://postgres:password@localhost:5432/{}'
        uri.format(name)

    return uri