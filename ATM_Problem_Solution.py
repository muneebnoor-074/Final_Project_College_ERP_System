# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 14:43:03 2026

@author: Muneeb Noor
"""

import hashlib
import os

def _hash_pin(pin, salt=None):
    if salt is None:
        salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', pin.encode(), salt, 100_000)
    return salt.hex() + ":" + key.hex()

def _verify_pin(pin, stored):
    try:
        salt_hex, key_hex = stored.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        key = hashlib.pbkdf2_hmac('sha256', pin.encode(), salt, 100_000)
        return key.hex() == key_hex
    except (ValueError, AttributeError):
        return False

HASHED_PIN = _hash_pin("1234")
balance = 5000


def verify_pin():
    attempts = 0
    while attempts < 3:
        pin = input("Enter your PIN: ")
        if _verify_pin(pin, HASHED_PIN):
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
    try:
        amount = float(input("Enter deposit amount: Rs. "))
    except ValueError:
        print("Invalid input. Please enter a numeric value.\n")
        return
    if amount <= 0:
        print("Invalid amount. Please enter a positive value.\n")
    else:
        balance += amount
        print(f"Rs. {amount:.2f} deposited successfully.")
        print(f"Updated balance: Rs. {balance:.2f}\n")


def withdraw():
    global balance
    try:
        amount = float(input("Enter withdrawal amount: Rs. "))
    except ValueError:
        print("Invalid input. Please enter a numeric value.\n")
        return
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