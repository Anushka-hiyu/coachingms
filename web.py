from flask import Flask, render_template, request, redirect, session, flash
from flask import make_response
import csv
import mysql.connector
import datetime
import os
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'anushka'

db_url = os.environ.get("MYSQL_URL")

if db_url:
    parsed_url = urlparse(db_url)

    #SQL wala part
    db = mysql.connector.connect(
        host = parsed_url.hostname,
        user = parsed_url.username,
        password = parsed_url.password,
        database = parsed_url.path[1:],
        port = parsed_url.port or 3306
    )
else:
    raise Exception("MYSQL_URL environment variable not set")

cursor = db.cursor()

#MAIN
@app.route('/', methods=['GET','POST'])
def login():
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        #check data in db
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
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

#Add a batch
@app.route('/add_batch', methods=['POST'])
def add_batch():
    name = request.form['name']
    subject = request.form['subject']
    teacher_id = request.form['teacher_id']
    days = request.form['days']
    timing = request.form['timing']
    capacity = request.form['capacity']

    cursor.execute("INSERT INTO batches(name, subject, teacher_id, days, timing, capacity) VALUES(%s, %s, %s, %s, %s, %s)", (name, subject, teacher_id or None, days, timing, capacity))
    db.commit()
    return redirect('/batches')

#Delete a batch
@app.route('/delete_batch/<int:batch_id>')
def delete_branch(batch_id):
    cursor.execute("DELETE FROM batches WHERE id = %s", (batch_id,))
    db.commit()
    return redirect('/batches')

#UPDATE/EDIT BATCH
@app.route('/edit_batch/<int:batch_id>', methods=['GET','POST'])
def edit_batch(batch_id):
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

    cursor.execute("SELECT s.id, s.name, s.email, s.phone, s.date_of_joining, s.fee_status, b.name AS batch_name FROM students s LEFT JOIN batches b ON s.batch_id = b.id")
    data = cursor.fetchall()
    return render_template('students.html', students=data)

@app.route('/student/<int:student_id>')
def student_profile(student_id):
    cursor.execute("""
        SELECT s.id, s.name, s.email, s.phone, s.date_of_joining, s.fee_status, b.name AS batch_name FROM students s LEFT JOIN batches b ON s.batch_id = b.id WHERE s.id = %s
                   """, (student_id,))
    student = cursor.fetchone()

    if not student:
        return "Student not found", 404
    
    return render_template('student_profile.html', student=student)

@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    doj = request.form['date_of_joining']
    batch_id = request.form['batch_id']
    fee_status = request.form['fee_status']

    print("Form Received: ", name, email, phone, doj, batch_id, fee_status)

    cursor.execute("INSERT INTO students(name, email, phone, date_of_joining, batch_id, fee_status) VALUES(%s, %s, %s, %s, %s, %s)", (name, email, phone, doj, batch_id or None, fee_status))
    db.commit()
    return redirect('/students')

@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
    db.commit()
    return redirect('/students')

#TOGGLE FEE
@app.route('/toggle_fee/<int:student_id>')
def toggle_fee(student_id):
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
    cursor.execute("SELECT * FROM teachers")
    data = cursor.fetchall()
    return render_template('teachers.html', teachers = data)

#Adding a new teacher
@app.route('/add_teacher', methods=['POST'])
def add_teacher():
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
    cursor.execute("DELETE FROM teachers WHERE id = %s", (teacher_id,))
    db.commit()
    return redirect('/teachers')

#UPDATE/EDIT TEACHER
@app.route('/edit_teacher/<int:teacher_id>', methods=['GET','POST'])
def edit_teacher(teacher_id):
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



@app.route('/dashboard')
def dashboard():
    try:
        cursor.fetchall() #clear unread results agr h koi toh
    except:
        pass #nhi h toh ignore
    if 'user' not in session:
        return redirect('/')
    
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

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!")
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
