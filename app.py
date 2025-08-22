import streamlit as st
import pickle
import pandas as pd
import numpy as np
import os

# Get the directory where app.py is located
BASE_DIR = os.path.dirname(__file__)

# -------------------------
# Load trained model
# -------------------------
model_path = "E:\\FoodieBay DataSet\\models\\random_forest_model.pkl"  # ensure this exists
with open(model_path, "rb") as file:
    model = pickle.load(file)

# -------------------------
# Load dataset to extract categories
# -------------------------
# data_path = "E:\\FoodieBay DataSet\\data\\Foodiebay.csv"   # 👈 make sure this exists
# df = pd.read_csv(data_path)
# Load dataset
data_path = os.path.join(BASE_DIR, "data", "Foodiebay.csv")
df = pd.read_csv(data_path)

# Create label encoding dictionaries (map text → number)
location_map = {name: idx for idx, name in enumerate(sorted(df["location"].dropna().unique()))}
rest_type_map = {name: idx for idx, name in enumerate(sorted(df["rest_type"].dropna().unique()))}
listed_type_map = {name: idx for idx, name in enumerate(sorted(df["listed_in_type"].dropna().unique()))}
listed_city_map = {name: idx for idx, name in enumerate(sorted(df["listed_in_city"].dropna().unique()))}

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="FoodieBay Restaurant Predictor", layout="wide")

st.title("🍴 FoodieBay Restaurant Rating Predictor")
st.markdown("Predict the **restaurant rating** based on features like location, cuisine, cost, and more.")

st.sidebar.header("📊 Input Features")

# Dropdowns with names (UI) → convert to encoded numbers later
location_name = st.sidebar.selectbox("📍 Location", list(location_map.keys()))
rest_type_name = st.sidebar.selectbox("🏢 Restaurant Type", list(rest_type_map.keys()))
listed_in_type_name = st.sidebar.selectbox("📑 Listed In Type", list(listed_type_map.keys()))
listed_in_city_name = st.sidebar.selectbox("🌆 Listed In City", list(listed_city_map.keys()))

# ✅ Replace 0/1 with Yes/No options
online_order_label = st.sidebar.radio("🛒 Online Order Available?", ["No", "Yes"])
book_table_label = st.sidebar.radio("📖 Table Booking Available?", ["No", "Yes"])

# 🔄 Map back to 0/1 for the model
online_order = 1 if online_order_label == "Yes" else 0
book_table = 1 if book_table_label == "Yes" else 0

# Numeric features
ave_cost_for_two = st.sidebar.slider("💰 Average Cost for Two", 40, 2500, 500, step=10)
votes = st.sidebar.slider("👍 Votes", 0, 12000, 100, step=50)
ave_review_ranking = st.sidebar.slider("⭐ Average Review Ranking", 1.0, 5.0, 3.5, step=0.1)
menu_item_count = st.sidebar.slider("🍽 Menu Item Count", 0, 700, 20, step=5)

# ✅ Full cuisine list from training
all_cuisine_columns = [
    "primary_cuisine_Arabian", "primary_cuisine_Asian", "primary_cuisine_Bakery",
    "primary_cuisine_Bengali", "primary_cuisine_Biryani", "primary_cuisine_Burger",
    "primary_cuisine_Cafe", "primary_cuisine_Chinese", "primary_cuisine_Continental",
    "primary_cuisine_Desserts", "primary_cuisine_Fast Food", "primary_cuisine_Hyderabadi",
    "primary_cuisine_Indian", "primary_cuisine_Italian", "primary_cuisine_Japanese",
    "primary_cuisine_Kerala", "primary_cuisine_Lebanese", "primary_cuisine_Mexican",
    "primary_cuisine_Mughlai", "primary_cuisine_North Indian", "primary_cuisine_Other",
    "primary_cuisine_Pizza", "primary_cuisine_Rolls", "primary_cuisine_Sandwich",
    "primary_cuisine_Seafood", "primary_cuisine_South Indian", "primary_cuisine_Street Food",
    "primary_cuisine_Healthy Food"
]

# Cuisine UI (human readable)
cuisine_display_names = [c.replace("primary_cuisine_", "") for c in all_cuisine_columns]
selected_cuisines = st.sidebar.multiselect("🍜 Select Cuisines", cuisine_display_names)

# Map to training format
cuisine_data = {col: 0 for col in all_cuisine_columns}
for cuisine in selected_cuisines:
    col_name = f"primary_cuisine_{cuisine}"
    if col_name in cuisine_data:
        cuisine_data[col_name] = 1

# -------------------------
# Predict Button
# -------------------------
if st.sidebar.button("🚀 Predict Rating"):
    input_data = pd.DataFrame([{
        "location": location_map[location_name],          # encoded value
        "rest_type": rest_type_map[rest_type_name],       # encoded value
        "listed_in_type": listed_type_map[listed_in_type_name],  # encoded value
        "listed_in_city": listed_city_map[listed_in_city_name],  # encoded value
        "online_order": online_order,
        "book_table": book_table,
        "ave_cost_for_two": ave_cost_for_two,
        "votes": votes,
        "ave_review_ranking": ave_review_ranking,
        "menu_item_count": menu_item_count,
        **cuisine_data
    }])

    # Prediction
    prediction = model.predict(input_data)[0]

    st.success(f"⭐ **Predicted Rating: {prediction:.2f} / 5**")
    st.progress(min(1.0, prediction / 5))
    st.metric(label="📊 Model Confidence (approx)", value=f"{(prediction/5)*100:.1f}%")

# -------------------------
# Footer
# -------------------------
st.markdown("---")
st.caption("Made with ❤️ using Streamlit & Random Forest")
