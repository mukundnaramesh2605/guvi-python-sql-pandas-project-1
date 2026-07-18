import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from streamlit_db import Database

st.set_page_config(page_title="Visualizations | BrickView", page_icon="📈", layout="wide")

db = Database()

st.title("Visualizations")
st.caption("A fixed set of charts summarizing the full portfolio — not affected by filters.")

listings = db.run_query(
    "SELECT listingid, city, propertytype, price, sqft, datelisted FROM listings"
)
listings["datelisted"] = pd.to_datetime(listings["datelisted"])

sales = db.run_query("SELECT listingid, saleprice, datesold, daysonmarket FROM sales")
sales["datesold"] = pd.to_datetime(sales["datesold"])

listings_with_sales = listings.merge(sales, on="listingid", how="inner")

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


def new_fig():
    fig, ax = plt.subplots(figsize=(6, 4))
    return fig, ax


row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("📊 Average Price by City")
    price_by_city = listings.groupby("city")["price"].mean().sort_values(ascending=False)
    fig, ax = new_fig()
    ax.bar(price_by_city.index, price_by_city.values,
           color=[CITY_COLORS.get(c, "#999999") for c in price_by_city.index])
    ax.set_ylabel("Avg Price ($)")
    ax.tick_params(axis="x", rotation=30)
    st.pyplot(fig)

with row1_col2:
    st.subheader("🥧 Property Type Distribution")
    type_counts = listings["propertytype"].value_counts()
    fig, ax = new_fig()
    ax.pie(
        type_counts.values,
        labels=type_counts.index,
        autopct="%1.0f%%",
        colors=[PROPERTY_TYPE_COLORS.get(t, "#999999") for t in type_counts.index],
    )
    ax.axis("equal")
    st.pyplot(fig)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("📈 Monthly Listings vs. Sales Trend")
    listings_trend = listings.copy()
    listings_trend["month"] = listings_trend["datelisted"].dt.to_period("M").astype(str)
    listings_trend = listings_trend.groupby("month").size()

    sales_trend = sales.copy()
    sales_trend["month"] = sales_trend["datesold"].dt.to_period("M").astype(str)
    sales_trend = sales_trend.groupby("month").size()

    months = sorted(set(listings_trend.index) | set(sales_trend.index))
    fig, ax = new_fig()
    ax.plot(months, [listings_trend.get(m, 0) for m in months], marker="o", label="Listings", color="#2a78d6")
    ax.plot(months, [sales_trend.get(m, 0) for m in months], marker="o", label="Sales", color="#008300")
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    st.pyplot(fig)

with row2_col2:
    st.subheader("💰 Sale Price Distribution")
    fig, ax = new_fig()
    ax.hist(sales["saleprice"], bins=20, color="#2a78d6", edgecolor="white")
    ax.set_xlabel("Sale Price ($)")
    ax.set_ylabel("Number of Sales")
    st.pyplot(fig)

row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.subheader("🏠 Price vs. Sqft")
    fig, ax = new_fig()
    for ptype, group in listings.groupby("propertytype"):
        ax.scatter(group["sqft"], group["price"], label=ptype,
                   color=PROPERTY_TYPE_COLORS.get(ptype, "#999999"), alpha=0.6, s=20)
    ax.set_xlabel("Sqft")
    ax.set_ylabel("Price ($)")
    ax.legend()
    st.pyplot(fig)

with row3_col2:
    st.subheader("📅 Average Days on Market by City")
    dom_by_city = listings_with_sales.groupby("city")["daysonmarket"].mean().sort_values(ascending=False)
    fig, ax = new_fig()
    ax.bar(dom_by_city.index, dom_by_city.values,
           color=[CITY_COLORS.get(c, "#999999") for c in dom_by_city.index])
    ax.set_ylabel("Avg Days on Market")
    ax.tick_params(axis="x", rotation=30)
    st.pyplot(fig)
