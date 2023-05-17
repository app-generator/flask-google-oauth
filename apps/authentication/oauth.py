# import os

from flask import redirect
from flask_login import current_user, login_user
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.contrib.google import google, make_google_blueprint
from sqlalchemy.orm.exc import NoResultFound

from ..config import Config

from .models import Users, db, OAuth

client_id = Config.GOOGLE_OAUTH_CLIENT_ID #os.getenv('GOOGLE_CLIENT_ID')
client_secret = Config.GOOGLE_OAUTH_CLIENT_SECRET #os.getenv('GOOGLE_CLIENT_SECRET')

google_blueprint = make_google_blueprint(
    client_id=client_id,
    client_secret=client_secret,
    scope='user',
    storage=SQLAlchemyStorage(
        OAuth,  
        db.session,
        user=current_user,
        user_required=False
    ),
)

@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    info = google.get('/user')

    if info.ok:
        account_info = info.json()
        print(account_info)
        username = account_info['login']

        query = Users.query.filter_by(oauth_google=username)
        try:
            user = query.one()
            login_user(user)
        except NoResultFound:
            user = Users()
            user.username = username
            user.oauth_google = username
            user.save()

            login_user(user)
