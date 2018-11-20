import os

from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy

# Initialise and configure flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')

# Configure database connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
db = SQLAlchemy(app)

# Initialise SocketIO
socketio = SocketIO(app)

@app.route("/", methods=["GET"])
def index():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        return

@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == 'GET':
        return render_template("main.html")
