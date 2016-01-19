from flask import request
from flask_restful import Resource
from bson.json_util import loads, dumps
from flask_pymongo import MongoClient
from pymongo.errors import OperationFailure


class LastRecord(Resource):
    def get(self):
        data = request.data
        l = loads(data)
        mongo = MongoClient(host="localhost", port=27999)
        try:
            mongo.sensorLog.authenticate(l["username"], l["pwd"])
            # return the latest record
            last_log = mongo["sensorLog"]["sensorlogs"].find().sort("_id", -1)[0]
            return {"err": "False", "result": {"data": dumps(last_log)}}
        except OperationFailure, err:
            return {"err": "True","result": err.details}
    def post(self):
        data = request.data
        l = loads(data)
        mongo = MongoClient(host="localhost", port=27999)
        try:
            mongo.sensorLog.authenticate(l["username"], l["pwd"])
            result = mongo["sensorLog"]["sensorlogs"].insert_one(l["data"])
            return {"err": "False", "result": {"data": dumps(l["data"]), "ack": str(result.acknowledged)}}
        except OperationFailure, err:
            return {"err": "True", "result": err.details}
