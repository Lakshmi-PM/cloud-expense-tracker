import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from datetime import date

# --- FIREBASE CONNECTION ---
# Your database URL: https://expense-tracker-c6baf-default-rtdb.firebaseio.com
FIREBASE_URL = 'https://expense-tracker-c6baf-default-rtdb.firebaseio.com'

# Load Firebase key
cred = credentials.Certificate("firebase-key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': FIREBASE_URL
    })

# Reference to the 'expenses' path in your database
ref = db.reference("expenses")

# --- STREAMLIT APP SETUP ---
st.set_page_config(page_title="Cloud Expense Tracker", layout="centered")
st.title("💰 Cloud-Based Expense Tracker")

menu = ["Add Expense", "View Expenses", "Summary"]
choice = st.sidebar.selectbox("Menu", menu)

# ----------------------------------------
# 1. ADD EXPENSE SECTION
# ----------------------------------------
if choice == "Add Expense":
    st.subheader("➕ Add a New Expense")

    with st.form("expense_form", clear_on_submit=True):
        category = st.selectbox("Category", ["Food", "Travel", "Bills", "Shopping", "Others"])
        # Ensure amount is treated as a float
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