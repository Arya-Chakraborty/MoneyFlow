from flask import Flask, redirect, request, render_template
import sqlite3
import random
from functions import *
import datetime

app = Flask(__name__)
db = sqlite3.connect("database.db", check_same_thread=False)
history = sqlite3.connect("user_history.db", check_same_thread=False)
account_number = None
password = None
    
@app.route("/")
def login():
    return render_template("login.html")

@app.route("/check_password/", methods=["GET", "POST"])
def check_password():
    global account_number
    global password
    if request.method == "GET":
        return render_template("login.html")
    account_number = request.form.get("account_number")
    password = request.form.get("password")
    temp = db.cursor()
    temp.execute("SELECT * FROM accounts WHERE account_number = ? AND password = ?", (account_number, password))
    lis = temp.fetchall()
    temp.close()
    if lis == []:
        return render_template("login.html", message="Invalid account number or password")
    else:
        account_number, name, password, email, balance = details(account_number, password)
        return render_template("user_homepage.html", account_number=account_number, name=name, password=password, email=email, balance=balance)

@app.route("/create_account/", methods=["GET", "POST"])
def create_account():
    try:
        if request.method == "GET":
            return render_template("create_account.html")
        name = request.form.get('name')
        password = request.form.get("created_password")
        confirmed_password = request.form.get("confirm_password")
        if name== "" or password == "":
            return render_template("create_account.html", message="Please Enter Username and Password")
        elif confirmed_password == "":
            return render_template("create_account.html", message="Please confirm your password.")
        elif password != confirmed_password:
            return render_template("create_account.html", message="Password and Confirmed Password did not match")
        balance = int(request.form.get('balance'))
        if balance < 5000:
            return render_template("create_account.html", message="Please enter amount greater than 5000.")
        email = request.form.get('email')
        account_number = create_account_number()
        temp = db.cursor()
        temp.execute("""INSERT INTO accounts VALUES(?, ?, ?, ?, ?)""", (account_number, name, password, email, balance))
        temp.close()
        db.commit()
        command ="CREATE TABLE user_"+str(account_number)+" (transaction_no INTEGER(50) PRIMARY KEY, type NOT NULL ,amount INTEGER(50) NOT NULL, time NOT NULL, comment NOT NULL)"
        hist = history.cursor()
        hist.execute(command)
        hist.close()
        history.commit()
        date = str(datetime.datetime.now())
        hist = history.cursor()
        hist.execute("INSERT INTO {} VALUES(?, ?, ?, ?, ?)".format("user_"+str(account_number)), (1, "Credit", balance, date, "Starting Amount"))
        hist.close()
        history.commit()        
        return render_template("user_homepage.html", account_number=account_number, name=name, password=password, email=email, balance=balance)
    except:
        return render_template("create_account.html", message="Something Went wrong. Please Try again.")

@app.route("/withdraw/", methods=["GET", "POST"])
def withdraw_page():
    if request.method == "GET":
        return render_template("w_and_d_layout.html", action="Withdraw", form_action="/withdraw/")
    try:
        account_number = request.form.get('account_number')
        password = request.form.get('password')
        amount = int(request.form.get('amount'))
        comment = request.form.get('comments')   
        message, max_ammount = withdraw(account_number, amount)
        if message == "Error":
            return render_template("w_and_d_layout.html", action="Withdraw", form_action="/withdraw/", message="Some Error Occured. Please Try Again.")
        if message == False:
            return render_template("w_and_d_layout.html", action="Withdraw", form_action="/withdraw/", message="Transaction Failed. Please enter amount less than "+str(max_ammount))
        account_number, name, password, email, balance = details(account_number, password)
        temp = history.cursor()
        temp.execute("SELECT * FROM {}".format("user_"+str(account_number)))
        records = temp.fetchall()
        temp.close()
        no_of_records = len(records)+1
        date = datetime.datetime.now() 
        temp = history.cursor() 
        temp.execute("INSERT INTO {} VALUES(?, ?, ?, ?, ?)".format("user_"+str(account_number)), (no_of_records, "Debit", amount, date, comment))
        temp.close()
        history.commit()
        return redirect("/")
    except:
        return render_template("w_and_d_layout.html", action="Withdraw", form_action="/withdraw/", message="Something went wrong. Please Try Again.")

@app.route("/deposit/", methods=["GET", "POST"])
def deposit_page():
    if request.method == "GET":
        return render_template("w_and_d_layout.html", action="Deposit", form_action="/deposit/")
    try:
        account_number = request.form.get('account_number')
        password = request.form.get('password')
        comment = request.form.get('comments')
        amount = int(request.form.get('amount'))
        message = deposit(account_number, amount)
        if message == "Error":
            return render_template("w_and_d_layout.html", action="Deposit", form_action="/deposit/", message="Some Error Occured. Please Try Again.")
        account_number, name, password, email, balance = details(account_number, password)
        temp = history.cursor()
        temp.execute("SELECT * FROM {}".format("user_"+str(account_number)))
        records = temp.fetchall()
        temp.close()
        no_of_records = len(records)+1
        date = datetime.datetime.now() 
        temp = history.cursor() 
        temp.execute("INSERT INTO {} VALUES(?, ?, ?, ?, ?)".format("user_"+str(account_number)), (no_of_records, "Credit", amount, date, comment))
        temp.close()
        history.commit()
        return redirect("/")
    except:
        return render_template("w_and_d_layout.html", action="Deposit", form_action="/deposit/", message="Something went wrong. Please Try Again.")

@app.route("/temp_change/")
def temp_change():
    return render_template("temp_change.html")

@app.route("/change_details/", methods=["GET", "POST"])
def change_details_page():
    parameter = request.args.get('parameter')
    if request.method == "GET":
        return render_template("change_details.html", parameter=parameter, form_action="/change_details/?parameter="+parameter, parameter_type="new_"+parameter, type=parameter)
    account_number = request.form.get('account_number')
    if parameter == "name":
        new_parameter = request.form.get("new_name")
        condition = change_details(account_number, "name", new_parameter)
    if parameter == "password":
        new_parameter = request.form.get("new_password")
        condition = change_details(account_number, "password", new_parameter)
    if parameter == "email":
        new_parameter = request.form.get("new_email")
        condition = change_details(account_number, "email_id", new_parameter)
    return redirect("/")

@app.route("/show_history/", methods=["GET", "POST"])
def show_history():
    try:
        if request.method == "GET":
            return render_template("user_history.html")
        account_number = request.form.get("account_number")
        table_name = "user_"+str(account_number)
        temp = history.cursor()
        temp.execute("SELECT * FROM {} ORDER BY transaction_no DESC LIMIT 10".format(table_name))
        records = temp.fetchall()
        temp.close()
        return render_template("user_history.html", records= records)
    except:
        return render_template("user_history.html")        

@app.route("/delete_account", methods=["GET", "POST"])
def delete_account_page():
    try:
        if request.method == "GET":
            return render_template("delete_account.html")
        account_number = request.form.get("account_number")
        password = request.form.get("password")
        condition = delete_account(account_number, password)
        if condition == "Error":
            return render_template("delete_account.html", message="There was an error. Please try again.")
        return redirect("/")
    except :
        return render_template("delete_account.html", message="There was an error. Please try again.")

@app.route("/money_transfer/", methods=["GET", "POST"])
def money_transfer_page():
    try:
        if request.method == "GET":
            return render_template("money_transfer.html")
        account_number_of_sender = request.form.get("account_number")
        account_number_of_reciever = request.form.get("account_number_of_reciever")
        amount = int(request.form.get("amount"))
        password_of_sender = request.form.get("password")
        comment = request.form.get("comment")
        condition, max_amount  = money_transfer(account_number_of_sender, password_of_sender, account_number_of_reciever, amount)
        if condition == "Error" and max_amount != None:
            return render_template("money_transfer.html", message = "You can send a max amount of "+str(max_amount)+".")
        temp = history.cursor()
        temp.execute("SELECT * FROM {}".format("user_"+str(account_number_of_sender)))
        records = temp.fetchall()
        temp.close()
        no_of_records = len(records)+1
        date = datetime.datetime.now() 
        temp = history.cursor() 
        temp.execute("INSERT INTO {} VALUES(?, ?, ?, ?, ?)".format("user_"+str(account_number_of_sender)), (no_of_records, "Debit", amount, date, comment))
        temp.close()
        history.commit()
        temp = history.cursor()
        temp.execute("SELECT * FROM {}".format("user_"+str(account_number_of_reciever)))
        records = temp.fetchall()
        temp.close()
        no_of_records = len(records)+1
        temp = history.cursor() 
        temp.execute("INSERT INTO {} VALUES(?, ?, ?, ?, ?)".format("user_"+str(account_number_of_reciever)), (no_of_records, "Credit", amount, date, comment))
        temp.close()
        history.commit()
        return redirect("/")
    except:
        return render_template("money_transfer.html", message="Some error occurred. Please try again.")

