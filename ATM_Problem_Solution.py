# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 14:43:03 2026

@author: Muneeb Noor
"""

CORRECT_PIN = "1234"
balance = 5000


def verify_pin():
    attempts = 0
    while attempts < 3:
        pin = input("Enter your PIN: ")
        if pin == CORRECT_PIN:
            print("Access granted.\n")
            return True
        else:
            attempts += 1
            remaining = 3 - attempts
            if remaining > 0:
                print(f"Incorrect PIN. {remaining} attempt(s) remaining.")
            else:
                print("Account locked. Too many failed attempts.")
    return False


def check_balance():
    print(f"\nYour current balance is: Rs. {balance:.2f}\n")


def deposit():
    global balance
    amount = float(input("Enter deposit amount: Rs. "))
    if amount <= 0:
        print("Invalid amount. Please enter a positive value.\n")
    else:
        balance += amount
        print(f"Rs. {amount:.2f} deposited successfully.")
        print(f"Updated balance: Rs. {balance:.2f}\n")


def withdraw():
    global balance
    amount = float(input("Enter withdrawal amount: Rs. "))
    if amount <= 0:
        print("Invalid amount. Please enter a positive value.\n")
    elif amount > balance:
        print("Insufficient funds.\n")
    else:
        balance -= amount
        print(f"Rs. {amount:.2f} withdrawn successfully.")
        print(f"Updated balance: Rs. {balance:.2f}\n")


def show_menu():
    print("--- ATM MENU ---")
    print("1. Check Balance")
    print("2. Deposit Money")
    print("3. Withdraw Money")
    print("4. Exit")
   


def main():
    print("--- Welcome to the ATM ---\n")

    if not verify_pin():
        return

    while True:
        show_menu()
        choice = input("Select an option (1-4): ")

        if choice == "1":
            check_balance()
        elif choice == "2":
            deposit()
        elif choice == "3":
            withdraw()
        elif choice == "4":
            print("\nThank you for using the ATM. Goodbye!")
            break
        else:
            print("Invalid option. Please choose between 1 and 4.\n")


main()