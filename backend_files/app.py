# ------------------------------------------------------------------
# SuperKart Sales Forecasting - Flask backend API
# ------------------------------------------------------------------
import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialise the Flask application
superkart_api = Flask("SuperKart Sales Predictor")

# Load the serialized model pipeline (preprocessing + tuned XGBoost) once at start-up
model = joblib.load("superkart_model.joblib")

# Features expected by the model, in the same order used during training
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]
NUMERIC_FEATURES = ["Product_Weight", "Product_Allocated_Area", "Product_MRP", "Store_Age_Years"]


def prepare_input(df):
    """Keeps the model features in the training order and converts numeric columns to numbers."""
    df = df[FEATURES].copy()
    for col in NUMERIC_FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce")  # invalid values become NaN -> imputed by the pipeline
    return df


# Home route - simple health check
@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart Sales Forecasting API!"


# Online (single) prediction endpoint
@superkart_api.post("/v1/predict")
def predict_sales():
    # Read the JSON payload sent by the client
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be a JSON object with the product and store details."}), 400

    # Check that every feature needed by the model is present
    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    # Build a one-row DataFrame and predict
    input_df = prepare_input(pd.DataFrame([data]))
    prediction = float(model.predict(input_df)[0])

    return jsonify({"Predicted Sales": round(prediction, 2)})


# Batch prediction endpoint - expects a CSV file uploaded with the key 'file'
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    if "file" not in request.files:
        return jsonify({"error": "Please upload a CSV file using the key 'file'."}), 400

    # Read the uploaded CSV file into a DataFrame
    input_df = pd.read_csv(request.files["file"])

    missing = [f for f in FEATURES if f not in input_df.columns]
    if missing:
        return jsonify({"error": f"Missing columns in the CSV file: {missing}"}), 400

    # Predict sales for every row
    predictions = model.predict(prepare_input(input_df))

    # Return a dictionary {row index: predicted sales}
    output = {str(idx): round(float(pred), 2) for idx, pred in zip(input_df.index, predictions)}
    return jsonify(output)


# Run the app locally (inside Docker the app is served by gunicorn instead)
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
