from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    usn = db.Column(db.String(15), unique=True, nullable=False)  # University Serial Number
    name = db.Column(db.String(100), nullable=False)  # Full name of the student
    email = db.Column(db.String(150), nullable=False, unique=True)  # Email address
    year = db.Column(db.String(4), nullable=False)

    def __repr__(self):
        return f"<Student {self.name} ({self.usn})>"
    
class PlacementUpdate(db.Model):
    __tablename__ = 'placement_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    usn = db.Column(db.String(20), unique=True, nullable=False)  # Unique Student Number
    year = db.Column(db.String(20), nullable=False)  # Year: e.g., "3rd Year", "Final Year"
    company = db.Column(db.String(100), nullable=False)
    placement_package = db.Column(db.Float, nullable=False)  # Package offered in LPA (lakhs per annum)
    role = db.Column(db.String(100), nullable=False)  # Selected Role
    placement_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"<PlacementUpdate {self.student_name} - {self.company}>"
  
class Roadmap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)  # URL or path to the roadmap image
    description = db.Column(db.Text, nullable=True)

class Placement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    students_placed = db.Column(db.Integer, nullable=False)
 
class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PlacementDrive(id={self.id}, name='{self.name}')>"
    
class AlumniVideo(db.Model):
    __tablename__ = 'alumni_videos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(255), nullable=False) # filename of the video file
    path = db.Column(db.String(255), nullable=False)  # Path of the video file in file system
    url = db.Column(db.String(500), nullable=False)  # public url of the video
    description = db.Column(db.Text, nullable=False) # Description of the video
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AlumniVideo(id={self.id}, url='{self.url}')>"

class SeniorGuidance(db.Model):
    __tablename__ = 'senior_guidance'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SeniorGuidance(id={self.id}, name='{self.name}')>"