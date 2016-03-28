import flask
import flask_restful
import route
import getpass
import flask_pymongo
import config


auth_db = flask_pymongo.MongoClient(host=config.db_config[config.config_name]["host"],
                                    port=config.db_config[config.config_name]["port"])[config.db_config[config.config_name]["auth_db"]]
auth_db.authenticate(raw_input("auth database username:"), getpass.getpass(prompt="auth database password:"))

api = flask_restful.Api()
route.init_route()

def create_app():
    flask_app = flask.Flask(__name__)
    api.init_app(flask_app)
    return flask_app
