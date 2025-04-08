# --- Imports --- #
from flask import Flask, render_template, request, redirect
from flask_limiter import Limiter  # Rate limiting lib
from flask_limiter.util import get_remote_address  # Used to get client's IP
import bcrypt  # For password hashing
from flask_wtf.csrf import CSRFProtect  # CSRF protection lib
import user_management as dbHandler  # Your custom DB module


# --- Flask App Initialization --- #
app = Flask(__name__)

# --- Rate Limiter Setup --- #
limiter = Limiter(
    get_remote_address,  # Identifies users by IP
    app=app,  # Bind to Flask app
    default_limits=["200 per day", "50 per hour"]  # Global limit for ALL routes (optional)
)

# --- Secret Key Required for CSRF + Sessions --- #
app.secret_key = b'_5ddfas$%34qrf/fda,.l'  # Keep this safe IRL

# --- Enable CSRF Protection Globally --- #
csrf = CSRFProtect(app)  # Every POST, PUT, PATCH now needs {{ csrf_token() }} in forms


# --- Feedback Route (Handles Feedback Submission) --- #
@app.route("/success.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def add_feedback():
    # Handle Redirect Injection (Very basic check)
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)  # Redirect user

    if request.method == "POST":
        feedback = request.form["feedback"]
        dbHandler.insert_feedback(feedback)  # Save feedback to DB
        dbHandler.list_feedback()  # Print/Display feedback (maybe for admin)
        return render_template("/success.html", state=True, value="Back")

    # Handle other methods (mostly GET)
    dbHandler.list_feedback()
    return render_template("/success.html", state=True, value="Back")


# --- Signup/Register Route --- #
@app.route("/signup.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def signup():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)

    if request.method == "POST":
        # Grab data from form
        username = request.form["username"]
        password = request.form["password"].encode('utf-8')  # Hashing needs bytes
        DoB = request.form["dob"]

        # Generate Salt + Hash Password (15 rounds is strong)
        salt = bcrypt.gensalt(rounds=15)
        hashed_password = bcrypt.hashpw(password, salt)

        # Store New User in DB
        dbHandler.insert_user(username, hashed_password, DoB)

        return render_template("/index.html")  # Redirect to Login

    return render_template("/signup.html")  # Show Signup Page


# --- Login/Home Route --- #
@app.route("/index.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@app.route("/", methods=["POST", "GET"])
@limiter.limit("2 per minute", methods=["POST"])  # Bruteforce Protection: 2 Login attempts per minute per IP
def home():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode('utf-8')  # bcrypt needs bytes

        # Check User Credentials
        isLoggedIn = dbHandler.retrieve_users(username, password)

        if isLoggedIn:
            dbHandler.list_feedback()
            return render_template("/success.html", value=username, state=isLoggedIn)
        else:
            return render_template("/index.html")  # Login Failed

    return render_template("/index.html")  # Show Login Page


# --- Flask App Runner --- #
if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True  # Auto-reload templates on changes
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0  # Disable caching for static files
    app.run(debug=True, host="0.0.0.0", port=5000)  # Run server on all interfaces
