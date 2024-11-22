# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tkinter import Tk, StringVar, OptionMenu, Button

# Load data and preprocess
file_path = r'C:\Users\thaku\OneDrive\Desktop\Combined.csv'
data = pd.read_csv(file_path, low_memory=False)

# Convert columns that should be numeric, handling non-numeric entries
numeric_columns = ['value', 'gas', 'gas_price', 'receipt_gas_used']
for column in numeric_columns:
    data[column] = pd.to_numeric(data[column], errors='coerce')

# Convert block_timestamp to datetime
data['block_timestamp'] = pd.to_datetime(data['block_timestamp'], errors='coerce', format='%d-%m-%Y %H:%M')
data.dropna(subset=['block_timestamp'], inplace=True)
data['date'] = data['block_timestamp'].dt.date

# Prepare data for different chart types
transactions_per_day = data['date'].value_counts().sort_index()
scam_counts = data['scam'].value_counts()

# Function to plot selected graph type
def plot_graph(chart_type):
    plt.figure(figsize=(10, 5))
    
    if chart_type == "Bar Chart (Transactions per Day)":
        plt.bar(transactions_per_day.index, transactions_per_day.values, color='skyblue')
        plt.title('Transactions per Day')
        plt.xlabel('Date')
        plt.ylabel('Number of Transactions')
        plt.xticks(rotation=45)
    
    elif chart_type == "Pie Chart (Scam vs Non-Scam)":
        plt.pie(scam_counts, labels=['Non-Scam', 'Scam'], autopct='%1.1f%%', startangle=140, colors=['#66b3ff','#ff6666'])
        plt.title('Scam vs Non-Scam Transactions')
    
    elif chart_type == "Heatmap (Correlation)":
        corr_matrix = data[numeric_columns].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
        plt.title('Correlation Heatmap of Numeric Columns')
    
    elif chart_type == "Line Chart (Transactions Over Time)":
        transactions_per_day.plot(kind='line', color='purple')
        plt.title('Transactions Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Transactions')
        plt.xticks(rotation=45)
    
    elif chart_type == "Histogram (Transaction Values)":
        data['value'].dropna().plot(kind='hist', bins=30, color='green')
        plt.title('Distribution of Transaction Values')
        plt.xlabel('Value')
    
    elif chart_type == "Box Plot (Gas Prices)":
        sns.boxplot(data=data, x='gas_price')
        plt.title('Gas Prices Distribution')
        plt.xlabel('Gas Price')
    
    elif chart_type == "Scatter Plot (Value vs Gas)":
        sns.scatterplot(data=data, x='value', y='gas', alpha=0.5)
        plt.title('Value vs Gas Scatter Plot')
        plt.xlabel('Value')
        plt.ylabel('Gas')
    
    plt.tight_layout()
    plt.show()

# Initialize Tkinter GUI
root = Tk()
root.title("Data Visualization Tool")

# Dropdown menu for selecting chart type
chart_types = [
    "Bar Chart (Transactions per Day)", 
    "Pie Chart (Scam vs Non-Scam)", 
    "Heatmap (Correlation)", 
    "Line Chart (Transactions Over Time)", 
    "Histogram (Transaction Values)", 
    "Box Plot (Gas Prices)", 
    "Scatter Plot (Value vs Gas)"
]
selected_chart = StringVar(root)
selected_chart.set(chart_types[0])  # Default selection

dropdown_menu = OptionMenu(root, selected_chart, *chart_types)
dropdown_menu.pack(pady=10)

# Button to plot the selected chart
plot_button = Button(root, text="Plot Graph", command=lambda: plot_graph(selected_chart.get()))
plot_button.pack(pady=10)

# Run the GUI loop
root.mainloop()

