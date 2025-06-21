from flask import Flask
from backend.models import *
from backend.api_controllers import *
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = None #global app initially set to None

def initialize_app():
    app = Flask(__name__)
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///IESCP.sqlite3"
    db.init_app(app)
    api.init_app(app)
    app.app_context().push()
    return app

app = initialize_app()

from backend.controllers import *

# Setting up the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_ad_requests, trigger="interval", days=1)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())     # Register shutdown handler to clean up scheduler

if __name__ == "__main__":
    app.run()