from flask import Flask, render_template, request 
from flask_sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

app = Flask(__name__)
lm = LoginManager() 
lm.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://localhost/ipark'
app.secret_key = "super secret"

db = SQLAlchemy(app)

from app import views