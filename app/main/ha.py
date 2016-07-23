import requests
from config import db_api_servers

status = {api_server["host"]+api_server["port"]: "online" for api_server in db_api_servers}

def heart_beat():
    for api_server in db_api_servers:
        req = requests.get(api_server["host"]+api_server["port"])
        if req.status_code!="200":
            status[api_server["host"]+api_server["port"]] = "offline"