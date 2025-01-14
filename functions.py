import sqlite3
import datetime
import random

db = sqlite3.connect("database.db", check_same_thread=False)
hist = sqlite3.connect("user_history.db", check_same_thread=False)


def create_account_number():
    string = ""
    for i in range(10):
        digit = random.choice([1,2,3,4,5,6,7,8,9,0])
        string += str(digit)
    if len(str(int(string)))<10:
        return create_account_number()
    temp = db.cursor()
    temp.execute("SELECT account_number FROM accounts")
    lis = temp.fetchall()
    if string in lis[0]:
        return create_account_number()
    return string


def details(account_number, password):
    temp = db.cursor()
    temp.execute("SELECT * FROM accounts WHERE account_number = ? AND password = ?", (account_number, password))
    details = temp.fetchall()
    temp.close()
    account_number = details[0][0]
    name = details[0][1]
    password = details[0][2]
    email = details[0][3]
    balance = details[0][4]
    return account_number, name, password, email, balance

def withdraw(account_number, amount):
    try:
        temp = db.cursor()
        temp.execute("SELECT balance FROM accounts WHERE account_number = ?", (account_number,))
        balance = temp.fetchall()
        temp.close()
        balance = balance[0][0]
        new_balance = balance - amount
        if new_balance < 5000:
            max_amount = balance-5000
            return False, max_amount
        else:
            temp= db.cursor()
            temp.execute("UPDATE accounts SET balance = {} WHERE account_number = ?".format(new_balance), (account_number, ))
            temp.close()
            db.commit()
            return True, None
    except:
        return "Error", None

def deposit(account_number, amount):
    try:
        temp = db.cursor()
        temp.execute("SELECT balance FROM accounts WHERE account_number = ?", (account_number,))
        balance = temp.fetchall()
        temp.close()
        balance = balance[0][0]
        new_balance = balance + amount
        temp = db.cursor()
        temp.execute("UPDATE accounts SET balance = {} WHERE account_number = ?".format(new_balance), (account_number, ))
        temp.close()
        db.commit()
        return True
    except:
        return "Error"

def change_details(account_number, parameter, changed_parameter):
    try:
        temp = db.cursor()
        temp.execute("UPDATE accounts SET {} = ? WHERE account_number = ?".format(parameter), (changed_parameter, account_number))
        temp.close()
        db.commit()
        return True
    except:
        return "Error"

def delete_account(account_number, password):
    try:
        temp = db.cursor()
        temp.execute("SELECT * FROM accounts WHERE account_number = ? AND password = ?", (account_number, password))
        lis = temp.fetchall()
        temp.close()
        if lis[0] == []:
            return "Error"
        temp = db.cursor()
        temp.execute("DELETE FROM accounts WHERE account_number = ?", (account_number,))
        temp.close()
        db.commit()
        temp = hist.cursor()
        temp.execute("DROP TABLE {}".format("user_"+str(account_number)))
        temp.close()
        hist.commit()
        return True
    except:
        return "Error"

def money_transfer(account_number_of_sender, password_of_sender, account_number_of_reciever, amount):
    try:
        temp = db.cursor()
        temp.execute("SELECT * FROM accounts WHERE account_number = ? AND password = ?", (account_number_of_sender, password_of_sender))
        lis = temp.fetchall()
        temp.close()
        if lis == []:
            return "Error", None

        temp = db.cursor()
        temp.execute("SELECT balance FROM accounts WHERE account_number = ?", (account_number_of_sender,))
        balance_of_sender = temp.fetchall()
        balance_of_sender = balance_of_sender[0]
        temp.close()
        new_balance = balance_of_sender[0] - amount
        if new_balance < 5000:
            return "Error", (balance_of_sender-5000)
        temp = db.cursor()
        temp.execute("UPDATE accounts SET balance = {} WHERE account_number = ?".format(new_balance), (account_number_of_sender, ))
        temp.close()
        db.commit()
        
        temp = db.cursor()
        temp.execute("SELECT balance FROM accounts WHERE account_number = ?", (account_number_of_reciever,))
        balance_of_reciever = temp.fetchall()
        balance_of_reciever = balance_of_reciever[0]
        temp.close()
        new_balance = balance_of_reciever[0] + amount
        temp = db.cursor()
        temp.execute("UPDATE accounts SET balance = {} WHERE account_number = ?".format(new_balance), (account_number_of_reciever, ))
        temp.close()
        db.commit()
        return True, None
    except:
        return "Error", None

