from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_ckeditor import CKEditor

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
ckeditor = CKEditor(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from blogsite import routes
