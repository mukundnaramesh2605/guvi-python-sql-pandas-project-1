import streamlit as st

from common import get_db

st.set_page_config(page_title="BrickView | Real Estate Analytics", page_icon="🏠", layout="wide")

db = get_db()

st.title("🏠 BrickView: Real Estate Analytics Platform")
st.markdown(
    "A **Real Estate Listings Dashboard** for analyzing property listings, agent performance, "
    "and sales patterns — with pricing and time-on-market insights, filtering by location, "
    "property type, price, and agent, and interactive maps and charts."
)

st.divider()

st.subheader("Portfolio at a Glance")

num_listings = db.run_query("SELECT COUNT(*) AS n FROM listings").iloc[0]["n"]
num_cities = db.run_query("SELECT COUNT(DISTINCT city) AS n FROM listings").iloc[0]["n"]
num_agents = db.run_query("SELECT COUNT(*) AS n FROM agents").iloc[0]["n"]
sales_summary = db.run_query(
    "SELECT COUNT(*) AS n, SUM(saleprice) AS revenue, AVG(daysonmarket) AS avg_dom FROM sales"
).iloc[0]

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Listings", f"{num_listings:,}")
col2.metric("Cities", f"{num_cities:,}")
col3.metric("Agents", f"{num_agents:,}")
col4.metric("Sales Closed", f"{sales_summary['n']:,}")
col5.metric("Total Revenue", f"${sales_summary['revenue']:,.0f}")
col6.metric("Avg Days on Market", f"{sales_summary['avg_dom']:,.1f}")

st.divider()

st.subheader("Explore the App")
nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    st.page_link(
        "pages/1_🔍_Filters_&_Visualizations.py",
        label="**Filters & Visualizations**",
        icon="🔍",
    )
    st.caption("Filter listings by city, property type, price, agent, and date — view them on a map, "
               "bar chart, pie chart, trend line, and table.")

with nav_col2:
    st.page_link("pages/2_📊_SQL_Insights.py", label="**SQL Insights**", icon="📊")
    st.caption("30 SQL queries covering pricing, sales performance, agent activity, and "
               "buyer financing — each with its query text and results.")

with nav_col3:
    st.page_link("pages/3_🛠️_CRUD_Operations.py", label="**CRUD Operations**", icon="🛠️")
    st.caption("View, add, update, and delete records in every table: agents, "
               "listings, sales, buyers, and property attributes.")
