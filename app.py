import streamlit as st
import json
from datetime import datetime
import time

# Load data
def load_data():
    try:
        with open('expenses.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"categories": {}}

# Save data
def save_data(data):
    with open('expenses.json', 'w') as f:
        json.dump(data, f)

# Calculate expenses per second
def calculate_expenses_per_second(expenses):
    total_monthly = sum(sum(item['amount'] for item in category.values())
                        for category in expenses['categories'].values())
    return total_monthly / (30 * 24 * 60 * 60)  # Assuming 30 days per month

# Format currency with adjustable decimal places
def format_currency(amount, decimal_places):
    return f"{amount:,.{decimal_places}f} kr.".replace(",", "X").replace(".", ",").replace("X", ".")

# Format datetime
def format_datetime(dt):
    months = ["januar", "februar", "marts", "april", "maj", "juni", "juli", "august", "september", "oktober", "november", "december"]
    return f"{dt.day}. {months[dt.month-1]} {dt.year} {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"

# Main app
def main():
    st.title("Live Udgifts Ticker")

    data = load_data()

    # Decimal places slider
    decimal_places = st.sidebar.slider("Antal decimaler", 0, 10, 6)

    # Add new category
    new_category = st.text_input("Tilføj ny kategori")
    if st.button("Tilføj Kategori") and new_category:
        if new_category not in data['categories']:
            data['categories'][new_category] = {}
            save_data(data)

    # Add new expense
    if data['categories']:
        category = st.selectbox("Vælg kategori", list(data['categories'].keys()))
        expense_name = st.text_input("Udgiftsnavn")
        expense_amount = st.number_input("Månedligt beløb", min_value=0.0, format=f"%.{decimal_places}f")
        if st.button("Tilføj Udgift") and expense_name and expense_amount > 0:
            data['categories'][category][expense_name] = {"amount": expense_amount}
            save_data(data)

    # Display live ticker
    if data['categories']:
        expenses_per_second = calculate_expenses_per_second(data)
        
        placeholder = st.empty()
        
        while True:
            now = datetime.now()
            seconds_passed = now.second + now.minute * 60 + now.hour * 3600
            
            expenses_second = expenses_per_second
            expenses_minute = expenses_per_second * 60
            expenses_hour = expenses_per_second * 3600
            daily_expenses = expenses_per_second * seconds_passed
            monthly_expenses = expenses_per_second * seconds_passed * 30
            yearly_expenses = expenses_per_second * seconds_passed * 365
            
            current_time = format_datetime(now)
            
            placeholder.markdown(f"""
            ## Aktuelle Udgifter (pr. {current_time})
            - Pr. Sekund: {format_currency(expenses_second, decimal_places)}
            - Pr. Minut: {format_currency(expenses_minute, decimal_places)}
            - Pr. Time: {format_currency(expenses_hour, decimal_places)}
            - Pr. Dag: {format_currency(daily_expenses, decimal_places)}
            - Pr. Måned: {format_currency(monthly_expenses, decimal_places)}
            - Pr. År: {format_currency(yearly_expenses, decimal_places)}
            """)
            
            time.sleep(1)

    # Display expenses by category
    if data['categories']:
        st.header("Udgifter pr. Kategori")
        for category, expenses in data['categories'].items():
            st.subheader(category)
            for name, details in expenses.items():
                st.write(f"{name}: {format_currency(details['amount'], decimal_places)} pr. måned")

if __name__ == "__main__":
    main()
