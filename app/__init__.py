from flask import Flask
from flask_restful import Api


api = Api()


def create_app():
    app = Flask(__name__)
    api.init_app(app)
    return app

import main