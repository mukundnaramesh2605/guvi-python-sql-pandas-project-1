import math

import pandas as pd
import streamlit as st
from db import Database
from ui_helpers import render_sidebar_footer
st.set_page_config(page_title="CRUD Operations | BrickView", layout="wide")

db = Database()
render_sidebar_footer()

st.title("CRUD Operations")
st.caption("Create, read, update, and delete records across every table in the schema.")

table = st.selectbox(
    "Choose a table", ["Agents", "Listings", "Sales", "Buyers", "Property Attributes"]
)


def paginate_dataframe(df: pd.DataFrame, key_prefix: str, label: str):
    total = len(df)
    size_key = f"{key_prefix}_page_size"
    page_key = f"{key_prefix}_page"

    col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
    with col1:
        page_size = st.selectbox("Rows per page", [10, 25, 50, 100], index=1, key=size_key)

    total_pages = max(1, math.ceil(total / page_size))
    st.session_state[page_key] = min(st.session_state.get(page_key, 1), total_pages)

    with col2:
        if st.button("⬅ Prev", key=f"{key_prefix}_prev", disabled=st.session_state[page_key] <= 1):
            st.session_state[page_key] -= 1
    with col3:
        st.markdown(
            f"<div style='text-align:center; padding-top:0.5rem'>Page {st.session_state[page_key]} of {total_pages}</div>",
            unsafe_allow_html=True,
        )
    with col4:
        if st.button("Next ➡", key=f"{key_prefix}_next", disabled=st.session_state[page_key] >= total_pages):
            st.session_state[page_key] += 1

    page = st.session_state[page_key]
    start = (page - 1) * page_size
    end = start + page_size
    display_df = df.iloc[start:end]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.caption(f"Showing {start + 1 if total else 0}-{min(end, total)} of {total} {label}")


# AGENTS


def view_agents():
    df = db.run_query("SELECT * FROM agents ORDER BY agentid")
    paginate_dataframe(df, "agents", "agents")


def add_agent():
    with st.form("add_agent_form"):
        agentid = st.text_input("Agent ID (e.g. A0051)")
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        email = st.text_input("Email")
        commissionrate = st.number_input("Commission Rate (%)", min_value=0.0, step=0.1)
        dealsclosed = st.number_input("Deals Closed", min_value=0, step=1)
        rating = st.number_input("Rating", min_value=0.0, max_value=5.0, step=0.1)
        experienceyears = st.number_input("Experience (years)", min_value=0, step=1)
        avgclosingdays = st.number_input("Avg Closing Days", min_value=0, step=1)
        submitted = st.form_submit_button("Add Agent")

    if submitted:
        try:
            db.cursor.execute(
                "INSERT INTO agents (agentid, name, phone, email, commissionrate, "
                "dealsclosed, rating, experienceyears, avgclosingdays) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (agentid, name, phone, email, commissionrate, dealsclosed, rating,
                 experienceyears, avgclosingdays),
            )
            db.conn.commit()
            st.success(f"Agent {agentid} added.")
            st.rerun()
        except Exception as e:
            db.conn.rollback()
            st.error(f"Could not add agent: {e}")


def update_agent():
    agent_ids = db.run_query("SELECT agentid FROM agents ORDER BY agentid")["agentid"].tolist()
    if not agent_ids:
        st.info("No agents yet.")
        return

    selected_id = st.selectbox("Select Agent ID to update", agent_ids)
    row = pd.read_sql("SELECT * FROM agents WHERE agentid = ?", db.conn, params=(selected_id,)).iloc[0]

    with st.form("update_agent_form"):
        name = st.text_input("Name", value=row["name"])
        phone = st.text_input("Phone", value=row["phone"])
        email = st.text_input("Email", value=row["email"])
        commissionrate = st.number_input("Commission Rate (%)", value=float(row["commissionrate"]), step=0.1)
        dealsclosed = st.number_input("Deals Closed", value=int(row["dealsclosed"]), step=1)
        rating = st.number_input("Rating", value=float(row["rating"]), min_value=0.0, max_value=5.0, step=0.1)
        experienceyears = st.number_input("Experience (years)", value=int(row["experienceyears"]), step=1)
        avgclosingdays = st.number_input("Avg Closing Days", value=int(row["avgclosingdays"]), step=1)
        submitted = st.form_submit_button("Update Agent")

    if submitted:
        try:
            db.cursor.execute(
                "UPDATE agents SET name=?, phone=?, email=?, commissionrate=?, dealsclosed=?, "
                "rating=?, experienceyears=?, avgclosingdays=? WHERE agentid=?",
                (name, phone, email, commissionrate, dealsclosed, rating,
                 experienceyears, avgclosingdays, selected_id),
            )
            db.conn.commit()
            st.success(f"Agent {selected_id} updated.")
            st.rerun()
        except Exception as e:
            db.conn.rollback()
            st.error(f"Could not update agent: {e}")


def delete_agent():
    agent_ids = db.run_query("SELECT agentid FROM agents ORDER BY agentid")["agentid"].tolist()
    if not agent_ids:
        st.info("No agents yet.")
        return

    selected_id = st.selectbox("Select Agent ID to delete", agent_ids, key="delete_agent_select")
    row = pd.read_sql("SELECT * FROM agents WHERE agentid = ?", db.conn, params=(selected_id,))
    st.dataframe(row, use_container_width=True, hide_index=True)

    confirm = st.checkbox(f"Yes, delete agent {selected_id}", key="confirm_delete_agent")
    if st.button("Delete Agent", disabled=not confirm):
        try:
            db.cursor.execute("DELETE FROM agents WHERE agentid = ?", (selected_id,))
            db.conn.commit()
            st.success(f"Agent {selected_id} deleted.")
            st.rerun()
        except Exception as e:
            db.conn.rollback()
            st.error(f"Could not delete agent (still referenced by listings): {e}")



# LISTINGS

def view_listings():
    df = db.run_query("SELECT * FROM listings ORDER BY listingid")
    paginate_dataframe(df, "listings", "listings")


def add_listing():
    agent_ids = db.run_query("SELECT agentid FROM agents ORDER BY agentid")["agentid"].tolist()

    with st.form("add_listing_form"):
        listingid = st.text_input("Listing ID (e.g. L21201)")
        city = st.text_input("City")
        propertytype = st.selectbox("Property Type", ["Apartment", "Condo", "House", "Townhouse"])
        price = st.number_input("Price", min_value=0.0, step=1000.0)
        sqft = st.number_input("Sqft", min_value=0.0, step=10.0)
        datelisted = st.date_input("Date Listed")
        agentid = st.selectbox("Agent ID", agent_ids)
        latitude = st.number_input("Latitude", value=0.0, format="%.2f")
        longitude = st.number_input("Longitude", value=0.0, format="%.2f")
        submitted = st.form_submit_button("Add Listing")

    if submitted:
        try:
            db.cursor.execute(
                "INSERT INTO listings (listingid, city, propertytype, price, sqft, datelisted, "
                "agentid, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (listingid, city, propertytype, price, sqft, str(datelisted), agentid, latitude, longitude),
            )
            db.conn.commit()
            st.success(f"Listing {listingid} added.")
            st.rerun()
        except Exception as e:
            db.conn.rollback()
            st.error(f"Could not add listing: {e}")


def update_listing():
    listing_ids = db.run_query("SELECT listingid FROM listings ORDER BY listingid")["listingid"].tolist()
    if not listing_ids:
        st.info("No listings yet.")
        return

    selected_id = st.selectbox("Select Listing ID to update", listing_ids)
    row = pd.read_sql("SELECT * FROM listings WHERE listingid = ?", db.conn, params=(selected_id,)).iloc[0]
    agent_ids = db.run_query("SELECT agentid FROM agents ORDER BY agentid")["agentid"].tolist()

    with st.form("update_listing_form"):
        city = st.text_input("City", value=row["city"])
        property_options = ["Apartment", "Condo", "House", "Townhouse"]
        propertytype = st.selectbox("Property Type", property_options, index=property_options.index(row["propertytype"]))
        price = st.number_input("Price", value=float(row["price"]), min_value=0.0, step=1000.0)
        sqft = st.number_input("Sqft", value=float(row["sqft"]), min_value=0.0, step=10.0)
        datelisted = st.date_input("Date Listed", value=pd.to_datetime(row["datelisted"]).date())
        agentid = st.selectbox("Agent ID", agent_ids, index=agent_ids.index(row["agentid"]) if row["agentid"] in agent_ids else 0)
        latitude = st.number_input("Latitude", value=float(row["latitude"]), format="%.2f")
        longitude = st.number_input("Longitude", value=float(row["longitude"]), format="%.2f")
        submitted = st.form_submit_button("Update Listing")

    if submitted:
        try:
            db.cursor.execute(
                "UPDATE listings SET city=?, propertytype=?, price=?, sqft=?, datelisted=?, "
                "agentid=?, latitude=?, longitude=? WHERE listingid=?",
                (city, propertytype, price, sqft, str(datelisted), agentid, latitude, longitude, selected_id),
            )
            db.conn.commit()
            st.success(f"Listing {selected_id} updated.")
            st.rerun()
        except Exception as e:
            db.conn.rollback()
            st.error(f"Could not update listing: {e}")


def delete_listing():
    listing_ids = db.run_query("SELECT listingid FROM listings ORDER BY listingid")["listingid"].tolist()
    if not listing_ids:
        st.info("No listings yet.")
        return

    selected_id = st.selectbox("Select Listing ID to delete", listing_ids, key="delete_listing_select")
    row = pd.read_sql("SELECT * FROM listings WHERE listingid = ?", db.conn, params=(selected_id,))
    st.dataframe(row, use_container_width=True, hide_index=True)

    confirm = st.checkbox(f"Yes, delete listing {selected_id}", key="confirm_delete_listing")
    if st.button("Delete Listing", disabled=not confirm):
        try:
            db.cursor.execute("DELETE FROM listings WHERE listingid = ?", (selected_id,))
            db.conn.commit()
            st.success(f"Listing {selected_id} deleted.")
            st.rerun()
        except Exception as e:
            db.conn.rollback()
            st.error(f"Could not delete listing (still referenced by sales/property attributes): {e}")

# SALES

def view_sales():
    df = db.run_query("SELECT * FROM sales ORDER BY listingid")
    paginate_dataframe(df, "sales", "sales")


def add_sale():
    with st.form("add_sale_form"):
        listingid = st.text_input("Listing ID (must already exist in Listings)")
        saleprice = st.number_input("Sale Price", min_value=0.0, step=1000.0)
        datesold = st.date_input("Date Sold")
        daysonmarket = st.number_input("Days on Market", min_value=0, step=1)
        submitted = st.form_submit_button("Add Sale")

    if submitted:
        try:
            db.cursor.execute(
                "INSERT INTO sales (listingid, saleprice, datesold, daysonmarket) VALUES (?, ?, ?, ?)",
                (listingid, saleprice, str(datesold), daysonmarket),
            )
            db.conn.commit()
            st.success(f"Sale for listing {listingid} added.")
            st.rerun()
        except Exception as e:
            db.conn.rollback()
            st.error(f"Could not add sale: {e}")


def update_sale():
    listing_ids = db.run_query("SELECT listingid FROM sales ORDER BY listingid")["listingid"].tolist()
    if not listing_ids:
        st.info("No sales yet.")
        return

    selected_id = st.selectbox("Select Listing ID to update", listing_ids)
    row = pd.read_sql("SELECT * FROM sales WHERE listingid = ?", db.conn, params=(selected_id,)).iloc[0]

    with st.form("update_sale_form"):
        saleprice = st.number_input("Sale Price", value=float(row["saleprice"]), min_value=0.0, step=1000.0)
        datesold = st.date_input("Date Sold", value=pd.to_datetime(row["datesold"]).date())
        daysonmarket = st.number_input("Days on Market", value=int(row["daysonmarket"]), min_value=0, step=1)
        submitted = st.form_submit_button("Update Sale")

    if submitted:
        try:
            db.cursor.execute(
                "UPDATE sales SET saleprice=?, datesold=?, daysonmarket=? WHERE listingid=?",
                (saleprice, str(datesold), daysonmarket, selected_id),
            )
            db.conn.commit()
            st.success(f"Sale for listing {selected_id} updated.")
            st.rerun()
        except Exception as e:
            db.conn.rollback()
            st.error(f"Could not update sale: {e}")


def delete_sale():
    listing_ids = db.run_query("SELECT listingid FROM sales ORDER BY listingid")["listingid"].tolist()
    if not listing_ids:
        st.info("No sales yet.")
        return

    selected_id = st.selectbox("Select Listing ID to delete", listing_ids, key="delete_sale_select")
    row = pd.read_sql("SELECT * FROM sales WHERE listingid = ?", db.conn, params=(selected_id,))
    st.dataframe(row, use_container_width=True, hide_index=True)

    confirm = st.checkbox(f"Yes, delete sale for listing {selected_id}", key="confirm_delete_sale")
    if st.button("Delete Sale", disabled=not confirm):
        try:
            db.cursor.execute("DELETE FROM sales WHERE listingid = ?", (selected_id,))
            db.conn.commit()
            st.success(f"Sale for listing {selected_id} deleted.")
            st.rerun()
        except Exception as e:
            db.conn.rollback()
            st.error(f"Could not delete sale (still referenced by buyers): {e}")

# BUYERS

def view_buyers():
    df = db.run_query("SELECT * FROM buyers ORDER BY buyerid")
    paginate_dataframe(df, "buyers", "buyers")


def add_buyer():
    sale_ids = db.run_query("SELECT listingid FROM sales ORDER BY listingid")["listingid"].tolist()
    next_id = db.run_query("SELECT COALESCE(MAX(buyerid), 0) + 1 AS next_id FROM buyers").iloc[0]["next_id"]

    with st.form("add_buyer_form"):
        buyerid = st.number_input("Buyer ID", value=int(next_id), min_value=1, step=1)
        saleid = st.selectbox("Sale (Listing ID)", sale_ids)
        buyertype = st.selectbox("Buyer Type", ["End User", "Investor"])
        paymentmode = st.selectbox("Payment Mode", ["Cash", "UPI", "Bank Transfer", "Cheque"])
        loantaken = st.checkbox("Loan Taken")
        loanprovider = st.text_input("Loan Provider (optional)")
        loanamount = st.number_input("Loan Amount", min_value=0.0, step=1000.0)
        submitted = st.form_submit_button("Add Buyer")

    if submitted:
        try:
            db.cursor.execute(
                "INSERT INTO buyers (buyerid, saleid, buyertype, paymentmode, loantaken, "
                "loanprovider, loanamount) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (buyerid, saleid, buyertype, paymentmode, int(loantaken),
                 loanprovider or None, loanamount),
            )
            db.conn.commit()
            st.success(f"Buyer {buyerid} added.")
            st.rerun()
        except Exception as e:
            db.conn.rollback()
            st.error(f"Could not add buyer: {e}")


def update_buyer():
    buyer_ids = db.run_query("SELECT buyerid FROM buyers ORDER BY buyerid")["buyerid"].tolist()
    if not buyer_ids:
        st.info("No buyers yet.")
        return

    selected_id = st.selectbox("Select Buyer ID to update", buyer_ids)
    row = pd.read_sql("SELECT * FROM buyers WHERE buyerid = ?", db.conn, params=(int(selected_id),)).iloc[0]
    sale_ids = db.run_query("SELECT listingid FROM sales ORDER BY listingid")["listingid"].tolist()

    with st.form("update_buyer_form"):
        saleid = st.selectbox("Sale (Listing ID)", sale_ids, index=sale_ids.index(row["saleid"]) if row["saleid"] in sale_ids else 0)
        type_options = ["End User", "Investor"]
        buyertype = st.selectbox("Buyer Type", type_options, index=type_options.index(row["buyertype"]))
        mode_options = ["Cash", "UPI", "Bank Transfer", "Cheque"]
        paymentmode = st.selectbox("Payment Mode", mode_options, index=mode_options.index(row["paymentmode"]))
        loantaken = st.checkbox("Loan Taken", value=bool(row["loantaken"]))
        loanprovider = st.text_input("Loan Provider (optional)", value=row["loanprovider"] or "")
        loanamount = st.number_input("Loan Amount", value=float(row["loanamount"]), min_value=0.0, step=1000.0)
        submitted = st.form_submit_button("Update Buyer")

    if submitted:
        try:
            db.cursor.execute(
                "UPDATE buyers SET saleid=?, buyertype=?, paymentmode=?, loantaken=?, "
                "loanprovider=?, loanamount=? WHERE buyerid=?",
                (saleid, buyertype, paymentmode, int(loantaken), loanprovider or None,
                 loanamount, int(selected_id)),
            )
            db.conn.commit()
            st.success(f"Buyer {selected_id} updated.")
            st.rerun()
        except Exception as e:
            db.conn.rollback()
            st.error(f"Could not update buyer: {e}")


def delete_buyer():
    buyer_ids = db.run_query("SELECT buyerid FROM buyers ORDER BY buyerid")["buyerid"].tolist()
    if not buyer_ids:
        st.info("No buyers yet.")
        return

    selected_id = st.selectbox("Select Buyer ID to delete", buyer_ids, key="delete_buyer_select")
    row = pd.read_sql("SELECT * FROM buyers WHERE buyerid = ?", db.conn, params=(int(selected_id),))
    st.dataframe(row, use_container_width=True, hide_index=True)

    confirm = st.checkbox(f"Yes, delete buyer {selected_id}", key="confirm_delete_buyer")
    if st.button("Delete Buyer", disabled=not confirm):
        try:
            db.cursor.execute("DELETE FROM buyers WHERE buyerid = ?", (int(selected_id),))
            db.conn.commit()
            st.success(f"Buyer {selected_id} deleted.")
            st.rerun()
        except Exception as e:
            db.conn.rollback()
            st.error(f"Could not delete buyer: {e}")


# PROPERTY ATTRIBUTES

def view_property_attributes():
    df = db.run_query("SELECT * FROM property_attributes ORDER BY attributeid")
    paginate_dataframe(df, "property_attributes", "records")


def add_property_attribute():
    next_id = db.run_query(
        "SELECT COALESCE(MAX(attributeid), 0) + 1 AS next_id FROM property_attributes"
    ).iloc[0]["next_id"]

    with st.form("add_property_attribute_form"):
        attributeid = st.number_input("Attribute ID", value=int(next_id), min_value=1, step=1)
        listingid = st.text_input("Listing ID (must already exist in Listings)")
        bedrooms = st.number_input("Bedrooms", min_value=0, step=1)
        bathrooms = st.number_input("Bathrooms", min_value=0, step=1)
        floornumber = st.number_input("Floor Number", min_value=0, step=1)
        totalfloors = st.number_input("Total Floors", min_value=0, step=1)
        yearbuilt = st.number_input("Year Built", min_value=1900, max_value=2100, step=1, value=2000)
        isrented = st.checkbox("Is Rented")
        tenantcount = st.number_input("Tenant Count", min_value=0, step=1)
        furnishingstatus = st.selectbox("Furnishing Status", ["Furnished", "Semi-Furnished", "Unfurnished"])
        metrodistancekm = st.number_input("Metro Distance (km)", min_value=0.0, step=0.1)
        parkingavailable = st.checkbox("Parking Available")
        powerbackup = st.checkbox("Power Backup")
        submitted = st.form_submit_button("Add Property Attribute")

    if submitted:
        try:
            db.cursor.execute(
                "INSERT INTO property_attributes (attributeid, listingid, bedrooms, bathrooms, "
                "floornumber, totalfloors, yearbuilt, isrented, tenantcount, furnishingstatus, "
                "metrodistancekm, parkingavailable, powerbackup) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (attributeid, listingid, bedrooms, bathrooms, floornumber, totalfloors, yearbuilt,
                 int(isrented), tenantcount, furnishingstatus, metrodistancekm,
                 int(parkingavailable), int(powerbackup)),
            )
            db.conn.commit()
            st.success(f"Property attribute {attributeid} added.")
            st.rerun()
        except Exception as e:
            db.conn.rollback()
            st.error(f"Could not add property attribute: {e}")


def update_property_attribute():
    ids = db.run_query("SELECT attributeid FROM property_attributes ORDER BY attributeid")["attributeid"].tolist()
    if not ids:
        st.info("No records yet.")
        return

    selected_id = st.selectbox("Select Attribute ID to update", ids)
    row = pd.read_sql(
        "SELECT * FROM property_attributes WHERE attributeid = ?", db.conn, params=(int(selected_id),)
    ).iloc[0]

    with st.form("update_property_attribute_form"):
        listingid = st.text_input("Listing ID", value=row["listingid"])
        bedrooms = st.number_input("Bedrooms", value=int(row["bedrooms"]), min_value=0, step=1)
        bathrooms = st.number_input("Bathrooms", value=int(row["bathrooms"]), min_value=0, step=1)
        floornumber = st.number_input("Floor Number", value=int(row["floornumber"]), min_value=0, step=1)
        totalfloors = st.number_input("Total Floors", value=int(row["totalfloors"]), min_value=0, step=1)
        yearbuilt = st.number_input("Year Built", value=int(row["yearbuilt"]), min_value=1900, max_value=2100, step=1)
        isrented = st.checkbox("Is Rented", value=bool(row["isrented"]))
        tenantcount = st.number_input("Tenant Count", value=int(row["tenantcount"]), min_value=0, step=1)
        status_options = ["Furnished", "Semi-Furnished", "Unfurnished"]
        furnishingstatus = st.selectbox("Furnishing Status", status_options, index=status_options.index(row["furnishingstatus"]))
        metrodistancekm = st.number_input("Metro Distance (km)", value=float(row["metrodistancekm"]), min_value=0.0, step=0.1)
        parkingavailable = st.checkbox("Parking Available", value=bool(row["parkingavailable"]))
        powerbackup = st.checkbox("Power Backup", value=bool(row["powerbackup"]))
        submitted = st.form_submit_button("Update Property Attribute")

    if submitted:
        try:
            db.cursor.execute(
                "UPDATE property_attributes SET listingid=?, bedrooms=?, bathrooms=?, floornumber=?, "
                "totalfloors=?, yearbuilt=?, isrented=?, tenantcount=?, furnishingstatus=?, "
                "metrodistancekm=?, parkingavailable=?, powerbackup=? WHERE attributeid=?",
                (listingid, bedrooms, bathrooms, floornumber, totalfloors, yearbuilt, int(isrented),
                 tenantcount, furnishingstatus, metrodistancekm, int(parkingavailable),
                 int(powerbackup), int(selected_id)),
            )
            db.conn.commit()
            st.success(f"Property attribute {selected_id} updated.")
            st.rerun()
        except Exception as e:
            db.conn.rollback()
            st.error(f"Could not update property attribute: {e}")


def delete_property_attribute():
    ids = db.run_query("SELECT attributeid FROM property_attributes ORDER BY attributeid")["attributeid"].tolist()
    if not ids:
        st.info("No records yet.")
        return

    selected_id = st.selectbox("Select Attribute ID to delete", ids, key="delete_property_attribute_select")
    row = pd.read_sql(
        "SELECT * FROM property_attributes WHERE attributeid = ?", db.conn, params=(int(selected_id),)
    )
    st.dataframe(row, use_container_width=True, hide_index=True)

    confirm = st.checkbox(f"Yes, delete property attribute {selected_id}", key="confirm_delete_property_attribute")
    if st.button("Delete Property Attribute", disabled=not confirm):
        try:
            db.cursor.execute("DELETE FROM property_attributes WHERE attributeid = ?", (int(selected_id),))
            db.conn.commit()
            st.success(f"Property attribute {selected_id} deleted.")
            st.rerun()
        except Exception as e:
            db.conn.rollback()
            st.error(f"Could not delete property attribute: {e}")

# Page layout: pick the right set of functions for the chosen table


tab_view, tab_add, tab_update, tab_delete = st.tabs(["View", "Add", "Update", "Delete"])

with tab_view:
    if table == "Agents":
        view_agents()
    elif table == "Listings":
        view_listings()
    elif table == "Sales":
        view_sales()
    elif table == "Buyers":
        view_buyers()
    elif table == "Property Attributes":
        view_property_attributes()

with tab_add:
    if table == "Agents":
        add_agent()
    elif table == "Listings":
        add_listing()
    elif table == "Sales":
        add_sale()
    elif table == "Buyers":
        add_buyer()
    elif table == "Property Attributes":
        add_property_attribute()

with tab_update:
    if table == "Agents":
        update_agent()
    elif table == "Listings":
        update_listing()
    elif table == "Sales":
        update_sale()
    elif table == "Buyers":
        update_buyer()
    elif table == "Property Attributes":
        update_property_attribute()

with tab_delete:
    if table == "Agents":
        delete_agent()
    elif table == "Listings":
        delete_listing()
    elif table == "Sales":
        delete_sale()
    elif table == "Buyers":
        delete_buyer()
    elif table == "Property Attributes":
        delete_property_attribute()
