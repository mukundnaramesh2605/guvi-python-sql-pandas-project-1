import pandas as pd
import plotly.express as px
import streamlit as st

from common import get_db

st.set_page_config(page_title="Filters & Visualizations | BrickView", page_icon="🔍", layout="wide")

db = get_db()

st.title("🔍 Filters & Visualizations")
st.caption("Explore listings, pricing, sales performance, and agent activity across the portfolio.")

# Load everything once, then filter with plain pandas below.
listings = db.run_query(
    """
    SELECT l.listingid, l.city, l.propertytype, l.price, l.sqft, l.datelisted,
           l.latitude, l.longitude, l.agentid, a.name AS agent_name
    FROM listings l
    JOIN agents a ON a.agentid = l.agentid
    """
)
listings["datelisted"] = pd.to_datetime(listings["datelisted"])

sales = db.run_query("SELECT listingid, saleprice, datesold, daysonmarket FROM sales")
sales["datesold"] = pd.to_datetime(sales["datesold"])

# Fixed colors so the same city/property type always gets the same color.
CITY_COLORS = {
    "Chicago": "#2a78d6",
    "Houston": "#008300",
    "Los Angeles": "#e87ba4",
    "New York": "#eda100",
    "Phoenix": "#1baf7a",
}
PROPERTY_TYPE_COLORS = {
    "Apartment": "#2a78d6",
    "Condo": "#008300",
    "House": "#e87ba4",
    "Townhouse": "#eda100",
}

# ---------------------------------------------------------------- Sidebar filters
st.sidebar.header("Filters")

cities = sorted(listings["city"].unique())
selected_cities = st.sidebar.multiselect("City", options=cities, default=cities)

property_types = sorted(listings["propertytype"].unique())
selected_types = st.sidebar.multiselect("Property Type", options=property_types, default=property_types)

price_min = float(listings["price"].min())
price_max = float(listings["price"].max())
selected_price = st.sidebar.slider(
    "Price Range", min_value=price_min, max_value=price_max, value=(price_min, price_max), step=1000.0
)

agent_options = ["All Agents"] + sorted(listings["agent_name"].unique())
selected_agent = st.sidebar.selectbox("Agent", options=agent_options)

date_min = listings["datelisted"].min().date()
date_max = listings["datelisted"].max().date()
selected_dates = st.sidebar.date_input("Listed Date Range", value=(date_min, date_max))
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

# ---------------------------------------------------------------- Map
st.subheader("🗺️ Listings Map")
map_fig = px.scatter_mapbox(
    filtered,
    lat="latitude",
    lon="longitude",
    color="city",
    color_discrete_map=CITY_COLORS,
    hover_name="listingid",
    hover_data=["propertytype", "price"],
    zoom=3,
    height=450,
)
map_fig.update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(map_fig, use_container_width=True)

# ---------------------------------------------------------------- Bar + Pie
bar_col, pie_col = st.columns(2)

with bar_col:
    st.subheader("📊 Average Price by City")
    price_by_city = filtered.groupby("city", as_index=False)["price"].mean()
    bar_fig = px.bar(price_by_city, x="city", y="price", color="city", color_discrete_map=CITY_COLORS)
    bar_fig.update_layout(showlegend=False, yaxis_title="Avg Price ($)", xaxis_title="")
    st.plotly_chart(bar_fig, use_container_width=True)

with pie_col:
    st.subheader("🥧 Property Type Distribution")
    type_counts = filtered["propertytype"].value_counts().reset_index()
    type_counts.columns = ["propertytype", "count"]
    pie_fig = px.pie(
        type_counts,
        names="propertytype",
        values="count",
        color="propertytype",
        color_discrete_map=PROPERTY_TYPE_COLORS,
    )
    st.plotly_chart(pie_fig, use_container_width=True)

# ---------------------------------------------------------------- Line chart
st.subheader("📈 Monthly Listings vs. Sales Trend")
listings_trend = filtered.copy()
listings_trend["month"] = listings_trend["datelisted"].dt.to_period("M").astype(str)
listings_trend = listings_trend.groupby("month").size().reset_index(name="count")
listings_trend["series"] = "Listings"

sales_trend = matched_sales.copy()
sales_trend["month"] = sales_trend["datesold"].dt.to_period("M").astype(str)
sales_trend = sales_trend.groupby("month").size().reset_index(name="count")
sales_trend["series"] = "Sales"

trend_df = pd.concat([listings_trend, sales_trend], ignore_index=True).sort_values("month")
line_fig = px.line(
    trend_df,
    x="month",
    y="count",
    color="series",
    markers=True,
    color_discrete_map={"Listings": "#2a78d6", "Sales": "#008300"},
)
line_fig.update_layout(yaxis_title="Count", xaxis_title="")
st.plotly_chart(line_fig, use_container_width=True)

# ---------------------------------------------------------------- Table view
st.subheader("📋 Listings Table")
st.dataframe(
    filtered.sort_values("price", ascending=False),
    use_container_width=True,
    hide_index=True,
)
