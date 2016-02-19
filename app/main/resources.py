from flask import request, make_response
from flask_restful import Resource
from bson.json_util import loads, dumps
from flask_pymongo import MongoClient
from pymongo.errors import OperationFailure
from run import config_name
from config import db_config


class RecordSeries(Resource):
    def get(self, start, end):
        mongo = MongoClient(host=db_config[config_name]["host"], port=db_config[config_name]["port"])
        try:
            mongo[db_config[config_name]["db"]].authenticate(request.authorization.username,
                                                             request.authorization.password)
            # QUERY: return the latest record
            # TODO records length need some restriction maybe
            records = mongo[db_config[config_name]["db"]][db_config[config_name]["collection"]].find(
                    {"$and": [{"timestamp": {"$gt": start}}, {"timestamp": {"$lt": end}}]}).sort("_id", 1)
            result = [record for record in records]
            return {
                       "err": "False",
                       "message": "Successfully get data",
                       "result": {"data": dumps(result)}
            }
        except OperationFailure, err:
            return {
                "err": "True",
                "message": "Failed getting data",
                "result": err.details
            }


class LatestRecord(Resource):
    def get(self):
        mongo = MongoClient(host=db_config[config_name]["host"], port=db_config[config_name]["port"])
        try:
            mongo[db_config[config_name]["db"]].authenticate(request.authorization.username,
                                                             request.authorization.password)
            # QUERY: return the latest record
            last_record = mongo[db_config[config_name]["db"]]\
                [db_config[config_name]["collection"]].find().sort("_id", -1)[0]
            return {
                       "err": "False",
                       "message": "Successfully get data",
                       "result": {"data": dumps(last_record)}
            }
        except OperationFailure, err:
            return {
                "err": "True",
                "message": "Failed getting data",
                "result": err.details
            }


class Record(Resource):
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

class Authenticate(Resource):
    def options(self):
        resp = make_response("")
        resp.headers.extend({
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Authorization"
            })
        return resp

    def get(self):
        mongo = MongoClient(host=db_config[config_name]["host"], port=db_config[config_name]["port"])
        try:
            auth = mongo[db_config[config_name]["db"]].authenticate(request.authorization.username,
                                                             request.authorization.password)
            data = {
                "err": "False",
                "message": "Successfully auth",
                "result": {"data": auth, "ack": auth}
            }
            resp = make_response(dumps(data))
            resp.headers.extend({
                "Access-Control-Allow-Origin": "*",
            })
            return resp
        except OperationFailure, err:
            return {
                "err": "True",
                "message": "",
                "result": err.details
            }

class LatestRecordSet(Resource):
    def get(self, amount):
        mongo = MongoClient(host=db_config[config_name]["host"], port=db_config[config_name]["port"])
        try:
            mongo[db_config[config_name]["db"]].authenticate(request.authorization.username,
                                                             request.authorization.password)
            last_record = mongo[db_config[config_name]["db"]]\
                [db_config[config_name]["collection"]].find().sort("_id", -1)[:amount]
            return {
                       "err": "False",
                       "message": "Successfully get data",
                       "result": {"data": dumps(last_record)}
            }
        except OperationFailure, err:
            return {
                "err": "True",
                "message": "Failed getting data",
                "result": err.details
            }