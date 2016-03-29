import flask
import flask_restful
import flask_pymongo
import pymongo.errors
import factory
import config
from bson.json_util import loads, dumps
import werkzeug.security
import uuid
import datetime


class BaseClassWithCORS(flask_restful.Resource):
    def options(self, **kwargs):
        resp = flask.make_response("")
        resp.headers.extend({
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST",
            "Access-Control-Allow-Headers": "Authorization, Content-Type"
        })
        return resp


class RecordSeries(BaseClassWithCORS):
    def get(self, start, end):
        data_db_host = config.db_config[config.config_name]["data_db"]["host"]
        data_db_port = config.db_config[config.config_name]["data_db"]["port"]
        data_db_mongo = flask_pymongo.MongoClient(host=data_db_host, port=data_db_port)
        db = config.db_config[config.config_name]["data_db"]["db"]
        data_db = data_db_mongo[db]
        trans_col = config.db_config[config.config_name]["data_db"]["trans_data_col"]
        try:
            auth_headers = flask.request.headers.get("Authorization")
            method, token = auth_headers.split(" ")
            checked = factory.auth_db["token"].find({"token": token})
            if checked:
                factory.auth_db["token"].update_one(
                    {"token": token},
                    {
                        "$inc": {
                            "expir": 604800000
                        }
                    }
                )
                records = data_db[trans_col].find({
                    "$and": [{"timestamp": {"$gte": start}},
                             {"timestamp": {"$lte": end}}]}
                ).sort("_id", -1)
                resp_data = {
                    "err": "False",
                    "message": "Successfully auth",
                    "result": records
                }
            else:
                resp_data = {
                    "err": "True",
                    "message": "Please login",
                    "result": ""
                }
            resp = flask.make_response(dumps(resp_data))
            resp.headers.extend({
                "Access-Control-Allow-Origin": "*"
            })
            return resp
        except pymongo.errors.OperationFailure, err:
            return {
                "err": "True",
                "message": "Failed getting data",
                "result": err.details
            }


class LatestRecord(BaseClassWithCORS):
    def get(self):
        data_db_host = config.db_config[config.config_name]["data_db"]["host"]
        data_db_port = config.db_config[config.config_name]["data_db"]["port"]
        data_db_mongo = flask_pymongo.MongoClient(host=data_db_host, port=data_db_port)
        db = config.db_config[config.config_name]["data_db"]["db"]
        data_db = data_db_mongo[db]
        trans_col = config.db_config[config.config_name]["data_db"]["trans_data_col"]
        try:
            auth_headers = flask.request.headers.get("Authorization")
            method, token = auth_headers.split(" ")
            checked = factory.auth_db["token"].find({"token": token})
            if checked:
                factory.auth_db["token"].update_one(
                    {"token": token},
                    {
                        "$inc": {
                            "expir": 604800000
                        }
                    }
                )
                latest_record = data_db[trans_col].find().sort("_id", -1)[0]
                data = {
                    "err": "False",
                    "message": "Successfully auth",
                    "result": latest_record
                }
            else:
                data = {
                    "err": "True",
                    "message": "Authenticate failed",
                    "result": ""
                }
            resp = flask.make_response(dumps(data))
            resp.headers.extend({
                "Access-Control-Allow-Origin": "*"
            })
            return resp
        except pymongo.errors.OperationFailure, err:
            return {
                "err": "True",
                "message": "Failed getting data",
                "result": err.details
            }


class Record(BaseClassWithCORS):
    def post(self):
        data_db_host = config.db_config[config.config_name]["data_db"]["host"]
        data_db_port = config.db_config[config.config_name]["data_db"]["port"]
        data_db_mongo = flask_pymongo.MongoClient(host=data_db_host, port=data_db_port)
        db = config.db_config[config.config_name]["data_db"]["db"]
        data_db = data_db_mongo[db]
        raw_col = config.db_config[config.config_name]["data_db"]["raw_data_col"]
        trans_col = config.db_config[config.config_name]["data_db"]["trans_data_col"]
        try:
            auth_headers = flask.request.headers.get("Authorization")
            method, token = auth_headers.split(" ")
            request_data = loads(flask.request.data)
            checked = factory.auth_db["token"].find_one({"token": token})
            if checked:
                factory.auth_db["token"].update_one(
                    {"token": token},
                    {
                        "$inc": {
                            "expir": 604800000
                        }
                    }
                )
                raw_json = request_data["data"]
                trans_json = config.transform_data(raw_json)
                raw_insert_result = data_db[raw_col].insert_one(raw_json)
                trans_insert_result = data_db[trans_col].insert_one(trans_json)
                resp_data = {
                    "err": "False",
                    "message": "Successfully inserted",
                    "result": {
                        "raw_insert_id": raw_insert_result.inserted_id,
                        "trans_insert_id": trans_insert_result.inserted_id
                    }
                }
            else:
                resp_data = {
                    "err": "True",
                    "message": "Please login",
                    "result": ""
                }
            resp = flask.make_response(dumps(resp_data))
            resp.headers.extend({
                "Access-Control-Allow-Origin": "*"
            })
            return resp
        except pymongo.errors.OperationFailure, err:
            return {
                "err": "True",
                "message": "Failed post data",
                "result": err.details
            }


class AuthenticateByPassword(BaseClassWithCORS):
    def post(self):
        try:
            request_data = loads(flask.request.data)
            user = factory.auth_db["user"].find_one({"un": request_data["un"]})
            checked = werkzeug.security.check_password_hash(user["pwd"], request_data["pwd"])
            if checked:
                token = uuid.uuid4().hex
                now = datetime.datetime.utcnow()
                expir = datetime.timedelta(days=7)
                expir_timestamp = int(((now + expir) - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)
                factory.auth_db["token"].insert({"token": token, "expir": expir_timestamp})
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
            resp = flask.make_response(dumps(data))
            resp.headers.extend({
                "Access-Control-Allow-Origin": "*"
            })
            return resp
        except pymongo.errors.OperationFailure, err:
            return {
                "err": "True",
                "message": "Auth failed!",
                "result": err.details
            }


class LatestRecordSet(BaseClassWithCORS):
    def get(self, amount):
        data_db_host = config.db_config[config.config_name]["data_db"]["host"]
        data_db_port = config.db_config[config.config_name]["data_db"]["port"]
        data_db_mongo = flask_pymongo.MongoClient(host=data_db_host, port=data_db_port)
        db = config.db_config[config.config_name]["data_db"]["db"]
        data_db = data_db_mongo[db]
        trans_col = config.db_config[config.config_name]["data_db"]["trans_data_col"]

        auth_headers = flask.request.headers.get("Authorization")
        method, token = auth_headers.split(" ")
        checked = factory.auth_db["token"].find({"token": token})
        if checked:
            factory.auth_db["token"].update_one(
                {"token": token},
                {
                    "$inc": {
                        "expir": 604800000
                    }
                }
            )
            latest_records = data_db[trans_col].find().sort("_id", -1)[:amount]
            data = {
                "err": "False",
                "message": "Successfully auth",
                "result": latest_records
            }
        else:
            data = {
                "err": "True",
                "message": "Authentication by token failed",
                "result": ""
            }
        resp = flask.make_response(dumps(data))
        resp.headers.extend({
            "Access-Control-Allow-Origin": "*"
        })
        return resp


class Register(BaseClassWithCORS):
    def post(self):
        try:
            request_data = loads(flask.request.data)
            new_json = {
                "un": request_data["un"],
                "pwd": werkzeug.security.generate_password_hash(request_data["pwd"], method='pbkdf2:sha1')
            }
            register_insert = factory.auth_db["user"].insert_one(new_json)
            resp_data = {
                "err": "False",
                "message": "Successfully auth",
                "result": register_insert.inserted_id
            }
            resp = flask.make_response(dumps(resp_data))
            resp.headers.extend({
                "Access-Control-Allow-Origin": "*"
            })
            return resp
        except pymongo.errors.OperationFailure, err:
            return {
                "err": "True",
                "message": "Failed registering",
                "result": err.details
            }
