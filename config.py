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


def transform_data(raw_json, last_trans_doc=None):
    trans_json = {
        "dtu_id": raw_json["dtu_id"],
        "timestamp": raw_json["timestamp"],
        "channel": {}
    }
    new_labels = [u"A路电机转速", u"B路电机转速", u"海流流速", u"海流流向", u"A路电机输出电压", u"B路电机输出电压",
                  u"A路电机输出电流", u"B路电机输出电流", u"A路电机功率", u"B路电机功率", u"累计发电量"]

    # AN1_sum = sum(map(lambda json: json["sensors"]["AN1"]["value"], copy.deepcopy(window)))
    # AN2_sum = sum(map(lambda json: json["sensors"]["AN2"]["value"], copy.deepcopy(window)))
    # AN7_sum = sum(map(lambda json: json["sensors"]["AN7"]["value"], copy.deepcopy(window)))
    # AN8_sum = sum(map(lambda json: json["sensors"]["AN8"]["value"], copy.deepcopy(window)))

    A_voltage = round(26.073 * raw_json["sensors"]["AN1"]["value"] - 1.1159, 2)
    # trans_json["channel"]["CH6"] = {
    trans_json["channel"]["CH1"] = {
        # A voltage
        "label": new_labels[4],
        "unit": u"V",
        "value": A_voltage if A_voltage > 0 else 0
        # "value": round(1.08 * 1.1 * (15.06 * (AN1_sum + raw_json["sensors"]["AN1"]["value"])/(window.count(True)+1) + 16.38),2)
    }
    B_voltage = round(26.073 * raw_json["sensors"]["AN2"]["value"] - 1.1159, 2)
    # trans_json["channel"]["CH5"] = {
    trans_json["channel"]["CH5"] = {
        # B voltage
        "label": new_labels[5],
        "unit": u"V",
        "value": B_voltage if B_voltage > 0 else 0
        # "value": round(1.08 * 1.1 * (15.06 * (AN2_sum + raw_json["sensors"]["AN2"]["value"])/(window.count(True)+1) + 16.38),2)
    }
    # trans_json["channel"]["CH7"] = {
    trans_json["channel"]["CH2"] = {
        # A current
        "label": new_labels[6],
        "unit": u"A",
        # "value": round(1.15/1.08 * (9.392 * (AN7_sum + raw_json["sensors"]["AN7"]["value"])/(window.count(True)+1) - 0.9334),2)
        "value": round(
            -0.8861 * raw_json["sensors"]["AN7"]["value"] ** 2 + 3.7949 * raw_json["sensors"]["AN7"]["value"] - 0.0139)
    }
    # trans_json["channel"]["CH8"] = {
    trans_json["channel"]["CH6"] = {
        # B current
        "label": new_labels[7],
        "unit": u"A",
        # "value": round(1.15/1.08 * (9.054 * (AN8_sum + raw_json["sensors"]["AN8"]["value"])/(window.count(True)+1) - 0.8262),2)
        "value": round(
            -0.8861 * raw_json["sensors"]["AN8"]["value"] ** 2 + 3.7949 * raw_json["sensors"]["AN8"]["value"] - 0.0139)
    }
    # trans_json["channel"]["CH9"] = {
    trans_json["channel"]["CH3"] = {
        # A power
        "label": new_labels[8],
        "unit": u"W",
        "value": round(0.7 * 1.732 * trans_json["channel"]["CH1"]["value"] * trans_json["channel"]["CH2"]["value"], 2)
    }
    # trans_json["channel"]["CH10"] = {
    trans_json["channel"]["CH7"] = {
        # B power
        "label": new_labels[9],
        "unit": u"W",
        "value": round(0.7 * 1.732 * trans_json["channel"]["CH5"]["value"] * trans_json["channel"]["CH6"]["value"], 2)
    }
    A_sp1 = trans_json["channel"]["CH1"]["value"] / 390.0 * 70
    A_sp2 = 1.74 * trans_json["channel"]["CH3"]["value"] / 1000
    # trans_json["channel"]["CH1"] = {
    trans_json["channel"]["CH4"] = {
        # A speed
        "label": new_labels[0],
        "unit": u"rpm",
        "value": round(A_sp1 + A_sp2 - 0.36, 2)
    }
    B_sp1 = trans_json["channel"]["CH5"]["value"] / 390.0 * 70
    B_sp2 = 1.74 * trans_json["channel"]["CH7"]["value"] / 1000
    # trans_json["channel"]["CH2"] = {
    trans_json["channel"]["CH8"] = {
        # B speed
        "label": new_labels[1],
        "unit": u"rpm",
        "value": round(B_sp1 + B_sp2 - 0.36, 2)
    }
    # trans_json["channel"]["CH3"] = {
    trans_json["channel"]["CH9"] = {
        # current speed
        "label": new_labels[2],
        "unit": u"m/s",
        "value": round((raw_json["sensors"]["AN3"]["value"] - 4.0) / 16.0 * 7.0, 2)
    }
    # trans_json["channel"]["CH4"] = {
    trans_json["channel"]["CH10"] = {
        # current direction
        "label": new_labels[3],
        "unit": u"度",
        "value": round((raw_json["sensors"]["AN3"]["value"] - 4.0) / 16.0 * 360.0, 2)
    }
    if last_trans_doc:
        trans_json["channel"]["CH11"] = {
            # acc power gen
            "label": new_labels[10],
            "unit": u"kWh",
            "value": round(last_trans_doc["channel"]["CH11"]["value"] + \
                (trans_json["channel"]["CH3"]["value"] + trans_json["channel"]["CH7"]["value"]) * \
                           (trans_json["timestamp"] - last_trans_doc["timestamp"]) / 1e6 / 3600, 2)
        }
    else:
        trans_json["channel"]["CH11"] = {
            # acc power gen
            "label": new_labels[10],
            "unit": u"kWh",
            "value": round((trans_json["channel"]["CH3"]["value"] + trans_json["channel"]["CH7"]["value"]) / 1e3 / 3600, 2)
        }
    return trans_json
