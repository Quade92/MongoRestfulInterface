import flask
import flask_restful
import route
import getpass
import flask_pymongo
import config

auth_db_host = config.db_config[config.config_name]["auth_db"]["host"]
auth_db_port = config.db_config[config.config_name]["auth_db"]["port"]
auth_db_client = flask_pymongo.MongoClient(host=auth_db_host,port=auth_db_port)
auth_db = auth_db_client[config.db_config[config.config_name]["auth_db"]["db"]]


data_db_host = config.db_config[config.config_name]["data_db"]["host"]
data_db_port = config.db_config[config.config_name]["data_db"]["port"]
data_db_mongo = flask_pymongo.MongoClient(host=data_db_host, port=data_db_port)
data_db = data_db_mongo[config.db_config[config.config_name]["data_db"]["db"]]
trans_col = config.db_config[config.config_name]["data_db"]["trans_data_col"]
raw_col = config.db_config[config.config_name]["data_db"]["raw_data_col"]


api = flask_restful.Api()
route.init_route()


def create_app():
    auth_db.authenticate(raw_input("auth database username:"),
                         getpass.getpass(prompt="auth database password:"))
    data_db.authenticate(raw_input("data database username:"),
                         getpass.getpass(prompt="data database password:"))
    flask_app = flask.Flask(__name__)
    api.init_app(flask_app)
    return flask_app
