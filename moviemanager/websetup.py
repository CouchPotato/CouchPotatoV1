"""Setup the MovieManager application"""
from moviemanager.config.environment import load_environment
from moviemanager.model.meta import Session, Base
import logging
import pylons.test

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup moviemanager here"""
    # Don't reload the app if it was loaded under the testing environment

    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)

    # Create the tables if they don't already exist
    log.info("Creating tables")
    #Base.metadata.drop_all(checkfirst=True, bind=Session.bind)
    Base.metadata.create_all(bind=Session.bind)
    log.info("Successfully setup")