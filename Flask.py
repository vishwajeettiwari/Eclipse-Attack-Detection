from flask import Flask, render_template, request
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import requests

app = Flask(__name__)

# Load and preprocess data
file_path = r'C:\Users\thaku\OneDrive\Desktop\Combined.csv'
data = pd.read_csv(file_path, low_memory=False)

# Convert to numeric columns where applicable
data['value'] = pd.to_numeric(data['value'], errors='coerce').fillna(0)
data['from_address'] = data['from_address'].astype(str)

# Feature Engineering
data['transaction_count'] = data.groupby('from_address')['from_address'].transform('count')
data['avg_transaction_value'] = data.groupby('from_address')['value'].transform('mean')

# Define features and target for training the classifier
features = data[['transaction_count', 'avg_transaction_value']].fillna(0)
data['scam'] = data['scam'].fillna(0).astype(int)  # Assuming 'scam' is the target

# Train a classifier for calculating metrics
classifier = RandomForestClassifier(n_estimators=100, random_state=42)
classifier.fit(features, data['scam'])
data['predicted_scam'] = classifier.predict(features)

# Calculate initial metrics
accuracy = accuracy_score(data['scam'], data['predicted_scam'])
precision = precision_score(data['scam'], data['predicted_scam'])
recall = recall_score(data['scam'], data['predicted_scam'])
f1 = f1_score(data['scam'], data['predicted_scam'])

# Define Etherscan API key
etherscan_api_key = 'KJMM2XGGBE6JCBEXVQCDAA56E5DIPWGSWB'

# Function to check legitimacy of an address
def check_legitimacy(from_address):
    if from_address in data['from_address'].values:
        address_data = data[data['from_address'] == from_address]
        if address_data['scam'].iloc[0] == 1:
            return f"Address {from_address}: Marked as Scam based on local data!"
        else:
            return f"Address {from_address}: Legitimate based on local data."
    else:
        return check_from_etherscan(from_address)

# Function to check Etherscan API
def check_from_etherscan(from_address):
    url = f'https://api.etherscan.io/api?module=account&action=txlist&address={from_address}&sort=asc&apikey={etherscan_api_key}'
    try:
        response = requests.get(url)
        data = response.json()
        if data['status'] == '1' and len(data['result']) > 0:
            for tx in data['result']:
                # Convert the value from Wei to Ether for comparison
                tx_value_eth = float(tx['value']) / 10**18  # Convert Wei to ETH
                if tx_value_eth > 2:  # Check if transaction value is greater than 2 ETH
                    return f"Address {from_address}: Suspicious: High-value transaction detected ({tx_value_eth} ETH)."
            return f"Address {from_address}: Legitimate: No suspicious transactions detected."
        else:
            return f"Address {from_address}: No transactions found on Etherscan."
    except requests.exceptions.RequestException as e:
        return f"Error fetching data from Etherscan: {e}"

# Define route for the homepage
@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    metrics = {
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    }
    if request.method == "POST":
        from_address = request.form["from_address"]
        if from_address:
            result = check_legitimacy(from_address)

            # Update metrics after each check
            y_pred = classifier.predict(features)
            metrics['Accuracy'] = accuracy_score(data['scam'], y_pred)
            metrics['Precision'] = precision_score(data['scam'], y_pred)
            metrics['Recall'] = recall_score(data['scam'], y_pred)
            metrics['F1 Score'] = f1_score(data['scam'], y_pred)

    return render_template("index.html", result=result, metrics=metrics)

if __name__ == "__main__":
    app.run(debug=True)
