from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import user_management as dbHandler
import pyotp
import pyqrcode
import os
import base64
from io import BytesIO




# Code snippet for logging a message
# app.logger.critical("message")
app = Flask(__name__)
app.secret_key = 'my_secret_key'
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]  # Global limits (optional)
)


@app.route("/success.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def add_feedback():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        feedback = request.form["feedback"]
        dbHandler.insert_feedback(feedback)
        dbHandler.list_feedback()
        return render_template("/success.html", state=True, value="Back")
    else:
        dbHandler.list_feedback()
        return render_template("/success.html", state=True, value="Back")


@app.route("/signup.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def signup():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        DoB = request.form["dob"]
        dbHandler.insert_user(username, password, DoB)
        return render_template("/index.html")
    else:
        return render_template("/signup.html")


@app.route("/index.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@app.route("/", methods=["POST", "GET"])
@limiter.limit("2 per minute", methods=["POST"])  # 👈 Limits login attempts to # per minute per IP
def home():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        otp_input = request.form['otp']
        username = request.form["username"]
        password = request.form["password"]
        isLoggedIn = dbHandler.retrieve_users(username, password)
         if totp.verify(otp_input):
            return redirect(url_for('home'))
        #return redirect(url_for('home'))  
        # Redirect to home if OTP is valid
        else:
            return "Invalid OTP. Please try again.", 401
            
        if isLoggedIn:
            dbHandler.list_feedback()
            return render_template("/success.html", value=username, state=isLoggedIn)
        else:
            return render_template("/index.html")
    else:
        return render_template("/index.html")

user_secret = pyotp.random_base32()
totp = pyotp.TOTP(user_secret)
otp_uri = totp.provisioning_uri(name="username",issuer_name="YourAppName")
qr_code = pyqrcode.create(otp_uri)
stream = BytesIO()
qr_code.png(stream, scale=5)
qr_code_b64 = base64.b64encode(stream.getvalue()).decode('utf-8')
otp_input = request.form['otp']

if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="0.0.0.0", port=5000)
    
