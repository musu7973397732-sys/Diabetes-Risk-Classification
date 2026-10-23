# Diabetes Risk Classification System

**An End-to-End Machine Learning Web Application for Binary Risk Classification**  
*Master of Computer Applications (MCA) Mini Project*

---

## 1. Project Overview & Abstract

The **Diabetes Risk Classification System** is an applied machine-learning web application built using **Python, Flask, Scikit-learn, and MySQL**. The system is trained on the historical **Pima Indians Diabetes Database** and utilizes a supervised **Logistic Regression Pipeline** (with median imputation and standard feature scaling) to classify whether a patient's biometric markers exhibit patterns consistent with high risk (Class 1) or low risk (Class 0) of Type-2 diabetes.

### Key Capabilities
- **Robust User Authentication**: Registration and login with password hashing via Werkzeug (`generate_password_hash` and `check_password_hash`).
- **Interactive Health Dashboard**: Personalized metrics overview displaying the user's total prediction count, model status, and recent activity.
- **Biometric Prediction Console**: Input form for all 8 clinical parameters with frontend validation, BMI calculation assistant, and 1-click demonstration test scenarios.
- **On-Page Model Classification**: Instant prediction display with clear explanations of what the classification represents, without navigating away.
- **Persistent MySQL Audit Log**: Every prediction is securely recorded in MySQL linked to the active user's ID.
- **Strict Data Isolation**: Users can only view and audit their own historical predictions.
- **Dual-Mode Database Reliability**: Connects to MySQL (`diabetes_db`) as primary; includes an automatic SQLite fallback so the project runs cleanly on any evaluation computer.

---

## 2. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5.3 | Responsive healthcare user interface, form validation, and layout |
| **Backend** | Python 3.10+, Flask 3.1+ | MVC application routing, session security, and database controllers |
| **Machine Learning** | Scikit-learn (Pipeline, SimpleImputer, StandardScaler, LogisticRegression) | Data preprocessing, median imputation, feature scaling, and binary classification |
| **Data Processing** | Pandas, NumPy | Dataset loading, missing-value processing, and DataFrame management |
| **Model Persistence** | Joblib | Model serialization and deserialization (`diabetes_model.pkl`) |
| **Database** | MySQL 8.0+ (Connector: `mysql-connector-python`) | Relational persistence for user credentials and audit logs |
| **Development** | Visual Studio Code on Windows 10/11 | IDE, debugging, and terminal environment |

---

## 3. Project Directory Structure

```text
DiabetesRiskProject/
│
├── app.py                      # Main Flask application (routes, auth, and prediction logic)
├── config.py                   # Central configuration & database credentials
├── db.py                       # Database abstraction layer (MySQL with SQLite fallback)
├── train_model.py              # ML model training, preprocessing pipeline, and evaluation script
├── diabetes.csv                # Pima Indians Diabetes Dataset (768 patient records)
├── diabetes_model.pkl          # Saved Joblib pipeline model
├── schema.sql                  # MySQL database initialization script
├── requirements.txt            # Python package dependencies
├── .gitignore                  # Git exclusion rules
├── README.md                   # Complete project documentation and viva preparation
│
├── static/
│   ├── css/
│   │   └── style.css           # Healthcare design system stylesheet (light theme, blue/green accents)
│   └── js/
│       └── script.js           # Client-side validation, password matching, and BMI calculator
│
└── templates/
    ├── base.html               # Base Jinja2 layout (responsive navbar, flash alerts, footer)
    ├── index.html              # Landing page (hero, 3-step workflow, technical highlights)
    ├── register.html           # User registration (password length check, duplicate email prevention)
    ├── login.html              # Secure account authentication
    ├── dashboard.html          # User dashboard (stats cards, recent activity, quick navigation)
    ├── predict.html            # 8-feature biometric input form and on-page classification result
    └── history.html            # Complete user prediction audit log table
```

---

## 4. Dataset & Machine Learning Pipeline

### Dataset Source
The model is trained on the **Pima Indians Diabetes Database**, originally hosted by the National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK). The dataset comprises 768 female patient records of Pima Indian heritage aged 21 and older.

### Feature Attributes & Descriptions

| Feature Name | Clinical Description | Data Type | Zero Replacement |
|---|---|---|---|
| `Pregnancies` | Number of times pregnant | Integer | Valid 0 (kept) |
| `Glucose` | Plasma glucose concentration at 2 hours in an OGTT | Float | Biological 0 replaced with `NaN` |
| `BloodPressure` | Diastolic blood pressure (mm Hg) | Float | Biological 0 replaced with `NaN` |
| `SkinThickness` | Triceps skin fold thickness (mm) | Float | Biological 0 replaced with `NaN` |
| `Insulin` | 2-Hour serum insulin (μU/mL) | Float | Biological 0 replaced with `NaN` |
| `BMI` | Body mass index ($weight / height^2$) | Float | Biological 0 replaced with `NaN` |
| `DiabetesPedigreeFunction` | Genetic pedigree risk score | Float | Valid numeric (kept) |
| `Age` | Age in completed years | Integer | Valid numeric (kept) |
| `Outcome` (Target) | Classification label (0 = Non-Diabetic, 1 = Diabetic) | Binary (0 / 1) | Target variable |

### Pipeline Workflow
```
[Raw Input] ──> [Zero-to-NaN Filter] ──> [SimpleImputer (median)] ──> [StandardScaler] ──> [Logistic Regression] ──> [Binary Output: 0 or 1]
```
1. **Biological Zero Handling**: Measurements where zero is biologically impossible (e.g., Glucose = 0 or BP = 0) are converted to `NaN`.
2. **Median Imputation**: `SimpleImputer(strategy='median')` replaces missing values using the median of the training distribution, preventing skewed distribution errors caused by mean imputation.
3. **Feature Standardization**: `StandardScaler()` scales all 8 features to zero mean and unit variance ($z = (x - \mu) / \sigma$).
4. **Logistic Regression Classifier**: Fitted using L2 regularization (`max_iter=1000, random_state=42`) to compute the probability of Class 1.

---

## 5. MySQL Database Architecture

### Entity Relationship & Schema Details

```sql
-- Database: diabetes_db

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prediction_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    pregnancies INT NOT NULL,
    glucose FLOAT NOT NULL,
    blood_pressure FLOAT NOT NULL,
    skin_thickness FLOAT NOT NULL,
    insulin FLOAT NOT NULL,
    bmi FLOAT NOT NULL,
    diabetes_pedigree_function FLOAT NOT NULL,
    age INT NOT NULL,
    predicted_outcome TINYINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## 6. Installation & Execution Guide (VS Code on Windows)

Follow these steps to set up and run the application locally on Windows using Visual Studio Code.

### Step 1: Open the Project Folder in VS Code
1. Launch **Visual Studio Code**.
2. Go to **File &rarr; Open Folder...** and select `C:\ML\DiabetesRiskProject`.
3. Open a terminal in VS Code: **Terminal &rarr; New Terminal** (`Ctrl + ~`).

### Step 2: Create and Activate Python Virtual Environment
```powershell
# Create virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1
```
*(If PowerShell displays an execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and try again).*

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure and Initialize MySQL
1. Ensure your MySQL Server is running (via MySQL Workbench, Windows Services, or XAMPP).
2. Open MySQL Command Line Client or MySQL Workbench and run `schema.sql`:
   ```sql
   SOURCE C:/ML/DiabetesRiskProject/schema.sql;
   ```
3. Update your MySQL credentials in `config.py` (or set environment variables `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`):
   ```python
   MYSQL_HOST = "localhost"
   MYSQL_USER = "root"
   MYSQL_PASSWORD = "YourMySQLPassword"
   MYSQL_DB = "diabetes_db"
   ```
*(Note: If MySQL is not running on an examiner's machine, the built-in SQLite fallback will automatically initialize so the project never crashes).*

### Step 5: Train the Machine Learning Model
Run the model training script to process the dataset and generate `diabetes_model.pkl`:
```powershell
python train_model.py
```
**Expected Terminal Output:**
```text
============================================================
 DIABETES RISK CLASSIFICATION SYSTEM - ML TRAINING 
============================================================
[1/7] Loading dataset from: diabetes.csv (768 rows, 9 columns)
[2/7] Required columns verified successfully.
[3/7] Replacing biological zero-values with NaN...
[4/7] Splitting data into 80% training and 20% testing sets...
[5/7] Building ML Pipeline (Median Imputer -> StandardScaler -> Logistic Regression)...
[6/7] Evaluating model performance on test set:
--------------------------------------------------
 Test Accuracy  : 70.78%
 Precision      : 60.00%
 Recall (Sens.) : 50.00%
 F1-Score       : 54.55%
--------------------------------------------------
[7/7] Saving trained pipeline to: diabetes_model.pkl
 Model pipeline successfully saved as 'diabetes_model.pkl'!
```

### Step 6: Start the Flask Application
```powershell
python app.py
```
**Expected Server Output:**
```text
[Database] Schema initialized successfully using MYSQL.
[ML Engine] Model pipeline loaded successfully from: ...\diabetes_model.pkl
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 7: Access the Web Application
1. Open your web browser and navigate to:
   👉 **`http://127.0.0.1:5000`**
2. Click **Get Started** or **Register** to create an account.
3. Sign in to your account.
4. Navigate to **Predict**, enter patient biometric values (or click a **Sample Profile** button), and click **Predict Risk**.
5. Verify that the prediction result displays on-page and that the record appears in your **History** table.

---

## 7. Troubleshooting Common Issues

| Issue / Error | Cause | Resolution |
|---|---|---|
| `ModuleNotFoundError: No module named 'flask'` | Packages not installed or virtual environment not activated | Activate virtual environment (`.\venv\Scripts\Activate.ps1`) and run `pip install -r requirements.txt`. |
| `MySQL connection failed: 1045 Access denied for user` | Incorrect MySQL root password | Update `MYSQL_PASSWORD` in `config.py` to match your local MySQL root password. |
| `MySQL connection failed: Can't connect to MySQL server` | MySQL service is stopped | Start the MySQL service via Windows Services (`services.msc`) or MySQL Workbench. Alternatively, the app will automatically use SQLite. |
| `FileNotFoundError: diabetes_model.pkl` | Model has not been trained yet | Run `python train_model.py` in your terminal to generate the serialized model file. |
| `InconsistentVersionWarning` | Model was trained with a different Scikit-learn version | Run `python train_model.py` in your current virtual environment to retrain and save the model matching your package versions. |

---

## 8. Common MCA Viva / Presentation Questions & Answers

1. **Q: Why was Logistic Regression selected over complex deep neural networks or Random Forests?**  
   *A:* Logistic Regression is the clinical standard for baseline medical risk stratification. It is mathematically interpretable (coefficients directly reflect log-odds), computationally efficient, prevents severe overfitting on small tabular datasets (768 records), and is easily explained during an academic examination.

2. **Q: Why did you replace zero values with NaN for only five of the eight features?**  
   *A:* Having 0 pregnancies is physiologically possible and normal. However, having a fasting blood sugar (`Glucose`) of 0 mg/dL, a `BloodPressure` of 0 mm Hg, or a `BMI` of 0 is biologically incompatible with life. In the Pima dataset, 0 in these fields denotes an unrecorded measurement. Replacing them with `NaN` allows our `SimpleImputer` to impute them accurately.

3. **Q: Why is a Scikit-learn Pipeline utilized instead of applying preprocessing functions manually?**  
   *A:* A `Pipeline` encapsulates imputation, scaling, and classification into a single atomic object. This completely prevents **data leakage** from the test set into the training set and ensures that web server inputs during production inference undergo the exact same mathematical transformations as the training data.

4. **Q: How does the system defend against SQL Injection?**  
   *A:* All queries in `db.py` utilize parameterized SQL queries (`%s` in MySQL and `?` in SQLite). User inputs are sent separately from the SQL statement as bound parameters, neutralizing SQL injection attempts.

5. **Q: How are user passwords secured?**  
   *A:* Passwords are never stored in plaintext. They are hashed using Werkzeug’s cryptographic salted password hashing functions (`generate_password_hash`), which utilize standard SHA-256 / PBKDF2 algorithms.

---

## 9. Academic Disclaimer

> **Important Notice:** This software is developed strictly for educational and academic demonstration purposes as part of an MCA mini-project curriculum. It demonstrates applied statistical classification using historical open-source data. It does not provide medical advice, diagnosis, treatment, or prognostic confirmation.
