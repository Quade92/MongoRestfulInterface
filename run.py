import sched, time

from app.main.factory import create_app
from config import db_config, config_name

flask_app = create_app()

print "login succeed!"
if __name__ == '__main__':
    # TODO add schedular
    flask_app.run(host=db_config[config_name]["api"]["host"], port=db_config[config_name]["api"]["port"], threaded=True)
