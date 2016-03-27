from app import create_app
from flask_pymongo import MongoClient
from config import db_config
import getpass

app = create_app()
config_name = "dev_config"
auth_db = MongoClient(host=db_config[config_name]["host"], port=db_config[config_name]["port"])[db_config[config_name]["auth_db"]]
auth_db.authenticate(raw_input("auth database username:"), getpass.getpass(prompt="auth database password:"))
print "login succeed!"
if __name__ == '__main__':
    app.run(threaded=True)
