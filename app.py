# Import necessary libraries
import os
import sys

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from psycopg2.errors import UniqueViolation
# Load the env file
load_dotenv()

# Create the flask app
app = Flask(__name__)

# Create a database connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models for the DB
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Sets information for the new user
    def __init__(self, fname, lname, email):
        self.firstname = fname
        self.lastname = lname
        self.email = email

    # Creates a list representation of the task object
    def to_list(self):
        return [self.id, self.firstname, self.lastname, self.email]

# Route to create a new user 
@app.route('/createuser', methods=['POST'])
def create_user():
    # Attempts to add new users to the database
    try:
        # Get the info sent in the POST request
        user_info=request.get_json()
        # Create a new User object with the given info
        new_user = User(user_info['fname'], user_info['lname'], user_info['email'])
        # Stage adding the new user to the database
        db.session.add(new_user)
        # Commit the staged changes
        db.session.commit()
        # If all goes well then return a success message
        return 'success', 200
    
    # Excepts missing key errors
    except KeyError as e:
        # Turn error into a string 
        error_str = str(e)
        # Create an error string based on the missing field
        error = 'missing_attribute_'+error_str.translate({ord("'"): None})
        # return error string with missing field
        return error, 200

    # Excepts non-unique or invalid information errors
    except exc.IntegrityError as e:
        # If non-unique find the key that was non-unique and return
        if isinstance(e.orig, UniqueViolation):
            if 'users_email_key' in str(e.orig):
                return 'duplicate_email', 200
            else: 
                return 'duplicate_other', 200
    
    return 'unknown_error', 200

if len(sys.argv) > 1:
    if sys.argv[1].lower() == 'migrate' or sys.argv[1].lower() == 'm':
        db.create_all()
    elif sys.argv[1].lower == 'demigrate' or sys.argv[1].lower() == 'd':
        db.drop_all()
else:
    app.run(debug=True)