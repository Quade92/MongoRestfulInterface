from app.main.factory import create_app
from gevent.pywsgi import WSGIServer


flask_app = create_app()

print "login succeed!"
if __name__ == '__main__':
    http_server = WSGIServer(('', 5000), flask_app)
    # flask_app.run(host="0.0.0.0", threaded=True)
    http_server.serve_forever()
