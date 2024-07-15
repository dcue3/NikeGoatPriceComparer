import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the dataset
data = pd.read_csv('MLTrainingData.csv')

# Data Cleaning
data = data.drop_duplicates()
data = data.dropna(subset=['Name', 'Resale Price ($)', 'Year'])

# Ensure 'Retail Price ($)' is numeric, replacing non-numeric values with 0
data['Retail Price ($)'] = pd.to_numeric(data['Retail Price ($)'], errors='coerce').fillna(0)

# Create a new feature indicating whether the retail price is missing (which were set to 0)
data['Retail Price Missing'] = (data['Retail Price ($)'] == 0).astype(int)

# Feature Engineering
features = ['Retail Price ($)', 'Year', 'Retail Price Missing', 'Resale Price ($)']

# Calculate the correlation matrix
correlation_matrix = data[features].corr()

# Plot the correlation matrix
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Feature Correlation Matrix')
plt.show()
