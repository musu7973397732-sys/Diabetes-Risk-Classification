import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# 1. Load the dataset
data = pd.read_csv("diabetes.csv")

# 2. Separate input features and target
X = data.drop("Outcome", axis=1)
y = data["Outcome"]

# 3. Treat zero values in these measurements as missing
zero_as_missing = [
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI"
]

X[zero_as_missing] = X[zero_as_missing].replace(0, float("nan"))

# 4. Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# 5. Create the ML pipeline
model = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("classifier", LogisticRegression(max_iter=1000))
])

# 6. Train the model
model.fit(X_train, y_train)

# 7. Check model accuracy
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print("Model trained successfully!")
print(f"Test accuracy: {accuracy:.2%}")

# 8. Save the trained model
joblib.dump(model, "diabetes_model.pkl")

print("Model saved as diabetes_model.pkl")