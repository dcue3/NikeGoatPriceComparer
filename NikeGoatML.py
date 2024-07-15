import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import sys

def main(file_path):
    data = pd.read_csv(file_path)

    data = data.drop_duplicates()
    data = data.dropna(subset=['Name', 'Resale Price ($)', 'Year'])

    data['Retail Price ($)'] = pd.to_numeric(data['Retail Price ($)'], errors='coerce').fillna(0)
    data['Retail Price Missing'] = (data['Retail Price ($)'] == 0).astype(int)

    features = ['Name', 'Retail Price ($)', 'Year', 'Retail Price Missing']
    target = 'Resale Price ($)'
    X = data[features]
    y = data[target]

    preprocessor = ColumnTransformer(
        transformers=[
            ('name', OneHotEncoder(handle_unknown='ignore'), ['Name']),
            ('scaler', StandardScaler(), ['Retail Price ($)', 'Year', 'Retail Price Missing'])
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = mse ** 0.5
    r2 = r2_score(y_test, y_pred)

    print(f"MAE: {mae}")
    print(f"MSE: {mse}")
    print(f"RMSE: {rmse}")
    print(f"R-squared: {r2}")

    # Save the trained model to a file
    import joblib
    joblib.dump(model, 'trained_model.pkl')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 train_model.py <file_path>")
    else:
        main(sys.argv[1])
