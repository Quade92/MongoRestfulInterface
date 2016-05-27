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
    # for index, label in enumerate(new_labels):
    #     trans_json["channel"]["CH" + str(index+1)] = {
    #         "label": label,
    #         "value": 0
    #     }
    # AN1_sum = sum(map(lambda json: json["sensors"]["AN1"]["value"], copy.deepcopy(window)))
    # AN2_sum = sum(map(lambda json: json["sensors"]["AN2"]["value"], copy.deepcopy(window)))
    AN7_sum = sum(map(lambda json: json["sensors"]["AN7"]["value"], copy.deepcopy(window)))
    AN8_sum = sum(map(lambda json: json["sensors"]["AN8"]["value"], copy.deepcopy(window)))

    A_voltage = round( 25.422*raw_json["sensors"]["AN1"]["value"]-2.7416 ,2)
    trans_json["channel"]["CH6"] = {
        # A voltage
        "label": new_labels[4],
        "unit": u"V",
        "value": A_voltage if A_voltage>0 else 0
        # "value": round(1.08 * 1.1 * (15.06 * (AN1_sum + raw_json["sensors"]["AN1"]["value"])/(window.count(True)+1) + 16.38),2)
    }
    B_voltage = round(25.422 * raw_json["sensors"]["AN2"]["value"] - 2.7416, 2)
    trans_json["channel"]["CH5"] = {
        # B voltage
        "label": new_labels[5],
        "unit": u"V",
        "value": B_voltage if B_voltage>0 else 0
        # "value": round(1.08 * 1.1 * (15.06 * (AN2_sum + raw_json["sensors"]["AN2"]["value"])/(window.count(True)+1) + 16.38),2)
    }
    trans_json["channel"]["CH7"] = {
        # A current
        "label": new_labels[6],
        "unit": u"A",
        "value": round(1.15/1.08 * (9.392 * (AN7_sum + raw_json["sensors"]["AN7"]["value"])/(window.count(True)+1) - 0.9334),2)
    }
    trans_json["channel"]["CH8"] = {
        # B current
        "label": new_labels[7],
        "unit": u"A",
        "value": round(1.15/1.08 * (9.054 * (AN8_sum + raw_json["sensors"]["AN8"]["value"])/(window.count(True)+1) - 0.8262),2)
    }
    trans_json["channel"]["CH9"] = {
        # A power
        "label": new_labels[8],
        "unit": u"W",
        "value": round(1/1.7*1.08 * 1.732 * trans_json["channel"]["CH6"]["value"] * trans_json["channel"]["CH7"]["value"], 2)
    }
    trans_json["channel"]["CH10"] = {
        # B power
        "label": new_labels[9],
        "unit": u"W",
        "value": round(1/1.7*1.08 * 1.732 * trans_json["channel"]["CH5"]["value"] * trans_json["channel"]["CH8"]["value"], 2)
    }
    A_p = trans_json["channel"]["CH6"]["value"]/1000.0
    A_n_dot = A_p / 390.0 * 70
    A_delta_n = -0.5396*A_p**3+2.2739*A_p**2-0.7664*A_p+0.2272
    trans_json["channel"]["CH1"] = {
        # A speed
        "label": new_labels[0],
        "unit": u"rpm",
        "value": A_n_dot+A_delta_n
    }
    B_p = trans_json["channel"]["CH5"]["value"]/1000.0
    B_n_dot = B_p / 390.0 * 70
    B_delta_n = -0.5396*B_p**3+2.2739*B_p**2-0.7664*B_p+0.2272
    trans_json["channel"]["CH2"] = {
        # B speed
        "label": new_labels[1],
        "unit": u"rpm",
        "value": B_n_dot + B_delta_n
    }
    trans_json["channel"]["CH3"] = {
        # current speed
        "label": new_labels[2],
        "unit": u"m/s",
        "value": (raw_json["sensors"]["AN3"]["value"]-4.0)/16.0*7.0
    }
    trans_json["channel"]["CH4"] = {
        # current direction
        "label": new_labels[3],
        "unit": u"度",
        "value": (raw_json["sensors"]["AN3"]["value"]-4.0)/16.0*360.0
    }
    return trans_json
