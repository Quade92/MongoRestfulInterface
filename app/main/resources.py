from flask import request, make_response
from flask_restful import Resource
from bson.json_util import loads, dumps
from flask_pymongo import MongoClient
from pymongo.errors import OperationFailure
from run import config_name, auth_db
from config import db_config, transform_data
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


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
            mongo[db_config[config_name]["data_db"]].authenticate(request.authorization.username,
                                                                  request.authorization.password)
            # QUERY: return the latest record
            # TODO records length need some restriction maybe
            records = mongo[db_config[config_name]["data_db"]][db_config[config_name]["trans_data_col"]].find(
                {"$and": [{"timestamp": {"$gte": start}}, {"timestamp": {"$lte": end}}]}).sort("_id", -1)
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
            mongo[db_config[config_name]["data_db"]].authenticate(request.authorization.username,
                                                                  request.authorization.password)
            # QUERY: return the latest record
            latest_record = mongo[db_config[config_name]["data_db"]] \
                [db_config[config_name]["trans_data_col"]].find().sort("_id", -1)[0]
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
            mongo[db_config[config_name]["data_db"]].authenticate(request.authorization.username,
                                                                  request.authorization.password)
            data = request.data
            # TODO: insert transformed data here
            raw_req = loads(data)
            raw_json = raw_req["data"]
            trans_json = transform_data(raw_json)
            raw_insert_result = mongo[db_config[config_name]["data_db"]] \
                [db_config[config_name]["raw_data_col"]].insert_one(raw_json)
            trans_insert_result = mongo[db_config[config_name]["data_db"]] \
                [db_config[config_name]["trans_data_col"]].insert_one(trans_json)
            resp_data = {
                "err": "False",
                "message": "Successfully inserted",
                "result": {
                    "raw_insert_id": raw_insert_result.inserted_id,
                    "trans_insert_id": trans_insert_result.inserted_id
                }
            }
            resp = make_response(dumps(resp_data))
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


class AuthenticateByPassword(BaseClassWithCORS):
    def get(self):
        try:
            request_data = loads(request.data)
            user = auth_db["user"].find_one({"un": request_data["un"]})
            checked = check_password_hash(user["pwd"], request_data["pwd"])
            if checked:
                token = uuid.uuid4().hex
                data = {
                    "err": "False",
                    "message": "Successfully auth",
                    "result": {"token": token}
                }
            else:
                data = {
                    "err": "True",
                    "message": "Auth failed!",
                    "result": {}
                }
            resp = make_response(dumps(data))
            resp.headers.extend({
                "Access-Control-Allow-Origin": "*"
            })
            return resp
        except OperationFailure, err:
            return {
                "err": "True",
                "message": "Auth failed!",
                "result": err.details
            }

    class LatestRecordSet(BaseClassWithCORS):
        def get(self, amount):
            mongo = MongoClient(host=db_config[config_name]["host"], port=db_config[config_name]["port"])
            try:
                mongo[db_config[config_name]["data_db"]].authenticate(request.authorization.username,
                                                                      request.authorization.password)
                latest_records = mongo[db_config[config_name]["data_db"]] \
                                     [db_config[config_name]["trans_data_col"]] \
                                     .find().sort("_id", -1)[:amount]
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

    class LatestRecordGivenTimestamp(BaseClassWithCORS):
        def get(self, timestamp):
            mongo = MongoClient(host=db_config[config_name]["host"], port=db_config[config_name]["port"])
            try:
                mongo[db_config[config_name]["data_db"]].authenticate(request.authorization.username,
                                                                      request.authorization.password)
                latest_record = mongo[db_config[config_name]["data_db"]][db_config[config_name]["trans_data_col"]]. \
                    find({"timestamp": {"$lte": timestamp}}).sort("_id", -1)[0]
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

    class LatestRecordSetGivenTimestamp(BaseClassWithCORS):
        def get(self, timestamp, amount):
            mongo = MongoClient(host=db_config[config_name]["host"], port=db_config[config_name]["port"])
            try:
                mongo[db_config[config_name]["data_db"]].authenticate(request.authorization.username,
                                                                      request.authorization.password)
                latest_record_set = mongo[db_config[config_name]["data_db"]][db_config[config_name]["trans_data_col"]]. \
                                        find({"timestamp": {"$lte": timestamp}}).sort("_id", -1)[:amount]
                data = {
                    "err": "False",
                    "message": "Successfully auth",
                    "result": latest_record_set
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

    class Register(BaseClassWithCORS):
        def post(self):
            try:
                request_data = loads(request.data)
                new_json = {
                    "un": request_data["un"],
                    "pwd": generate_password_hash(request_data["pwd"], method='pbkdf2:sha1')
                }
                register_insert = auth_db["user"].insert_one(new_json)
                resp_data = {
                    "err": "False",
                    "message": "Successfully auth",
                    "result": register_insert.inserted_id
                }
                resp = make_response(dumps(resp_data))
                resp.headers.extend({
                    "Access-Control-Allow-Origin": "*"
                })
                return resp
            except OperationFailure, err:
                return {
                    "err": "True",
                    "message": "Failed registering",
                    "result": err.details
                }
