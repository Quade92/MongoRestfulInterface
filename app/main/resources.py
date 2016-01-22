from flask import request
from flask_restful import Resource
from bson.json_util import loads, dumps
from flask_pymongo import MongoClient
from pymongo.errors import OperationFailure
from run import config_name
from config import db_config


class LastRecord(Resource):
    def get(self):
        mongo = MongoClient(host=db_config[config_name]["host"], port=db_config[config_name]["port"])
        try:
            mongo[db_config[config_name]["db"]].authenticate(request.authorization.username,
                                                             request.authorization.password)
            # return the latest record
            last_log = mongo[db_config[config_name]["db"]]\
                [db_config[config_name]["collection"]].find().sort("_id", -1)[0]
            return {
                       "err": "False",
                       "message": "Successfully get data",
                       "result": {"data": dumps(last_log)}
            }
        except OperationFailure, err:
            return {
                "err": "True",
                "message": "Failed getting data",
                "result": err.details
            }

    def post(self):
        mongo = MongoClient(host=db_config[config_name]["host"], port=db_config[config_name]["port"])
        try:
            mongo[db_config[config_name]["db"]].authenticate(request.authorization.username,
                                                             request.authorization.password)
            data = request.data
            l = loads(data)
            result = mongo[db_config[config_name]["db"]]\
                [db_config[config_name]["collection"]].insert_one(l["data"])
            return {
                "err": "False",
                "message": "Successfully post data",
                "result": {"data": dumps(l["data"]), "ack": str(result.acknowledged)}
            }
        except OperationFailure, err:
            return {
                "err": "True",
                "message": "Failed post data",
                "result": err.details
            }
