from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
import os
from datetime import datetime
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key_123"

UPLOAD_FOLDER = "uploads"
KEY_FILE = "secret.key"
HASH_FILE = "hashes.txt"
LOG_FILE = "logs.txt"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create or load encryption key
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()

    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)

else:
    with open(KEY_FILE, "rb") as key_file:
        key = key_file.read()

cipher = Fernet(key)

# Demo users for testing
users = {
    "admin": {
        "password": generate_password_hash("admin123"),
        "role": "Admin"
    },

    "investigator": {
        "password": generate_password_hash("invest123"),
        "role": "Investigator"
    }
}


# Save logs
def log_action(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{time}] {message}\n")


# Start page
@app.route("/")
def start():
    return redirect(url_for("login"))


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():

    error = ""

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = users.get(username)

        if user and check_password_hash(user["password"], password):

            session["username"] = username
            session["role"] = user["role"]

            log_action(f"User {username} logged in as {user['role']}")

            return redirect(url_for("home"))

        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


# Logout
@app.route("/logout")
def logout():

    username = session.get("username", "Unknown")

    log_action(f"User {username} logged out")

    session.clear()

    return redirect(url_for("login"))


# Home page
@app.route("/home", methods=["GET", "POST"])
def home():

    if "username" not in session:
        return redirect(url_for("login"))

    message = ""
    hash_value = ""
    filename = ""
    encrypted_filename = ""
    results = []

    if request.method == "POST":

        action = request.form.get("action")

        # Upload file
        if action == "upload":

            file = request.files.get("file")

            if file and file.filename != "":

                file_data = file.read()

                hash_value = hashlib.sha256(file_data).hexdigest()

                existing = False

                if os.path.exists(HASH_FILE):

                    with open(HASH_FILE, "r", encoding="utf-8") as f:

                        for line in f:

                            line = line.strip()

                            if not line or "|" not in line:
                                continue

                            saved_name = line.split("|", 1)[0]

                            if file.filename == saved_name:
                                existing = True
                                break

                if not existing:

                    with open(HASH_FILE, "a", encoding="utf-8") as f:
                        f.write(file.filename + "|" + hash_value + "\n")

                encrypted_data = cipher.encrypt(file_data)

                encrypted_filename = file.filename + ".enc"

                filepath = os.path.join(UPLOAD_FOLDER, encrypted_filename)

                with open(filepath, "wb") as f:
                    f.write(encrypted_data)

                filename = file.filename

                message = "File uploaded and encrypted successfully! 🔐"

                log_action(
                    f"User {session['username']} uploaded file {file.filename}"
                )

            else:
                message = "Please select a file first."

        # Check integrity
        elif action == "check":

            if os.path.exists(HASH_FILE):

                with open(HASH_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                for line in lines:

                    line = line.strip()

                    if not line or "|" not in line:
                        continue

                    saved_filename, old_hash = line.split("|", 1)

                    encrypted_file = saved_filename + ".enc"

                    filepath = os.path.join(
                        UPLOAD_FOLDER,
                        encrypted_file
                    )

                    if os.path.exists(filepath):

                        with open(filepath, "rb") as file:
                            encrypted_data = file.read()

                        try:
                            decrypted_data = cipher.decrypt(encrypted_data)

                            new_hash = hashlib.sha256(
                                decrypted_data
                            ).hexdigest()

                            if new_hash == old_hash:
                                status = "✅ Valid Evidence"

                            else:
                                status = "❌ Tampered Evidence"

                        except:
                            status = "❌ Cannot Decrypt File"

                    else:
                        status = "❌ File Missing"

                    results.append((saved_filename, status))

                log_action(
                    f"User {session['username']} checked evidence integrity"
                )

            else:
                message = "No evidence records found."

    return render_template(
        "index.html",
        message=message,
        hash_value=hash_value,
        filename=filename,
        encrypted_filename=encrypted_filename,
        results=results,
        username=session.get("username"),
        role=session.get("role")
    )


# Logs page (Admin only)
@app.route("/logs")
def view_logs():

    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Admin":
        return "Access Denied: Admin only"

    if os.path.exists(LOG_FILE):

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.readlines()

    else:
        logs = []

    return render_template("logs.html", logs=logs)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)