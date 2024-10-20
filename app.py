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
    return f"{amount:.{decimal_places}f} kr".replace(".", ",")

# Format datetime
def format_datetime(dt):
    months = ["januar", "februar", "marts", "april", "maj", "juni", "juli", "august", "september", "oktober", "november", "december"]
    return f"{dt.day}. {months[dt.month-1]} {dt.year} {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"

# Main app
def main():
    st.set_page_config(layout="wide")
    st.title("Live Udgifts Ticker")

    data = load_data()

    # Sidebar for adding new categories and expenses
    with st.sidebar:
        st.header("Tilføj Ny Kategori/Udgift")
        new_category = st.text_input("Ny kategori")
        if st.button("Tilføj Kategori") and new_category:
            if new_category not in data['categories']:
                data['categories'][new_category] = {}
                save_data(data)

        if data['categories']:
            category = st.selectbox("Vælg kategori", list(data['categories'].keys()))
            expense_name = st.text_input("Udgiftsnavn")
            expense_amount = st.number_input("Månedligt beløb", min_value=0.0, format="%.2f")
            if st.button("Tilføj Udgift") and expense_name and expense_amount > 0:
                data['categories'][category][expense_name] = {"amount": expense_amount}
                save_data(data)

    # Main content
    if data['categories']:
        expenses_per_second = calculate_expenses_per_second(data)

        # Decimal place settings
        st.sidebar.header("Indstillinger for Decimaler")
        decimal_settings = {}
        for interval in ['Sekund', 'Minut', 'Time', 'Dag', 'Måned', 'År']:
            decimal_settings[interval] = st.sidebar.number_input(f"Decimaler for {interval}", 0, 10, 2)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Samlet Udgiftsoversigt")
            total_placeholder = st.empty()

        with col2:
            st.subheader("Udgifter per Kategori")
            category_placeholders = {category: st.empty() for category in data['categories']}

        while True:
            now = datetime.now()
            seconds_passed = now.second + now.minute * 60 + now.hour * 3600
            
            expenses = {
                'Sekund': expenses_per_second,
                'Minut': expenses_per_second * 60,
                'Time': expenses_per_second * 3600,
                'Dag': expenses_per_second * 86400,
                'Måned': expenses_per_second * 2592000,  # 30 days
                'År': expenses_per_second * 31536000  # 365 days
            }
            
            current_time = format_datetime(now)
            
            total_markdown = f"**Opdateret: {current_time}**\n\n"
            for interval, amount in expenses.items():
                total_markdown += f"**{interval}:** {format_currency(amount, decimal_settings[interval])}\n\n"
            
            total_placeholder.markdown(total_markdown)

            # Update category tickers
            for category, placeholder in category_placeholders.items():
                category_total = sum(item['amount'] for item in data['categories'][category].values())
                category_per_second = category_total / (30 * 24 * 60 * 60)
                
                category_markdown = f"**{category}**\n\n"
                for interval, amount in expenses.items():
                    category_amount = amount * (category_per_second / expenses_per_second)
                    category_markdown += f"{interval}: {format_currency(category_amount, decimal_settings[interval])}\n\n"
                
                for expense, details in data['categories'][category].items():
                    expense_per_second = details['amount'] / (30 * 24 * 60 * 60)
                    expense_amount = expenses['Måned'] * (expense_per_second / expenses_per_second)
                    category_markdown += f"- {expense}: {format_currency(expense_amount, decimal_settings['Måned'])} /måned\n\n"
                
                placeholder.markdown(category_markdown)
            
            time.sleep(1)

if __name__ == "__main__":
    main()
