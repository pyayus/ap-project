from flask_sqlalchemy import SQLAlchemy

import logging
logging.basicConfig()
logger = logging.getLogger('sqlalchemy.engine')
logger.setLevel(logging.DEBUG)

db = SQLAlchemy()
