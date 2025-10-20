import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from datetime import date
import json # CRITICAL: Needed to parse the JSON key from Streamlit secrets

# NOTE: Your Firebase URL is https://expense-tracker-c6baf-default-rtdb.firebaseio.com

# -------------------- FIREBASE CONNECTION (CLOUD-READY) --------------------
# This block connects securely using credentials stored in Streamlit Secrets.
ref = None
try:
    # 1. Load the secrets from Streamlit Cloud's st.secrets dictionary
    firebase_secrets = st.secrets["firebase"]
    
    # 2. The JSON key is stored as a string, so we must load it as a dictionary
    key_dict = json.loads(firebase_secrets["key_json"])
    
    # 3. Initialize the app with the secure credentials and database URL from secrets
    cred = credentials.Certificate(key_dict)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {
            'databaseURL': firebase_secrets["database_url"]
        })
    
    # 4. Set the reference to the 'expenses' node
    ref = db.reference("expenses")
    
except Exception as e:
    # This error will show on the Streamlit App if the secrets are missing or incorrect
    st.error("🚨 Deployment Error: Failed to connect to Firebase.")
    st.warning("Please check your app's 'Secrets' configuration on the Streamlit dashboard.")
    # st.code(f"Error Details: {e}") # Uncomment this line for debugging the exact error
    ref = None

# -------------------- STREAMLIT APP SETUP --------------------
st.set_page_config(page_title="Cloud Expense Tracker", layout="centered")
st.title("💰 Cloud-Based Expense Tracker")

menu = ["Add Expense", "View Expenses", "Summary"]
choice = st.sidebar.selectbox("Menu", menu)

# The entire app logic is inside this main conditional block:
# It only runs if the Firebase connection (ref) was successful.
if ref is not None:
    
    # ----------------------------------------
    # 1. ADD EXPENSE SECTION
    # ----------------------------------------
    if choice == "Add Expense":
        st.subheader("➕ Add a New Expense")
    
        with st.form("expense_form", clear_on_submit=True):
            category = st.selectbox("Category", ["Food", "Travel", "Bills", "Shopping", "Others"])
            amount = st.number_input("Amount (₹)", min_value=0.0, step=0.1)
            desc = st.text_input("Description")
            exp_date = st.date_input("Date", date.today())
            
            submitted = st.form_submit_button("Add Expense")
    
            if submitted:
                # Prepare data dictionary
                data = {
                    "category": category,
                    "amount": amount,
                    "description": desc,
                    "date": str(exp_date) # Convert date object to string for Firebase
                }
                # Push data to Firebase (generates a unique key)
                ref.push(data)
                st.success("✅ Expense added successfully!")
    
    # ----------------------------------------
    # 2. VIEW EXPENSES SECTION
    # ----------------------------------------
    elif choice == "View Expenses":
        st.subheader("📋 View All Expenses")
        
        # Fetch all data from the 'expenses' node
        data = ref.get()
    
        if data:
            # Convert Firebase data (dictionary of dictionaries) to a pandas DataFrame
            df = pd.DataFrame(data.values())
            
            # Display the data table
            st.dataframe(df, use_container_width=True)
    
            if st.button("Export to Excel"):
                # Export the dataframe to a file
                df.to_excel("expenses.xlsx", index=False)
                st.success("✅ Exported as expenses.xlsx")
        else:
            st.warning("No expenses found. Use the 'Add Expense' tab to start tracking.")
    
    # ----------------------------------------
    # 3. SUMMARY SECTION
    # ----------------------------------------
    else:
        st.subheader("📊 Expense Summary")
        
        # Fetch all data
        data = ref.get()
    
        if data:
            # Convert data to DataFrame
            df = pd.DataFrame(data.values())
            
            # Calculate Total Spent
            total = df["amount"].sum()
            st.metric("Total Spent (₹)", total)
            
            st.write("---")
    
            # Group by category for chart
            st.subheader("Spending by Category")
            summary = df.groupby("category")["amount"].sum().reset_index()
            
            # Display Bar Chart
            st.bar_chart(summary.set_index("category"))
    
        else:
            st.info("No data to show yet. Add some expenses first!")

# Display a message if Firebase connection failed (Indentation corrected here)
else:
    st.error("Application could not load due to Firebase connection error.")
