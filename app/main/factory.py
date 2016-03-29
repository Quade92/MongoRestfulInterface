import flask
import flask_restful
import route
import getpass
import flask_pymongo
import config

auth_db_host = config.db_config[config.config_name]["auth_db"]["host"]
auth_db_port = config.db_config[config.config_name]["auth_db"]["port"]
auth_db_client = flask_pymongo.MongoClient(host=auth_db_host,port=auth_db_port)
db = config.db_config[config.config_name]["auth_db"]["db"]
auth_db = auth_db_client[db]
api = flask_restful.Api()
route.init_route()


def create_app():
    auth_db.authenticate(raw_input("auth database username:"),
                         getpass.getpass(prompt="auth database password:"))
    flask_app = flask.Flask(__name__)
    api.init_app(flask_app)
    return flask_app
