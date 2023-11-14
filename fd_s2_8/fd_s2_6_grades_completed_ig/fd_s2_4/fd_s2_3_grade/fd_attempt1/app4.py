import json
from flask import Flask, render_template, request, redirect, url_for, session,send_file,send_from_directory,send_file
from flask import make_response
from flask import make_response
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import random
import string
import pandas as pd
import os
import pdfkit
import math
import io
import base64
import matplotlib.pyplot as plt
# from flask_weasyprint import HTML, render_pdf
app = Flask(__name__, static_folder='static')


# Configure the database connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'faculty'
# app.config['UPLOAD_FOLDER'] = r'F:\fd_s2_1\fd_attempt_finale_BY_MASTER\fd_attempt_finale\fd_attempt_4\fd_attempt_latest\fd_attempt1\uploads'
# app.config['UPLOAD_FOLDER'] = r'C:\Users\triam\Downloads\fd_s2_2\fd_s2_1\fd_attempt_finale_BY_MASTER\fd_attempt_finale\fd_attempt_4\fd_attempt_latest\fd_attempt1\uploads'
app.config['UPLOAD FOLDER'] = r'F:\fd_s2_6_grades_completed_ig\fd_s2_4\fd_s2_3_grade\fd_attempt1\uploads'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'facdashemail@gmail.com'
app.config['MAIL_PASSWORD'] = 'mwhqzbjlitxgabqy'
# app.config['MAIL_DEFAULT_SENDER'] = 'your_sender_email_address'
mysql = MySQL(app)
mail = Mail(app)

# Set a secret key for the session
app.secret_key = 'your_secret_key_here'

# Generate a verification code
def generate_verification_code():
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(6))

@app.route('/')
def index():
    return redirect(url_for('login'))  
@app.route('/signup', methods=['GET', 'POST'])
def signup(): #works
    # Handle the form submission
    if request.method == 'POST':
        faculty_id = request.form.get('faculty_id')
        faculty_name = request.form.get('faculty_name')
        faculty_email = request.form.get('faculty_email')
        password = request.form.get('password')

        # Insert the faculty details into the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO faculty_details (faculty_id, faculty_name, faculty_email, password) VALUES (%s, %s, %s, %s)", (faculty_id, faculty_name, faculty_email, password))
        mysql.connection.commit()
        cur.close()

        # Redirect the user to the login page
        return redirect(url_for('login'))
    else:
        return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():#works
    # Handle the form submission
    if request.method == 'POST':
        faculty_id = request.form['faculty_id']
        password = request.form['password']
        # app.logger.info("inside the login")
        # Query the database to check if the credentials are correct
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM faculty_details WHERE faculty_id=%s AND password=%s", (faculty_id, password))
        result = cur.fetchone()
        cur.close()

        # If the credentials are correct, set the session variables and redirect the user to the home page
        if result:
            session['faculty_id'] = result[0]
            return redirect(url_for('home'))

        # If the credentials are incorrect, show an error message
        else:
            error = 'Invalid credentials. Please try again.'
            return "invalid cred"
    else:
        return render_template('login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password(): #works
    if request.method == 'POST':
        faculty_id = request.form['faculty_id']
        
        # Query the database to get the faculty's email
        cur = mysql.connection.cursor()
        cur.execute("SELECT faculty_email FROM faculty_details WHERE faculty_id=%s", (faculty_id,))
        result = cur.fetchone()
        cur.close()

        if result:
            email = result[0]
            verification_code = generate_verification_code()

            # Store the verification code in the session
            session['verification_code'] = verification_code
            session['faculty_id'] = faculty_id

            # Send the verification code to the faculty's email
            msg = Message('Password Reset Verification Code', sender='facdashemail@gmail.com', recipients=[email])
            msg.body = f"Your verification code is: {verification_code}"
            mail.send(msg)

            # Redirect to the verification page
            return redirect(url_for('verify_code'))

        # If the faculty ID does not exist, show an error message
        else:
            error = 'Faculty ID does not exist. Please try again.'
            return "Faculty ID does not exist"
    else:
        return render_template('forgot_password.html')

@app.route('/verify_code', methods=['GET', 'POST'])
def verify_code(): #works
    if request.method == 'POST':
        entered_code = request.form['verification_code']
        stored_code = session.get('verification_code')
        faculty_id = session.get('faculty_id')

        if entered_code == stored_code:
            # Verification successful, redirect to the password reset form
            return redirect(url_for('reset_password', faculty_id=faculty_id))
        else:
            # Incorrect verification code, show an error message
            error = 'Incorrect verification code. Please try again.'
            return "Incorrect verification code"
    else:
        return render_template('verify_code.html')

@app.route('/reset_password/<faculty_id>', methods=['GET', 'POST'])
def reset_password(faculty_id): #works
    if request.method == 'POST':
        new_password = request.form['new_password']

        # Update the faculty's password in the database
        cur = mysql.connection.cursor()
        cur.execute("UPDATE faculty_details SET password=%s WHERE faculty_id=%s", (new_password, faculty_id))
        mysql.connection.commit()
        cur.close()

        # Redirect to the login page
        return redirect(url_for('login'))
    else:
        return render_template('reset_password.html', faculty_id=faculty_id)



@app.route('/home')
def home(): #works
    # Check if the user is logged in
    if 'faculty_id' not in session:
        return redirect(url_for('login'))

    # Get the logged-in faculty member's name and courses from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT faculty_name FROM faculty_details WHERE faculty_id=%s", (session['faculty_id'],))
    result = cur.fetchone()
    faculty_name = result[0]

    cur.execute("SELECT * FROM faculty_course WHERE faculty_id=%s", (session['faculty_id'],))
    courses = cur.fetchall()
    cur.close()

    # Render the home page with the faculty member's name and courses
    return render_template('home.html', faculty_name=faculty_name, courses=courses)

@app.route('/add_course', methods=['GET', 'POST'])
def add_course():#works
    # Check if the user is logged in
    if 'faculty_id' not in session:
        return redirect(url_for('login'))

    # If the request is a POST, process the form data
    if request.method == 'POST':
        course_id = request.form['course_id']
        faculty_id = session['faculty_id']

        # Obtain the course_name from the courses table
        cur = mysql.connection.cursor()
        cur.execute("SELECT course_name FROM courses WHERE course_id = %s", (course_id,))
        course_name = cur.fetchone()[0]
        cur.close()

        # Insert the new course into the faculty_course table
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO faculty_course (faculty_id, course_id, course_name) VALUES (%s, %s, %s)",
                    (faculty_id, course_id, course_name))
        mysql.connection.commit()
        cur.close()

        # Redirect to the home page
        return redirect(url_for('home'))

    # If the request is a GET, display the form
    cur = mysql.connection.cursor()
    cur.execute("SELECT course_id, course_name FROM courses WHERE course_id NOT IN (SELECT course_id FROM faculty_course WHERE faculty_id=%s)",
                (session['faculty_id'],))
    available_courses = cur.fetchall()
    cur.close()

    return render_template('add_course.html', available_courses=available_courses)


@app.route('/delete_course/<string:course_id>', methods=['POST'])
def delete_course(course_id): #works
    # Check if the user is logged in
    if 'faculty_id' not in session:
        return redirect(url_for('login'))

    # Delete the course from the database
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM faculty_course WHERE faculty_id=%s AND course_id=%s", (session['faculty_id'], course_id))
    mysql.connection.commit()
    cur.close()

    # Redirect to the home page
    return redirect(url_for('home'))


@app.route('/course_home/<course_id>')
def course_home(course_id): #works
    # Check if the user is logged in
    if 'faculty_id' not in session:
        return redirect(url_for('login'))

    # Query the database to get the course name
    cur = mysql.connection.cursor()
    cur.execute("SELECT course_name FROM courses WHERE course_id = %s", (course_id,))
    course_name = cur.fetchone()[0]
    cur.close()

    # Render the course homepage
    return render_template('course_home.html', course_name=course_name,course_id=course_id)

# ...

@app.route('/add_students/<string:course_id>', methods=['GET', 'POST'])
def add_students(course_id): #works
    # Check if the user is logged in
    if 'faculty_id' not in session:
        return redirect(url_for('login'))

    faculty_id = session['faculty_id']

    # If the request is a POST, process the form data
    if request.method == 'POST':
        # Get the uploaded file from the form
        file = request.files['file']
        
        # Read the Excel file using pandas
        df = pd.read_excel(file)
        
        # Get the MySQL cursor
        cur = mysql.connection.cursor()
        
        # Loop through the rows of the DataFrame and insert records into the table
        for _, row in df.iterrows():
            student_id = row['Student_ID']
            
            # Check if the record already exists
            cur.execute("SELECT COUNT(*) FROM student_course WHERE student_id = %s AND faculty_id = %s AND course_id = %s",
                        (student_id, faculty_id, course_id,))
            result = cur.fetchone()
            if result[0] == 0:
                # Insert the record into the student_course table
                cur.execute("INSERT INTO student_course (student_id, faculty_id, course_id) VALUES (%s, %s, %s)",
                            (student_id, faculty_id, course_id,))
        
        # Commit the changes and close the cursor
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('course_home', course_id=course_id))
    
    
    return render_template('add_students.html',course_id=course_id)


@app.route('/delete_student/<string:course_id>', methods=['GET', 'POST'])
def delete_student(course_id): 
    # Check if the user is logged in
    if 'faculty_id' not in session:
        return redirect(url_for('login'))

    faculty_id = session['faculty_id']

    # If the request is a POST, process the form data
    if request.method == 'POST':
        student_id = request.form['student_id']

        # Delete the student from the student_course table
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM student_course WHERE student_id = %s AND course_id = %s AND faculty_id = %s",
                    (student_id, course_id, faculty_id))
        mysql.connection.commit()
        cur.close()

        # Redirect to the course homepage
        return redirect(url_for('course_home', course_id=course_id))

    # If the request is a GET, display the form
    cur = mysql.connection.cursor()
    cur.execute("SELECT student_id FROM student_course WHERE course_id = %s AND faculty_id = %s",
                (course_id, faculty_id))
    enrolled_students = cur.fetchall()
    cur.close()

    return render_template('delete_students.html', enrolled_students=enrolled_students, course_id=course_id)

@app.route('/attendance_home/<course_id>')
def attendance_home(course_id):
    # Check if the user is logged in
    if 'faculty_id' not in session:
        return redirect(url_for('login'))

    # Query the database to get the course name
    cur = mysql.connection.cursor()
    cur.execute("SELECT course_name FROM courses WHERE course_id = %s", (course_id,))
    course_name = cur.fetchone()[0]
    cur.close()

    return render_template('attendance_home.html', course_name=course_name, course_id=course_id)


@app.route('/take_attendance/<course_id>', methods=['GET', 'POST'])
def take_attendance(course_id):
    # Check if the user is logged in
    if 'faculty_id' not in session:
        return redirect(url_for('login'))

    # If the request is a POST, process the form data
    if request.method == 'POST':
        hour = request.form['hour']
        date = request.form['date']

        # Get the attendance status for each student
        attendance_data = {}
        for key, value in request.form.items():
            if key.startswith('status_'):
                student_id = key.replace('status_', '')
                attendance_data[student_id] = value

        # Update the attendance records in the database
        cur = mysql.connection.cursor()
        for student_id, status in attendance_data.items():
            cur.execute("INSERT INTO attendance (faculty_id, course_id, student_id, date_, hour_, status_) VALUES (%s, %s, %s, %s, %s, %s)",
                        (session['faculty_id'], course_id, student_id, date, hour, status,))
        mysql.connection.commit()
        cur.close()

        # Redirect to the attendance management page
        return redirect(url_for('take_attendance', course_id=course_id))

    else:
        # Retrieve the course name and student information
        cur = mysql.connection.cursor()
        cur.execute("SELECT course_name FROM courses WHERE course_id = %s", (course_id,))
        course_name = cur.fetchone()[0]
        
        cur.execute("SELECT student_id  FROM student_course WHERE course_id = %s AND faculty_id = %s",
                    (course_id, session['faculty_id'],))
        students = cur.fetchall()
        cur.close()

        return render_template('take_attendance.html', course_id=course_id, students=students)
#attendance management end

@app.route('/grade/<course_id>')
def grade(course_id):
    # Check if the user is logged in
    if 'faculty_id' not in session:
        return redirect(url_for('login'))

    # Connect to the database
    cursor = mysql.connection.cursor()

    # Retrieve the course name from the database using the course_id)
    cursor.execute("SELECT course_name FROM courses WHERE course_id = %s", (course_id, ))

    # Close the database connection and cursor
    cursor.close()

    # Redirect to the grade.html template, passing the course_id and course_name as arguments
    return render_template('grade.html', course_id=course_id)

@app.route('/view_grades/<course_id>', methods=['GET', 'POST'])
def view_grades(course_id):
    if 'faculty_id' not in session:
        return redirect(url_for('login'))
    # Retrieve the student grades from the database using the course_id
    faculty_id = session['faculty_id']
    if request.method == 'POST':
        # Get the uploaded file from the form
        file = request.files['file']
        
        # Read the Excel file using pandas
        df = pd.read_excel(file)
        
        # Get the MySQL cursor
        cur = mysql.connection.cursor()
        
        # Loop through the rows of the DataFrame and insert records into the table
        for _, row in df.iterrows():
            student_id = row['Student_ID']
            test_name = row['Test_Name']
            test_score = row['Test_Score']
            total_marks = row['Total_Marks']

            
            # Check if the record already exists
            cur.execute("SELECT COUNT(*) FROM grades WHERE student_id = %s AND faculty_id = %s AND course_id = %s and test_name = %s",
                        (student_id, faculty_id, course_id,test_name,))
            result = cur.fetchone()
            if result[0] == 0:
                # Insert the record into the student_course table
                cur.execute("INSERT INTO grades (student_id, faculty_id, course_id,test_name,test_score,total_marks) VALUES (%s, %s, %s,%s,%s,%s)",
                            (student_id, faculty_id, course_id,test_name,test_score,total_marks,))
        
        # Commit the changes and close the cursor
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('view_grades', course_id=course_id))
    
    cursor = mysql.connection.cursor()
    # Retrieve the course name from the database using the course_id
    cursor.execute("SELECT course_name FROM courses WHERE course_id = %s", (course_id,))
    result = cursor.fetchone()

    if result is None:
        course_name = "Unknown"
    else:
        course_name = result[0]
    cursor.execute("SELECT student_id, test_name, test_score, total_marks from grades WHERE course_id = %s AND faculty_id = %s ORDER BY test_name", (course_id, session['faculty_id'],))
    student_grades = cursor.fetchall()
    # Retrieve the test names from the database for the given course_id
    cursor.execute("SELECT DISTINCT test_name FROM grades WHERE course_id = %s", (course_id,))
    test_names = [row[0] for row in cursor.fetchall()]

    return render_template('view_grades.html',course_id=course_id, course_name=course_name, student_grades=student_grades, test_names=test_names)

#this is for customize_grading
@app.route('/customize_grading/<string:course_id>', methods=['GET', 'POST'])
def customize_grading(course_id):
    # Check if the user is logged in
    if 'faculty_id' not in session:
        return redirect(url_for('login'))

    # Connect to the database
    cursor = mysql.connection.cursor()

    # Retrieve the course name from the database using the course_id
    cursor.execute("SELECT course_name FROM courses WHERE course_id = %s", (course_id,))
    course_name = cursor.fetchone()[0]

    # Retrieve the test names for the given course from the grades table
    cursor.execute("SELECT DISTINCT test_name FROM grades WHERE course_id = %s", (course_id,))
    test_names = [row[0] for row in cursor.fetchall()]

    # Retrieve the grading scale for the given course
    cursor.execute("SELECT test_name, weight FROM scale WHERE course_id = %s AND faculty_id = %s", (course_id, session['faculty_id']))
    grading_scale = [{'test_name': row[0], 'weight': row[1]} for row in cursor.fetchall()]

    # Handle form submission
    if request.method == 'POST':
        # Retrieve the submitted data
        test_name = request.form['test_name']
        weight = request.form['weight']

        # Update the weight for the selected test in the scale table
        # cursor.execute("INSERT INTO scale (weight, course_id, faculty_id, test_name) VALUES (%s, %s, %s, %s)",
        #        (weight, course_id, session['faculty_id'], test_name,))
        cursor.execute("""INSERT INTO scale (weight, course_id, faculty_id, test_name) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE weight = VALUES(weight),faculty_id = VALUES(faculty_id),test_name = VALUES(test_name)""", (weight, course_id, session['faculty_id'], test_name,))

        mysql.connection.commit()

        # Redirect to the view_grades page for the current course
        return redirect(url_for('view_grades', course_id=course_id))

    # Close the database connection and cursor
    cursor.close()

    # Render the customize_grading.html template, passing the test_names and grading_scale for the current course as arguments
    return render_template('customize_grading.html', course_id=course_id, course_name=course_name, test_names=test_names, grading_scale=grading_scale)

@app.route('/assignment_home/<course_id>')
def assignment_home(course_id):
    # Render assignment_home.html with the course_id
    return render_template('assignment_home.html', course_id=course_id)
@app.route('/add_assignment/<course_id>', methods=['GET', 'POST'])
def add_assignment(course_id):
    if request.method == 'POST':
        # Get the assignment details from the form
        faculty_id=session['faculty_id']
        query = "SELECT student_id FROM student_course WHERE course_id = %s AND faculty_id = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(query, (course_id, faculty_id))
        student_ids = [row[0] for row in cursor.fetchall()]
        cursor.close()

        # Step 2 and 3: Iterate over student IDs and insert data into the attendance table
        for student_id in student_ids:
            assignment_name = request.form['assignment_name']
            due_date = request.form['due_date']
            instructions = request.form['instructions']

            # Insert the data into the attendance table
            insert_query = "INSERT INTO assignment (student_id, course_id, faculty_id, assignment_name, due_date, instructions) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor = mysql.connection.cursor()
            cursor.execute(insert_query, (student_id, course_id, faculty_id, assignment_name, due_date, instructions))
            mysql.connection.commit()
            cursor.close()
        return "Assignment created successfully"
    else:
        return render_template('add_assignment.html', course_id=course_id)


@app.route('/set_attendance_grade_weight/<course_id>', methods=['GET', 'POST'])
def set_attendance_grade_weight(course_id):
    if request.method == 'POST':
        attendance_grade_weight = float(request.form.get('attendance_grade_weight'))

        # Update the attendance grade weight in the database for the specified course
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE courses SET attendance_grade_weight = %s WHERE course_id = %s", (attendance_grade_weight, course_id))
        mysql.connection.commit()

        # Redirect back to the view grades page or any other desired page
        return redirect(url_for('view_grades', course_id=course_id))

    # If the method is GET, render the set_attendance_grade_weight.html template
    return render_template('set_attendance_grade_weight.html', course_id=course_id)

@app.route('/view_assignments/<course_id>', methods=['GET', 'POST'])
def view_assignments(course_id):
    # Retrieve assignments for the given course_id
    faculty_id=session["faculty_id"]
    query = "SELECT DISTINCT assignment_name FROM assignment WHERE course_id = %s and faculty_id =%s"
    cursor = mysql.connection.cursor()
    cursor.execute(query, (course_id,faculty_id,))
    assignments = [row[0] for row in cursor.fetchall()]
    cursor.close()

    if request.method == 'POST':
        selected_assignment = request.form['assignment']
        # Retrieve and display student submissions for the selected assignment
        query = "SELECT student_id, submitted_date, student_submission FROM submissions WHERE course_id = %s AND faculty_id =%s AND assignment_name = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(query, (course_id, faculty_id,selected_assignment,))
        submissions = cursor.fetchall()
        cursor.close()

        return render_template('view_assignment.html', course_id=course_id, assignments=assignments, selected_assignment=selected_assignment, submissions=submissions)
    return render_template('view_assignment.html', course_id=course_id, assignments=assignments)


@app.route('/logout')
def logout():
    # Clear the session variables and redirect the user to the login page
    session.clear()
    return redirect(url_for('login'))
# Sample data - replace with your actual data or database integration


@app.route('/materials/<string:course_id>', methods=['GET', 'POST'])
def materials(course_id):
    faculty_id=session["faculty_id"]
    if request.method == 'POST':
        title = request.form['title']
        # description = request.form['description']
        file = request.files['file']
        

        # Save the file
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Create a new material entry in the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO materials (course_id, faculty_id,file_name,file_path) VALUES (%s, %s,%s, %s)",
                    (course_id, faculty_id,title,filename,))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('materials', course_id=course_id))

    else:
        # Retrieve materials for the given course_id and faculty_id from the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM materials WHERE course_id = %s AND faculty_id = %s", (course_id, faculty_id,))
        materials = cur.fetchall()
        cur.close()

        return render_template('materials.html', materials=materials,course_id=course_id)


@app.route('/download/<filename>')
def download(filename):
    # Get the path to the file based on the filename
    # Replace 'your_query_to_get_file_path' with your actual query
    cur = mysql.connection.cursor()
    cur.execute("SELECT file_path FROM materials WHERE file_name = %s", (filename,))
    result = cur.fetchone()
    if result:
        file_path = result[0]
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found"

@app.route('/download_submission/<path:filename>')
def download_submission(filename):
    file_path = os.path.abspath(filename.strip())
    return send_file(file_path, as_attachment=True)


@app.route('/discussions/<string:course_id>', methods=['GET', 'POST'])
def discussions(course_id):
    cur = mysql.connection.cursor()
    faculty_id=session["faculty_id"]
    if request.method == 'POST':
        message = request.form['message']
        cur.execute("INSERT INTO discussions (course_id, faculty_id, message) VALUES (%s, %s, %s)",
                    (course_id, faculty_id, message,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('discussions', course_id=course_id))

    else:
        cur.execute("SELECT message FROM discussions WHERE course_id=%s AND faculty_id=%s",
                    (course_id, faculty_id,))
        messages = cur.fetchall()
        cur.close()
        return render_template('discussions.html', course_id=course_id, messages=messages)


@app.route('/view_attendance/<course_id>', methods=['GET', 'POST'])
def view_attendance(course_id):
    # Check if the user is logged in
    if 'faculty_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get the form data
        roll_number = request.form.get('search')
        date = request.form.get('date')
        hour = request.form.get('hour')

        # Retrieve attendance records based on the input values
        cur = mysql.connection.cursor()
        if roll_number and date and hour:
            # Case 1: Specific student, date, and hour
            cur.execute("SELECT * FROM attendance WHERE student_id = %s AND course_id = %s AND date_ = %s AND hour_ = %s",
                        (roll_number, course_id, date, hour))
        elif roll_number:
            # Case 2: Specific student
            cur.execute("SELECT * FROM attendance WHERE student_id = %s AND course_id = %s",
                        (roll_number, course_id))
        elif date and hour:
            # Case 3: All students based on date and hour
            cur.execute("SELECT * FROM attendance WHERE course_id = %s AND date_ = %s AND hour_ = %s",
                        (course_id, date, hour))
        else:
            # No input values provided, redirect back to the page
            return redirect(url_for('view_attendance', course_id=course_id))

        attendance = cur.fetchall()
        cur.close()

        # Render the template with the attendance records
        return render_template('view_attendance.html', attendance=attendance, course_id=course_id)

    # Render the template for initial page load
    return render_template('view_attendance.html', course_id=course_id)

def fetch_attendance(roll_number, course_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM attendance WHERE student_id = %s AND course_id = %s", (roll_number, course_id))
    attendance = cur.fetchall()
    cur.close()
    return attendance
    

def get_student_attendance(roll_number):
    try:
        # Query the attendance table to get the attendance records for the student
        cur = mysql.connection.cursor()
        cur.execute("SELECT date_, hour_, status_ FROM attendance WHERE student_id = %s", (roll_number,))
        attendance = cur.fetchall()
        cur.close()

        if len(attendance) > 0:
            attendance_records = []
            for record in attendance:
                attendance_records.append({
                    'date_': record[0],
                    'hour_': record[1],
                    'status_': record[2]
                })
            return attendance_records
        else:
            return None
    except Exception as e:
        print(f"Error fetching attendance records: {str(e)}")
        return None

@app.route('/convert_to_pdf', methods=['POST'])
def convert_to_pdf():
    attendance_data = request.form.get('attendance_data')
    # Parse the JSON data received
    attendance_records = json.loads(attendance_data)
    
    # Generate HTML for the attendance table
    html_content = '''
    <html>
    <head>
      <style>
        /* Add your custom CSS styles for the PDF here */
      </style>
    </head>
    <body>
      <h2>Attendance Records</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Hour</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
    '''

    for record in attendance_records:
        html_content += f'''
          <tr>
            <td>{record['date_']}</td>
            <td>{record['hour_']}</td>
            <td>{record['status_']}</td>
          </tr>
        '''

    html_content += '''
        </tbody>
      </table>
    </body>
    </html>
    '''

    # Generate PDF from HTML content
    pdf = pdfkit.from_string(html_content, False)

    # Create a response with PDF content
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=attendance.pdf'

    return response



# Calculate the final grade for each student
def calculate_final_grade(test_scores, scale):
    final_grades = []
    for student_scores in test_scores:
        total_marks = 0
        obtained_marks = 0

        # Calculate the total marks and obtained marks based on the test scores and scale
        for score in student_scores:
            total_marks += score[2]  # Consider the total marks for each test
            obtained_marks += (score[2] * scale[score[1]])  # Multiply the test marks with the respective weight from the scale

        # Calculate the percentage and assign the grade
        percentage = (obtained_marks / total_marks) * 100
        final_grade = assign_grade(percentage)
        final_grades.append((student_scores[0][0], final_grade))

    return final_grades

# Assign grade based on the percentage
def assign_grade(percentage):
    if percentage >= 90:
        return "O"
    elif percentage >= 80:
        return "A+"
    elif percentage >= 70:
        return "A"
    elif percentage >= 60:
        return "B+"
    elif percentage >= 50:
        return "B"
    elif percentage >= 40:
        return "C+"
    elif percentage >= 35:
        return "C"
    else:
        return "F"
    

@app.route('/final_grades/<course_id>', methods=['GET', 'POST'])
def final_grades(course_id):
    faculty_id=session['faculty_id']
    if request.method == 'POST': #editing the grades
        # Handle the form submission for updating grades
        student_id = request.form['student_id']
        grade = request.form['grade']

        # Update the grade in the database for the given student_id and course_id
        cur = mysql.connection.cursor()
        cur.execute("UPDATE final_grades SET final_grade = %s WHERE student_id = %s AND course_id = %s AND faculty_id=%s",(grade, student_id, course_id,faculty_id,))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('final_grades', course_id=course_id))

    else:
        # Retrieve grades for the given course_id from the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT student_id, test_name, test_score, total_marks FROM grades WHERE course_id = %s and faculty_id =%s", (course_id,faculty_id,))
        grades = cur.fetchall()
        cur.close()

        # Calculate the final grade for each student
        final_grades = []
        for grade in grades:
            student_id = grade[0]
            test_name = grade[1]
            test_score = grade[2]
            total_marks = grade[3]

            # Calculate the percentage
            percentage = (test_score / total_marks) * 100

            # Retrieve the weight for the test from the scale table
            cur = mysql.connection.cursor()
            cur.execute("SELECT weight FROM scale WHERE course_id = %s AND test_name = %s", (course_id, test_name,))
            result = cur.fetchone()
            cur.close()

            if result:
                weight = result[0]
                # Calculate the weighted percentage
                weighted_percentage = percentage * weight

                # Assign the grade based on the weighted percentage
                if weighted_percentage >= 90:
                    final_grade = 'O'
                elif weighted_percentage >= 80:
                    final_grade = 'A+'
                elif weighted_percentage >= 70:
                    final_grade = 'A'
                elif weighted_percentage >= 60:
                    final_grade = 'B+'
                elif weighted_percentage >= 50:
                    final_grade = 'B'
                elif weighted_percentage >= 40:
                    final_grade = 'C+'
                elif weighted_percentage >= 30:
                    final_grade = 'C'
                elif weighted_percentage >= 20:
                    final_grade = 'D'
                else:
                    final_grade = 'F'

                final_grades.append((student_id, final_grade))

        # Update the existing records or insert new records into the final_grades table
        cur = mysql.connection.cursor()
        for grade in final_grades:
            student_id = grade[0]
            final_grade = grade[1]

            # cur.execute("INSERT INTO final_grades (student_id, course_id, final_grade) VALUES (%s, %s, %s)", (student_id, course_id, final_grade, ))
            cur.execute("INSERT INTO final_grades (student_id, course_id,faculty_id, final_grade) VALUES (%s, %s, %s,%s) ON DUPLICATE KEY UPDATE final_grade = VALUES(final_grade)", (student_id, course_id, faculty_id,final_grade,))

        mysql.connection.commit()
        cur.close()

        # Retrieve the course name for display
        cur = mysql.connection.cursor()
        cur.execute("SELECT course_name FROM courses WHERE course_id = %s", (course_id,))
        result = cur.fetchone()
        cur.close()

        course_name = result[0] if result else "Unknown Course"

        # Retrieve the final grades for the given course_id from the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT student_id, final_grade FROM final_grades WHERE course_id = %s and faculty_id=%s", (course_id,faculty_id,))
        final_grades = cur.fetchall()
        cur.close()

        return render_template('final_grade.html', course_name=course_name, final_grades=final_grades,course_id=course_id)
    
# @app.route('/update_grade/<course_id>', methods=['GET', 'POST'])
# def update_grade(course_id):
#     if request.method == 'POST':
#         # Handle the form submission for updating grades
#         student_id = request.form['student_id']
#         grade = request.form['grade']

#         # Update the grade in the database for the given student_id and course_id
#         cur = mysql.connection.cursor()
#         cur.execute("UPDATE final_grades SET final_grade = %s WHERE student_id = %s AND course_id = %s",
#                     (grade, student_id, course_id))
#         mysql.connection.commit()
#         cur.close()

#         return redirect(url_for('final_grades', course_id=course_id))

#     else:
#         # Retrieve the course name for display
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT course_name FROM courses WHERE course_id = %s", (course_id,))
#         result = cur.fetchone()
#         cur.close()

#         course_name = result[0] if result else "Unknown Course"

#         # Retrieve the final grades for the given course_id from the database
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT student_id, final_grade FROM final_grades WHERE course_id = %s", (course_id,))
#         final_grades = cur.fetchall()
#         cur.close()

#         return render_template('final_grades.html', course_id=course_id, course_name=course_name, final_grades=final_grades)

@app.route('/view_distribution/<course_id>')
def view_distribution(course_id):
    # Retrieve the grades for the given course_id from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT final_grade FROM final_grades WHERE course_id = %s", (course_id,))
    grades = cur.fetchall()
    cur.close()

    # Perform data processing and generate histogram
    grade_values = [grade[0] for grade in grades]
    plt.hist(grade_values, bins=10)
    plt.xlabel('Grade')
    plt.ylabel('Count')
    plt.title('Grade Distribution')

    # Save the histogram plot as an image in memory
    histogram_buffer = io.BytesIO()
    plt.savefig(histogram_buffer, format='png')
    histogram_buffer.seek(0)
    histogram_data = histogram_buffer.getvalue()
    histogram_buffer.close()

    # Perform data processing and generate pie chart
    plt.figure()
    unique_grades = list(set(grade_values))
    grade_counts = [grade_values.count(grade) for grade in unique_grades]
    plt.pie(grade_counts, labels=unique_grades, autopct='%1.1f%%')
    plt.title('Grade Distribution')

    # Save the pie chart plot as an image
    pie_chart_file = 'fd_s2_4/static/pie_chart.png'
    plt.savefig(pie_chart_file)

    # Encode the pie chart image as base64
    with open(pie_chart_file, 'rb') as f:
        pie_chart_data = f.read()
    pie_chart_base64 = base64.b64encode(pie_chart_data).decode('utf-8')

    # Clear the current figure to release memory
    plt.clf()
    # Encode the histogram plot data as base64 and convert it to a string
    histogram_base64 = base64.b64encode(histogram_data).decode('utf-8')
    pie_chart_base64 = base64.b64encode(pie_chart_data).decode('utf-8')
    return render_template('view_distribution.html', course_id=course_id, histogram_base64=histogram_base64, pie_chart_base64=pie_chart_base64)

@app.route('/export_csv/<course_id>', methods=['GET'])
def export_csv(course_id): #downloading to csv works
    # Retrieve the final grades from the database
    faculty_id=session['faculty_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM final_grades where course_id = %s and faculty_id=%s",(course_id,faculty_id,))
    final_grades = cur.fetchall()
    cur.close()

    # Create a CSV string from the final grades data
    csv_data = "Student ID,Course ID,Faculty_ID,Final Grade\n"
    for grade in final_grades:
        csv_data += f"{grade[0]},{grade[1]},{grade[2]},{grade[3]}\n"

    # Create a response with the CSV data
    response = make_response(csv_data)
    response.headers['Content-Disposition'] = 'attachment; filename=final_grades.csv'
    response.headers['Content-type'] = 'text/csv'

    return response

if __name__ == '__main__':
    app.run(debug=True)


