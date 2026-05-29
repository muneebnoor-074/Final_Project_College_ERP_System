# -*- coding: utf-8 -*-
"""
Created on Sat May 23 22:29:40 2026

@author: Muneeb Noor
"""

import sqlite3
import hashlib
import os
import re
import secrets
import sys
from datetime import date

# DATABASE SETUP

DB_NAME = "college_erp.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
    return salt.hex() + ":" + key.hex()

def verify_password(password, stored):
    try:
        salt_hex, key_hex = stored.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
        return key.hex() == key_hex
    except (ValueError, AttributeError):
        return False

def is_strong_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit."
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        return False, "Password must contain at least one special character."
    return True, ""

def validate_date(date_str):
    try:
        parts = date_str.split('-')
        if len(parts) != 3:
            return False
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        date(year, month, day)
        return True
    except (ValueError, IndexError):
        return False

def setup_database():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'teacher', 'student')),
        name TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        roll_number TEXT UNIQUE NOT NULL,
        semester INTEGER NOT NULL,
        department_id INTEGER NOT NULL,
        contact TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (department_id) REFERENCES departments(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        employee_id TEXT UNIQUE NOT NULL,
        department_id INTEGER NOT NULL,
        contact TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (department_id) REFERENCES departments(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        credit_hours INTEGER NOT NULL,
        department_id INTEGER NOT NULL,
        teacher_id INTEGER,
        FOREIGN KEY (department_id) REFERENCES departments(id),
        FOREIGN KEY (teacher_id) REFERENCES teachers(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        UNIQUE(student_id, course_id),
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (course_id) REFERENCES courses(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('P', 'A')),
        UNIQUE(student_id, course_id, date),
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (course_id) REFERENCES courses(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        marks_obtained REAL NOT NULL,
        total_marks REAL NOT NULL,
        UNIQUE(student_id, course_id),
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (course_id) REFERENCES courses(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        paid REAL NOT NULL DEFAULT 0,
        semester INTEGER NOT NULL,
        due_date TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id)
    )''')

    conn.commit()

    c.execute("SELECT id FROM users WHERE username = 'admin'")
    if not c.fetchone():
        default_pw = secrets.token_urlsafe(16)
        c.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, 'admin', 'System Admin')",
                  ('admin', hash_password(default_pw)))
        conn.commit()
        print(f"[INFO] Default admin created — username: admin")
        print(f"[INFO] Generated admin password: {default_pw}")
        print("[INFO] Change this password immediately after first login.")

    c.execute("SELECT id FROM departments WHERE name = 'Computer Science'")
    if not c.fetchone():
        for dept in ['Computer Science', 'Electrical Engineering', 'Mechanical Engineering']:
            c.execute("INSERT INTO departments (name) VALUES (?)", (dept,))
        conn.commit()

    conn.close()


# UTILITIES

def print_header(title):
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)

def print_table(headers, rows):
    if not rows:
        print("  [No records found]")
        return
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))
    fmt = "  " + "  ".join(f"{{:<{w}}}" for w in col_widths)
    print(fmt.format(*headers))
    print("  " + "-" * (sum(col_widths) + 2 * len(headers)))
    for row in rows:
        print(fmt.format(*[str(v) for v in row]))

def get_int_input(prompt, min_val=None, max_val=None):
    while True:
        try:
            val = int(input(prompt))
            if min_val is not None and val < min_val:
                print(f"  Enter a value >= {min_val}")
                continue
            if max_val is not None and val > max_val:
                print(f"  Enter a value <= {max_val}")
                continue
            return val
        except ValueError:
            print("  Invalid input. Enter a number.")

def get_float_input(prompt, min_val=0):
    while True:
        try:
            val = float(input(prompt))
            if val < min_val:
                print(f"  Enter a value >= {min_val}")
                continue
            return val
        except ValueError:
            print("  Invalid input. Enter a number.")

def calculate_grade(marks, total):
    pct = (marks / total) * 100
    if pct >= 85: return "A+"
    elif pct >= 80: return "A"
    elif pct >= 75: return "B+"
    elif pct >= 70: return "B"
    elif pct >= 65: return "C+"
    elif pct >= 60: return "C"
    elif pct >= 50: return "D"
    else: return "F"

def pause():
    input("\n  Press Enter to continue...")


# AUTHENTICATION

def login():
    print_header("COLLEGE ERP SYSTEM - LOGIN")
    print("  Roles: admin / teacher / student\n")
    username = input("  Username: ").strip()
    password = input("  Password: ").strip()

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, role, name, password FROM users WHERE username=?",
              (username,))
    user = c.fetchone()
    conn.close()

    if user and verify_password(password, user[4]):
        print(f"\n  Welcome, {user[3]} ({user[2].upper()})!")
        return {"id": user[0], "username": user[1], "role": user[2], "name": user[3]}
    elif user:
        print("\n  Invalid credentials. Try again.")
        return None
    else:
        print("\n  Invalid credentials. Try again.")
        return None


# STUDENT MANAGEMENT

def add_student():
    print_header("ADD STUDENT")
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT id, name FROM departments")
    depts = c.fetchall()
    print("  Departments:")
    for d in depts:
        print(f"    {d[0]}. {d[1]}")

    name     = input("\n  Full Name: ").strip()
    username = input("  Username: ").strip()
    password = input("  Password: ").strip()
    strong, msg = is_strong_password(password)
    if not strong:
        print(f"\n  Weak password: {msg}")
        conn.close()
        pause()
        return
    roll     = input("  Roll Number: ").strip()
    semester = get_int_input("  Semester (1-8): ", 1, 8)
    dept_id  = get_int_input("  Department ID: ", 1)
    contact  = input("  Contact (optional): ").strip()

    try:
        c.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, 'student', ?)",
                  (username, hash_password(password), name))
        user_id = c.lastrowid
        c.execute("INSERT INTO students (user_id, roll_number, semester, department_id, contact) VALUES (?, ?, ?, ?, ?)",
                  (user_id, roll, semester, dept_id, contact))
        conn.commit()
        print(f"\n  Student '{name}' added successfully.")
    except Exception as e:
        print(f"\n  Error: {e}")
    finally:
        conn.close()
    pause()

def view_all_students():
    print_header("ALL STUDENTS")
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT s.roll_number, u.name, d.name, s.semester, u.username, s.contact
                 FROM students s
                 JOIN users u ON s.user_id = u.id
                 JOIN departments d ON s.department_id = d.id
                 ORDER BY s.roll_number''')
    rows = c.fetchall()
    conn.close()
    print_table(["Roll No", "Name", "Department", "Semester", "Username", "Contact"], rows)
    pause()

def search_student():
    print_header("SEARCH STUDENT")
    keyword = input("  Enter roll number or name: ").strip()
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT s.roll_number, u.name, d.name, s.semester, u.username
                 FROM students s
                 JOIN users u ON s.user_id = u.id
                 JOIN departments d ON s.department_id = d.id
                 WHERE s.roll_number LIKE ? OR u.name LIKE ?''',
              (f'%{keyword}%', f'%{keyword}%'))
    rows = c.fetchall()
    conn.close()
    print_table(["Roll No", "Name", "Department", "Semester", "Username"], rows)
    pause()

def delete_student():
    print_header("DELETE STUDENT")
    roll = input("  Enter Roll Number to delete: ").strip()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT s.id, s.user_id, u.name FROM students s JOIN users u ON s.user_id=u.id WHERE s.roll_number=?", (roll,))
    row = c.fetchone()
    if not row:
        print("  Student not found.")
        conn.close()
        pause()
        return
    confirm = input(f"  Delete student '{row[2]}'? (yes/no): ").strip().lower()
    if confirm == 'yes':
        c.execute("DELETE FROM students WHERE id=?", (row[0],))
        c.execute("DELETE FROM users WHERE id=?", (row[1],))
        conn.commit()
        print("  Student deleted.")
    else:
        print("  Cancelled.")
    conn.close()
    pause()

def view_my_profile(user):
    print_header("MY PROFILE")
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT s.roll_number, u.name, d.name, s.semester, s.contact
                 FROM students s
                 JOIN users u ON s.user_id = u.id
                 JOIN departments d ON s.department_id = d.id
                 WHERE s.user_id = ?''', (user['id'],))
    row = c.fetchone()
    conn.close()
    if row:
        print(f"  Roll Number : {row[0]}")
        print(f"  Name        : {row[1]}")
        print(f"  Department  : {row[2]}")
        print(f"  Semester    : {row[3]}")
        print(f"  Contact     : {row[4]}")
    pause()

def admin_students_menu():
    while True:
        print_header("STUDENT MANAGEMENT")
        print("  1. Add Student")
        print("  2. View All Students")
        print("  3. Search Student")
        print("  4. Delete Student")
        print("  0. Back")
        choice = input("\n  Choice: ").strip()
        if choice == '1': add_student()
        elif choice == '2': view_all_students()
        elif choice == '3': search_student()
        elif choice == '4': delete_student()
        elif choice == '0': break


# TEACHER MANAGEMENT

def add_teacher():
    print_header("ADD TEACHER")
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT id, name FROM departments")
    depts = c.fetchall()
    print("  Departments:")
    for d in depts:
        print(f"    {d[0]}. {d[1]}")

    name     = input("\n  Full Name: ").strip()
    username = input("  Username: ").strip()
    password = input("  Password: ").strip()
    strong, msg = is_strong_password(password)
    if not strong:
        print(f"\n  Weak password: {msg}")
        conn.close()
        pause()
        return
    emp_id   = input("  Employee ID: ").strip()
    dept_id  = get_int_input("  Department ID: ", 1)
    contact  = input("  Contact (optional): ").strip()

    try:
        c.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, 'teacher', ?)",
                  (username, hash_password(password), name))
        user_id = c.lastrowid
        c.execute("INSERT INTO teachers (user_id, employee_id, department_id, contact) VALUES (?, ?, ?, ?)",
                  (user_id, emp_id, dept_id, contact))
        conn.commit()
        print(f"\n  Teacher '{name}' added successfully.")
    except Exception as e:
        print(f"\n  Error: {e}")
    finally:
        conn.close()
    pause()

def view_all_teachers():
    print_header("ALL TEACHERS")
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT t.employee_id, u.name, d.name, u.username, t.contact
                 FROM teachers t
                 JOIN users u ON t.user_id = u.id
                 JOIN departments d ON t.department_id = d.id
                 ORDER BY t.employee_id''')
    rows = c.fetchall()
    conn.close()
    print_table(["Emp ID", "Name", "Department", "Username", "Contact"], rows)
    pause()

def delete_teacher():
    print_header("DELETE TEACHER")
    emp_id = input("  Enter Employee ID to delete: ").strip()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT t.id, t.user_id, u.name FROM teachers t JOIN users u ON t.user_id=u.id WHERE t.employee_id=?", (emp_id,))
    row = c.fetchone()
    if not row:
        print("  Teacher not found.")
        conn.close()
        pause()
        return
    confirm = input(f"  Delete teacher '{row[2]}'? (yes/no): ").strip().lower()
    if confirm == 'yes':
        c.execute("DELETE FROM teachers WHERE id=?", (row[0],))
        c.execute("DELETE FROM users WHERE id=?", (row[1],))
        conn.commit()
        print("  Teacher deleted.")
    else:
        print("  Cancelled.")
    conn.close()
    pause()

def view_my_teacher_profile(user):
    print_header("MY PROFILE")
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT t.employee_id, u.name, d.name, t.contact
                 FROM teachers t
                 JOIN users u ON t.user_id = u.id
                 JOIN departments d ON t.department_id = d.id
                 WHERE t.user_id = ?''', (user['id'],))
    row = c.fetchone()
    conn.close()
    if row:
        print(f"  Employee ID : {row[0]}")
        print(f"  Name        : {row[1]}")
        print(f"  Department  : {row[2]}")
        print(f"  Contact     : {row[3]}")
    pause()

def admin_teachers_menu():
    while True:
        print_header("TEACHER MANAGEMENT")
        print("  1. Add Teacher")
        print("  2. View All Teachers")
        print("  3. Delete Teacher")
        print("  0. Back")
        choice = input("\n  Choice: ").strip()
        if choice == '1': add_teacher()
        elif choice == '2': view_all_teachers()
        elif choice == '3': delete_teacher()
        elif choice == '0': break


# COURSE MANAGEMENT

def add_course():
    print_header("ADD COURSE")
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT id, name FROM departments")
    depts = c.fetchall()
    print("  Departments:")
    for d in depts:
        print(f"    {d[0]}. {d[1]}")

    c.execute("SELECT t.id, u.name, d.name FROM teachers t JOIN users u ON t.user_id=u.id JOIN departments d ON t.department_id=d.id")
    teachers = c.fetchall()
    print("\n  Teachers:")
    for t in teachers:
        print(f"    {t[0]}. {t[1]} ({t[2]})")

    code      = input("\n  Course Code: ").strip()
    name      = input("  Course Name: ").strip()
    credits   = get_int_input("  Credit Hours: ", 1, 6)
    dept_id   = get_int_input("  Department ID: ", 1)
    teacher_id = get_int_input("  Assign Teacher ID (0 for none): ", 0)

    try:
        c.execute("INSERT INTO courses (course_code, name, credit_hours, department_id, teacher_id) VALUES (?, ?, ?, ?, ?)",
                  (code, name, credits, dept_id, teacher_id if teacher_id > 0 else None))
        conn.commit()
        print(f"\n  Course '{name}' added successfully.")
    except Exception as e:
        print(f"\n  Error: {e}")
    finally:
        conn.close()
    pause()

def view_all_courses():
    print_header("ALL COURSES")
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT c.course_code, c.name, c.credit_hours, d.name, COALESCE(u.name, 'Unassigned')
                 FROM courses c
                 JOIN departments d ON c.department_id = d.id
                 LEFT JOIN teachers t ON c.teacher_id = t.id
                 LEFT JOIN users u ON t.user_id = u.id
                 ORDER BY c.course_code''')
    rows = c.fetchall()
    conn.close()
    print_table(["Code", "Course Name", "Credits", "Department", "Teacher"], rows)
    pause()

def enroll_student():
    print_header("ENROLL STUDENT IN COURSE")
    conn = get_connection()
    c = conn.cursor()

    roll = input("  Student Roll Number: ").strip()
    c.execute("SELECT id FROM students WHERE roll_number=?", (roll,))
    student = c.fetchone()
    if not student:
        print("  Student not found.")
        conn.close()
        pause()
        return

    c.execute("SELECT id, course_code, name FROM courses")
    courses = c.fetchall()
    print("\n  Available Courses:")
    for course in courses:
        print(f"    {course[0]}. [{course[1]}] {course[2]}")

    course_id = get_int_input("\n  Course ID to enroll: ", 1)

    try:
        c.execute("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)", (student[0], course_id))
        conn.commit()
        print("  Student enrolled successfully.")
    except Exception as e:
        print(f"  Error: {e}")
    finally:
        conn.close()
    pause()

def view_my_courses_student(user):
    print_header("MY ENROLLED COURSES")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM students WHERE user_id=?", (user['id'],))
    student = c.fetchone()
    if not student:
        print("  Student record not found.")
        conn.close()
        pause()
        return
    c.execute('''SELECT c.course_code, c.name, c.credit_hours, COALESCE(u.name,'Unassigned')
                 FROM enrollments e
                 JOIN courses c ON e.course_id = c.id
                 LEFT JOIN teachers t ON c.teacher_id = t.id
                 LEFT JOIN users u ON t.user_id = u.id
                 WHERE e.student_id = ?''', (student[0],))
    rows = c.fetchall()
    conn.close()
    print_table(["Code", "Course Name", "Credits", "Teacher"], rows)
    pause()

def view_my_courses_teacher(user):
    print_header("MY ASSIGNED COURSES")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM teachers WHERE user_id=?", (user['id'],))
    teacher = c.fetchone()
    if not teacher:
        print("  Teacher record not found.")
        conn.close()
        pause()
        return
    c.execute('''SELECT c.course_code, c.name, c.credit_hours, d.name
                 FROM courses c
                 JOIN departments d ON c.department_id = d.id
                 WHERE c.teacher_id = ?''', (teacher[0],))
    rows = c.fetchall()
    conn.close()
    print_table(["Code", "Course Name", "Credits", "Department"], rows)
    pause()

def delete_course():
    print_header("DELETE COURSE")
    code = input("  Enter Course Code to delete: ").strip()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name FROM courses WHERE course_code=?", (code,))
    course = c.fetchone()
    if not course:
        print("  Course not found.")
        conn.close()
        pause()
        return
    confirm = input(f"  Delete course '{course[1]}'? (yes/no): ").strip().lower()
    if confirm == 'yes':
        c.execute("DELETE FROM courses WHERE id=?", (course[0],))
        conn.commit()
        print("  Course deleted.")
    else:
        print("  Cancelled.")
    conn.close()
    pause()

def admin_courses_menu():
    while True:
        print_header("COURSE MANAGEMENT")
        print("  1. Add Course")
        print("  2. View All Courses")
        print("  3. Enroll Student in Course")
        print("  4. Delete Course")
        print("  0. Back")
        choice = input("\n  Choice: ").strip()
        if choice == '1': add_course()
        elif choice == '2': view_all_courses()
        elif choice == '3': enroll_student()
        elif choice == '4': delete_course()
        elif choice == '0': break


# ATTENDANCE

def mark_attendance(user):
    print_header("MARK ATTENDANCE")
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT id FROM teachers WHERE user_id=?", (user['id'],))
    teacher = c.fetchone()
    if not teacher:
        print("  Teacher record not found.")
        conn.close()
        pause()
        return

    c.execute("SELECT id, course_code, name FROM courses WHERE teacher_id=?", (teacher[0],))
    courses = c.fetchall()
    if not courses:
        print("  No courses assigned to you.")
        conn.close()
        pause()
        return

    print("  Your Courses:")
    for course in courses:
        print(f"    {course[0]}. [{course[1]}] {course[2]}")

    course_id = get_int_input("\n  Select Course ID: ", 1)
    att_date  = input("  Date (YYYY-MM-DD) [blank = today]: ").strip()
    if not att_date:
        att_date = str(date.today())
    elif not validate_date(att_date):
        print("  Invalid date format. Use YYYY-MM-DD.")
        conn.close()
        pause()
        return

    c.execute('''SELECT s.id, s.roll_number, u.name
                 FROM enrollments e
                 JOIN students s ON e.student_id = s.id
                 JOIN users u ON s.user_id = u.id
                 WHERE e.course_id = ?
                 ORDER BY s.roll_number''', (course_id,))
    students = c.fetchall()

    if not students:
        print("  No students enrolled in this course.")
        conn.close()
        pause()
        return

    print(f"\n  Marking attendance for {att_date}")
    print("  Enter P (Present) or A (Absent):\n")

    records = []
    for s in students:
        while True:
            status = input(f"  {s[1]} - {s[2]}: ").strip().upper()
            if status in ('P', 'A'):
                records.append((s[0], course_id, att_date, status))
                break
            print("  Enter P or A only.")

    try:
        c.executemany("INSERT OR REPLACE INTO attendance (student_id, course_id, date, status) VALUES (?, ?, ?, ?)", records)
        conn.commit()
        print(f"\n  Attendance marked for {len(records)} students.")
    except Exception as e:
        print(f"  Error: {e}")
    finally:
        conn.close()
    pause()

def view_attendance_admin():
    print_header("VIEW ATTENDANCE")
    conn = get_connection()
    c = conn.cursor()
    roll = input("  Enter Student Roll Number: ").strip()
    c.execute("SELECT id FROM students WHERE roll_number=?", (roll,))
    student = c.fetchone()
    if not student:
        print("  Student not found.")
        conn.close()
        pause()
        return
    c.execute('''SELECT c.course_code, c.name,
                        SUM(CASE WHEN a.status='P' THEN 1 ELSE 0 END),
                        COUNT(a.id)
                 FROM enrollments e
                 JOIN courses c ON e.course_id = c.id
                 LEFT JOIN attendance a ON a.student_id = e.student_id AND a.course_id = e.course_id
                 WHERE e.student_id = ?
                 GROUP BY c.id''', (student[0],))
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        total   = row[3] or 0
        present = row[2] or 0
        pct     = f"{(present/total*100):.1f}%" if total > 0 else "N/A"
        result.append((row[0], row[1], present, total, pct))
    print_table(["Code", "Course", "Present", "Total", "Attendance%"], result)
    pause()

def view_my_attendance_student(user):
    print_header("MY ATTENDANCE")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM students WHERE user_id=?", (user['id'],))
    student = c.fetchone()
    if not student:
        print("  Student record not found.")
        conn.close()
        pause()
        return
    c.execute('''SELECT c.course_code, c.name,
                        SUM(CASE WHEN a.status='P' THEN 1 ELSE 0 END),
                        COUNT(a.id)
                 FROM enrollments e
                 JOIN courses c ON e.course_id = c.id
                 LEFT JOIN attendance a ON a.student_id = e.student_id AND a.course_id = e.course_id
                 WHERE e.student_id = ?
                 GROUP BY c.id''', (student[0],))
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        total   = row[3] or 0
        present = row[2] or 0
        pct     = f"{(present/total*100):.1f}%" if total > 0 else "N/A"
        result.append((row[0], row[1], present, total, pct))
    print_table(["Code", "Course", "Present", "Total", "Attendance%"], result)
    pause()

def view_course_attendance_teacher(user):
    print_header("COURSE ATTENDANCE REPORT")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM teachers WHERE user_id=?", (user['id'],))
    teacher = c.fetchone()
    if not teacher:
        conn.close()
        pause()
        return
    c.execute("SELECT id, course_code, name FROM courses WHERE teacher_id=?", (teacher[0],))
    courses = c.fetchall()
    print("  Your Courses:")
    for course in courses:
        print(f"    {course[0]}. [{course[1]}] {course[2]}")
    course_id = get_int_input("\n  Select Course ID: ", 1)
    c.execute('''SELECT s.roll_number, u.name,
                        SUM(CASE WHEN a.status='P' THEN 1 ELSE 0 END),
                        COUNT(a.id)
                 FROM enrollments e
                 JOIN students s ON e.student_id = s.id
                 JOIN users u ON s.user_id = u.id
                 LEFT JOIN attendance a ON a.student_id = e.student_id AND a.course_id = e.course_id
                 WHERE e.course_id = ?
                 GROUP BY s.id''', (course_id,))
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        total   = row[3] or 0
        present = row[2] or 0
        pct     = f"{(present/total*100):.1f}%" if total > 0 else "N/A"
        result.append((row[0], row[1], present, total, pct))
    print_table(["Roll No", "Name", "Present", "Total", "Attendance%"], result)
    pause()


# GRADES

def enter_grades(user):
    print_header("ENTER GRADES")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM teachers WHERE user_id=?", (user['id'],))
    teacher = c.fetchone()
    if not teacher:
        print("  Teacher record not found.")
        conn.close()
        pause()
        return
    c.execute("SELECT id, course_code, name FROM courses WHERE teacher_id=?", (teacher[0],))
    courses = c.fetchall()
    if not courses:
        print("  No courses assigned to you.")
        conn.close()
        pause()
        return
    print("  Your Courses:")
    for course in courses:
        print(f"    {course[0]}. [{course[1]}] {course[2]}")
    course_id   = get_int_input("\n  Select Course ID: ", 1)
    total_marks = get_float_input("  Total Marks for this course: ", 1)
    c.execute('''SELECT s.id, s.roll_number, u.name
                 FROM enrollments e
                 JOIN students s ON e.student_id = s.id
                 JOIN users u ON s.user_id = u.id
                 WHERE e.course_id = ?
                 ORDER BY s.roll_number''', (course_id,))
    students = c.fetchall()
    if not students:
        print("  No students enrolled in this course.")
        conn.close()
        pause()
        return
    print("\n  Enter marks obtained for each student:\n")
    records = []
    for s in students:
        marks = get_float_input(f"  {s[1]} - {s[2]} (out of {total_marks}): ", 0)
        records.append((s[0], course_id, marks, total_marks))
    try:
        c.executemany("INSERT OR REPLACE INTO grades (student_id, course_id, marks_obtained, total_marks) VALUES (?, ?, ?, ?)", records)
        conn.commit()
        print(f"\n  Grades entered for {len(records)} students.")
    except Exception as e:
        print(f"  Error: {e}")
    finally:
        conn.close()
    pause()

def view_result_card_admin():
    print_header("STUDENT RESULT CARD")
    conn = get_connection()
    c = conn.cursor()
    roll = input("  Enter Student Roll Number: ").strip()
    c.execute('''SELECT s.id, u.name, s.roll_number, d.name, s.semester
                 FROM students s JOIN users u ON s.user_id=u.id JOIN departments d ON s.department_id=d.id
                 WHERE s.roll_number=?''', (roll,))
    student = c.fetchone()
    if not student:
        print("  Student not found.")
        conn.close()
        pause()
        return
    print(f"\n  Name       : {student[1]}")
    print(f"  Roll No    : {student[2]}")
    print(f"  Department : {student[3]}")
    print(f"  Semester   : {student[4]}\n")
    c.execute('''SELECT c.course_code, c.name, g.marks_obtained, g.total_marks
                 FROM grades g JOIN courses c ON g.course_id = c.id
                 WHERE g.student_id = ?''', (student[0],))
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        pct   = (row[2] / row[3]) * 100
        grade = calculate_grade(row[2], row[3])
        result.append((row[0], row[1], f"{row[2]}/{row[3]}", f"{pct:.1f}%", grade))
    print_table(["Code", "Course", "Marks", "Percentage", "Grade"], result)
    pause()

def view_my_grades_student(user):
    print_header("MY RESULT CARD")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM students WHERE user_id=?", (user['id'],))
    student = c.fetchone()
    if not student:
        print("  Student record not found.")
        conn.close()
        pause()
        return
    c.execute('''SELECT c.course_code, c.name, g.marks_obtained, g.total_marks
                 FROM grades g JOIN courses c ON g.course_id = c.id
                 WHERE g.student_id = ?''', (student[0],))
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        pct   = (row[2] / row[3]) * 100
        grade = calculate_grade(row[2], row[3])
        result.append((row[0], row[1], f"{row[2]}/{row[3]}", f"{pct:.1f}%", grade))
    print_table(["Code", "Course", "Marks", "Percentage", "Grade"], result)
    pause()

def view_course_grades_teacher(user):
    print_header("COURSE GRADE REPORT")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM teachers WHERE user_id=?", (user['id'],))
    teacher = c.fetchone()
    if not teacher:
        conn.close()
        pause()
        return
    c.execute("SELECT id, course_code, name FROM courses WHERE teacher_id=?", (teacher[0],))
    courses = c.fetchall()
    print("  Your Courses:")
    for course in courses:
        print(f"    {course[0]}. [{course[1]}] {course[2]}")
    course_id = get_int_input("\n  Select Course ID: ", 1)
    c.execute('''SELECT s.roll_number, u.name, g.marks_obtained, g.total_marks
                 FROM grades g
                 JOIN students s ON g.student_id = s.id
                 JOIN users u ON s.user_id = u.id
                 WHERE g.course_id = ?
                 ORDER BY g.marks_obtained DESC''', (course_id,))
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        pct   = (row[2] / row[3]) * 100
        grade = calculate_grade(row[2], row[3])
        result.append((row[0], row[1], f"{row[2]}/{row[3]}", f"{pct:.1f}%", grade))
    print_table(["Roll No", "Name", "Marks", "Percentage", "Grade"], result)
    pause()


# FEE MANAGEMENT

def add_fee_record():
    print_header("ADD FEE RECORD")
    conn = get_connection()
    c = conn.cursor()
    roll = input("  Student Roll Number: ").strip()
    c.execute("SELECT id FROM students WHERE roll_number=?", (roll,))
    student = c.fetchone()
    if not student:
        print("  Student not found.")
        conn.close()
        pause()
        return
    amount   = get_float_input("  Total Fee Amount: ", 1)
    semester = get_int_input("  Semester: ", 1, 8)
    due_date = input("  Due Date (YYYY-MM-DD): ").strip()
    if not validate_date(due_date):
        print("  Invalid date format. Use YYYY-MM-DD.")
        conn.close()
        pause()
        return
    try:
        c.execute("INSERT INTO fees (student_id, amount, paid, semester, due_date) VALUES (?, ?, 0, ?, ?)",
                  (student[0], amount, semester, due_date))
        conn.commit()
        print("  Fee record added.")
    except Exception as e:
        print(f"  Error: {e}")
    finally:
        conn.close()
    pause()

def record_payment():
    print_header("RECORD FEE PAYMENT")
    conn = get_connection()
    c = conn.cursor()
    roll = input("  Student Roll Number: ").strip()
    c.execute("SELECT id FROM students WHERE roll_number=?", (roll,))
    student = c.fetchone()
    if not student:
        print("  Student not found.")
        conn.close()
        pause()
        return
    c.execute("SELECT id, semester, amount, paid, due_date FROM fees WHERE student_id=? ORDER BY semester", (student[0],))
    fees = c.fetchall()
    if not fees:
        print("  No fee records found.")
        conn.close()
        pause()
        return
    print("\n  Fee Records:")
    for f in fees:
        status = "PAID" if f[2] <= f[3] else "PENDING"
        print(f"    ID:{f[0]} | Sem:{f[1]} | Total:{f[2]} | Paid:{f[3]} | Due:{f[4]} | {status}")
    fee_id      = get_int_input("\n  Fee Record ID to add payment: ", 1)
    amount_paid = get_float_input("  Amount Paid: ", 1)
    try:
        c.execute("UPDATE fees SET paid = paid + ? WHERE id=?", (amount_paid, fee_id))
        conn.commit()
        print("  Payment recorded.")
    except Exception as e:
        print(f"  Error: {e}")
    finally:
        conn.close()
    pause()

def view_fee_status_admin():
    print_header("VIEW FEE STATUS")
    conn = get_connection()
    c = conn.cursor()
    roll = input("  Student Roll Number: ").strip()
    c.execute("SELECT s.id, u.name FROM students s JOIN users u ON s.user_id=u.id WHERE s.roll_number=?", (roll,))
    student = c.fetchone()
    if not student:
        print("  Student not found.")
        conn.close()
        pause()
        return
    print(f"\n  Student: {student[1]}\n")
    c.execute("SELECT semester, amount, paid, due_date FROM fees WHERE student_id=? ORDER BY semester", (student[0],))
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        pending = max(0, row[1] - row[2])
        status  = "PAID" if row[1] <= row[2] else "PENDING"
        result.append((row[0], row[1], row[2], pending, row[3], status))
    print_table(["Semester", "Total", "Paid", "Pending", "Due Date", "Status"], result)
    pause()

def view_my_fees_student(user):
    print_header("MY FEE STATUS")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM students WHERE user_id=?", (user['id'],))
    student = c.fetchone()
    if not student:
        print("  Student record not found.")
        conn.close()
        pause()
        return
    c.execute("SELECT semester, amount, paid, due_date FROM fees WHERE student_id=? ORDER BY semester", (student[0],))
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        pending = max(0, row[1] - row[2])
        status  = "PAID" if row[1] <= row[2] else "PENDING"
        result.append((row[0], row[1], row[2], pending, row[3], status))
    print_table(["Semester", "Total", "Paid", "Pending", "Due Date", "Status"], result)
    pause()

def admin_fees_menu():
    while True:
        print_header("FEE MANAGEMENT")
        print("  1. Add Fee Record for Student")
        print("  2. Record Fee Payment")
        print("  3. View Fee Status by Student")
        print("  0. Back")
        choice = input("\n  Choice: ").strip()
        if choice == '1': add_fee_record()
        elif choice == '2': record_payment()
        elif choice == '3': view_fee_status_admin()
        elif choice == '0': break


# ROLE-BASED MENUS

def admin_menu(user):
    while True:
        print_header(f"ADMIN PANEL  |  {user['name']}")
        print("  1. Student Management")
        print("  2. Teacher Management")
        print("  3. Course Management")
        print("  4. Attendance - View by Student")
        print("  5. Grades - View Result Card")
        print("  6. Fee Management")
        print("  0. Logout")
        choice = input("\n  Choice: ").strip()
        if choice == '1': admin_students_menu()
        elif choice == '2': admin_teachers_menu()
        elif choice == '3': admin_courses_menu()
        elif choice == '4': view_attendance_admin()
        elif choice == '5': view_result_card_admin()
        elif choice == '6': admin_fees_menu()
        elif choice == '0':
            print("\n  Logged out.\n")
            break

def teacher_menu(user):
    while True:
        print_header(f"TEACHER PANEL  |  {user['name']}")
        print("  1. My Profile")
        print("  2. My Courses")
        print("  3. Mark Attendance")
        print("  4. View Attendance Report (My Courses)")
        print("  5. Enter Grades")
        print("  6. View Grade Report (My Courses)")
        print("  0. Logout")
        choice = input("\n  Choice: ").strip()
        if choice == '1': view_my_teacher_profile(user)
        elif choice == '2': view_my_courses_teacher(user)
        elif choice == '3': mark_attendance(user)
        elif choice == '4': view_course_attendance_teacher(user)
        elif choice == '5': enter_grades(user)
        elif choice == '6': view_course_grades_teacher(user)
        elif choice == '0':
            print("\n  Logged out.\n")
            break

def student_menu(user):
    while True:
        print_header(f"STUDENT PORTAL  |  {user['name']}")
        print("  1. My Profile")
        print("  2. My Courses")
        print("  3. My Attendance")
        print("  4. My Grades / Result Card")
        print("  5. My Fee Status")
        print("  0. Logout")
        choice = input("\n  Choice: ").strip()
        if choice == '1': view_my_profile(user)
        elif choice == '2': view_my_courses_student(user)
        elif choice == '3': view_my_attendance_student(user)
        elif choice == '4': view_my_grades_student(user)
        elif choice == '5': view_my_fees_student(user)
        elif choice == '0':
            print("\n  Logged out.\n")
            break


# MAIN

def main():
    setup_database()

    while True:
        user     = None
        attempts = 0
        while not user and attempts < 3:
            user = login()
            if not user:
                attempts += 1
                if attempts < 3:
                    print(f"  {3 - attempts} attempt(s) remaining.")
                else:
                    print("  Too many failed attempts. Exiting.")
                    sys.exit()

        role = user['role']
        if role == 'admin':
            admin_menu(user)
        elif role == 'teacher':
            teacher_menu(user)
        elif role == 'student':
            student_menu(user)

        again = input("  Login again? (yes/no): ").strip().lower()
        if again != 'yes':
            print("\n  Goodbye!\n")
            break

if __name__ == "__main__":
    main()