#adding students via excel-working
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import random
import string
import pandas as pd
app = Flask(__name__)

# Configure the database connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'faculty'

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
def signup():
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
def login():
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
def forgot_password():
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
def verify_code():
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
def reset_password(faculty_id):
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
def home():
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
def add_course():
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
def delete_course(course_id):
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
def course_home(course_id):
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
def add_students(course_id):
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

@app.route('/view_attendance/<course_id>', methods=['GET', 'POST'])
def view_attendance(course_id):
    # Check if the user is logged in
    if 'faculty_id' not in session:
        return redirect(url_for('login'))

    # Query the database to get the course name
    cur = mysql.connection.cursor()
    cur.execute("SELECT course_name FROM courses WHERE course_id = %s", (course_id,))
    course_name = cur.fetchone()[0]
    cur.close()

    # Handle the form submission
    if request.method == 'POST':
        date_ = request.form['date']
        hour_ = request.form['hour']

        # Query the attendance table to get the student IDs for the selected date and hour
        cur = mysql.connection.cursor()
        cur.execute("SELECT status_,student_id FROM attendance WHERE course_id = %s AND faculty_id = %s AND date_ = %s AND hour_ = %s",
                    (course_id, session['faculty_id'], date_, hour_,))
        student_ids = cur.fetchall()
        cur.close()

        # Render the attendance view with the student IDs
        return render_template('view_attendance.html', course_name=course_name, course_id=course_id, student_ids=student_ids)

    return render_template('view_attendance.html', course_name=course_name, course_id=course_id)


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
        
        cur.execute("SELECT sc.student_id, s.name FROM student_course sc INNER JOIN students s ON sc.student_id = s.student_id WHERE sc.course_id = %s AND sc.faculty_id = %s",
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

@app.route('/view_grades/<course_id>')
def view_grades(course_id):
    # Retrieve the student grades from the database using the course_id
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT student_id, test_name, test_score, total_marks from grades WHERE course_id = %s AND faculty_id = %s ORDER BY test_name", (course_id, session['faculty_id'],))
    student_grades = cursor.fetchall()

    # Retrieve the course name from the database using the course_id
    cursor.execute("SELECT course_name FROM courses WHERE course_id = %s", (course_id,))
    result = cursor.fetchone()

    if result is None:
        course_name = "Unknown"
    else:
        course_name = result[0]

    # Retrieve the test names from the database for the given course_id
    cursor.execute("SELECT DISTINCT test_name FROM grades WHERE course_id = %s", (course_id,))
    test_names = [row[0] for row in cursor.fetchall()]

    return render_template('view_grades.html', course_name=course_name, student_grades=student_grades, test_names=test_names)

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

if __name__ == '__main__':
    app.run(debug=True)


