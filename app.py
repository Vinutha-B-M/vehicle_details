import os
from flask import (Flask, render_template, request, redirect,
                   make_response, url_for, flash )
import mysql.connector
from itsdangerous import URLSafeTimedSerializer, BadSignature
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_mail import Mail, Message

# from flask_bcrypt import bcrypt

app = Flask(__name__)

app.secret_key = os.urandom(32)  # Generate a random secret key
app.config['SECURITY_PASSWORD_SALT'] = os.urandom(16).hex()  # Generate a random salt value and convert it to hexadecimal

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # or the appropriate port for your mail server
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'manebharat85@gmail.com'
app.config['MAIL_PASSWORD'] = 'YwdMB@93!!'

mail = Mail(app)
# bcrypt = Bcrypt(app)

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="vehicle_details"
)
cursor = cnx.cursor()

users = [{
    "id": "",
    "name":"User1",
    "email": "user@email.com",
    "phone": "987654321",
    "gender": "M",
    "password": "1111",
}]
vehicleDetails = [{}]
serviceDetails = []

@app.route('/')
def index():
    sql = "SELECT * FROM user_details"
    cursor.execute(sql)
    users = cursor.fetchall() # Fetch all user records
    print(users)  # Add this line to check the contents of the users variable
    return render_template("index.html", users=users, page="home")

@app.route("/signup", methods=["GET", "POST"])
def addUser():
    sql = "SELECT count(*) FROM user_details"
    cursor.execute(sql)
    totalusers = cursor.fetchone()[0]
    if request.method == "POST":
        id = int(totalusers + 1)
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phno"]
        gender = request.form["gender"]
        password = request.form["password"]

        sql = "INSERT INTO user_details (id, name, email, phone, gender, password) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (id, name, email, phone, gender, password)
        cursor.execute(sql, values)
        cnx.commit()
        return redirect("/signin")
    else:
        return render_template("signup.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        sql = "SELECT * FROM user_details WHERE email = %s AND password = %s"
        values = (email, password)
        cursor.execute(sql, values)

        user_record = cursor.fetchone()  # Fetch a single matching user record

        if user_record:
            response = make_response(redirect("/"))
            response.set_cookie("user_signedin", "true")
            return response
        else:
            error_message = "Invalid email and/or password"
            return render_template("signin.html", error_message=error_message)

    return render_template("signin.html")

@app.route("/signout", methods=["GET"])
def signout():
    response = make_response(redirect(url_for("signin")))
    response.set_cookie("user_signedin", "", expires=0)  # Clear the cookie by setting an empty value and expiration to the past
    return response

@app.route("/vehicle", methods=["GET", "POST"])
def addVehicleDetails():
    sql = "SELECT count(*) FROM vehicle_details"
    cursor.execute(sql)
    totalvehicles = cursor.fetchone()[0]
    if request.method == "POST":
        id = int(totalvehicles + 1)
        vin = request.form["vin"]
        year = request.form["year"]
        make = request.form["make"]
        model = request.form["model"]
        state = request.form["state"]
        lic = request.form["lic"]
        odometer = request.form["odometer"]
        gvwr = request.form["gvwr"]
        ofcylinder = request.form["ofcylinder"]
        enginegroup = request.form["enginegroup"]
        pcv = request.form["pcv"]
        tailpipe = request.form["tailpipe"]

        sql = "INSERT INTO vehicle_details (id, vin, year, make, model, state, lic_plate, odometer, gvwr, ofcylinder, engine_group, pcv, tail_pipe) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (id, vin, year, make, model, state, lic, odometer, gvwr, ofcylinder, enginegroup, pcv, tailpipe)
        cursor.execute(sql, values)
        cnx.commit()

        sqlq2 = "SELECT * FROM vehicle_details"
        cursor.execute(sqlq2)
        vehicles_details = cursor.fetchall()  # Fetch all user records
        print(vehicles_details)
        return render_template("vehicle.html", vehicleDetails=vehicles_details )
    else:
        return render_template("vehicle.html")

@app.route("/service", methods=["GET", "POST"])
def addServiceDetails():
    sql = "SELECT count(*) FROM service_details"
    cursor.execute(sql)
    totalservice = cursor.fetchone()[0]
    if request.method == "POST":
        id = int(totalservice + 1)
        servicetype = request.form["servicetype"]
        description = request.form["description"]
        amount = request.form["amount"]
        # serviceDetails.append({
        #     "servicetype": servicetype,
        #     "description": description,
        #     "amount": amount,
        # })
        sql = "INSERT INTO service_details (id, service_type, description, amount) VALUES (%s, %s, %s, %s)"
        values = (id, servicetype, description, amount)
        cursor.execute(sql, values)
        cnx.commit()

        sqlq2 = "SELECT * FROM service_details"
        cursor.execute(sqlq2)
        services_details = cursor.fetchall()  # Fetch all user records
        print(services_details)
        return render_template("service.html", serviceDetails=services_details)
    else:
        return  render_template("service.html")

# ======================= generate reset token ================================
#
# def generate_reset_token(email):
#     serializer = URLSafeTimedSerializer(app.secret_key)
#     return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])
#
#
# def send_password_reset_email(email):
#     token = generate_reset_token(email)
#     reset_url = f"http://127.0.0.1:5000/reset_password/{token}"
#     message = f"Click the link below to reset your password: {reset_url}"
#     msg = Message("Password Reset Request", recipients=[email])
#     msg.body = message
#     mail.send(msg)
#
#
# def verify_reset_token(token):
#     serializer = URLSafeTimedSerializer(app.secret_key)
#     try:
#         email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=3600)
#     except BadSignature:
#         return None
#     return email
#
#
# def hash_password(password):
#     hashed_password = generate_password_hash(password)
#     return hashed_password
#
# @app.route('/reset_password/<token>', methods=['GET', 'POST'])
# def reset_password(token):
#     email = verify_reset_token(token)
#     if not email:
#         flash('Invalid or expired token.', 'error')
#         return redirect(url_for('index'))
#     if request.method == 'POST':
#         password = request.form['password']
#         confirm_password = request.form['confirm_password']
#         if password == confirm_password:
#             # Update user's password
#             sql = "UPDATE user_details SET password = %s WHERE email = %s"
#             hashed_password = hash_password(password)
#             values = (hashed_password, email)  # Add email to the values tuple
#             cursor.execute(sql, values)
#             cnx.commit()
#             flash('Your password has been reset successfully.', 'success')
#             return redirect(url_for('signin'))
#         else:
#             flash('Passwords do not match.', 'error')
#     return render_template('reset_password.html', token=token)



if __name__ == '__main__':
    app.run()
