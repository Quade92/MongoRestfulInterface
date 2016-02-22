from flask import request, make_response
from flask_restful import Resource
from bson.json_util import loads, dumps
from flask_pymongo import MongoClient
from pymongo.errors import OperationFailure
from run import config_name
from config import db_config

class BaseClassWithCORS(Resource):
    def options(self, **kwargs):
        resp = make_response("")
        resp.headers.extend({
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST",
                "Access-Control-Allow-Headers": "Authorization"
            })
        return resp


class RecordSeries(BaseClassWithCORS):
    def get(self, start, end):
        mongo = MongoClient(host=db_config[config_name]["host"], port=db_config[config_name]["port"])
        try:
            mongo[db_config[config_name]["db"]].authenticate(request.authorization.username,
                                                             request.authorization.password)
            # QUERY: return the latest record
            # TODO records length need some restriction maybe
            records = mongo[db_config[config_name]["db"]][db_config[config_name]["collection"]].find(
                    {"$and": [{"timestamp": {"$gt": start}}, {"timestamp": {"$lt": end}}]}).sort("_id", 1)
            records = [record for record in records]
            data = {
                "err": "False",
                "message": "Successfully auth",
                "result": records
            }
            resp = make_response(dumps(data))
            resp.headers.extend({
                "Access-Control-Allow-Origin": "*"
            })
            return resp
        except OperationFailure, err:
            return {
                "err": "True",
                "message": "Failed getting data",
                "result": err.details
            }


class LatestRecord(BaseClassWithCORS):
    def get(self):
        mongo = MongoClient(host=db_config[config_name]["host"], port=db_config[config_name]["port"])
        try:
            mongo[db_config[config_name]["db"]].authenticate(request.authorization.username,
                                                             request.authorization.password)
            # QUERY: return the latest record
            latest_record = mongo[db_config[config_name]["db"]]\
                [db_config[config_name]["collection"]].find().sort("_id", -1)[0]
            data = {
                "err": "False",
                "message": "Successfully auth",
                "result": latest_record
            }
            resp = make_response(dumps(data))
            resp.headers.extend({
                "Access-Control-Allow-Origin": "*"
            })
            return resp
        except OperationFailure, err:
            return {
                "err": "True",
                "message": "Failed getting data",
                "result": err.details
            }


class Record(BaseClassWithCORS):
    def post(self):
        mongo = MongoClient(host=db_config[config_name]["host"], port=db_config[config_name]["port"])
        try:
            mongo[db_config[config_name]["db"]].authenticate(request.authorization.username,
                                                             request.authorization.password)
            data = request.data
            l = loads(data)
            result = mongo[db_config[config_name]["db"]]\
                [db_config[config_name]["collection"]].insert_one(l["data"])
            data = {
                "err": "False",
                "message": "Successfully auth",
                "result": result
            }
            resp = make_response(dumps(data))
            resp.headers.extend({
                "Access-Control-Allow-Origin": "*"
            })
            return resp
        except OperationFailure, err:
            return {
                "err": "True",
                "message": "Failed post data",
                "result": err.details
            }

class Authenticate(BaseClassWithCORS):
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
                "Access-Control-Allow-Origin": "*"
            })
            return resp
        except OperationFailure, err:
            return {
                "err": "True",
                "message": "",
                "result": err.details
            }

class LatestRecordSet(BaseClassWithCORS):
    def get(self, amount):
        mongo = MongoClient(host=db_config[config_name]["host"], port=db_config[config_name]["port"])
        try:
            mongo[db_config[config_name]["db"]].authenticate(request.authorization.username,
                                                             request.authorization.password)
            latest_records = mongo[db_config[config_name]["db"]]\
                [db_config[config_name]["collection"]].find().sort("_id", -1)[:amount]
            data = {
                "err": "False",
                "message": "Successfully auth",
                "result": latest_records
            }
            resp = make_response(dumps(data))
            resp.headers.extend({
                "Access-Control-Allow-Origin": "*"
            })
            return resp
        except OperationFailure, err:
            return {
                "err": "True",
                "message": "Failed getting data",
                "result": err.details
            }