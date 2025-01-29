import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Database setup
def init_db():
    conn = sqlite3.connect('expense_tracker.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    category TEXT,
                    amount REAL,
                    description TEXT
                )''')
    conn.commit()
    conn.close()


# Add expense to the database
def add_expense(date, category, amount, description):
    conn = sqlite3.connect('expense_tracker.db')
    c = conn.cursor()
    c.execute('''INSERT INTO expenses (date, category, amount, description)
                 VALUES (?, ?, ?, ?)''', (date, category, amount, description))
    conn.commit()
    conn.close()


# Fetch all expenses
def get_expenses():
    conn = sqlite3.connect('expense_tracker.db')
    df = pd.read_sql_query("SELECT * FROM expenses", conn)
    conn.close()
    return df


# Calculate total expenses
def calculate_total_expenses():
    df = get_expenses()
    return df['amount'].sum()


# Streamlit App
def main():
    st.title("Personal Expense Tracker 💰")
    st.sidebar.header("Settings")

    # Initialize database
    init_db()

    # Budget setting in the sidebar
    budget = st.sidebar.number_input("Set Monthly Budget", min_value=0.0, value=1000.0, step=100.0)

    # Create two columns for side-by-side layout
    col1, col2 = st.columns(2)

    # Column 1: Add New Expense
    with col1:
        st.header("Add New Expense")
        date = st.date_input("Date")
        category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Utilities", "Other"])
        amount = st.number_input("Amount", min_value=0.0, step=10.0)
        description = st.text_input("Description")
        if st.button("Add Expense"):
            add_expense(date, category, amount, description)
            st.success("Expense added successfully!")

    # Column 2: Expense History and Insights
    with col2:
        st.header("Expense History")
        expenses_df = get_expenses()
        if not expenses_df.empty:
            st.dataframe(expenses_df)

            # Visualizations
            st.header("Expense Insights")
            st.subheader("Total Expenses")
            total_expenses = calculate_total_expenses()
            st.write(f"Total Expenses: ${total_expenses:.2f}")

            # Budget vs Expenses
            remaining_budget = budget - total_expenses
            st.write(f"Remaining Budget: ${remaining_budget:.2f}")
            if total_expenses > budget:
                st.warning("You have exceeded your budget!")

            # Pie chart for expense categories
            st.subheader("Expense Distribution by Category")
            category_sum = expenses_df.groupby('category')['amount'].sum()
            fig1, ax1 = plt.subplots()
            ax1.pie(category_sum, labels=category_sum.index, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            st.pyplot(fig1)

            # Bar chart for monthly spending
            st.subheader("Monthly Spending Trend")
            expenses_df['date'] = pd.to_datetime(expenses_df['date'])
            monthly_spending = expenses_df.resample('M', on='date')['amount'].sum()
            fig2, ax2 = plt.subplots()
            ax2.bar(monthly_spending.index.strftime('%Y-%m'), monthly_spending, color='skyblue')
            ax2.set_xlabel("Month")
            ax2.set_ylabel("Total Spending")
            st.pyplot(fig2)

            # Export data
            st.subheader("Export Data")
            if st.button("Export Expenses as CSV"):
                csv = expenses_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="expenses.csv",
                    mime="text/csv"
                )
        else:
            st.write("No expenses recorded yet.")


if __name__ == "__main__":
    main()