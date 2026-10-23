"""
Diabetes Risk Classification System - Flask Application Controller
Author: MCA Mini Project
Technology Stack: Python, Flask, Scikit-learn, Pandas, MySQL, Bootstrap 5
"""

import sys
import os

# Auto-switch to project virtual environment if launched with system Python on Windows
_venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
if os.path.exists(_venv_python) and os.path.normcase(sys.executable) != os.path.normcase(_venv_python):
    import subprocess
    sys.exit(subprocess.call([_venv_python, os.path.abspath(__file__)] + sys.argv[1:]))

from datetime import datetime
from functools import wraps
import joblib
import pandas as pd
import numpy as np
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
import db

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Database Schema on Application Startup
db.init_db()

# Load Saved Machine Learning Model Pipeline
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diabetes_model.pkl")
try:
    model = joblib.load(MODEL_PATH)
    print(f"[ML Engine] Model pipeline loaded successfully from: {MODEL_PATH}")
except Exception as e:
    model = None
    print(f"[ML Engine Error] Could not load model pipeline: {e}")

# Exact 8 Feature Column Names required by the Scikit-learn pipeline
FEATURE_COLUMNS = [
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age"
]

def login_required(f):
    """
    Decorator to protect routes from unauthorized access.
    Redirects unauthenticated users to the login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ==============================================================
# Public Routes: Landing, Authentication & Documentation
# ==============================================================

@app.route("/")
def home():
    """Landing / Home page explaining the system and workflow."""
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles new user registration with password validation and hashing."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # 1. Validate Required Fields
        if not name or not email or not password or not confirm_password:
            flash("All fields are required. Please fill in all fields.", "danger")
            return render_template("register.html")

        # 2. Check Password Length
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return render_template("register.html")

        # 3. Check Password Confirmation
        if password != confirm_password:
            flash("Passwords do not match. Please verify your password.", "danger")
            return render_template("register.html")

        # 4. Hash Password and Insert into MySQL
        hashed_password = generate_password_hash(password)
        success, error_code = db.insert_user(name, email, hashed_password)

        if success:
            flash("Registration successful! You may now sign in.", "success")
            return redirect(url_for("login"))
        elif error_code == "DUPLICATE_EMAIL":
            flash("An account with this email address already exists. Please login instead.", "danger")
            return render_template("register.html")
        else:
            flash("Registration failed due to a database error. Please try again.", "danger")
            return render_template("register.html")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user authentication and session creation."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template("login.html")

        user = db.find_user_by_email(email)
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password. Please verify your credentials.", "danger")
            return render_template("login.html")

    return render_template("login.html")

@app.route("/logout")
def logout():
    """Clears user session and redirects to the login screen."""
    session.clear()
    flash("You have been successfully signed out.", "info")
    return redirect(url_for("login"))

# ==============================================================
# Authenticated Routes: Dashboard, Prediction & History
# ==============================================================

@app.route("/dashboard")
@login_required
def dashboard():
    """Displays user overview statistics and recent prediction history."""
    user_id = session["user_id"]
    prediction_count = db.get_user_prediction_count(user_id)
    recent_history = db.get_user_predictions(user_id, limit=5)

    return render_template(
        "dashboard.html",
        user_name=session.get("user_name"),
        prediction_count=prediction_count,
        history=recent_history
    )

@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict_page():
    """
    Renders the biometric prediction form and evaluates machine learning classification.
    Displays the prediction result on the same page.
    """
    prediction_result = None

    if request.method == "POST":
        # 1. Ensure Model Is Loaded
        if model is None:
            flash("The ML model is not currently available. Please verify that 'diabetes_model.pkl' exists.", "danger")
            return render_template("predict.html", prediction_result=None)

        # 2. Extract and Validate Numerical Input Fields
        try:
            pregnancies = int(request.form.get("pregnancies", 0))
            glucose = float(request.form.get("glucose", 0))
            blood_pressure = float(request.form.get("blood_pressure", 0))
            skin_thickness = float(request.form.get("skin_thickness", 0))
            insulin = float(request.form.get("insulin", 0))
            bmi = float(request.form.get("bmi", 0))
            dpf = float(request.form.get("diabetes_pedigree_function", 0))
            age = int(request.form.get("age", 0))
        except (ValueError, TypeError):
            flash("Invalid input format. Please enter valid numeric values for all features.", "danger")
            return render_template("predict.html", prediction_result=None)

        # 3. Server-side Range Constraints
        if glucose <= 0 or blood_pressure < 0 or bmi <= 0 or age <= 0:
            flash("Glucose, BMI, and Age must be greater than zero.", "danger")
            return render_template("predict.html", prediction_result=None)

        # 4. Construct DataFrame Matching Training Columns
        input_df = pd.DataFrame([[
            pregnancies,
            glucose,
            blood_pressure,
            skin_thickness,
            insulin,
            bmi,
            dpf,
            age
        ]], columns=FEATURE_COLUMNS)

        # Replace biological zeroes with NaN for median imputation (matching train_model.py)
        zero_as_missing = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
        input_df[zero_as_missing] = input_df[zero_as_missing].replace(0, np.nan)

        # 5. Run Model Prediction
        try:
            predicted_outcome = int(model.predict(input_df)[0])
        except Exception as e:
            app.logger.exception("Inference failed")
            flash(f"Machine learning inference error: {e}", "danger")
            return render_template("predict.html", prediction_result=None)

        # 6. Save Prediction Record in MySQL for the Logged-in User
        user_id = session["user_id"]
        db.insert_prediction(
            user_id=user_id,
            pregnancies=pregnancies,
            glucose=glucose,
            blood_pressure=blood_pressure,
            skin_thickness=skin_thickness,
            insulin=insulin,
            bmi=bmi,
            dpf=dpf,
            age=age,
            predicted_outcome=predicted_outcome
        )

        prediction_result = {
            "outcome": predicted_outcome,
            "timestamp": datetime.now().strftime("%B %d, %Y at %I:%M %p")
        }

    return render_template("predict.html", prediction_result=prediction_result)

@app.route("/history")
@login_required
def history_page():
    """Displays the complete historical log of predictions for the active user."""
    user_id = session["user_id"]
    user_records = db.get_user_predictions(user_id, limit=100)

    return render_template(
        "history.html",
        history=user_records,
        user_name=session.get("user_name")
    )

# ==============================================================
# Entry Point
# ==============================================================
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=Config.DEBUG)
