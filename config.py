# coding=utf-8
import random
import copy


config_name = "dev_config"

db_config = {
    "dev_config": {
        "data_db": {
            "db": "data_db",
            "host": "localhost",
            "port": 27999,
            "raw_data_col": "raw_data",
            "trans_data_col": "trans_data"
        },
        "auth_db": {
            "db": "auth_db",
            "host": "localhost",
            "port": 27998
        }
    }
}


def transform_data(window, raw_json):
    trans_json = {}
    trans_json["dtu_id"] = raw_json["dtu_id"]
    trans_json["timestamp"] = raw_json["timestamp"]
    trans_json["channel"] = {}
    new_labels = [u"A路电机转速", u"B路电机转速", u"海流流速", u"海流流向", u"A路电机输出电压", u"B路电机输出电压",
                  u"A路电机输出电流", u"B路电机输出电流", u"A路电机功率", u"B路电机功率", u"累计发电量"]
    for index, label in enumerate(new_labels):
        trans_json["channel"]["CH" + str(index+1)] = {
            "label": label,
            "value": 0
        }
    AN1_sum = sum(map(lambda json: json["sensors"]["AN1"]["value"], copy.deepcopy(window)))
    AN2_sum = sum(map(lambda json: json["sensors"]["AN2"]["value"], copy.deepcopy(window)))
    AN7_sum = sum(map(lambda json: json["sensors"]["AN7"]["value"], copy.deepcopy(window)))
    AN8_sum = sum(map(lambda json: json["sensors"]["AN8"]["value"], copy.deepcopy(window)))
    trans_json["channel"]["CH5"] = {
        "label": new_labels[4],
        "value": round(15.06 * (AN1_sum + raw_json["sensors"]["AN1"]["value"])/100 + 16.38,2)
    }
    trans_json["channel"]["CH6"] = {
        "label": new_labels[5],
        "value": round(15.06 * (AN2_sum + raw_json["sensors"]["AN2"]["value"])/100 + 16.38,2)
    }
    trans_json["channel"]["CH7"] = {
        "label": new_labels[6],
        "value": round(9.392 * (AN7_sum + raw_json["sensors"]["AN7"]["value"])/100 - 0.9334,2)
    }
    trans_json["channel"]["CH8"] = {
        "label": new_labels[7],
        "value": round(9.054 * (AN8_sum + raw_json["sensors"]["AN8"]["value"])/100 - 0.8262,2)
    }
    # TODO modify value in tran_json.channel
    return trans_json
