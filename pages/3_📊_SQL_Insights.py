import streamlit as st

from common import get_db
from queries import SQL_QUERIES

st.set_page_config(page_title="SQL Insights | BrickView", page_icon="📊", layout="wide")

db = get_db()

st.title("📊 SQL Insights")
st.caption("30 curated SQL queries covering pricing, sales performance, agents, and buyer financing. "
           "Expand any query to see its SQL and live results.")

for category, queries_in_category in SQL_QUERIES.items():
    st.subheader(category)
    for query in queries_in_category:
        with st.expander(query["title"]):
            st.code(query["sql"].strip(), language="sql")
            try:
                result = db.run_query(query["sql"])
                st.dataframe(result, use_container_width=True, hide_index=True)
                st.caption(f"{len(result):,} rows")
            except Exception as exc:
                st.error(f"Query failed: {exc}")
