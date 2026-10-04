import streamlit as st
import sqlite3
import pandas as pd
import time

st.set_page_config(page_title="Hospital Management System", layout="wide")

DB_FILE = "hospital.db"


def init_db():
    """Tabloları oluşturur."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Departments (
                dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dept_name TEXT NOT NULL,
                location TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Doctors (
                doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_name TEXT NOT NULL,
                title TEXT,
                dept_id INTEGER,
                FOREIGN KEY (dept_id) REFERENCES Departments(dept_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Patients (
                patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                phone TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Appointments (
                app_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                doc_id INTEGER,
                app_date DATE,
                app_time TIME,
                status TEXT DEFAULT 'Scheduled',
                FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
                FOREIGN KEY (doc_id) REFERENCES Doctors(doc_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Prescriptions (
                presc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id INTEGER,
                medication TEXT,
                dosage TEXT,
                notes TEXT,
                FOREIGN KEY (app_id) REFERENCES Appointments(app_id) ON DELETE CASCADE
            )
        """)
        conn.commit()

def add_sample_data():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT count(*) FROM Departments")
        if cursor.fetchone()[0] == 0:
            depts = [('Cardiology', 'Block A'), ('Neurology', 'Block B'), 
                     ('General Surgery', 'Block C'), ('Urology', 'Block A'), 
                     ('Dermatology', 'Block D')]
            cursor.executemany("INSERT INTO Departments (dept_name, location) VALUES (?, ?)", depts)
            
            docs = [('Dr. House', 'MD', 1), ('Dr. Strange', 'Surgeon', 2), 
                    ('Dr. Grey', 'Specialist', 5), ('Dr. Shepherd', 'Specialist', 4), 
                    ('Dr. Quinn', 'MD', 5)]
            cursor.executemany("INSERT INTO Doctors (doc_name, title, dept_id) VALUES (?, ?, ?)", docs)

            patients = [('Ali Yilmaz', 27, 'Male', '555 444 3333'), 
                        ('Ayse Demir', 24, 'Female', '555 777 6666'),
                        ('Mehmet Kaya', 43, 'Male', '555 222 1111'), 
                        ('Fatma Celik', 57, 'Female', '555 999 8888'),
                        ('Ahmet Can', 19, 'Male', '555 000 5555')]
            cursor.executemany("INSERT INTO Patients (patient_name, age, gender, phone) VALUES (?, ?, ?, ?)", patients)

            apps = [(1, 1, '2025-12-12', '09:00', 'Scheduled'), 
                    (2, 4, '2025-12-12', '10:00', 'Scheduled'),
                    (3, 3, '2025-12-15', '11:00', 'Completed'), 
                    (4, 5, '2025-12-16', '14:00', 'Cancelled'),
                    (5, 2, '2025-12-17', '09:30', 'Scheduled')]
            cursor.executemany("INSERT INTO Appointments (patient_id, doc_id, app_date, app_time, status) VALUES (?, ?, ?, ?, ?)", apps)

            prescs = [(1, 'Aspirin', '100mg', 'Take daily'), 
                      (2, 'Antibiotic', '500mg', 'Twice a day'),
                      (3, 'Gel', '200mg', 'Before sleep'), 
                      (4, 'Cream', '5%', 'Apply externally'),
                      (5, 'Painkiller', '25mg', 'If needed')]
            cursor.executemany("INSERT INTO Prescriptions (app_id, medication, dosage, notes) VALUES (?, ?, ?, ?)", prescs)
            conn.commit()


def run_query(query, params=()):
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql(query, conn, params=params)

def execute_command(command, params=()):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute(command, params)
        conn.commit()


st.title(" Hospital Appointment & Patient Tracking System")

init_db()
add_sample_data()

menu = ["Control Board", "Add Appointment", "Patients", "Cancel Appointment"]
choice = st.sidebar.selectbox("MENU", menu)

if choice == "Control Board":
    st.subheader("Hospital Dashboard")
    
    tab1, tab2, tab3, tab4 = st.tabs([" Appointments", " Prescriptions", " Doctors", " Patients"])

    with tab1:
        st.info("List of all appointments (Joined with Patient & Doctor names)")
        sql_join = """
            SELECT 
                A.app_id, 
                P.patient_name AS Patient, 
                D.doc_name AS Doctor, 
                Dep.dept_name AS Department,
                A.app_date, 
                A.app_time, 
                A.status
            FROM Appointments A
            JOIN Patients P ON A.patient_id = P.patient_id
            JOIN Doctors D ON A.doc_id = D.doc_id
            JOIN Departments Dep ON D.dept_id = Dep.dept_id
            ORDER BY A.app_date DESC
        """
        df = run_query(sql_join)
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.success("Prescription Records (Joined with Appointments to see Patient names)")
        presc_sql = """
            SELECT 
                PR.presc_id,
                P.patient_name AS Patient,
                D.doc_name AS Doctor,
                PR.medication AS Medicine,
                PR.dosage,
                PR.notes
            FROM Prescriptions PR
            JOIN Appointments A ON PR.app_id = A.app_id
            JOIN Patients P ON A.patient_id = P.patient_id
            JOIN Doctors D ON A.doc_id = D.doc_id
        """
        df_presc = run_query(presc_sql)
        if df_presc.empty:
            st.warning("No prescription records found.")
        else:
            st.dataframe(df_presc, use_container_width=True)

    with tab3:
        st.write("Medical Staff")
        doc_sql = """
            SELECT D.doc_id, D.doc_name, D.title, Dep.dept_name, Dep.location 
            FROM Doctors D 
            JOIN Departments Dep ON D.dept_id = Dep.dept_id
        """
        st.dataframe(run_query(doc_sql), use_container_width=True)

    with tab4:
        st.write("Registered Patients")
        st.dataframe(run_query("SELECT * FROM Patients"), use_container_width=True)

elif choice == "Add Appointment":
    st.subheader("Make a New Appointment")
    
    patients = run_query("SELECT patient_id, patient_name FROM Patients")
    doctors = run_query("SELECT doc_id, doc_name FROM Doctors")
    
    if patients.empty or doctors.empty:
        st.error("No patients or doctors found in the database.")
    else:
        patient_dict = dict(zip(patients['patient_name'], patients['patient_id']))
        doctor_dict = dict(zip(doctors['doc_name'], doctors['doc_id']))

        with st.form("add_app_form"):
            col1, col2 = st.columns(2)
            selected_patient = col1.selectbox("Select Patient", list(patient_dict.keys()))
            selected_doctor = col2.selectbox("Select Doctor", list(doctor_dict.keys()))
            
            date = st.date_input("Date")
            time_slot = st.time_input("Time")
            
            submitted = st.form_submit_button("Make Appointment")
            
            if submitted:
                p_id = patient_dict[selected_patient]
                d_id = doctor_dict[selected_doctor]
                execute_command(
                    "INSERT INTO Appointments (patient_id, doc_id, app_date, app_time) VALUES (?, ?, ?, ?)",
                    (p_id, d_id, date, str(time_slot))
                )
                st.success(f"Appointment made for {selected_patient} with {selected_doctor}!")
                time.sleep(1)
                st.rerun()

elif choice == "Patients":
    st.subheader("Update Patient Information")
    
    patients_df = run_query("SELECT * FROM Patients")
    st.dataframe(patients_df)
    
    st.write("---")
    
    if not patients_df.empty:
        patient_to_update = st.selectbox("Select Patient to Update", patients_df['patient_name'])
        
        current_info = patients_df[patients_df['patient_name'] == patient_to_update].iloc[0]
        p_id = int(current_info['patient_id'])
        
        with st.form("update_form"):
            new_phone = st.text_input("Update Phone Number", value=current_info['phone'])
            new_age = st.number_input("Update Age", value=int(current_info['age']))
            
            update_btn = st.form_submit_button("Update Patient")
            
            if update_btn:
                execute_command(
                    "UPDATE Patients SET phone = ?, age = ? WHERE patient_id = ?",
                    (new_phone, new_age, p_id)
                )
                st.success("Patient information updated successfully!")
                time.sleep(1)
                st.rerun()

elif choice == "Cancel Appointment":
    st.subheader("Cancel Appointment")
    
    active_apps = run_query("""
        SELECT A.app_id, P.patient_name, A.app_date, A.app_time 
        FROM Appointments A
        JOIN Patients P ON A.patient_id = P.patient_id
        WHERE A.status = 'Scheduled'
    """)
    
    if not active_apps.empty:
        active_apps['display'] = active_apps.apply(lambda x: f"ID: {x['app_id']} - {x['patient_name']} ({x['app_date']} @ {x['app_time']})", axis=1)
        
        app_to_delete = st.selectbox("Select Appointment to Cancel", active_apps['display'])
        app_id_del = int(app_to_delete.split(" - ")[0].replace("ID: ", ""))
        
        if st.button("Delete Appointment"):
            execute_command("DELETE FROM Appointments WHERE app_id = ?", (app_id_del,))
            st.warning("Appointment cancelled and removed from database.")
            time.sleep(1)
            st.rerun()
    else:
        st.info("No active scheduled appointments to cancel.")