import pandas as pd
import streamlit as st
from db import get_db
from ui_helpers import render_sidebar_footer

st.set_page_config(page_title="Filters | BrickView", page_icon="🔍", layout="wide")

db = get_db()
render_sidebar_footer()

st.title("🔍 Filters")
st.caption("Filter listings by city, property type, price, agent, and date to explore the underlying data.")

listings = db.run_query(
    """
    SELECT l.listingid, l.city, l.propertytype, l.price, l.sqft, l.datelisted,
           l.latitude, l.longitude, l.agentid, a.name AS agent_name
    FROM listings l
    JOIN agents a ON a.agentid = l.agentid
    """
)
listings["datelisted"] = pd.to_datetime(listings["datelisted"], format="mixed")

sales = db.run_query("SELECT listingid, saleprice, datesold, daysonmarket FROM sales")
sales["datesold"] = pd.to_datetime(sales["datesold"], format="mixed")

# ---------------------------------------------------------------- Filters
st.header("Filters")

cities = sorted(listings["city"].unique())
selected_cities = st.multiselect("City", options=cities, default=cities)

property_types = sorted(listings["propertytype"].unique())
selected_types = st.multiselect("Property Type", options=property_types, default=property_types)

price_min = float(listings["price"].min())
price_max = float(listings["price"].max())
selected_price = st.slider(
    "Price Range", min_value=price_min, max_value=price_max, value=(price_min, price_max), step=1000.0
)

agent_options = ["All Agents"] + sorted(listings["agent_name"].unique())
selected_agent = st.selectbox("Agent", options=agent_options)

date_min = listings["datelisted"].min().date()
date_max = listings["datelisted"].max().date()
selected_dates = st.date_input("Listed Date Range", value=(date_min, date_max))
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    date_start, date_end = selected_dates
else:
    date_start, date_end = date_min, date_max

# ---------------------------------------------------------------- Apply filters
filtered = listings[
    listings["city"].isin(selected_cities)
    & listings["propertytype"].isin(selected_types)
    & listings["price"].between(selected_price[0], selected_price[1])
    & listings["datelisted"].between(pd.Timestamp(date_start), pd.Timestamp(date_end))
]
if selected_agent != "All Agents":
    filtered = filtered[filtered["agent_name"] == selected_agent]

matched_sales = sales[sales["listingid"].isin(filtered["listingid"])]

if filtered.empty:
    st.warning("No listings match the current filters.")
    st.stop()

# ---------------------------------------------------------------- KPI row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Listings", f"{len(filtered):,}")
col2.metric("Avg Price", f"${filtered['price'].mean():,.0f}")
col3.metric("Sold (in view)", f"{len(matched_sales):,}")
col4.metric(
    "Avg Days on Market",
    f"{matched_sales['daysonmarket'].mean():,.1f}" if len(matched_sales) else "—",
)

st.divider()

# ---------------------------------------------------------------- Table view
st.subheader("📋 Listings Table")
st.dataframe(
    filtered.sort_values("price", ascending=False),
    use_container_width=True,
    hide_index=True,
)
