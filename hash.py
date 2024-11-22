import requests
import pandas as pd
from datetime import datetime
import time

# Replace with your Etherscan API key
API_KEY = 'KJMM2XGGBE6JCBEXVQCDAA56E5DIPWGSWB'

# Define your scam addresses and categories here
scam_addresses = {
    '0xAddress1': 'Phishing',
    '0xAddress2': 'Scamming',
    # Add more addresses and categories here
}

# Function to fetch the latest 10 transactions for a specific address
def fetch_latest_transactions(address, limit=10):
    url = 'https://api.etherscan.io/api'
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'sort': 'desc',  # Sort transactions by latest first
        'apikey': API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] != '1' or 'result' not in data:
        print(f"Error fetching transactions for address {address}: {data.get('message', 'Unknown error')}")
        return []

    transactions = data['result']
    # Return only the latest `limit` transactions
    return transactions[:limit]

# Function to fetch transaction details by hash
def fetch_transaction_by_hash(tx_hash):
    url = 'https://api.etherscan.io/api'
    params = {
        'module': 'proxy',
        'action': 'eth_getTransactionByHash',
        'txhash': tx_hash,
        'apikey': API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()

# Function to fetch the transaction receipt
def fetch_transaction_receipt(tx_hash):
    url = 'https://api.etherscan.io/api'
    params = {
        'module': 'proxy',
        'action': 'eth_getTransactionReceipt',
        'txhash': tx_hash,
        'apikey': API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()

# Function to convert Unix timestamp to a readable date and time
def convert_timestamp(timestamp):
    try:
        return datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return 'Invalid timestamp'

# Function to determine scam status and category
def get_scam_info(address):
    if address in scam_addresses:
        return 1, scam_addresses[address]  # Flag and category
    return 0, 'null'

# Function to process and save data to CSV
def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, mode='a', header=not pd.io.common.file_exists(filename), index=False)  # Append mode

def main(addresses_file, filename):
    all_data = []

    # Read addresses from file
    try:
        with open(addresses_file, 'r') as f:
            addresses = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(f"File not found: {addresses_file}")
        return

    total_addresses = len(addresses)
    print(f"Total addresses to process: {total_addresses}")

    for address in addresses:
        print(f'Fetching latest 10 transactions for address: {address}')
        transactions = fetch_latest_transactions(address)

        for tx in transactions:
            # Fetch detailed transaction information using the hash
            tx_hash = tx.get('hash')
            tx_details = fetch_transaction_by_hash(tx_hash)
            tx_data = tx_details.get('result', {})

            # Fetch the transaction receipt
            tx_receipt_data = fetch_transaction_receipt(tx_hash)
            receipt = tx_receipt_data.get('result', {})

            # Determine scam status and categories for both from and to addresses
            from_scam, from_category = get_scam_info(tx_data.get('from'))
            to_scam, to_category = get_scam_info(tx_data.get('to'))

            # Prepare transaction information for saving
            transaction_info = {
                'hash': tx_data.get('hash'),
                'nonce': int(tx_data.get('nonce', '0'), 16),
                'transaction_index': int(tx_data.get('transactionIndex', '0'), 16),
                'from_address': tx_data.get('from'),
                'to_address': tx_data.get('to'),
                'value': int(tx_data.get('value', '0'), 16),
                'gas': int(tx_data.get('gas', '0'), 16),
                'gas_price': int(tx_data.get('gasPrice', '0'), 16),
                'input': tx_data.get('input'),
                'receipt_cumulative_gas_used': int(receipt.get('cumulativeGasUsed', '0'), 16),
                'receipt_gas_used': int(receipt.get('gasUsed', '0'), 16),
                'block_timestamp': convert_timestamp(tx_data.get('timeStamp', '0')),
                'block_number': int(tx_data.get('blockNumber', '0'), 16),
                'block_hash': tx_data.get('blockHash'),
                'from_scam': from_scam,
                'to_scam': to_scam,
                'from_category': from_category,
                'to_category': to_category,
            }
            all_data.append(transaction_info)

        # Delay to handle API rate limits (e.g., 1 second delay)
        time.sleep(1)

        # Save data to CSV
        save_to_csv(all_data, filename)
        print(f'Data saved to {filename}')

if __name__ == '__main__':
    addresses_file = r'C:\Users\vishw\Downloads\project\address.txt'  # Full path to your addresses file
    filename = 'latest_10_transaction_data.csv'  # Output CSV filename
    main(addresses_file, filename)
