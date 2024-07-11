import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Load the dataset
data = pd.read_csv('NikeParserResults.csv')

# Data Cleaning
data = data.drop_duplicates()
data = data.dropna(subset=['Name', 'Retail Price ($)', 'Resale Price ($)', 'Year'])

# Feature Engineering
features = ['Name', 'Retail Price ($)', 'Year']
target = 'Resale Price ($)'
X = data[features]
y = data[target]

# Encoding Categorical Variables
preprocessor = ColumnTransformer(
    transformers=[
        ('name', OneHotEncoder(handle_unknown='ignore'), ['Name'])
    ],
    remainder='passthrough'
)

# Split the Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and Train the Model
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', LinearRegression())
])

model.fit(X_train, y_train)

# Make Predictions
y_pred = model.predict(X_test)

# Evaluate the Model
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = mse ** 0.5
r2 = r2_score(y_test, y_pred)

print(f'MAE: {mae}')
print(f'MSE: {mse}')
print(f'RMSE: {rmse}')
print(f'R-squared: {r2}')


# Function to predict resale price
def predict_resale_price(name, retail_price, year):
    input_data = pd.DataFrame({
        'Name': [name],
        'Retail Price ($)': [retail_price],
        'Year': [year]
    })

    predicted_price = model.predict(input_data)
    return predicted_price[0]


# CLI for user input
def main():
    print("Enter the details of the shoe to predict its resale price:")
    name = input("Name: ")
    retail_price = float(input("Retail Price ($): "))
    year = int(input("Year: "))

    predicted_price = predict_resale_price(name, retail_price, year)
    print(f"The predicted resale price for the shoe is: ${predicted_price:.2f}")


if __name__ == "__main__":
    main()
