import streamlit as st
import json
from datetime import datetime
import time
import calendar

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

# Calculate expenses per second for the current month
def calculate_expenses_per_second(expenses, current_date):
    total_monthly = sum(sum(item['amount'] for item in category.values())
                        for category in expenses['categories'].values())
    days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
    return total_monthly / (days_in_month * 24 * 60 * 60)

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

    if 'data' not in st.session_state:
        st.session_state.data = load_data()

    # Sidebar for adding new categories and expenses
    with st.sidebar:
        st.header("Tilføj/Slet Kategori/Udgift")
        new_category = st.text_input("Ny kategori")
        if st.button("Tilføj Kategori") and new_category:
            if new_category not in st.session_state.data['categories']:
                st.session_state.data['categories'][new_category] = {}
                save_data(st.session_state.data)

        if st.session_state.data['categories']:
            category = st.selectbox("Vælg kategori", list(st.session_state.data['categories'].keys()))
            if st.button("Slet Kategori"):
                del st.session_state.data['categories'][category]
                save_data(st.session_state.data)
                st.rerun()

            expense_name = st.text_input("Udgiftsnavn")
            expense_amount = st.number_input("Månedligt beløb", min_value=0, step=1)
            if st.button("Tilføj Udgift") and expense_name and expense_amount > 0:
                st.session_state.data['categories'][category][expense_name] = {"amount": expense_amount}
                save_data(st.session_state.data)

            if category in st.session_state.data['categories']:
                expense_to_delete = st.selectbox("Vælg udgift at slette", list(st.session_state.data['categories'][category].keys()))
                if st.button("Slet Udgift"):
                    del st.session_state.data['categories'][category][expense_to_delete]
                    save_data(st.session_state.data)
                    st.rerun()

    # Decimal place settings
    st.sidebar.header("Indstillinger for Decimaler")
    decimal_settings = {}
    for interval in ['Minut', 'Dag', 'Uge', 'Måned', 'År']:
        decimal_settings[interval] = st.sidebar.number_input(f"Decimaler for {interval}", 0, 10, 2)

    # Main content
    if st.session_state.data['categories']:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Månedens Udgifter")
            monthly_placeholder = st.empty()

        with col2:
            st.subheader("Samlede Faste Udgifter")
            total_placeholder = st.empty()

        st.subheader("Udgifter per Kategori")
        category_container = st.container()

        # Live update loop
        while True:
            now = datetime.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            seconds_passed = (now - start_of_month).total_seconds()
            
            expenses_per_second = calculate_expenses_per_second(st.session_state.data, now)
            
            # Calculate expenses
            monthly_expenses = expenses_per_second * seconds_passed
            
            # Calculate total fixed expenses
            total_monthly = sum(sum(item['amount'] for item in category.values())
                                for category in st.session_state.data['categories'].values())
            total_expenses = {
                'Minut': total_monthly / (30 * 24 * 60),
                'Dag': total_monthly / 30,
                'Uge': total_monthly / 4,
                'Måned': total_monthly,
                'År': total_monthly * 12
            }
            
            current_time = format_datetime(now)
            
            # Update monthly ticker
            monthly_markdown = f"**Opdateret: {current_time}**\n\n"
            monthly_markdown += f"**Månedens udgifter: {format_currency(monthly_expenses, decimal_settings['Måned'])}**\n\n"
            monthly_placeholder.markdown(monthly_markdown)
            
            # Update total fixed expenses
            total_markdown = f"**Faste udgifter:**\n\n"
            for interval, amount in total_expenses.items():
                total_markdown += f"**{interval}:** {format_currency(amount, decimal_settings[interval])}\n\n"
            total_placeholder.markdown(total_markdown)

            # Update category tickers
            with category_container:
                for category in st.session_state.data['categories']:
                    st.subheader(category)
                    category_total = sum(item['amount'] for item in st.session_state.data['categories'][category].values())
                    category_per_second = category_total / (30 * 24 * 60 * 60)
                    
                    category_monthly = category_per_second * seconds_passed
                    st.write(f"Denne måned: {format_currency(category_monthly, decimal_settings['Måned'])}")
                    
                    for expense, details in st.session_state.data['categories'][category].items():
                        expense_monthly = details['amount']
                        st.write(f"- {expense}: {format_currency(expense_monthly, decimal_settings['Måned'])} /måned")
                    
                    st.write("---")

            time.sleep(1)
            st.empty()  # This triggers a rerun without using experimental_rerun

if __name__ == "__main__":
    main()
