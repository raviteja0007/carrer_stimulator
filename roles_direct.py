from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User

# Initialize Flask app
app = Flask(__name__)

# Configure the database URI to use a specific SQLite file (database.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # This will create database.db file in the current directory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disables a warning related to modification tracking

# Initialize the SQLAlchemy object
db.init_app(app)

# Function to insert HOD and Coordinator roles into the database
def insert_roles():
    # Create HOD and Coordinator roles if they don't already exist
    if User.query.filter_by(email='aiml@gmail.com').first() is None:
        # Create HOD and Coordinator users
        hod_user = User(email='aiml@gmail.com', password='hod@1234', role='HOD')
        coordinator_user = User(email='coordinator@gmail.com', password='pc@1234', role='Coordinator')

        # Add to session and commit to the database
        db.session.add(hod_user)
        db.session.add(coordinator_user)
        db.session.commit()

        print("HOD and Coordinator roles inserted successfully!")
    else:
        print("HOD and Coordinator users already exist.")

# Run the app and insert roles into the database
with app.app_context():
    db.create_all()  # Creates all tables in the database (if not already created)
    insert_roles()   # Call the function to insert the roles into the database

# If running as a standalone script
if __name__ == '__main__':
    app.run(debug=True)
