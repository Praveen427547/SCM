import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime, timedelta

# 📌 Load Excel file and sheets
file_path = 'SCM_Data.xlsx'
inventory_data = pd.read_excel(file_path, sheet_name='Inventory')
sales_data = pd.read_excel(file_path, sheet_name='Sales')

# 📌 Demand Forecasting Function (Simple Moving Average)
def forecast_demand(product_id, months=3):
    product_sales = sales_data[sales_data['Product ID'] == product_id]
    if product_sales.empty:
        st.error("❌ No sales data available for this product.")
        return None

    product_sales = product_sales.sort_values(by='Date')
    product_sales['SMA'] = product_sales['Sales Quantity'].rolling(window=months).mean()
    forecast = product_sales['SMA'].iloc[-1]
    return round(forecast) if not pd.isna(forecast) else None

# 📌 Stock Check Function
def stock_check():
    product_id = st.text_input("Enter Product ID (e.g., P0023):").strip().upper()
    required_quantity = st.number_input("Enter Required Quantity:", min_value=1, value=1, step=1)
    required_date = st.date_input("Enter Required Date (YYYY-MM-DD):")
    required_date = datetime.combine(required_date, datetime.min.time())
    
    if st.button("Check Stock"):
        if product_id in inventory_data['Product ID'].values:
            product = inventory_data[inventory_data['Product ID'] == product_id].iloc[0]
            available_stock = product['Stock Quantity']
            reorder_level = product['Reorder Level']
            lead_time = product['Lead Time (Days)']
            reorder_quantity = product['Reorder Quantity']
            supplier_lead_time = product['Supplier Lead Time (Days)']

            st.write(f"\n📦 Available Stock for {product_id}: {available_stock} units")
            st.write(f"Reorder Level: {reorder_level} units")

            # Demand Forecast
            forecasted_demand = forecast_demand(product_id)
            if forecasted_demand:
                st.write(f"📊 Forecasted Demand for Next Month: {forecasted_demand} units")
                if available_stock >= forecasted_demand:
                    st.write("✅ Stock is sufficient for forecasted demand.")
                else:
                    st.write(f"⚠️ Expected Shortage: {forecasted_demand - available_stock} units")

            if available_stock >= required_quantity:
                st.write("✅ Stock is sufficient to meet the demand.")
            else:
                shortage = required_quantity - available_stock
                st.write(f"⚠️ Stock is insufficient by {shortage} units.")
                st.write(f"📢 Suggestion: Reorder {reorder_quantity} units.")
                reorder_arrival_date = datetime.today() + timedelta(days=int(supplier_lead_time))
                st.write(f"Expected Reorder Arrival Date: {reorder_arrival_date.date()}")

                if reorder_arrival_date > required_date:
                    st.write("🚨 Alarm: Reorder cannot arrive before required date!")
                else:
                    st.write("✅ Reorder can arrive before required date.")
        else:
            st.error("❌ Product not found in inventory!")

# 📌 Product Stats Function
def product_stats():
    product_id = st.text_input("Enter Product ID (e.g., P0023):").strip().upper()
    
    if st.button("View Product Stats"):
        if product_id in inventory_data['Product ID'].values:
            product_info = inventory_data[inventory_data['Product ID'] == product_id].iloc[0]
            
            product_name = product_info['Product Name']
            suppliers = product_info['Supplier Name']
            current_stock = product_info['Stock Quantity']
            reorder_level = product_info['Reorder Level']
            
            st.write(f"\n🏷️ Product Name: {product_name}")
            st.write(f"📦 Current Stock: {current_stock} units")
            st.write(f"📦 Reorder Level: {reorder_level} units")
            st.write(f"🏷️ Suppliers: {suppliers}")
            
            # On-Time Delivery Rate for the Product
            product_sales = sales_data[sales_data['Product ID'] == product_id]
            if not product_sales.empty:
                on_time_deliveries = product_sales[product_sales['Delivery Date'] <= product_sales['Promised Date']].shape[0]
                total_deliveries = product_sales.shape[0]
                on_time_delivery_rate = (on_time_deliveries / total_deliveries) * 100 if total_deliveries > 0 else 0
                st.write(f"🚚 On-Time Delivery Rate: {on_time_delivery_rate:.2f}%")
            else:
                st.write("🚚 On-Time Delivery Rate: No deliveries found for this product.")
            
            # Total Sales
            total_sales = product_sales['Sales Quantity'].sum() if not product_sales.empty else 0
            st.write(f"📊 Total Sales: {total_sales} units")
        else:
            st.error("❌ Product not found in inventory!")

# 📌 KPI Calculation Functions (Updated)
def calculate_kpis():
    st.write("\n📊 Key Performance Indicators (KPIs) 📊")
    
    # On-Time Delivery Rate
    on_time_deliveries = sales_data[sales_data['Delivery Date'] <= sales_data['Promised Date']].shape[0]
    total_deliveries = sales_data.shape[0]
    on_time_delivery_rate = (on_time_deliveries / total_deliveries) * 100
    st.write(f"🚚 On-Time Delivery Rate: {on_time_delivery_rate:.2f}%")
    
    # Top 5 Selling Products
    top_selling = sales_data.groupby('Product ID')['Sales Quantity'].sum().sort_values(ascending=False).head(5)
    st.write("\n🔥 Top 5 Selling Products:")
    for product_id, sales in top_selling.items():
        st.write(f"{product_id}: {sales} units sold")
    
    # 🆕 Top 5 Least Sold Products
    least_selling = sales_data.groupby('Product ID')['Sales Quantity'].sum().sort_values().head(5)
    st.write("\n❄️ Top 5 Least Sold Products:")
    for product_id, sales in least_selling.items():
        st.write(f"{product_id}: {sales} units sold")

# 📌 Main Function with Menu
def main():
    st.title("📦 Supply Chain Management System")
    
    menu = ["Check Stock", "View KPIs", "View Product Stats", "Exit"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == 'Check Stock':
        st.subheader("Check Stock")
        stock_check()
    elif choice == 'View KPIs':
        st.subheader("View KPIs")
        calculate_kpis()
    elif choice == 'View Product Stats':
        st.subheader("View Product Stats")
        product_stats()
    elif choice == 'Exit':
        st.write("👋 Exiting... Have a great day!")
        st.stop()

# Run the main function
if __name__ == "__main__":
    main()
