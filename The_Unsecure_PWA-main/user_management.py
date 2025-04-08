# --- Imports --- #
import sqlite3 as sql  # SQLite3 for lightweight DB
import time  # For adding delay (anti-bruteforce / obfuscation)
import random  # For randomness in delay
import bcrypt  # For hashing + verifying passwords


# --- Insert a New User into Database --- #
def insert_user(username, password, DoB):
    con = sql.connect("database_files/database.db")  # Open connection to DB
    cur = con.cursor()  # Get cursor object to execute SQL

    # Insert new user into 'users' table
    cur.execute(
        "INSERT INTO users (username,password,dateOfBirth) VALUES (?,?,?)",
        (username, password, DoB),  # Parameters passed safely (avoids SQLi)
    )

    con.commit()  # Save changes
    con.close()   # Close connection


# --- Validate User Credentials for Login --- #
def retrieve_users(username, password):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()

    # Retrieve hashed password from DB for the given username
    cur.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()  # Get first result

    if row is None:
        con.close()
        return False  # Username not found

    stored_hashed_password = row[0]  # Extract hashed pw from result tuple

    # Check input password against stored hashed pw using bcrypt
    if bcrypt.checkpw(password, stored_hashed_password):
        # If password is correct, increment visitor log (stored in a text file lol)
        with open("visitor_log.txt", "r") as file:
            number = int(file.read().strip())
            number += 1  # Increment visitor count
        with open("visitor_log.txt", "w") as file:
            file.write(str(number))

        # Add delay (80ms to 90ms) — can be used to slow down attackers
        time.sleep(random.randint(80, 90) / 1000)

        con.close()
        return True  # Successful login
    else:
        con.close()
        return False  # Incorrect password


# --- Insert Feedback into Database --- #
def insert_feedback(feedback):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()

    # Filter input to only allow numbers (lol wtf) — removes all non-numeric chars
    f = filter(str.isdecimal, feedback)
    s1 = "".join(f)  # Join the filtered characters back into a string
    print(s1)  # Debug print for logging

    # BAD PRACTICE: Directly formatting SQL query (possible SQL Injection if filter fails)
    cur.execute("INSERT INTO feedback (feedback) VALUES (?)", (feedback,))
    con.commit()
    con.close()


# --- Generate Partial HTML of Feedback Entries --- #
def list_feedback():
    con = sql.connect("database_files/database.db")
    cur = con.cursor()

    # Fetch all feedback entries
    data = cur.execute("SELECT * FROM feedback").fetchall()
    con.close()

    # Overwrite the feedback partial HTML
    f = open("templates/partials/success_feedback.html", "w")
    for row in data:
        f.write("<p>\n")
        f.write(f"{row[1]}\n")  # row[1] is the feedback text
        f.write("</p>\n")
    f.write("</html>")
    f.close()
