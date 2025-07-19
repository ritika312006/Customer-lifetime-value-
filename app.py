import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Page Config ---
st.set_page_config(page_title="CLV Prediction", layout="wide")
st.title("Customer Lifetime Value (CLV) - Prediction")

st.markdown("This dashboard loads sales data directly from your project directory for CLV insights and sales trends.")

# --- Read CSV directly from folder ---
file_path = "online_retail_II(Year 2010-2011).csv"

if os.path.exists(file_path):
    try:
        df = pd.read_csv(
            file_path,
            encoding='ISO-8859-1',
            names=['invoice', 'stockcode', 'description', 'quantity', 'invoicedate',
                   'unitprice', 'customerid', 'country'],
            header=0,
            parse_dates=['invoicedate']
        )

        # --- Clean & Prepare ---
        df['invoicedate'] = pd.to_datetime(df['invoicedate'], errors='coerce')
        df = df.dropna(subset=['invoicedate', 'quantity', 'unitprice'])
        df['profit'] = df['quantity'] * df['unitprice'] * 0.2

        st.success("✅ Dataset loaded successfully!")

        # --- Dataset Overview ---
        st.subheader("🧾 Dataset Overview")
        col1, col2 = st.columns(2)
        col1.markdown(f"- **Rows:** {df.shape[0]:,}")
        col1.markdown(f"- **Columns:** {df.shape[1]}")
        col2.markdown(f"- **Unique Products:** {df['description'].nunique()}")
        col2.markdown(f"- **Unique Customers:** {df['customerid'].nunique()}")

        # --- Product & Country Insights ---
        st.subheader("🏆 Top Insights (Visualized)")

        # Top 5 selling products
        top_selling_products = df.groupby('description')['quantity'].sum().sort_values(ascending=False).head(5)
        st.markdown("**🔝 Top 5 Selling Products**")
        fig_top_selling = px.bar(
            top_selling_products,
            x=top_selling_products.values,
            y=top_selling_products.index,
            orientation='h',
            labels={'x': 'Units Sold', 'description': 'Product'},
            title="Top 5 Selling Products",
            color=top_selling_products.values,
            color_continuous_scale="Teal"
        )
        st.plotly_chart(fig_top_selling, use_container_width=True)

        # Top 5 profitable products
        top_profitable_products = df.groupby('description')['profit'].sum().sort_values(ascending=False).head(5)
        st.markdown("**💸 Top 5 Most Profitable Products**")
        fig_top_profit = px.bar(
            top_profitable_products,
            x=top_profitable_products.values,
            y=top_profitable_products.index,
            orientation='h',
            labels={'x': 'Profit', 'description': 'Product'},
            title="Top 5 Profitable Products",
            color=top_profitable_products.values,
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_top_profit, use_container_width=True)

        # Top 3 countries by orders
        top_countries = df['country'].value_counts().head(3)
        st.markdown("**🌍 Top 3 Countries by Order Volume**")
        fig_countries = px.pie(
            names=top_countries.index,
            values=top_countries.values,
            title="Top 3 Countries by Orders",
            hole=0.4
        )
        st.plotly_chart(fig_countries, use_container_width=True)

        # Customers with loss (negative profit)
        loss_customers = df.groupby('customerid')['profit'].sum()
        num_loss_customers = (loss_customers < 0).sum()
        st.info(f"⚠️ **{num_loss_customers} customers** had a **net loss**, mostly due to returns or cancellations.")

        # --- Filters ---
        st.subheader("🔍 Filter Data")
        col1, col2 = st.columns(2)
        search_text = col1.text_input("Search Description")
        countries = df['country'].dropna().unique().tolist()
        selected_country = col2.selectbox("Select Country", options=["All"] + sorted(countries))

        filtered_df = df.copy()
        if search_text:
            filtered_df = filtered_df[filtered_df['description'].str.contains(search_text, case=False, na=False)]
        if selected_country != "All":
            filtered_df = filtered_df[filtered_df['country'] == selected_country]

        # --- KPIs ---
        st.subheader("📊 Key Metrics")
        total_sales = (filtered_df['quantity'] * filtered_df['unitprice']).sum()
        total_profit = filtered_df['profit'].sum()
        date_min = filtered_df['invoicedate'].min()
        date_max = filtered_df['invoicedate'].max()

        k1, k2, k3 = st.columns(3)
        k1.metric("🛒 Total Sales", f"${total_sales:,.2f}")
        k2.metric("💰 Total Profit", f"${total_profit:,.2f}")
        k3.metric("📅 Date Range", f"{date_min.date()} → {date_max.date()}")

        # --- Download Filtered Data ---
        st.download_button("⬇️ Download Filtered Data as CSV", data=filtered_df.to_csv(index=False),
                           file_name="filtered_sales.csv", mime="text/csv")

        # --- Data Table ---
        st.subheader("📄 Data Preview")
        st.dataframe(filtered_df.head(20), use_container_width=True)

        # --- Sales Over Time ---
        st.subheader("📈 Sales Over Time")
        sales_over_time = filtered_df.groupby('invoicedate').apply(lambda x: (x['quantity'] * x['unitprice']).sum())
        st.line_chart(sales_over_time)

        # --- Monthly Trend ---
        st.subheader("📆 Monthly Sales Trend")
        monthly_sales = filtered_df.resample('M', on='invoicedate').apply(lambda x: (x['quantity'] * x['unitprice']).sum())
        st.line_chart(monthly_sales)

        # --- CLV Chart: Top Customers ---
        st.subheader("👤 Top 10 Customers by Total Spend")
        clv = filtered_df.groupby('customerid').apply(lambda x: (x['quantity'] * x['unitprice']).sum())
        clv = clv.sort_values(ascending=False).head(10)
        st.bar_chart(clv)

        # --- Pie Chart: Orders by Country ---
        st.subheader("🌍 Orders Distribution by Country")
        order_dist = filtered_df['country'].value_counts()
        fig = px.pie(values=order_dist.values, names=order_dist.index, title="Orders by Country")
        st.plotly_chart(fig)

        st.markdown("---")
        st.caption("Built for CLV Prediction — Simple, Reusable, and Insightful.")

    except Exception as e:
        st.error(f"❌ Failed to process file: {e}")
else:
    st.error(f"❌ File not found: `{file_path}` — Please ensure it exists in the same folder as this app.")

# --- Use Cases and About section ---
st.markdown("---")
with st.expander("💡 Use Cases: How This Dashboard Helps"):
    st.markdown("""
    - 📊 **Track sales performance** over time to identify seasonal trends.
    - 👤 **Discover high-value customers** by calculating total spending.
    - 🌍 **Understand geographic demand** using country-wise sales insights.
    - 💰 **Optimize marketing spend** by focusing on top-performing customers.
    """)

with st.expander("📘 About This Project"):
    st.markdown("""
    This project was created as part of my internship to demonstrate how businesses can analyze transactional sales data
    to make smarter decisions using Customer Lifetime Value (CLV) principles.

    **Built With:**
    - Python 🐍
    - Streamlit 📈
    - Pandas + Plotly for interactive charts

    **Made by:** *Ritika Bagoria*  
    [GitHub Repo](https://github.com/ritika312006/CLV---prediction)
    """)
