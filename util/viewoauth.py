import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
from flask_dance.contrib.google import make_google_blueprint, google
from werkzeug.security import check_password_hash,generate_password_hash
from flask import flash
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_login import current_user, login_user
from sqlalchemy.orm.exc import NoResultFound

from model.oauth import OAuth, db, User

google_blueprint = make_google_blueprint(
    client_id='447506769931-0ie1s413dtk88rfg7gaa2k3afo81jfkj.apps.googleusercontent.com',
    client_secret='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',
    scope=['openid', 'https://www.googleapis.com/auth/userinfo.profile',
           'https://www.googleapis.com/auth/userinfo.email'],
    storage=SQLAlchemyStorage(
        OAuth,
        db.session,
        user=current_user,
        user_required=False,
    ),
)


@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    info = google.get("/oauth2/v2/userinfo")
    if info.ok:
        account_info = info.json()
        username = account_info["email"]
        name = account_info["name"] 
        query = User.query.filter_by(username=username)
        try:
            user = query.one()
        except NoResultFound:
            user = User(username=username,name=name)
            db.session.add(user)
            db.session.commit()
        login_user(user)



def login_user_with_credentials(username, password):
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        return True
    else:
        flash("Invalid email or password", "danger")
        return False


def register_user(username, password,name):
    user = User.query.filter_by(username=username).first()
    if user:
        return False, "Email already exists. Please choose a different one."

    new_user = User(username=username,name=name, password=generate_password_hash(password))

    try:
        db.session.add(new_user)
        db.session.commit()
        return True, "Registration successful! You can now log in."
    except:
        db.session.rollback()
        return False, "An error occurred. Please try again."
