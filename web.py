from flask import Flask, render_template, request, redirect, session, flash
from flask import make_response
import re
import csv
import mysql.connector
import datetime
import sqlite3
import os
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY","fallbackkey")
#app.secret_key = "anushka"

app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db_url = os.environ.get("MYSQL_URL")
parsed_url = urlparse(db_url) #comment out later

#if db_url:
#    parsed_url = urlparse(db_url)
#
    #SQL wala part
#    db = mysql.connector.connect(
#        host = parsed_url.hostname,
#        user = parsed_url.username,
#        password = parsed_url.password,
#        database = parsed_url.path[1:],
#        port = parsed_url.port or 3306
#    )
#else:
#    raise Exception("MYSQL_URL environment variable not set")

if db_url:
    parsed_url = urlparse(db_url)

    #SQL wala part
    db = mysql.connector.connect(
        host = parsed_url.hostname,
        user = parsed_url.username,
        password = parsed_url.password,
        database = parsed_url.path[1:],
        port = int(parsed_url.port) if parsed_url.port else 3306
    )
else:
    db = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = 'jimin',
        database = 'coachingms',
        port = 3306
    )

cursor = db.cursor()

#MAIN HOME
@app.route('/')
def home():
    return render_template('home.html')

#Login
@app.route('/login', methods=['GET','POST'])
def login():
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    session.pop('teacher', None)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        #check data in db
        cursor.execute("SELECT * FROM users WHERE username = %s AND user_password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            session['user'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error = 'Invalid Credentials')
    return render_template('login.html')

#View all batches
@app.route('/batches')
def batches():
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session or 'teacher' in session:
        return redirect('/login')
    
    cursor.execute("""
                   SELECT b.id, b.`name`, b.`subject`, t.`name` AS teacher_name, b.days, b.timing, b.capacity,
                   (SELECT COUNT(*) FROM students s WHERE s.batch_id = b.id) AS student_count FROM batches b 
                   LEFT JOIN teachers t ON b.teacher_id = t.id
                   """)
    data = cursor.fetchall()

    #Also, fetch teachers for dropdown
    cursor.execute("SELECT id, `name` FROM teachers")
    teachers = cursor.fetchall()

    return render_template('batches.html', batches=data, teachers=teachers)

#Add a Batch
@app.route('/add_batch', methods=['POST'])
def add_batch():
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session or 'teacher' in session:
        return redirect('/login')
    
    name = request.form['name']
    subject = request.form['subject']
    teacher_id = request.form['teacher_id']
    days = request.form['days']
    timing = request.form['timing']
    capacity = request.form['capacity']

    #Validating time
    timing = request.form['timing'].strip()
    timing_pattern = r'^\s*\d{1,2}(:\d{2})?\s*(AM|PM|am|pm)\s*-\s*\d{1,2}(:\d{2})?\s*(AM|PM|am|pm)\s*$'
    if not re.match(timing_pattern, timing):
        flash("Invalid timing format! Use HH:MM AM - HH:MM PM")
        return redirect('/batches')

    cursor.execute("INSERT INTO batches(name, subject, teacher_id, days, timing, capacity) VALUES(%s, %s, %s, %s, %s, %s)", (name, subject, teacher_id or None, days, timing, capacity))
    db.commit()
    return redirect('/batches')

#Delete a batch
@app.route('/delete_batch/<int:batch_id>')
def delete_branch(batch_id):
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session or 'teacher' in session:
        return redirect('/login')
    
    cursor.execute("DELETE FROM batches WHERE id = %s", (batch_id,))
    db.commit()
    return redirect('/batches')

#UPDATE/EDIT BATCH
@app.route('/edit_batch/<int:batch_id>', methods=['GET','POST'])
def edit_batch(batch_id):#Add a batch

    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session or 'teacher' in session:
        return redirect('/login')
    
    if request.method=='POST':
        name = request.form['name']
        subject = request.form['subject']
        teacher_id = request.form['teacher_id']
        days = request.form['days']
        timing = request.form['timing']
        capacity = request.form['capacity']

        cursor.execute("""
                UPDATE batches SET name=%s, subject=%s, teacher_id=%s, days=%s, timing=%s, capacity=%s WHERE id=%s
                       """, (name, subject, teacher_id or None, days, timing, capacity, batch_id))
        db.commit()

        #Notification idhr!!
        if teacher_id:
            message = f"Your batch '{name}' has been updated. New Timing: {timing}, Days: {days}."
            cursor.execute("INSERT INTO notifications (teacher_id, message) VALUES (%s, %s)",(teacher_id,message))
            db.commit()
        return redirect('/batches')
    
    #fetch current batch details
    cursor.execute("SELECT * FROM batches WHERE id=%s", (batch_id,))
    batch = cursor.fetchone()

    #fetch all teachers for dropdown
    cursor.execute("SELECT id, name FROM teachers")
    teachers = cursor.fetchall()

    return render_template('edit_batch.html',batch=batch, teachers=teachers)


#Students 
@app.route('/students')
def students():
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session or 'teacher' in session:
        return redirect('/login')

    cursor.execute("SELECT s.id, s.name, s.email, s.phone, s.date_of_joining, s.fee_status, b.name AS batch_name FROM students s LEFT JOIN batches b ON s.batch_id = b.id")
    data = cursor.fetchall()
    return render_template('students.html', students=data)

@app.route('/student/<int:student_id>')
def student_profile(student_id):
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session or 'teacher' in session:
        return redirect('/login')
    cursor.execute("""
        SELECT s.id, s.name, s.email, s.phone, s.date_of_joining, s.fee_status, b.name AS batch_name FROM students s LEFT JOIN batches b ON s.batch_id = b.id WHERE s.id = %s
                   """, (student_id,))
    student = cursor.fetchone()

    if not student:
        return "Student not found", 404
    
    return render_template('student_profile.html', student=student)

@app.route('/add_student', methods=['POST'])
def add_student():
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session or 'teacher' in session:
        return redirect('/login')
    
    name = request.form['name'].strip()
    email = request.form['email'].strip()
    phone = request.form['phone'].strip()
    doj = request.form['date_of_joining']
    batch_id = request.form['batch_id']
    fee_status = request.form['fee_status']

    #Validating name
    if not re.match(r"^[A-Za-z ]+$", name):
        flash("Invalid name: Only letters and spaces are allowed!")
        return redirect('/students')
    
    #Validating phone
    if not re.match(r"^\d{10}$", phone):
        flash("Invalid phone number: Please enter a 10-digit phone number.")
        return redirect('/students')

    print("Form Received: ", name, email, phone, doj, batch_id, fee_status)

    cursor.execute("INSERT INTO students(name, email, phone, date_of_joining, batch_id, fee_status) VALUES(%s, %s, %s, %s, %s, %s)", (name, email, phone, doj, batch_id or None, fee_status))
    db.commit()
    return redirect('/students')

@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session or 'teacher' in session:
        return redirect('/login')
    cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
    db.commit()
    return redirect('/students')

#TOGGLE FEE
@app.route('/toggle_fee/<int:student_id>')
def toggle_fee(student_id):
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session or 'teacher' in session:
        return redirect('/login')
    #GET current status
    cursor.execute("SELECT fee_status FROM students WHERE id=%s",(student_id,))
    current_status = cursor.fetchone()[0]

    #Toggling the value
    new_status = 'Paid' if current_status == 'Unpaid' else 'Unpaid'

    #update the db
    cursor.execute("UPDATE students SET fee_status = %s WHERE id=%s",(new_status, student_id))
    db.commit()
    return redirect('/students')

#UPDATE/EDIT STUDENT
@app.route('/edit_student/<int:student_id>', methods=['GET','POST'])
def edit_student(student_id):
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session or 'teacher' in session:
        return redirect('/login')

    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        date_of_joining = request.form['date_of_joining']
        fee_status = request.form['fee_status']

        cursor.execute("""
            UPDATE students SET name = %s, email = %s, phone = %s, date_of_joining = %s, fee_status = %s WHERE id = %s
                       """, (name, email, phone, date_of_joining, fee_status, student_id))
        db.commit()
        return redirect('/students')
    
    cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    student = cursor.fetchone()

    return render_template('edit_student.html', student=student)

#EXPORT TO CSV
@app.route('/export_students')
def export_students():
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session or 'teacher' in session:
        return redirect('/login')
    cursor.execute("""
        SELECT s.name, s.email, s.phone, s.date_of_joining, s.fee_status, b.name AS batch_name FROM students s LEFT JOIN batches b ON s.batch_id = b.id
                   """)
    data = cursor.fetchall()

    output = []
    output.append(['Name','Email','Phone','Date of Joining','Fee Status','Batch'])

    for row in data:
        output.append(list(row))

    #Convert to csv string
    from io import StringIO
    si = StringIO()
    writer = csv.writer(si)
    writer.writerows(output)
    csv_output = si.getvalue()

    #Create CSV response
    response = make_response(csv_output)

    response.headers["Content-Disposition"] = "attachment;filename=students.csv"
    response.headers["Content-type"]="text/csv"
    return response



#For Teachers! 
#To show all teachers
@app.route('/teachers')
def teachers():
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session:
        return redirect('/login')
    
    cursor.execute("SELECT * FROM teachers")
    data = cursor.fetchall()
    return render_template('teachers.html', teachers = data)

#Adding a new teacher
@app.route('/add_teacher', methods=['POST'])
def add_teacher():
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session:
        return redirect('/login')
    
    name = request.form['name']
    subject = request.form['subject']
    email = request.form['email']
    availability = request.form['availability']

    cursor.execute("INSERT INTO teachers(name, subject, email, availability) VALUES(%s, %s, %s, %s)",(name, subject, email, availability))
    db.commit()
    return redirect('/teachers')

#Delete a Teacher aur fir wapas redirect krna teacher's page pr
@app.route('/delete_teacher/<int:teacher_id>')
def delete_teacher(teacher_id):
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session:
        return redirect('/login')

    cursor.execute("DELETE FROM teachers WHERE id = %s", (teacher_id,))
    db.commit()
    return redirect('/teachers')

#UPDATE/EDIT TEACHER
@app.route('/edit_teacher/<int:teacher_id>', methods=['GET','POST'])
def edit_teacher(teacher_id):
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        name = request.form['name']
        subject = request.form['subject']
        email = request.form['email']
        availability = request.form['availability']

        cursor.execute("""
                       UPDATE teachers SET name = %s, subject = %s, email = %s, availability = %s WHERE id = %s
                       """, (name, subject, email, availability, teacher_id))
        db.commit()
        return redirect('/teachers')
    
    cursor.execute("SELECT * FROM teachers WHERE id = %s", (teacher_id,))
    teacher = cursor.fetchone()
    return render_template('edit_teacher.html', teacher=teacher)

#Assignment
@app.route('/assign', methods=['GET', 'POST'])
def assign():
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session or 'teacher' in session:
        return redirect('/')
    
    #fetch all students (abhi tak assigned nhi hue h kisi bhi batch me)
    cursor.execute("SELECT id, name FROM students WHERE batch_id IS NULL")
    students = cursor.fetchall()

    #fetch all teachers
    cursor.execute("SELECT id, name FROM teachers")
    teachers = cursor.fetchall()

    #fetch all batches with current count
    cursor.execute("""
                    SELECT b.id, b.name, b.capacity,
                   (SELECT COUNT(*) FROM students s WHERE s.batch_id = b.id)
                   AS current_count FROM batches b
                   """)
    batches = cursor.fetchall()

    message = ""

    #HANDLE POST
    if request.method == "POST":
        student_id = request.form.get('student_id')
        teacher_id = request.form.get('teacher_id')
        batch_id = request.form.get('batch_id')

        cursor.execute("SELECT capacity FROM batches WHERE id = %s", (batch_id,))
        capacity = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM students WHERE batch_id = %s", (batch_id,))
        current = cursor.fetchone()[0]
 
        if int(current) < int(capacity):
            #Assign student
            cursor.execute("UPDATE students SET batch_id = %s WHERE id = %s", (batch_id, student_id))
            db.commit()
            message = "Student assigned successfully!"
        else:
            message = "Batch is already full!"

        #Assign teacher (hamesha override hoga)
        cursor.execute("UPDATE batches SET teacher_id = %s WHERE id = %s", (teacher_id, batch_id))
        db.commit()

    return render_template('assign.html', students=students, teachers=teachers, batches=batches, message=message)


#DASHBOARD
@app.route('/dashboard')
def dashboard():
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session or 'teacher' in session:
        return redirect('/login')
    
    #Count total students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    #Count total students
    cursor.execute("SELECT COUNT(*) FROM teachers")
    total_teachers = cursor.fetchone()[0]

    #Count total batches
    cursor.execute("SELECT COUNT(*) FROM batches")
    total_batches = cursor.fetchone()[0]

    #Count unpaid students
    cursor.execute("SELECT COUNT(*) FROM students WHERE fee_status = 'Unpaid'")
    total_unpaid = cursor.fetchone()[0]

    return render_template('dashboard.html', user=session['user'],
                           total_students = total_students,
                           total_teachers = total_teachers,
                           total_batches = total_batches,
                           total_unpaid = total_unpaid
                           )


#Teacher Login
@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
  
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email and password:
            cursor.execute("SELECT id FROM teachers WHERE email = %s AND password = %s", (email, password))
            teacher = cursor.fetchone()

            if teacher:
                session["teacher"] = teacher[0]  # teacher[0] = teacher ID
                print("Session Set:", session["teacher"])
                return redirect('/teacher_dashboard')  # or anywhere you want
            else:
                return render_template('teacher_login.html', error="Invalid credentials")
    
    return render_template('teacher_login.html', error="Missing form data")
    

@app.route('/whoami')
def whoami():
    print("Current session:", dict(session))
    return f"Session contents: {dict(session)}"

#Teacher's Dashboard
@app.route('/teacher_dashboard')
def teacher_dashboard():
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if "teacher" not in session:
        return redirect('/teacher_login')
    
    teacher_id = session['teacher']
    cursor.execute("""
        SELECT b.name, b.subject, b.days, b.timing 
        FROM batches b 
        WHERE b.teacher_id = %s
    """, (teacher_id,))
    timetable = cursor.fetchall()

    return render_template('teacher_dashboard.html', timetable=timetable)

#Teacher Registration
@app.route('/teacher_register', methods=['GET', 'POST'])
def teacher_register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("UPDATE teachers SET password = %s WHERE email = %s", (password, email))
        db.commit()
        return redirect('/teacher_login')
    return render_template('teacher_register.html')

#Notifications
@app.route('/notifications')
def notifications():
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    print(f"Session Contents: {session}")
    if "teacher" not in session:
        return redirect('/teacher_login')
    
    teacher_id = session['teacher']

    #only for this
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT id, title, message, seen, created_at FROM notifications WHERE teacher_id = %s ORDER BY created_at DESC", (teacher_id,))
    notifications = cursor.fetchall()
    return render_template('notifications.html', notifications=notifications)

#SEEN
@app.route('/mark_as_seen', methods=["POST"])
def mark_as_read():
    if "teacher" not in session:
        return redirect('/teacher_login')
    
    notif_id = request.form.get('notification_id')
    teacher_id = session['teacher']

    cursor.execute("""
    UPDATE notifications SET seen = TRUE WHERE id = %s AND teacher_id = %s 
""", (notif_id, teacher_id))
    db.commit()
    return redirect('/notifications')

#Admin notify
@app.route('/admin/notify', methods=['GET', 'POST'])
def admin_notify():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')  # or 'all'
        message = request.form.get('message')
        title = request.form.get('title')

        if teacher_id == 'all':
            cursor.execute("SELECT id FROM teachers")
            teachers = cursor.fetchall()
            for t in teachers:
                cursor.execute("INSERT INTO notifications (teacher_id, title, message) VALUES (%s, %s, %s)", (t[0], title, message))
        else:
            cursor.execute("INSERT INTO notifications (teacher_id, title, message) VALUES (%s, %s, %s)", (teacher_id, title, message))

        db.commit()
        return render_template('admin_notify.html', success="Notification sent!")

    cursor.execute("SELECT id, name FROM teachers")
    teachers = cursor.fetchall()
    return render_template('admin_notify.html', teachers=teachers)

#timetable k liye
@app.route('/timetable')
def timetable():
    try:
        cursor.fetchall()
    except:
        pass
    cursor.execute('''
        SELECT batches.name, batches.subject, teachers.name, batches.days, batches.timing FROM batches LEFT JOIN teachers ON batches.teacher_id = teachers.id
                ''')
    schedule = cursor.fetchall()
    return render_template("timetable.html", schedule=schedule)

#logout dono k liye
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('teacher', None)
    flash("Logged out successfully!")
    return redirect('/')

#ADMIN MESSAGES
@app.route('/admin_messages/<int:teacher_id>', methods=['GET', 'POST'])
def admin_messages(teacher_id):
    if not session.get('user'):
        return redirect('/login')

    conn = mysql.connector.connect(
        host = url.hostname,
        user=url.username,
        password=url.password,
        database=url.path[1:],
        port = url.port
    )
    cursor = conn.cursor(dictionary=True)

    # If method is POST, insert message
    if request.method == 'POST':
        message = request.form.get('message','').strip()
        if message:
            cursor.execute("INSERT INTO messages (sender_id, receiver_id, message, is_teacher_sender) VALUES (%s, %s, %s, %s)",
                           (1, teacher_id, message, False))
            conn.commit()

    
    cursor.execute("""
        SELECT * FROM messages 
        WHERE (sender_id = 1 AND receiver_id = %s AND is_teacher_sender = False) 
           OR (sender_id = %s AND receiver_id = 1 AND is_teacher_sender = True)
        ORDER BY timestamp
    """, (teacher_id, teacher_id))
    messages = cursor.fetchall()

    # Also fetch teacher's name
    cursor.execute("SELECT id, name FROM teachers WHERE id = %s", (teacher_id,))
    teacher = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("admin_messages.html", messages=messages, teacher=teacher)
    #return render_template("admin_messages.html", messages=messages, teacher=teacher, teacher_id=teacher_id)
 

#ADMIN SELECT TEACHER
@app.route('/admin_select_teacher')
def admin_select_teacher():
    if not session.get('user'):
        return redirect('/login')
    
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM teachers")
    teachers = cursor.fetchall()
    
    return render_template('admin_select_teacher.html', teachers=teachers)

#TEACHER MESSAGES
@app.route('/teacher_messages/<int:admin_id>', methods=['GET', 'POST'])
def teacher_messages(admin_id):
    if not session.get('teacher'):
        return redirect('/teacher_login')

    teacher_id = session['teacher']
    cursor = db.cursor(dictionary=True)

    # Always fetch admin info
    cursor.execute("SELECT id, username FROM users WHERE id = %s", (admin_id,))
    admin = cursor.fetchone()

    if request.method == 'POST':
        message = request.form['message'].strip()
        if message:
            cursor.execute("""
                INSERT INTO messages (sender_id, receiver_id, message, is_teacher_sender)
                VALUES (%s, %s, %s, %s)
            """, (teacher_id, admin_id, message, True))
            db.commit()

    # Always fetch messages
    cursor.execute("""
        SELECT * FROM messages
        WHERE (sender_id = %s AND receiver_id = %s)
           OR (sender_id = %s AND receiver_id = %s)
        ORDER BY timestamp
    """, (teacher_id, admin_id, admin_id, teacher_id))
    messages = cursor.fetchall()

    return render_template('teacher_messages.html', messages=messages, admin=admin, teacher_id=teacher_id)


if __name__ == "__main__":
    app.run(debug=True)
