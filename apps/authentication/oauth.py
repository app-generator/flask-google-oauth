# import os

from flask_login import current_user, login_user
from flask_dance.consumer import oauth_authorized, oauth_error
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
    offline=True,
    storage=SQLAlchemyStorage(
        OAuth,  
        db.session,
        user=current_user,
        user_required=False
    ),
    scope=["profile", "email"],
    reprompt_consent=True
)

@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    info = google.get('/oauth2/v1/userinfo')

    if info.ok:
        account_info = info.json()
        print(account_info)
        user_id = account_info['id']

        query = Users.query.filter_by(oauth_google=user_id)
        try:
            user = query.one()
            login_user(user)
        except NoResultFound:
            oauth = OAuth(
                provider=blueprint.name,
                token=token,
                user_id=user_id
            )

            user = Users()
            user.username = 'google_' + account_info['given_name'] + account_info['family_name']
            user.email = account_info['email']
            user.oauth_google = user_id
    
            db.session.add_all([user, oauth])
            db.session.commit()
    
            login_user(user)

    return False
