from flask import *
import os
from flask_migrate import Migrate
from model.oauth import db, login_manager
from view.home import home
from view.oauth import auth
from view.bot import bot
app = Flask(__name__)
from dotenv import load_dotenv
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') 
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI') 
migrate = Migrate(app, db)
db.init_app(app)
login_manager.init_app(app)
app.register_blueprint(home)
app.register_blueprint(auth)
app.register_blueprint(bot)
@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


if __name__ == '__main__':
    app.run(debug=True)
