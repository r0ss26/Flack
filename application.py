import os
import re
from pytz import timezone
from momentjs import momentjs
from database import db_session
from werkzeug import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from flask import Flask, render_template, request, session, redirect, url_for, Session

# Import models in order to modify and query database
from models import User, Channel, Message

# Initialise and configure flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')
app.jinja_env.globals['momentjs'] = momentjs

# Make sessions permanent
@app.before_request
def before_request():
    session.permanent = True
    # Force https (src: https://stackoverflow.com/questions/32237379/python-flask-redirect-to-https-from-http)
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)


# Configure database connection
if not os.environ.get('DATABASE_URL'):
    raise RuntimeError("DATABASE_URL not set")

# Initialise SocketIO
socketio = SocketIO(app)

# Retrieve message channels from database
channels = []
for channel in db_session.query(Channel).all():
    channels.append(channel.channel)

@app.route("/")
def index():
    # if there is no user logged in take them to the signup page
    if not session.get("username"):
        return redirect(url_for("signup"))
    # if a user is logged in take them to the chatroom
    else:
        # If the user has previously visited then take them to the chatroom they were last in
        if session.get('current_channel'):
            return redirect(url_for("display_channel", channel=session.get('current_channel')))
        # Otherwise take them to the first channel in the list
        else:
            return redirect(url_for("display_channel", channel=channels[0]))

# Dynamic URL for different chatrooms
@app.route("/channel/<channel>", methods=['GET', 'POST'])
def display_channel(channel):
    # Request method is GET
    if request.method == 'GET':
        # If a user is not logged in redirect them to the index route
        # This stops users from viewing chatrooms without first signing up
        if not session.get('userid'):
            return redirect(url_for("index"))

        # Get mesages in the current channel and pass them to the template
        messages = db_session.query(Message).filter_by(channel=channel).all()
        session['current_channel']=channel
        return render_template("main.html", messages=messages, channels=channels)

    # Otherwise request method is POST
    # User has created a new channel
    else:
        error = None
        
        # Get users channel name input
        channel_name = request.form.get('channel-name')

        if ' ' in channel_name:
            error = ' Channels must not contain spaces'
            return render_template('main.html', error=error, channels=channels)

        # Add this channel to the database
        try:
            new_channel = Channel(channel=channel_name, created_by=session.get('userid'))
            db_session.add(new_channel)
            db_session.commit()
            channels.append(channel_name)

            # Take the user back to the chatroom
            return redirect(url_for("display_channel", channel=channel_name))

        # If the channel already exists, display an error
        except:
            error = ' Channel already exists'
            return render_template('main.html', error=error, channels=channels)

@app.route("/login", methods=["GET", "POST"])
def login():
    # Request method is GET
    if request.method == 'GET':
        # If there is no user logged in, take them to the login page
        if not session.get("username"):
            return render_template("login.html")
        # if a user us logged in then take them to the chatroom
        else:
            return redirect(url_for("index"))
        
    # Otherwise request method is POST and a user has submitted login info
    else:
        error = None

        # get login form input
        username = request.form.get('username')
        password = request.form.get('password')

        # Authenticate the login information
        # Check user input Username
        if username == '':
            error = 'Please enter a username'
            return render_template('login.html', error=error)

        # Check user input password
        if password == '':
            error = ' Please enter a password'
            return render_template('login.html', error=error)

        # Check if username exists
        try:
            user = db_session.query(User).filter_by(username = username).one()
        # If not return an error to the user
        except:
            error = ' Username does not exist'
            return render_template('login.html', error=error)

        # If username exists check that the password matches, if it doesn't
        # then return an error
        if check_password_hash(user.hash, password) == False:
            error = ' Incorrect password'
            return render_template('login.html', error=error)

        # Otherwise the username and password are correct
        else:
            # add the user to the current session and take them to the index page
            session['username'] = request.form.get("username")
            session['userid'] = db_session.query(User).filter_by(username = username).one().id
            return redirect(url_for('index'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None

    # Request method is GET
    if request.method == 'GET':

        # If there is no user logged in then continue to the signup page
        if not session.get("username"):
            return render_template("signup.html")

        # If there a user is already logged in then take them to the index page
        else:
            return redirect(url_for("index"))

    # Otherwise request method is POST
    else:
        # Get user input
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        # Check if the username is valid
        if not re.search(r'^[A-Za-z0-9_-]+$', username):
            error = ' Invalid username: Must only contain characters, numbers, underscores and/or hyphens'
            return render_template('signup.html', error=error)

        # Check if the username is available
        if db_session.query(User).filter_by(username = request.form.get("username")).all() == []:
            # If the username is availble, check if passwords match
            if password == confirm_password:
                # create a new user object
                new_user = User(username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))

                # add the user to the session
                session['username'] = request.form.get("username")

                # Submit the user into the database and take them to the index page
                db_session.add(new_user)
                db_session.commit()
                session['userid'] = db_session.query(User).filter_by(username = username).one().id
                session['username'] = username
                return redirect(url_for("index"))
                
            # If the passwords dont match, show an error and prompt user to enter
            # signup information again
            else:
                error = ' Passwords do not match'
                return render_template('signup.html', error=error)

        # Otherwise the username is taken
        else:
            error = ' Username is taken'
            return render_template('signup.html', error=error)

@app.route("/logout")
def logout():
    session.pop('username')
    session.pop('userid')
    return redirect(url_for('login'))

# Shutdown database session
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# SocketIO
# When a user submits a post at it to the database
# and broadcast the post to other users
@socketio.on('submit post')
def post(data):
    new_post = Message(user_id=session.get('userid'), channel=data['room'], message=data['message'])
    db_session.add(new_post)
    db_session.commit()
    emit('announce post', data, room=data['room'], broadcast=True)

# Anounce when a user enters a chatroom
@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    data['message'] = ': joined the room'
    emit('join room', data, room=room, broadcast=True)

# Anounce when a user leaves a chatroom
@socketio.on('leave')
def on_leave(data):
    room = data['room']   
    data['message'] = ': has left the room' 
    emit('leave room', data, room=room, broadcast=True)
    leave_room(room)
