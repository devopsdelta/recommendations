import os
import json
import logging
import config

def get_database_uri(db_name='development'):
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
        username = 'postgres'
        password = 'password'
        hostname = 'localhost'
        port = '5432'

        raise ValueError(TESTING)

        logging.info("Connecting to database on host %s port %s",
                     hostname, port)

        uri = 'postgres://{}:{}@{}:{}/{}'
        uri = uri.format(username, password, hostname, port, db_name)

    return uri
