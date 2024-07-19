import sys
import pandas as pd
import joblib

def predict_resale_price(name, retail_price, year):
    model = joblib.load('trained_model.pkl')

    input_data = pd.DataFrame({
        'Name': [name],
        'Retail Price ($)': [retail_price],
        'Year': [year],
        'Retail Price Missing': [1 if retail_price == 0 else 0]
    })

    predicted_price = model.predict(input_data)
    return predicted_price[0]

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 PredictResale.py <name> <retail_price> <year>")
    else:
        name = sys.argv[1]
        retail_price = float(sys.argv[2])
        year = int(sys.argv[3])

        predicted_price = predict_resale_price(name, retail_price, year)
        print(f"The predicted resale price for the shoe is: ${predicted_price:.2f}")
