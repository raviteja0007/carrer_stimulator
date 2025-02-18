from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from models import db, User , Student, PlacementUpdate ,Placement,PlacementDrive ,SeniorGuidance,AlumniVideo , Roadmap
from werkzeug.security import generate_password_hash
from datetime import datetime
from roles_direct import insert_roles
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'static/uploads1'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)

# Create tables when app runs for the first time
with app.app_context():
    db.create_all()

# Route to fetch student details
@app.route('/api/students')
def get_students():
    students = Student.query.all()
    student_data = [{"name": student.name, "year": student.year} for student in students]
    return jsonify(student_data)

# Route to fetch placement updates
@app.route('/api/updates', methods=['GET', 'POST'])
def manage_updates():
    if request.method == 'GET':
        # Fetch all updates
        updates = PlacementUpdate.query.all()
        updates_data = [
            {
                "id": update.id,
                "name": update.student_name,
                "usn": update.usn,
                "year": update.year,
                "company": update.company,
                "package": update.placement_package,
                "role": update.role,
                "placement_date": update.placement_date.strftime('%Y-%m-%d')
            }
            for update in updates
        ]
        return jsonify(updates_data)

    if request.method == 'POST':
        # Add a new placement update
        data = request.json

        try:
            # Validate input data
            required_fields = ['name', 'usn', 'year', 'company', 'package', 'role']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({"error": f"'{field}' is required."}), 400

            # Create a new placement update record
            new_update = PlacementUpdate(
                student_name=data['name'],
                usn=data['usn'],
                year=data['year'],
                company=data['company'],
                placement_package=float(data['package']),
                role=data['role'],
                placement_date=datetime.utcnow()
            )
            db.session.add(new_update)
            db.session.commit()
            return jsonify({"message": "Placement update added successfully"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

# Route to get all roadmaps
@app.route('/api/roadmaps', methods=['GET'])
def get_roadmaps():
    roadmaps = Roadmap.query.all()
    return jsonify([
        {
            "id": roadmap.id,
            "title": roadmap.title,
            "image_url": url_for('static', filename="uploads1/{}".format(roadmap.image_url)) if roadmap.image_url else None,
            "description": roadmap.description
        } for roadmap in roadmaps
    ])

@app.route('/api/roadmaps', methods=['POST'])
def add_roadmap():
    if 'image_url' not in request.files or 'title' not in request.form or 'description' not in request.form:
        return jsonify({"error": "Missing required fields"}), 400

    file = request.files['image_url']
    title = request.form['title']
    description = request.form['description']

    if file and file.filename != '':
        # Secure the filename
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Save the file
        try:
            file.save(file_path)
        except Exception as e:
            return jsonify({"error": "Failed to save file", "details": str(e)}), 500
    else:
        return jsonify({"error": "Invalid or missing file"}), 400

    # Create a new Roadmap object
    new_roadmap = Roadmap(
        title=title,
        image_url=filename,
        description=description
    )

    # Save the roadmap to the database
    try:
        db.session.add(new_roadmap)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": "Failed to save roadmap to the database", "details": str(e)}), 500

    # Generate the public URL for the image
    image_url = url_for('static', filename=os.path.join(app.config['UPLOAD_FOLDER'], filename), _external=True)

    return jsonify({
        "id": new_roadmap.id,
        "title": new_roadmap.title,
        "image_url": image_url,
        "description": new_roadmap.description
    }), 201

# Route to delete a roadmap
@app.route('/api/roadmaps/<int:id>', methods=['DELETE'])
def delete_roadmap(id):
    roadmap = Roadmap.query.get(id)
    if not roadmap:
        return jsonify({"error": "Roadmap not found"}), 404

    if roadmap.image_url:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], roadmap.image_url)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(roadmap)
    db.session.commit()

    return jsonify({"message": "Roadmap deleted"}), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        # Query the database using SQLAlchemy
        user = User.query.filter_by(email=email).first()

        if user and user.password == password and user.role == role:
            # Redirect based on role
            if role == 'student':
                return redirect(url_for('student_dashboard'))
            elif role == 'HOD':
                return redirect(url_for('hod_dashboard'))
            elif role == 'Coordinator':
                return redirect(url_for('coordinator_dashboard'))
        else:
            flash('Invalid email, password, or role. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        usn = request.form.get('usn')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        year = request.form.get('year')

        # Check if the USN or email already exists in the Student table
        existing_student = Student.query.filter((Student.usn == usn) | (Student.email == email)).first()

        # Check if the email already exists in the User table
        existing_user = User.query.filter_by(email=email).first()

        if existing_student or existing_user:
            flash('USN or Email already exists. Please use a different one.', 'danger')
            return redirect(url_for('signup'))

        # Hash the password for security

        # Create a new Student object
        new_student = Student(usn=usn, name=name, email=email, year=year)

        # Create a new User object with role 'student'
        new_user = User(email=email, password=password, role='student')

        # Add both the student and user to the database
        db.session.add(new_student)
        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


# Define other routes for login, dashboard, etc.
@app.route('/student_dashboard')
def student_dashboard():
    # Fetch student data from the database
    return render_template('student_dashboard.html')

@app.route('/hod_dashboard')
def hod_dashboard():
    # Fetch HOD data from the database
    return render_template('hod_dashboard.html')

@app.route('/coordinator_dashboard')
def coordinator_dashboard():
    # Fetch placement coordinator data from the database
    return render_template('coordinator_dashboard.html')


# cordinator api belows
# API to Add Placement Data
@app.route('/api/placement/add', methods=['POST'])
def add_placement():
    data = request.get_json()
    try:
        new_placement = Placement(
            company_name=data['company_name'],
            year=data['year'],
            students_placed=data['students_placed'],
        )
        db.session.add(new_placement)
        db.session.commit()
        return jsonify({"message": "Placement data added successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# API to Retrieve Placement Data
@app.route('/api/placement', methods=['GET'])
def get_placements():
    try:
        placements = Placement.query.order_by(Placement.year.desc(), Placement.company_name).all()
        results = [
            {
                "id": placement.id,
                "company_name": placement.company_name,
                "year": placement.year,
                "students_placed": placement.students_placed,
            }
            for placement in placements
        ]
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# placemt drive api
@app.route('/api/drives/add', methods=['POST'])
def add_drive():
    try:
        # Parse JSON data from the request
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')

        # Validate the inputs
        if not name or not description:
            return jsonify({'error': 'Name and description are required'}), 400

        # Create a new PlacementDrive instance
        drive = PlacementDrive(name=name, description=description)

        # Add and commit the new drive to the database
        db.session.add(drive)
        db.session.commit()

        # Return a success response
        return jsonify({
            'message': 'Placement drive added successfully',
            'drive': {
                'id': drive.id,
                'name': drive.name,
                'description': drive.description,
                'created_at': drive.created_at
            }
        }), 201
    except Exception as e:
        # Handle unexpected errors
        return jsonify({'error': str(e)}), 500

# API to fetch all placement drives
@app.route('/api/drives', methods=['GET'])
def get_drives():
    """
    Fetch all placement drives.
    """
    drives = PlacementDrive.query.all()
    drives_list = [
        {"id": drive.id, "name": drive.name, "description": drive.description, "created_at": drive.created_at}
        for drive in drives
    ]
    return jsonify(drives_list), 200

# API to delete a specific placement drive by ID
@app.route('/api/drives/delete/<int:drive_id>', methods=['DELETE'])
def delete_drive(drive_id):
    """
    Delete a placement drive by ID.
    """
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return jsonify({"error": "Drive not found"}), 404

    db.session.delete(drive)
    db.session.commit()
    return jsonify({"message": f"Drive with ID {drive_id} deleted successfully."}), 200

# ------------------ Alumni Video Routes ------------------
# Add an alumni video (now handles file uploads)
@app.route('/api/alumni-videos/upload', methods=['POST'])
def upload_alumni_video():
    if 'video' not in request.files or 'description' not in request.form:
        return jsonify({'error': 'Video file and description are required'}), 400

    video_file = request.files['video']
    description = request.form['description']

    if video_file.filename == '':
        return jsonify({'error': 'No video selected'}), 400

    try:
         filename = secure_filename(video_file.filename)
         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
         video_file.save(file_path)

         video_url = url_for('static', filename="uploads1/{}".format(filename), _external=True)
         new_video = AlumniVideo(filename=filename, path=file_path, url=video_url, description=description)
         db.session.add(new_video)
         db.session.commit()
         return jsonify({'message': 'Alumni video uploaded successfully', 'video_url': video_url})

    except Exception as e:
         return jsonify({'error': f'Error saving video to storage: {str(e)}'}), 500

# Get all alumni videos
@app.route('/api/alumni-videos', methods=['GET'])
def get_alumni_videos():
    videos = AlumniVideo.query.all()
    video_list = []
    for video in videos:
        video_list.append({
            "id": video.id,
            "filename": video.filename,
            "path": video.path,
            "url": video.url,
            "description": video.description
        })
    return jsonify(video_list), 200

# Delete an alumni video by ID (now deletes from storage)
@app.route('/api/alumni-videos/delete/<int:video_id>', methods=['DELETE'])
def delete_alumni_video(video_id):
    video = AlumniVideo.query.get(video_id)
    if not video:
        return jsonify({'error': 'Video not found'}), 404

    try:
        # remove file from storage
        os.remove(video.path)
        db.session.delete(video)
        db.session.commit()
        return jsonify({'message': 'Alumni video deleted successfully'})
    except Exception as e:
      return jsonify({'error': f'Failed to delete video from storage: {str(e)}'}), 500

# ------------------ Senior Guidance Routes ------------------

# Add a senior guidance entry
@app.route('/api/senior-guidance/add', methods=['POST'])
def add_senior_guidance():
    data = request.json
    if not data.get('name') or not data.get('text'):
        return jsonify({'error': 'Name and text are required.'}), 400

    new_guidance = SeniorGuidance(name=data['name'], text=data['text'])
    db.session.add(new_guidance)
    db.session.commit()

    return jsonify({'message': 'Senior guidance added successfully!', 'id': new_guidance.id})

# Get all senior guidance entries
@app.route('/api/senior-guidance', methods=['GET'])
def get_senior_guidance():
    guidances = SeniorGuidance.query.all()
    return jsonify([
        {'id': guidance.id, 'name': guidance.name, 'text': guidance.text, 'created_at': guidance.created_at}
        for guidance in guidances
    ])

# Delete a senior guidance entry by ID
@app.route('/api/senior-guidance/delete/<int:guidance_id>', methods=['DELETE'])
def delete_senior_guidance(guidance_id):
    guidance = SeniorGuidance.query.get(guidance_id)
    if not guidance:
        return jsonify({'error': 'Guidance not found.'}), 404

    db.session.delete(guidance)
    db.session.commit()

    return jsonify({'message': 'Senior guidance deleted successfully!'})

# Error Handling
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

def insert_roles():
    with app.app_context():  # Ensures the function runs with the app context
        hod_user = User(email='aiml@gmail.com', password='hod1234', role='HOD')
        coordinator_user = User(email='coordinator@gmail.com', password='pc1234', role='Coordinator')

        # Add to the session and commit to the database
        db.session.add(hod_user)
        db.session.add(coordinator_user)
        db.session.commit()

        print("HOD and Coordinator roles inserted successfully!")

if __name__ == '__main__':
    with app.app_context():  # Create tables before running the app
        db.create_all()
    # Optionally, call the function to insert roles (comment out after the first run)
    # insert_roles()
    app.run(debug=True)