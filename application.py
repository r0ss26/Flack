import os

from flask import Flask, render_template, request, session, redirect, url_for, Session
from flask_socketio import SocketIO, emit
from werkzeug import generate_password_hash, check_password_hash
from database import db_session
from flask_login import LoginManager, login_required

# Import models in order to modify database
from models import *

# Initialise and configure flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')

# Configure flask-login for login required functionality
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure database connection
if not os.environ.get('DATABASE_URL'):
    raise RuntimeError("DATABASE_URL not set")

# Initialise SocketIO
socketio = SocketIO(app)

@app.route("/")
def index():
    # if there is no user logged in take them to the login page
    if not session.get("username"):
        return redirect(url_for("signup"))
    # if a user is logged in take them to the home page
    else:
        return redirect(url_for("home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    # Request method is 'get'
    if request.method == 'GET':
        # If there is no user logged in, take them to the login page
        if not session.get("username"):
            return render_template("login.html")
        # if a user us logged in then take them to the home page
        else:
            return redirect(url_for("home"))

    # Otherwise request method is 'post' and a user has submitted login info
    else:

        error = None
        # Authenticate the login information
        # Check if username exists
        try:
            user = db_session.query(User).filter_by(username = request.form.get('username')).one()
        # If not return an error to the user
        except:
            error = ' Username does not exist'
            return render_template('login.html', error=error)

        # If username exists check that the password matches, if it doesn't
        # then return an error
        if check_password_hash(user.hash, request.form.get('password')) == False:
            error = ' Incorrect password'
            return render_template('login.html', error=error)

        # Otherwise the username and password are correct
        else:
            # add the user to the current session and take them to the home page
            session['username'] = request.form.get("username")
            return redirect(url_for('home'))


@app.route("/signup", methods=["GET", "POST"])
def signup():


    error = None
    # Request method is 'get'
    if request.method == 'GET':

        # If there is no user logged in then continue to the signup page
        if not session.get("username"):
            return render_template("signup.html")

        # If there a user is already logged in then take them to the home page
        else:
            return redirect(url_for("home"))

    # Otherwise request method is 'post'
    else:

        # Check if the username is available
        if db_session.query(User).filter_by(username = request.form.get("username")).all() == []:

            # If the username is availble, check if passwords match
            if request.form.get('password') == request.form.get('confirm-password'):

                # create a new user object
                new_user = User(username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))

                # add the user to the session
                session['username'] = request.form.get("username")

                # Submit the user into the database and take them to the home page
                db_session.add(new_user)
                db_session.commit()
                return redirect(url_for("home"))
            # If the passwords dont match, show an error and prompt user to enter
            # signup information again
            else:
                error = ' Passwords do not match'
                return render_template('signup.html', error=error)

        # Otherwise the username is taken
        else:
            error = ' Username is taken'
            return render_template('signup.html', error=error)


@app.route("/home", methods=["GET", "POST"])
def home():
    # Request method is 'get'
    if request.method == 'GET':

        # If there is no user logged in take them to the login page
        if not session.get('username'):
            return redirect(url_for("login"))

        # If they are logged in then continue to the home page
        else:
            return render_template("main.html")

    # Otherwise request method is POST
    else:
        return #TODO

@app.route("/logout")
def logout():
    session.pop('username')
    return redirect(url_for('login'))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
