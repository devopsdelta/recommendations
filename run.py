"""
Recommendation Service Runner

Start the Pet Service and initializes logging
"""

import os
from app import app, server, views

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '8081')

#########################################################################
#   M A I N
#########################################################################
if __name__ == "__main__":
    print "*************************************************************"
    print " R E C O M M E N D A T I O N   S E R V I C E   R U N N I N G "
    print "*************************************************************"
    server.initialize_logging()
    server.initialize_db()
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
