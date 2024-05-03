from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_doctor", methods=["POST"])
def add_doctor():
    doctor_name = request.form.get("doctor_name")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    if not (doctor_name and start_time and end_time):
        return "Missing form data", 400
    doctor = (doctor_name, start_time, end_time)
    conn = create_connection()
    if not conn:
        return "Error! Cannot create the database connection.", 500
    doctor_id = insert_doctor(conn, doctor)
    conn.close()
    return "Doctor added successfully!"

@app.route("/add_appointment", methods=["POST"])
def add_appointment():
    appointment_date = request.form.get("appointment_date")
    appointment_time = request.form.get("appointment_time")
    patient_name = request.form.get("patient_name")
    doctor_id = request.form.get("doctor_id")
    reason = request.form.get("reason")
    if not (appointment_date and appointment_time and patient_name and doctor_id and reason):
        return "Missing form data", 400
    appointment = (appointment_date, appointment_time, patient_name, reason)
    conn = create_connection()
    if not conn:
        return "Error! Cannot create the database connection.", 500
    doctor_id = int(doctor_id)
    if not insert_appointment(conn, appointment, doctor_id):
        return "Doctor is not available!!", 400
    conn.close()
    return "Appointment added successfully!"

@app.route("/display_doctors")
def display_doctors():
    conn = create_connection()
    if not conn:
        return "Error! Cannot create the database connection.", 500
    rows = select_all_doctors(conn)
    conn.close()
    return render_template("display_doctors.html", rows=rows)

@app.route("/display_appointments")
def display_appointments():
    conn = create_connection()
    if not conn:
        return "Error! Cannot create the database connection.", 500
    rows = select_all_appointments(conn)
    conn.close()
    return render_template("display_appointments.html", rows=rows)

@app.route("/modify_appointments", methods=["GET", "POST"])
def modify_appointment():
    if request.method == "GET":
        appointment_id = request.args.get("appointment_id")
        conn = create_connection()
        if not conn:
            return "Error! Cannot create the database connection.", 500
        cur = conn.cursor()
        cur.execute("SELECT * FROM appointment WHERE id =?", (appointment_id,))
        row = cur.fetchone()
        conn.commit()
        conn.close()
        return render_template("modify_appointment.html", row=row)
    elif request.method == "POST":
        appointment_id = request.form.get("appointment_id")
        appointment_date = request.form.get("appointment_date")
        appointment_time = request.form.get("appointment_time")
        patient_name = request.form.get("patient_name")
        reason = request.form.get("reason")
        if not (appointment_id and appointment_date and appointment_time and patient_name and reason):
            return "Missing form data", 400
        conn = create_connection()
        if not conn:
            return "Error! Cannot create the database connection.", 500
        cur = conn.cursor()
        cur.execute("UPDATE appointment SET appointment_date=?, appointment_time=?, patient_name=?, reason=? WHERE id=?",
                    (appointment_date, appointment_time, patient_name, reason, appointment_id))
        conn.commit()
        conn.close()
        return "Appointment modified successfully!"

@app.route("/delete_doctor", methods=["POST"])
def delete_doctor():
    doctor_id = request.form.get("doctor_id")
    if not doctor_id:
        return "Missing doctor ID", 400
    conn = create_connection()
    if not conn:
        return "Error! Cannot create the database connection.", 500
    cur = conn.cursor()
    cur.execute("DELETE FROM doctor WHERE id =?", (doctor_id,))
    conn.commit()
    cur.execute("DELETE FROM appointment WHERE doctor_id =?", (doctor_id,))
    conn.commit()
    conn.close()
    return "Doctor deleted successfully!"

@app.route("/delete_appointment", methods=["POST"])
def delete_appointment():
    appointment_id = request.form.get("appointment_id")
    if not appointment_id:
        return "Missing appointment ID", 400
    conn = create_connection()
    if not conn:
        return "Error! Cannot create the database connection.", 500
    cur = conn.cursor()
    cur.execute("DELETE FROM appointment WHERE id =?", (appointment_id,))
    conn.commit()
    conn.close()
    return "Appointment deleted successfully!"

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('appointments.db')
        conn.row_factory = sqlite3.Row
    except sqlite3.Error as e:
        print(e)
    return conn

def select_all_doctors(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM doctor")
    rows = cur.fetchall()
    return rows

def select_all_appointments(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM appointment")
    rows = cur.fetchall()
    return rows

def insert_doctor(conn, doctor):
    cur = conn.cursor()
    cur.execute("INSERT INTO doctor (name, start_time, end_time) VALUES (?,?,?)", doctor)
    conn.commit()
    return cur.lastrowid

def insert_appointment(conn, appointment, doctor_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM doctor WHERE id =?", (doctor_id,))
    doctor = cur.fetchone()
    if not doctor:
        return False
    cur.execute("INSERT INTO appointment (appointment_date, appointment_time, patient_name, reason, doctor_id) VALUES (?,?,?,?,?)", appointment + (doctor_id,))
    conn.commit()
    return True

def modify_appointment_data(conn, appointment):
    cur = conn.cursor()
    cur.execute("""
        UPDATE appointment
        SET appointment_date =?, appointment_time =?, patient_name =?, reason =?
        WHERE id =?
    """, appointment)
    conn.commit()
    return True

def create_doctor_table(conn):
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS doctor (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            start_time TIME,
            end_time TIME
        )
    ''')
    conn.commit()

def create_appointment_table(conn):
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS appointment (
            id INTEGER PRIMARY KEY,
            appointment_date DATE NOT NULL,
            appointment_time TIME NOT NULL,
            patient_name TEXT NOT NULL,
            reason TEXT NOT NULL,
            doctor_id INTEGER NOT NULL,
            FOREIGN KEY (doctor_id) REFERENCES doctor (id)
        )
    ''')
    conn.commit()

conn = create_connection()
if conn:
    create_doctor_table(conn)
    create_appointment_table(conn)
    conn.close()

app.run(port=5023)
