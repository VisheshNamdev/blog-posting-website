from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_mail import Mail
from .config import Config
import os
from os import path
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
import logging
from logging.handlers import RotatingFileHandler
from flask_session import Session

mail = Mail()
db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "helloworld"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads/images')
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max file size
    app.config['UPLOADED_PATH'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    app.config['CKEDITOR_PKG_TYPE'] = 'full'
    app.config['CKEDITOR_ENABLE_CODESNIPPET'] = True
    app.config['CKEDITOR_FILE_UPLOADER'] = 'views.upload'
    app.config.from_object(Config)
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)           
    db.init_app(app)
    mail.init_app(app)
    
    oauth = OAuth(app)
    # Print environment variables to debug
    # print("LINKEDIN_CLIENT_ID:", os.getenv('LINKEDIN_CLIENT_ID'))
    # print("LINKEDIN_CLIENT_SECRET:", os.getenv('LINKEDIN_CLIENT_SECRET'))
    linkedin = oauth.register(
        name='linkedin',
        client_id=os.getenv('LINKEDIN_CLIENT_ID'),
        client_secret=os.getenv('LINKEDIN_CLIENT_SECRET'),
        request_token_url=None,
        request_token_params=None,
        access_token_method='POST',
        access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
        authorize_url='https://www.linkedin.com/oauth/v2/authorization',
        client_kwargs={'scope': 'openid profile email'}
    )
    
    google = oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid profile email'}
    )
    
    

    app.config['oauth'] = oauth
    
    
     
    if not app.debug:
        file_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=10)
        
        
        file_handler.setLevel(logging.ERROR)
        
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        file_handler.setFormatter(formatter)
        
        app.logger.addHandler(file_handler)
    
    
    
    
    migrate = Migrate(app, db)
    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  
    login_manager.init_app(app)

    ckeditor = CKEditor(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User

    # Move ALLOWED_EXTENSIONS assignment inside app context
    with app.app_context():
        app.allowed_extensions = app.config['ALLOWED_EXTENSIONS']

    create_database(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

def create_database(app):
    if not path.exists("website/" + DB_NAME):
        with app.app_context():
            db.create_all()
        print("Connected database!")
