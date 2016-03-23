# coding=utf-8
import random
db_config = {
    "dev_config": {
        "host": "localhost",
        "port": 27999,
        "db": "data_db",
        "raw_data_col": "raw_data",
        "trans_data_col": "trans_data"
    }
}


def transform_data(raw_json):
    trans_json = {}
    trans_json["dtu_id"] = raw_json["dtu_id"]
    trans_json["timestamp"] = raw_json["timestamp"]
    trans_json["channel"] = {}
    new_labels = [u"A路电机转速", u"B路电机转速", u"海流流速", u"海流流向", u"A路电机输出电压", u"B路电机输出电压",
                  u"A路电机输出电流", u"B路电机输出电流", u"A路电机功率", u"B路电机功率"]
    for index, label in enumerate(new_labels):
        trans_json["channel"]["CH" + str(index+1)] = {
            "label": label,
            "value": 10*index+random.random()-0.5
        }
    # TODO modify value in tran_json.channel
    return trans_json
