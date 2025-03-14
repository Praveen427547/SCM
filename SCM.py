import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime, timedelta
import matplotlib.dates as mdates

st.title("📦 Supply Chain Management System")

# Data source selection
data_source = st.sidebar.radio("Select Data Source:", ["Upload your ERP Data","Use Owner Data"])

# Initialize inventory_data and sales_data as None
inventory_data = None
sales_data = None

# Load data based on selection
if data_source == "Use Owner Data":
    # Load from default file path
    try:
        file_path = 'SCM_Data.xlsx'
        inventory_data = pd.read_excel(file_path, sheet_name='Inventory')
        sales_data = pd.read_excel(file_path, sheet_name='Sales')
        st.sidebar.success("✅ Default data loaded successfully!")
    except Exception as e:
        st.sidebar.error(f"❌ Error loading default data: {e}")
else:
    # File upload
    uploaded_file = st.sidebar.file_uploader("Upload ypur ERP Data", type="xlsx")
    if uploaded_file is not None:
        try:
            inventory_data = pd.read_excel(uploaded_file, sheet_name='Inventory')
            sales_data = pd.read_excel(uploaded_file, sheet_name='Sales')
            st.sidebar.success("✅ Uploaded data loaded successfully!")
        except Exception as e:
            st.sidebar.error(f"❌ Error loading uploaded data: {e}")

# Only show the app if data is loaded
if inventory_data is not None and sales_data is not None:
    # Ensure date columns are datetime objects
    date_columns = ['Date', 'Promised Date', 'Delivery Date']
    for col in date_columns:
        if col in sales_data.columns:
            sales_data[col] = pd.to_datetime(sales_data[col])

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

    # 📌 Product Stats Function with Last 12 Sales Time Series
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
                product_sales = sales_data[sales_data['Product ID'] == product_id].copy()
                
                if not product_sales.empty:
                    on_time_deliveries = product_sales[product_sales['Delivery Date'] <= product_sales['Promised Date']].shape[0]
                    total_deliveries = product_sales.shape[0]
                    on_time_delivery_rate = (on_time_deliveries / total_deliveries) * 100 if total_deliveries > 0 else 0
                    st.write(f"🚚 On-Time Delivery Rate: {on_time_delivery_rate:.2f}%")
                
                    # Total Sales
                    total_sales = product_sales['Sales Quantity'].sum()
                    st.write(f"📊 Total Sales: {total_sales} units")
                    
                    # Last 12 Sales Plot (Time Series)
                    st.subheader("📈 Last 12 Sales Transactions")
                    
                    # Ensure Date column is datetime
                    product_sales['Date'] = pd.to_datetime(product_sales['Date'])
                    
                    # Sort by date and get the last 12 sales
                    product_sales = product_sales.sort_values(by='Date', ascending=True)
                    last_12_sales = product_sales.tail(12)
                    
                    if not last_12_sales.empty:
                        # Create the plot
                        fig, ax = plt.subplots(figsize=(12, 6))
                        
                        # Plot the data with markers
                        ax.plot(
                            last_12_sales['Date'], 
                            last_12_sales['Sales Quantity'],
                            marker='o', 
                            linestyle='-', 
                            color='#1f77b4', 
                            linewidth=2,
                            markersize=8
                        )
                        
                        # Set labels and title
                        ax.set_xlabel('Date')
                        ax.set_ylabel('Sales Quantity')
                        ax.set_title(f'Last 12 Sales for {product_name} ({product_id})')
                        
                        # Format x-axis to show dates clearly
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                        plt.xticks(rotation=45)
                        
                        # Add grid
                        ax.grid(True, linestyle='--', alpha=0.7)
                        
                        # Add data point labels
                        for i, row in last_12_sales.iterrows():
                            ax.annotate(
                                f'{int(row["Sales Quantity"])}', 
                                (row['Date'], row['Sales Quantity']),
                                textcoords="offset points", 
                                xytext=(0,10), 
                                ha='center'
                            )
                        
                        # Adjust y-axis to start from 0 and have some headroom
                        max_sales = last_12_sales['Sales Quantity'].max()
                        ax.set_ylim(0, max_sales * 1.2 if max_sales > 0 else 10)
                        
                        # Add tight layout
                        plt.tight_layout()
                        
                        # Show the plot
                        st.pyplot(fig)
                        
                    else:
                        st.write("❌ No sales data found for this product.")
                else:
                    st.write("🚚 On-Time Delivery Rate: No deliveries found for this product.")
                    st.write("📊 Total Sales: 0 units")
                    st.write("❌ No sales data available for plotting.")
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
        menu = ["Check Stock", "View KPIs", "View Product Stats"]
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

    # Run the main function
    main()
else:
    if data_source == "Upload Excel File" and not st.sidebar.file_uploader:
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
