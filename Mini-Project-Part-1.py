# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 10:12:07 2026

@author: Muneeb Noor
"""


# Mini-Project_Part-1:

import csv

def is_password_strong(password):
    special_characters = ["@", "#", "$", "%", "&", "*"]

    if len(password) < 8:
        print("Your password must be more than 8 characters.")
        return False

    has_upper   = any(c.isupper() for c in password)
    has_lower   = any(c.islower() for c in password)
    has_special = any(c in special_characters for c in password)

    if not has_upper:   print("Your password must contain at least one uppercase letter.")
    if not has_lower:   print("Your password must contain at least one lowercase letter.")
    if not has_special: print("Your password must contain at least one special character (@#$%&*).")

    if has_upper and has_lower and has_special:
        print("Your password is strong...")
        return True
    return False

def registration():
    print("Registration Process:")
    while True:
        password = input("Set your password: ")
        strong = is_password_strong(password)
        
        if strong:
            with open("password.csv","w",newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Password"])
                writer.writerow([password])
                print("Password saved successfully.")
                break
        else:
            print("Your passwrod is weak...Try Again...")
            
def login_process():
    with open("password.csv","r") as file:
        reader = csv.reader(file)
        next(reader)
        saved_password = next(reader)[0]
    
    attempts = 0
    while attempts < 3:
        new_password = input("Enter your password: ")
        if new_password == saved_password:
            print("Login Successfully...")
            break
        else:
            attempts += 1
            remaining = 3 - attempts
            if remaining > 0:
                print(f"Wrong password only {remaining} attempts are ramaining.")
            else:
                print("To many failed attempts:")
                break
                
def read_all_students():
    students = []
    with open("data.csv","r") as file:
        reader = csv.DictReader(file)
        for i in reader:
            students.append(i)
    return students

def write_all_students(students=None):
    with open("data.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Name", "Marks", "Section"])
        writer.writeheader()

        if students:
            for s in students:
                writer.writerow(s)
        else:
            while True:
                num = int(input("Enter number of students: "))
                for i in range(num):
                    name    = input(f"Enter Name of student-{i+1}: ")
                    marks   = input(f"Enter Marks of student-{i+1}: ")
                    section = input(f"Enter Section of student-{i+1}: ")
                    writer.writerow({"Name": name, "Marks": marks, "Section": section})
                print("Students added successfully.")
                break

def view_all_students():
    students = read_all_students()
    
    if not students:
        print("No Record Found: ")
        return
    
    print(f"{'Name':<13} {'Marks':<8} {'Section'}")
    print("-" * 30)
    for s in students:
        print(f"{s['Name']:<13} {s['Marks']:<8} {s['Section']}")
        
def update_student():
    name = input("Enter student name to update: ")
    students = read_all_students()

    for s in students:
        if s["Name"].lower() == name.lower():
            print(f"Current: \nName: {s['Name']}, Marks: {s['Marks']}, Section: {s['Section']}")

            new_marks   = input("Enter new marks: ")
            new_section = input("Enter new section: ")

            s["Marks"]   = new_marks   
            s["Section"] = new_section 

            write_all_students(students)
            print(f"Student '{name}' updated successfully!")
            return

    print(f"Student '{name}' not found.")

def dashboard():
    while True:
        print("--- Welcome to Dashboard---")
        print("1. View all Students: ")
        print("2. Write Students")
        print("3. Update Student")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")

        if   choice == "1":  view_all_students()
        elif choice == "2":  write_all_students()
        elif choice == "3":  update_student()
        elif choice == "4":
            print("Goodbye! Exiting safely.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")
        
def main():
    print("\n---Welcome to the File-Based User System---")

    try:
        open("password.csv", "r").close()
        print("Account found. Please login.")
    except FileNotFoundError:
        print("No account found. Please register first.")
        registration()

    login_process()
    dashboard()

main() 
        