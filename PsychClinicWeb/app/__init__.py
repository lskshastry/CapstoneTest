from flask import Flask, session
from flask_mongoengine import MongoEngine

from config import Config
from flask_login import LoginManager
from flask_moment import Moment
from pymongo import MongoClient

#cluster = "mongodb+srv://jillianplahn:a7cT5drBKQR3WagR@cluster0.qmfy4wl.mongodb.net/?retryWrites=true&w=majority"
#client = MongoClient(cluster)

db = MongoEngine()
login = LoginManager()
login.login_view = 'auth.login'

moment = Moment()

def create_app(config_class=Config):
    app = Flask(__name__)

    # New walts database
    app.config['MONGODB_SETTINGS'] = {
        'host': 'mongodb+srv://jillian:Plahn1218!@cluster0.xv4vght.mongodb.net/PsychWebApp?retryWrites=true&w=majority',
                'connectTimeoutMS': 30000,
                'socketTimeoutMS': None,
                'connect': False,
                'maxPoolsize': 1
    }

    # established connection
    db = MongoEngine(app)

    # Connect to MongoDB using MongoEngine
    #connect(db='test', alias='default', host=app.config['MONGODB_SETTINGS']['host'])


    try:
        #connect('test', alias='default', host=app.config['MONGODB_SETTINGS']['host'])
        print("Successfully connected to MongoDB.")
    except Exception as e:
        print(f"Failed to connect to MongoDB. Error: {e}")

    app.config.from_object(config_class)
    app.static_folder = config_class.STATIC_FOLDER 
    app.template_folder = config_class.TEMPLATE_FOLDER
    #db.init_app(app)
    login.init_app(app) 
    moment.init_app(app)
    app.secret_key = 'jpsecret'

    # blueprint registration
    from app.Controller.errors import bp_errors as errors
    app.register_blueprint(errors)
    from app.Controller.auth_routes import bp_auth as auth
    app.register_blueprint(auth)
    from app.Controller.routes import bp_routes as routes
    app.register_blueprint(routes)

    if not app.debug and not app.testing:
        pass
        # ... no changes to logging setup
    return app

