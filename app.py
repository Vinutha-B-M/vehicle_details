import os
from flask import (Flask, render_template, request, redirect,
                   make_response, url_for, flash )
import mysql.connector
from flask_mail import Mail,Message
import redis, jwt, datetime
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

app = Flask(__name__)

app.secret_key = os.urandom(32)  # Generate a random secret key
app.config['SECURITY_PASSWORD_SALT'] = os.urandom(16).hex()  # Generate a random salt value and convert it to hexadecimal

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # or the appropriate port for your mail server
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'bmvinutha21@gmail.com'
app.config['MAIL_PASSWORD'] = 'zkvssqgeidvjbeem'
app.config['MAIL_DEFAULT_SENDER'] = 'manebharat85@gmail.com'

mail = Mail(app)


# Configure Redis connection
redis_host = 'localhost'
redis_port = 6379
redis_db = 0
redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)


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
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phno"]
        gender = request.form["gender"]
        password = request.form["password"]

        # Check if the email already exists
        sql_check_email = "SELECT COUNT(*) FROM user_details WHERE email = %s"
        values_check_email = (email,)
        cursor.execute(sql_check_email, values_check_email)
        count_email = cursor.fetchone()[0]
        if count_email > 0:
            # Email already exists, display an error message
            flash("Email already exists. Please use a different email.")
            return redirect("/signup")

        # Insert the new user into the database
        sql_insert = "INSERT INTO user_details (name, email, phone, gender, password) VALUES (%s, %s, %s, %s, %s)"
        values_insert = (name, email, phone, gender, password)
        cursor.execute(sql_insert, values_insert)
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
    if request.method == "POST":
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

        sql = "INSERT INTO vehicle_details (vin, year, make, model, state, lic_plate, odometer, gvwr, ofcylinder, engine_group, pcv, tail_pipe) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (vin, year, make, model, state, lic, odometer, gvwr, ofcylinder, enginegroup, pcv, tailpipe)
        cursor.execute(sql, values)
        cnx.commit()

    sqlq2 = "SELECT * FROM vehicle_details"
    cursor.execute(sqlq2)
    vehicle_details = cursor.fetchall()  # Fetch all vehicle records
    print(vehicle_details)
    return render_template("vehicle.html", vehicleDetails=vehicle_details)

@app.route("/delete_vehicle/<int:vehicle_id>", methods=["POST"])
def deleteVehicle(vehicle_id):
    if request.method == "POST":
        sql = "DELETE FROM vehicle_details WHERE id = %s"
        values = (vehicle_id,)
        cursor.execute(sql, values)
        cnx.commit()
        return redirect("/vehicle")

@app.route("/service", methods=["GET", "POST"])
def addServiceDetails():
    if request.method == "POST":
        servicetype = request.form["servicetype"]
        description = request.form["description"]
        amount = request.form["amount"]

        # Check if a similar service already exists
        sql_check = "SELECT COUNT(*) FROM service_details WHERE service_type = %s AND description = %s AND amount = %s"
        values_check = (servicetype, description, amount)
        cursor.execute(sql_check, values_check)
        count = cursor.fetchone()[0]
        if count > 0:
            # Service already exists, do not insert duplicate
            flash("Service already exists!")
        else:
            # Insert the new service into the database
            sql_insert = "INSERT INTO service_details (service_type, description, amount) VALUES (%s, %s, %s)"
            values_insert = (servicetype, description, amount)
            cursor.execute(sql_insert, values_insert)
            cnx.commit()

    # Fetch all service records
    sql_select = "SELECT * FROM service_details"
    cursor.execute(sql_select)
    service_details = cursor.fetchall()

    return render_template("service.html", serviceDetails=service_details)

@app.route("/delete_service/<int:service_id>", methods=["POST"])
def deleteService(service_id):
    if request.method == "POST":
        sql = "DELETE FROM service_details WHERE id = %s"
        values = (service_id,)
        cursor.execute(sql, values)
        cnx.commit()
        return redirect("/service")

@app.route("/delete_user/<int:user_id>", methods=["GET", "POST"])
def delete_user(user_id):
    if request.method == "POST":
        sql = "DELETE FROM user_details WHERE id = %s"
        values = (user_id,)
        cursor.execute(sql, values)
        cnx.commit()
        return redirect("/")
    else:
        sql = "SELECT * FROM user_details WHERE id = %s"
        values = (user_id,)
        cursor.execute(sql, values)
        user = cursor.fetchone()
        if user:
            return render_template("delete_user.html", user=user)
        else:
            return "User not found"


# ======================= generate reset token ================================

def generate_token():
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    payload = {
        'some': 'payload',
        'exp': expiration_time.timestamp()  # Encode the expiration time as a UNIX timestamp
    }
    token = jwt.encode(payload, app.secret_key, algorithm='HS256')
    print(token)
    return token

def send_password_reset_email(email, reset_link):
    subject = "Password Reset Request"
    body = f"Click the link below to reset your password:\n\n{reset_link}"
    msg = Message(subject=subject, recipients=[email], body=body)

    try:
        mail.send(msg)
        print("Password reset email sent successfully.")
    except Exception as e:
        print("Error sending password reset email:", str(e))

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form["email"]

        # Generate a password reset token
        token = generate_token()  # Replace with your token generation logic

        print("decoded token", token)
        # Store the token in Redis with an expiration time
        redis_key = f"reset_token:{email}"
        redis_client.set(redis_key, token, ex=3600)  # Set the expiration time to 1 hour (3600 seconds)

        # Create the password reset link
        reset_link = url_for('reset_password_token', token=token, _external=True)

        # Send the password reset email
        send_password_reset_email(email, reset_link)

        # Redirect the user to a page indicating that an email has been sent
        return render_template("reset_password_email_sent.html", email=email)

    return render_template("reset_password.html")


def verify_token(email, token):
    # Retrieve the token from Redis
    redis_key = f"reset_token:{email}"
    stored_token = redis_client.get(redis_key)

    # Check if the stored token exists and matches the provided token
    if stored_token and stored_token.decode('utf-8') == token:
        return True

    return False


def get_email_from_token(token):
    try:
        payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        email = payload.get('email')
        expiration_time = payload.get('exp')

        # Check if the token has expired
        if expiration_time is not None:
            current_time = datetime.datetime.utcnow()
            if current_time > datetime.datetime.fromtimestamp(expiration_time):
                raise Exception("Token has expired.")

        return email
    except jwt.ExpiredSignatureError:
        # Handle token expiration error
        raise Exception("Token has expired.")
    except jwt.InvalidTokenError:
        # Handle invalid token error
        raise Exception("Invalid token.")


def update_password(email, new_password):
    sql = "UPDATE user_details SET password = %s WHERE email = %s"
    values = (new_password, email)
    cursor.execute(sql, values)
    cursor.close()

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password_token(token):
    email = get_email_from_token(token)  # Replace with your logic to extract the email from the token

    # Verify the token and email
    if not verify_token(email, token):
        error_message = "Invalid or expired password reset link."
        return render_template("reset_password_error.html", error_message=error_message)

    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password == confirm_password:
            # Update the user's password in the database
            update_password(email, password)  # Replace with your logic to update the password

            # Delete the token from Redis
            redis_key = f"reset_token:{email}"
            redis_client.delete(redis_key)

            # Display a success message or redirect the user to a success page
            return render_template("password_reset_success.html")
        else:
            error_message = "Password and Confirm Password do not match"
            return render_template("reset_password_token.html", error_message=error_message)

    return render_template("reset_password_token.html")

if __name__ == '__main__':
    app.run()
