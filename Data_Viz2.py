# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt  # Add this line to import matplotlib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

# Load the dataset
file_path = r'C:\Users\thaku\OneDrive\Desktop\Combined.csv'
data = pd.read_csv(file_path, low_memory=False)

# Preprocess the data
numeric_columns = ['value', 'gas', 'gas_price', 'receipt_gas_used']
for column in numeric_columns:
    data[column] = pd.to_numeric(data[column], errors='coerce')

# Drop rows with NaN values in the target or key features
data.dropna(subset=['scam', 'value', 'gas', 'gas_price', 'receipt_gas_used'], inplace=True)

# Feature selection and preprocessing
X = data[numeric_columns]  # Features
y = data['scam'].astype(int)  # Target

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Standardize the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Initialize a dictionary to store model performance
performance = {}

# List of models to evaluate
models = {
    "Logistic Regression": LogisticRegression(),
    "Random Forest": RandomForestClassifier(),
    "Decision Tree": DecisionTreeClassifier(),
    "Support Vector Classifier": SVC(),
    "K-Nearest Neighbors": KNeighborsClassifier(),
    "Naive Bayes": GaussianNB()
}

# Train each model and calculate metrics
for model_name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    # Store metrics in the dictionary
    performance[model_name] = [accuracy, precision, recall, f1]

# Convert the performance dictionary to a DataFrame for better visualization
performance_df = pd.DataFrame(performance, index=["Accuracy", "Precision", "Recall", "F1 Score"]).T

# Display the results
print("Model Performance Comparison:")
print(performance_df)






