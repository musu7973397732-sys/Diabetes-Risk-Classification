"""
Diabetes Risk Classification System - Model Training Script
Dataset: Pima Indians Diabetes Database
Pipeline: SimpleImputer (median) -> StandardScaler -> Logistic Regression
"""

import os
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

def train_and_evaluate_model():
    dataset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diabetes.csv")
    model_output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diabetes_model.pkl")

    print("=" * 60)
    print(" DIABETES RISK CLASSIFICATION SYSTEM - ML TRAINING ")
    print("=" * 60)

    # 1. Verify Dataset Existence
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(
            f"Dataset not found at {dataset_path}. Please place 'diabetes.csv' (Pima Indians Diabetes Dataset) in the project directory."
        )

    print(f"\n[1/7] Loading dataset from: {dataset_path}")
    data = pd.read_csv(dataset_path)
    print(f"      Dataset successfully loaded: {data.shape[0]} rows, {data.shape[1]} columns.")

    # 2. Check Required Columns
    expected_features = [
        "Pregnancies",
        "Glucose",
        "BloodPressure",
        "SkinThickness",
        "Insulin",
        "BMI",
        "DiabetesPedigreeFunction",
        "Age"
    ]
    target_column = "Outcome"

    missing_cols = [c for c in expected_features + [target_column] if c not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in dataset: {missing_cols}")

    print("[2/7] Required columns verified successfully.")

    # 3. Separate Input Features (X) and Target Label (y)
    X = data[expected_features].copy()
    y = data[target_column].copy()

    # 4. Handle Biological Zeroes
    # In clinical measurements, a value of 0 for Glucose, BloodPressure, SkinThickness,
    # Insulin, and BMI represents missing/unrecorded observations rather than true physiological 0.
    zero_as_missing = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
    print(f"[3/7] Replacing biological zero-values with NaN for: {', '.join(zero_as_missing)}")
    X[zero_as_missing] = X[zero_as_missing].replace(0, np.nan)

    # 5. Train/Test Split (80% Train, 20% Test, Stratified by Outcome)
    print("[4/7] Splitting data into 80% training and 20% testing sets (random_state=42)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )
    print(f"      Training samples: {X_train.shape[0]} | Testing samples: {X_test.shape[0]}")

    # 6. Build the Scikit-learn Machine Learning Pipeline
    print("[5/7] Building ML Pipeline (Median Imputer -> StandardScaler -> Logistic Regression)...")
    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(max_iter=1000, random_state=42))
    ])

    print("      Fitting pipeline on training data...")
    pipeline.fit(X_train, y_train)

    # 7. Evaluate Model Performance on Unseen Test Data
    print("\n[6/7] Evaluating model performance on test set:")
    y_pred = pipeline.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    print("-" * 50)
    print(f" Test Accuracy  : {acc * 100:.2f}%")
    print(f" Precision      : {prec * 100:.2f}%")
    print(f" Recall (Sens.) : {rec * 100:.2f}%")
    print(f" F1-Score       : {f1 * 100:.2f}%")
    print("-" * 50)
    print(" Confusion Matrix (Test Set):")
    print(f"   [[True Negative={cm[0][0]}, False Positive={cm[0][1]}]")
    print(f"    [False Negative={cm[1][0]}, True Positive={cm[1][1]}]]")
    print("-" * 50)
    print("\n Full Classification Report:\n")
    print(classification_report(y_test, y_pred, target_names=["Non-Diabetic (0)", "Diabetic (1)"]))

    print(" NOTE:")
    print(" Test accuracy is evaluated on the held-out test split of the historical")
    print(" Pima Indians Diabetes dataset. It demonstrates statistical pattern classification")
    print(" for academic demonstration and does not guarantee clinical diagnostic certainty.\n")

    # 8. Save Pipeline Model
    print(f"[7/7] Saving trained pipeline to: {model_output_path}")
    joblib.dump(pipeline, model_output_path)
    print(" Model pipeline successfully saved as 'diabetes_model.pkl'!\n")

if __name__ == "__main__":
    train_and_evaluate_model()
