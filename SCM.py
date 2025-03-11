import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Supply Chain Management", layout="wide")
st.title("📦 Supply Chain Management System")

# File upload
uploaded_file = st.sidebar.file_uploader("Upload Excel File", type="xlsx")

if uploaded_file is not None:
    # Load Excel file and sheets
    inventory_data = pd.read_excel(uploaded_file, sheet_name='Inventory')
    sales_data = pd.read_excel(uploaded_file, sheet_name='Sales')
    
    # Demand Forecasting Function (Simple Moving Average)
    def forecast_demand(product_id, months=3):
        product_sales = sales_data[sales_data['Product ID'] == product_id]
        if product_sales.empty:
            st.error("❌ No sales data available for this product.")
            return None

        product_sales = product_sales.sort_values(by='Date')
        product_sales['SMA'] = product_sales['Sales Quantity'].rolling(window=months).mean()
        forecast = product_sales['SMA'].iloc[-1]
        return round(forecast) if not pd.isna(forecast) else None

    # Stock Check Function
    def stock_check():
        st.subheader("Check Stock")
        
        product_id = st.text_input("Enter Product ID (e.g., P0023):").strip().upper()
        required_quantity = st.number_input("Enter Required Quantity:", min_value=1, value=10)
        required_date = st.date_input("Enter Required Date:")
        required_date = datetime.combine(required_date, datetime.min.time())
        
        if st.button("Check Stock"):
            if product_id in inventory_data['Product ID'].values:
                product = inventory_data[inventory_data['Product ID'] == product_id].iloc[0]
                available_stock = product['Stock Quantity']
                reorder_level = product['Reorder Level']
                lead_time = product['Lead Time (Days)']
                reorder_quantity = product['Reorder Quantity']
                supplier_lead_time = product['Supplier Lead Time (Days)']

                results = []
                results.append(f"📦 Available Stock for {product_id}: {available_stock} units")
                results.append(f"Reorder Level: {reorder_level} units")

                # Demand Forecast
                forecasted_demand = forecast_demand(product_id)
                if forecasted_demand:
                    results.append(f"📊 Forecasted Demand for Next Month: {forecasted_demand} units")
                    if available_stock >= forecasted_demand:
                        results.append("✅ Stock is sufficient for forecasted demand.")
                    else:
                        results.append(f"⚠️ Expected Shortage: {forecasted_demand - available_stock} units")

                if available_stock >= required_quantity:
                    results.append("✅ Stock is sufficient to meet the demand.")
                else:
                    shortage = required_quantity - available_stock
                    results.append(f"⚠️ Stock is insufficient by {shortage} units.")
                    results.append(f"📢 Suggestion: Reorder {reorder_quantity} units.")
                    reorder_arrival_date = datetime.today() + timedelta(days=int(supplier_lead_time))
                    results.append(f"Expected Reorder Arrival Date: {reorder_arrival_date.date()}")

                    if reorder_arrival_date > required_date:
                        results.append("🚨 Alarm: Reorder cannot arrive before required date!")
                    else:
                        results.append("✅ Reorder can arrive before required date.")
                
                for result in results:
                    st.write(result)
            else:
                st.error("❌ Product not found in inventory!")

    # Product Stats Function
    def product_stats():
        st.subheader("Product Statistics")
        
        product_id = st.text_input("Enter Product ID (e.g., P0023) for statistics:").strip().upper()
        
        if st.button("View Product Stats"):
            if product_id in inventory_data['Product ID'].values:
                product_info = inventory_data[inventory_data['Product ID'] == product_id].iloc[0]
                
                product_name = product_info['Product Name']
                suppliers = product_info['Supplier Name']
                current_stock = product_info['Stock Quantity']
                reorder_level = product_info['Reorder Level']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"🏷️ Product Name: {product_name}")
                    st.write(f"📦 Current Stock: {current_stock} units")
                
                with col2:
                    st.write(f"📦 Reorder Level: {reorder_level} units")
                    st.write(f"🏷️ Suppliers: {suppliers}")
                
                # On-Time Delivery Rate for the Product
                product_sales = sales_data[sales_data['Product ID'] == product_id]
                if not product_sales.empty:
                    on_time_deliveries = product_sales[product_sales['Delivery Date'] <= product_sales['Promised Date']].shape[0]
                    total_deliveries = product_sales.shape[0]
                    on_time_delivery_rate = (on_time_deliveries / total_deliveries) * 100 if total_deliveries > 0 else 0
                    st.write(f"🚚 On-Time Delivery Rate: {on_time_delivery_rate:.2f}%")
                    
                    # Total Sales
                    total_sales = product_sales['Sales Quantity'].sum()
                    st.write(f"📊 Total Sales: {total_sales} units")
                    
                    # Sales Trend Chart
                    st.subheader("Sales Trend")
                    product_sales_by_date = product_sales.groupby('Date')['Sales Quantity'].sum().reset_index()
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.plot(product_sales_by_date['Date'], product_sales_by_date['Sales Quantity'])
                    ax.set_xlabel('Date')
                    ax.set_ylabel('Sales Quantity')
                    ax.set_title(f'Sales Trend for {product_name}')
                    st.pyplot(fig)
                else:
                    st.write("🚚 On-Time Delivery Rate: No deliveries found for this product.")
                    st.write("📊 Total Sales: 0 units")
            else:
                st.error("❌ Product not found in inventory!")

    # KPI Calculation Functions
    def calculate_kpis():
        st.subheader("📊 Key Performance Indicators (KPIs)")
        
        # On-Time Delivery Rate
        on_time_deliveries = sales_data[sales_data['Delivery Date'] <= sales_data['Promised Date']].shape[0]
        total_deliveries = sales_data.shape[0]
        on_time_delivery_rate = (on_time_deliveries / total_deliveries) * 100
        
        # Create metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🚚 On-Time Delivery Rate", f"{on_time_delivery_rate:.2f}%")
        
        # Top 5 Selling Products
        top_selling = sales_data.groupby('Product ID')['Sales Quantity'].sum().sort_values(ascending=False).head(5)
        
        # Top 5 Least Sold Products
        least_selling = sales_data.groupby('Product ID')['Sales Quantity'].sum().sort_values().head(5)
        
        # Create two columns for the charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔥 Top 5 Selling Products")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(top_selling.index, top_selling.values)
            ax.set_xlabel('Product ID')
            ax.set_ylabel('Sales Quantity')
            ax.set_title('Top 5 Selling Products')
            plt.xticks(rotation=45)
            st.pyplot(fig)
            
            # Also show as text
            for product_id, sales in top_selling.items():
                st.write(f"{product_id}: {sales} units sold")
        
        with col2:
            st.subheader("❄️ Top 5 Least Sold Products")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(least_selling.index, least_selling.values)
            ax.set_xlabel('Product ID')
            ax.set_ylabel('Sales Quantity')
            ax.set_title('Top 5 Least Sold Products')
            plt.xticks(rotation=45)
            st.pyplot(fig)
            
            # Also show as text
            for product_id, sales in least_selling.items():
                st.write(f"{product_id}: {sales} units sold")

    # Main App with Sidebar Navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Select a page:", 
                               ["Check Stock", "View KPIs", "View Product Stats"])

    if app_mode == "Check Stock":
        stock_check()
    elif app_mode == "View KPIs":
        calculate_kpis()
    elif app_mode == "View Product Stats":
        product_stats()
else:
    st.info("Please upload an Excel file with 'Inventory' and 'Sales' sheets to begin.")
    
    # Sample data structure explanation
    st.header("Expected Data Format")
    st.subheader("Inventory Sheet")
    st.markdown("""
    The inventory sheet should contain the following columns:
    - Product ID (e.g., P0023)
    - Product Name
    - Stock Quantity
    - Reorder Level
    - Reorder Quantity
    - Lead Time (Days)
    - Supplier Name
    - Supplier Lead Time (Days)
    """)
    
    st.subheader("Sales Sheet")
    st.markdown("""
    The sales sheet should contain the following columns:
    - Product ID (e.g., P0023)
    - Date
    - Sales Quantity
    - Promised Date
    - Delivery Date
    """)
