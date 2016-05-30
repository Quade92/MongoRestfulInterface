from app.main.factory import create_app


flask_app = create_app()

print "login succeed!"
if __name__ == '__main__':
    flask_app.run(host="0.0.0.0", threaded=True)
