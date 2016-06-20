# coding=utf-8
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


def transform_data(raw_json, window, last_trans_doc=None):
    trans_json = {
        "dtu_id": raw_json["dtu_id"],
        "timestamp": raw_json["timestamp"],
        "channel": {}
    }
    new_labels = [u"A路电机转速", u"B路电机转速", u"海流流速", u"海流流向", u"A路电机输出电压", u"B路电机输出电压",
                  u"A路电机输出电流", u"B路电机输出电流", u"A路电机功率", u"B路电机功率", u"累计发电量"]

    AN1_sum = sum(map(lambda json: json["sensors"]["AN1"]["value"], copy.deepcopy(window)))
    AN2_sum = sum(map(lambda json: json["sensors"]["AN2"]["value"], copy.deepcopy(window)))
    AN7_sum = sum(map(lambda json: json["sensors"]["AN7"]["value"], copy.deepcopy(window)))
    AN8_sum = sum(map(lambda json: json["sensors"]["AN8"]["value"], copy.deepcopy(window)))

    # trans_json["channel"]["CH6"] = {
    trans_json["channel"]["CH1"] = {
        # A voltage
        "label": new_labels[4],
        "unit": u"V",
        # "value": A_voltage if A_voltage > 0 else 0
        # "value": 26.073 * (AN1_sum + raw_json["sensors"]["AN1"]["value"])/(window.count(True)+1) - 1.1159
        "value": 1.03 * (AN1_sum + raw_json["sensors"]["AN1"]["value"])/(window.count(True)+1)
    }
    # trans_json["channel"]["CH5"] = {
    trans_json["channel"]["CH5"] = {
        # B voltage
        "label": new_labels[5],
        "unit": u"V",
        # "value": B_voltage if B_voltage > 0 else 0
        # "value": 26.073 * (AN2_sum + raw_json["sensors"]["AN2"]["value"])/(window.count(True)+1) - 1.1159
        "value": 1.03 * (AN2_sum + raw_json["sensors"]["AN2"]["value"])/(window.count(True)+1)
    }
    A_id = (AN7_sum + raw_json["sensors"]["AN7"]["value"])/(window.count(True)+1)
    # trans_json["channel"]["CH7"] = {
    trans_json["channel"]["CH2"] = {
        # A current
        "label": new_labels[6],
        "unit": u"A",
        # "value": 0.25*A_id**3-1.71*A_id**2+5.07*A_id if A_id > 0.04 else 0
        # "value": -0.8861 * A_id ** 2 + 3.7949 * A_id - 0.0139
        "value": 0.99 * A_id + 0.19 if A_id > 0.04 else 0
    }
    B_id = (AN8_sum + raw_json["sensors"]["AN8"]["value"])/(window.count(True)+1)
    # trans_json["channel"]["CH8"] = {
    trans_json["channel"]["CH6"] = {
        # B current
        "label": new_labels[7],
        "unit": u"A",
        # "value": -0.8861 * B_id ** 2 + 3.7949 * B_id - 0.0139
        # "value": 0.25 * B_id ** 3 - 1.71 * B_id ** 2 + 5.07 * B_id if B_id > 0.04 else 0
        "value": 0.99 * B_id + 0.19 if B_id > 0.04 else 0
    }
    # trans_json["channel"]["CH9"] = {
    trans_json["channel"]["CH3"] = {
        # A power
        "label": new_labels[8],
        "unit": u"W",
        "value": 0.7 * 1.732 * trans_json["channel"]["CH1"]["value"] * trans_json["channel"]["CH2"]["value"]
    }
    # trans_json["channel"]["CH10"] = {
    trans_json["channel"]["CH7"] = {
        # B power
        "label": new_labels[9],
        "unit": u"W",
        "value": 0.7 * 1.732 * trans_json["channel"]["CH5"]["value"] * trans_json["channel"]["CH6"]["value"]
    }
    A_sp1 = trans_json["channel"]["CH1"]["value"] / 390.0 * 70
    A_sp2 = 1.74 * trans_json["channel"]["CH3"]["value"] / 1000
    # trans_json["channel"]["CH1"] = {
    trans_json["channel"]["CH4"] = {
        # A speed
        "label": new_labels[0],
        "unit": u"rpm",
        "value": A_sp1 + A_sp2 - 0.36
    }
    B_sp1 = trans_json["channel"]["CH5"]["value"] / 390.0 * 70
    B_sp2 = 1.74 * trans_json["channel"]["CH7"]["value"] / 1000
    # trans_json["channel"]["CH2"] = {
    trans_json["channel"]["CH8"] = {
        # B speed
        "label": new_labels[1],
        "unit": u"rpm",
        "value": B_sp1 + B_sp2 - 0.36
    }
    # trans_json["channel"]["CH3"] = {
    trans_json["channel"]["CH9"] = {
        # current speed
        "label": new_labels[2],
        "unit": u"m/s",
        "value": (raw_json["sensors"]["AN3"]["value"] - 4.0) / 16.0 * 7.0
    }
    # trans_json["channel"]["CH4"] = {
    trans_json["channel"]["CH10"] = {
        # current direction
        "label": new_labels[3],
        "unit": u"度",
        "value": (raw_json["sensors"]["AN3"]["value"] - 4.0) / 16.0 * 360.0
    }
    if last_trans_doc:
        trans_json["channel"]["CH11"] = {
            # acc power gen
            "label": new_labels[10],
            "unit": u"kWh",
            "value": last_trans_doc["channel"]["CH11"]["value"] + \
                (trans_json["channel"]["CH3"]["value"] + trans_json["channel"]["CH7"]["value"]) * \
                           (trans_json["timestamp"] - last_trans_doc["timestamp"]) / 3600.0 / 1e6
        }
    else:
        trans_json["channel"]["CH11"] = {
            # acc power gen
            "label": new_labels[10],
            "unit": u"kWh",
            "value": (trans_json["channel"]["CH3"]["value"] + trans_json["channel"]["CH7"]["value"]) / 3600.0 / 1e3
        }
    return trans_json
