# coding=utf-8
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
import StringIO
import gzip
import ha
from bson.json_util import loads


def with_restful_servers_status(resp_func):
    def wrapper(*args, **kwargs):
        resp = resp_func(args, kwargs)
        data = loads(resp.data)
        data.update({"status":ha.status})
        resp.data = data
        return resp
    return wrapper


class BaseClassWithCORS(flask_restful.Resource):
    def options(self, **kwargs):
        resp = flask.make_response("")
        resp.headers.extend({
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST",
            "Access-Control-Allow-Headers": "Authorization, Content-Type"
        })
        return resp


class DownloadHistoryCSV(BaseClassWithCORS):
    def get(self, start, end):
        data_db_host = config.db_config[config.config_name]["data_db"]["host"]
        data_db_port = config.db_config[config.config_name]["data_db"]["port"]
        data_db_mongo = flask_pymongo.MongoClient(host=data_db_host, port=data_db_port)
        data_db = data_db_mongo[config.db_config[config.config_name]["data_db"]["db"]]
        trans_col = config.db_config[config.config_name]["data_db"]["trans_data_col"]
        raw_col = config.db_config[config.config_name]["data_db"]["raw_data_col"]
        try:
            auth_headers = flask.request.headers.get("Authorization")
            method, token = auth_headers.split(" ")
            checked = factory.auth_db["token"].find({"token": token})
            if checked.count(True) > 0:
                factory.auth_db["token"].update_one(
                    {"token": token},
                    {
                        "$inc": {
                            "expir": 604800000
                        }
                    }
                )
                raw_records = data_db[raw_col].find({
                    "$and": [{"timestamp": {"$gte": start}},
                             {"timestamp": {"$lte": end}}]}
                )
                trans_records = data_db[trans_col].find({
                    "$and": [{"timestamp": {"$gte": start}},
                             {"timestamp": {"$lte": end}}]}
                )
                csv_io = StringIO.StringIO()
                header = ["timestamp"]
                for sensor in raw_records[0]["sensors"]:
                    header.append(sensor)
                for channel in trans_records[0]["channel"]:
                    header.append(channel)
                csv_io.write(",".join(header) + "\n")
                for raw_json, trans_json in zip(raw_records, trans_records):
                    row = [datetime.datetime.fromtimestamp(raw_json["timestamp"]/1000).strftime("%Y-%m-%d %H:%M:%S")]
                    for sensor in raw_json["sensors"]:
                        row.append(str(raw_json["sensors"][sensor]["value"]))
                    for channel in trans_json["channel"]:
                        row.append(str(trans_json["channel"][channel]["value"]))
                    csv_io.write(",".join(row) + "\n")
                resp = flask.make_response(csv_io.getvalue())
                resp.headers.extend({
                    "Access-Control-Allow-Origin": "*",
                    "Content-Disposition": "attachment; filename=export.csv"
                })
                resp.headers["Content-Type"] = "text/csv; charset=utf-8"
                return resp
        except Exception, err:
            resp_data = {
                "err": "True",
                "message": str(err),
                "result": ""
            }
            resp = flask.make_response(dumps(resp_data))
            resp.headers.extend({
                "Access-Control-Allow-Origin": "*"
            })
            return resp


class RecordSeries(BaseClassWithCORS):
    @with_restful_servers_status
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
            if checked.count(True) > 0:
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
            gzip_buffer = StringIO.StringIO()
            gzip_file = gzip.GzipFile(mode="wb", fileobj=gzip_buffer)
            gzip_file.write(dumps(resp_data))
            gzip_file.close()
            resp = flask.make_response(gzip_buffer.getvalue())
            resp.headers.extend({
                "Access-Control-Allow-Origin": "*",
                "Content-Encoding": "gzip",
                "Vary": "Accept-Encoding",
                "Content-Length": len(resp.data)
            })
            return resp
        except pymongo.errors.OperationFailure, err:
            return {
                "err": "True",
                "message": "Failed getting data",
                "result": str(err)
            }
        except Exception, err:
            return {
                "err": "True",
                "message": "unknow error",
                "result": str(err)
            }


class LatestRecord(BaseClassWithCORS):
    @with_restful_servers_status
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
            if checked.count(True) > 0:
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
    @with_restful_servers_status
    def post(self):
        try:
            data_db_host = config.db_config[config.config_name]["data_db"]["host"]
            data_db_port = config.db_config[config.config_name]["data_db"]["port"]
            data_db_mongo = flask_pymongo.MongoClient(host=data_db_host, port=data_db_port)
            db = config.db_config[config.config_name]["data_db"]["db"]
            data_db = data_db_mongo[db]
            raw_col = config.db_config[config.config_name]["data_db"]["raw_data_col"]
            trans_col = config.db_config[config.config_name]["data_db"]["trans_data_col"]
            auth_headers = flask.request.headers.get("Authorization")
            method, token = auth_headers.split(" ")
            request_data = loads(flask.request.data)
            checked = factory.auth_db["token"].find_one({"token": token})["role"] == "writer"
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
                raw_insert_result = data_db[raw_col].insert_one(raw_json)
                # windows size 100
                WINDOW_SIZE = 15
                window = data_db[raw_col].find().sort("_id", -1)[:WINDOW_SIZE-1].limit(WINDOW_SIZE-1)
                last_trans_doc = data_db[trans_col].find().sort("_id",-1)[:1]
                if last_trans_doc.count()==0:
                    trans_json = config.transform_data(raw_json, window)
                    trans_insert_result = data_db[trans_col].insert_one(trans_json)
                    resp_data = {
                        "err": "False",
                        "message": "first data record",
                        "result": {
                            "raw_insert_id": raw_insert_result.inserted_id,
                            "trans_insert_id": trans_insert_result.inserted_id
                        }
                    }
                    resp = flask.make_response(dumps(resp_data))
                    resp.headers.extend({
                        "Access-Control-Allow-Origin": "*"
                    })
                    return resp
                # if window.count(True) < WINDOW_SIZE-1:
                #     resp_data = {
                #         "err": "True",
                #         "message": "not enough data for smoothing",
                #         "result": {
                #             "raw_insert_id": raw_insert_result.inserted_id,
                #         }
                #     }
                #     resp = flask.make_response(dumps(resp_data))
                #     resp.headers.extend({
                #         "Access-Control-Allow-Origin": "*"
                #     })
                #     return resp
                trans_json = config.transform_data(raw_json, window, last_trans_doc[0])
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
        except Exception, err:
            resp_data = {
                "err": "True",
                "message": "Unknown error",
                "result": str(err)
            }
            resp = flask.make_response(dumps(resp_data))
            resp.headers.extend({
                "Access-Control-Allow-Origin": "*"
            })
            return resp


class AuthenticateByPassword(BaseClassWithCORS):
    @with_restful_servers_status
    def post(self):
        try:
            request_data = loads(flask.request.data)
            user = factory.auth_db["user"].find_one({"un": request_data["un"]})
            checked = werkzeug.security.check_password_hash(user["pwd"], request_data["pwd"])
            if checked > 0:
                token = uuid.uuid4().hex
                now = datetime.datetime.utcnow()
                expir = datetime.timedelta(days=7)
                expir_timestamp = int(((now + expir) - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)
                factory.auth_db["token"].insert({
                    "token": token,
                    "un": request_data["un"],
                    "expir": expir_timestamp,
                    "role": user["role"]}
                )
                data = {
                    "err": "False",
                    "message": "Successfully auth",
                    "result": {
                        "un": request_data["un"],
                        "token": token
                    }
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
    @with_restful_servers_status
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
        if checked.count(True) > 0:
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
                "pwd": werkzeug.security.generate_password_hash(request_data["pwd"], method='pbkdf2:sha1'),
                "role": request_data["role"]
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


class HeartBeat(object):
    def get(self):
        client_ip = flask.request.environ.get('REMOTE_ADDR')
        client_port = flask.request.environ.get('REMOTE_PORT')
        ha.status[client_ip+":"+client_port] = "online"
        resp_data = {
            "err": "False",
            "message": "Online",
            "result": ""
        }
        resp = flask.make_response(dumps(resp_data))
        return resp