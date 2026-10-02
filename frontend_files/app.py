# ------------------------------------------------------------------
# SuperKart Sales Forecasting - Streamlit frontend
# ------------------------------------------------------------------
import os
import requests
import pandas as pd
import streamlit as st

# URL of the Flask backend (container name on the Docker network by default)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:7860").rstrip("/")

st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒", layout="centered")
st.title("🛒 SuperKart Sales Forecasting")
st.write("Predict the total sales revenue of a product in a SuperKart store.")

tab_single, tab_batch = st.tabs(["Single prediction", "Batch prediction"])

# ------------------------------------------------------------------ Single prediction
with tab_single:
    st.subheader("Product details")
    col1, col2 = st.columns(2)
    with col1:
        product_id_char = st.selectbox(
            "Product group (Product_Id prefix)", ["FD", "DR", "NC"],
            help="FD = Food, DR = Drinks, NC = Non-consumables",
        )
        product_type_category = st.selectbox("Product type category", ["Perishables", "Non Perishables"])
        product_sugar_content = st.selectbox("Sugar content", ["Low Sugar", "Regular", "No Sugar"])
    with col2:
        product_weight = st.number_input("Product weight", min_value=0.0, max_value=50.0, value=12.66, step=0.01)
        product_allocated_area = st.number_input("Allocated display area (ratio)", min_value=0.0,
                                                 max_value=1.0, value=0.027, step=0.001, format="%.3f")
        product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=1000.0, value=117.08, step=0.01)

    st.subheader("Store details")
    col3, col4 = st.columns(2)
    with col3:
        store_size = st.selectbox("Store size", ["Small", "Medium", "High"], index=1)
        store_location_city_type = st.selectbox("City type", ["Tier 1", "Tier 2", "Tier 3"], index=1)
    with col4:
        store_type = st.selectbox("Store type", ["Supermarket Type1", "Supermarket Type2",
                                                 "Departmental Store", "Food Mart"], index=1)
        store_establishment_year = st.number_input("Store establishment year", min_value=1950,
                                                   max_value=2026, value=2009, step=1)

    if st.button("Predict sales", type="primary"):
        # Build the JSON payload exactly as expected by the backend API
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": product_allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location_city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": 2026 - int(store_establishment_year),  # same rule as in training
            "Product_Type_Category": product_type_category,
        }
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if response.status_code == 200:
                prediction = response.json()["Predicted Sales"]
                st.success(f"Predicted sales revenue: **{prediction:,.2f}**")
            else:
                st.error(f"API error ({response.status_code}): {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the backend API at {BACKEND_URL}: {e}")

# ------------------------------------------------------------------ Batch prediction
with tab_batch:
    st.subheader("Upload a CSV file")
    st.write("The file must contain these columns: `Product_Weight`, `Product_Sugar_Content`, "
             "`Product_Allocated_Area`, `Product_MRP`, `Store_Size`, `Store_Location_City_Type`, "
             "`Store_Type`, `Product_Id_char`, `Store_Age_Years`, `Product_Type_Category`.")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
        st.write(f"Preview ({len(batch_df)} rows):")
        st.dataframe(batch_df.head())

        if st.button("Predict batch", type="primary"):
            try:
                uploaded_file.seek(0)
                response = requests.post(f"{BACKEND_URL}/v1/predictbatch",
                                         files={"file": uploaded_file.getvalue()}, timeout=120)
                if response.status_code == 200:
                    predictions = response.json()  # {row index: predicted sales}
                    batch_df["Predicted_Sales"] = [predictions[str(i)] for i in range(len(batch_df))]
                    st.success("Batch predictions completed.")
                    st.dataframe(batch_df)
                    st.download_button("Download predictions as CSV",
                                       batch_df.to_csv(index=False).encode("utf-8"),
                                       file_name="superkart_predictions.csv", mime="text/csv")
                else:
                    st.error(f"API error ({response.status_code}): {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach the backend API at {BACKEND_URL}: {e}")
