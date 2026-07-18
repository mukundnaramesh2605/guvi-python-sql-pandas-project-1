# BrickView — Real Estate Analytics Platform

BrickView is a multi-page Streamlit application for exploring a real estate portfolio: property listings, sales, agents, buyers, and property attributes. It combines interactive filtering, fixed portfolio-level charts, a library of curated SQL queries, and full CRUD access to the underlying SQLite database — all backed by a single `project.db` file.

**Live app:** [guvi-python-sql-pandas-project-1-ezjufepeeefanufx4sfzjm.streamlit.app](https://guvi-python-sql-pandas-project-1-ezjufepeeefanufx4sfzjm.streamlit.app/)

## Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Data Model](#data-model)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Data Pipeline](#data-pipeline)
- [Notes](#notes)

## Features

### 🏠 Home
Portfolio snapshot: total listings, cities covered, agents, sales closed, total revenue (auto-abbreviated to K/M/B with the exact figure on hover), and average days on market — plus quick links into each page.

### 🔍 Filters
Interactively filter listings by city, property type, price range, agent, and listing date. KPIs (listing count, average price, sales in view, average days on market) and the results table update live as filters change.

### 📈 Visualizations
A fixed set of 6 charts covering the full portfolio (not affected by the Filters page): average price by city, property type mix, monthly listings vs. sales trend, sale price distribution, price vs. square footage, and average days on market by city.

### 📊 SQL Insights
30 curated SQL queries grouped into four categories — Property & Pricing Analysis, Sales & Market Performance, Agent Performance, and Buyer & Financing Behavior. Each query is shown in an expander with its raw SQL and live results run against the database.

### 🛠️ CRUD Operations
Create, read, update, and delete records in every table (Agents, Listings, Sales, Buyers, Property Attributes) through a tabbed interface (View / Add / Update / Delete). The View tab is paginated with adjustable page size and Prev/Next navigation. Deletes require an explicit confirmation checkbox, and foreign-key errors (e.g. deleting an agent still referenced by listings) surface as inline error messages instead of crashing the app.

## Tech Stack

- [Streamlit](https://streamlit.io/) 1.39 — multi-page app framework and UI
- [pandas](https://pandas.pydata.org/) — data wrangling and SQL result handling
- [Matplotlib](https://matplotlib.org/) — charts on the Visualizations page
- SQLite (via `sqlite3`) — embedded database, no external server required
- Plotly / Jupyter (`project.ipynb`) — used for exploratory data analysis and building the database from source datasets, outside of the running app

## Data Model

`project.db` has five tables:

| Table | Key columns | Rows |
|---|---|---|
| `agents` | `agentid` (PK), name, phone, email, commissionrate, dealsclosed, rating, experienceyears, avgclosingdays | 50 |
| `listings` | `listingid` (PK), city, propertytype, price, sqft, datelisted, `agentid` (FK → agents), latitude, longitude | 21,200 |
| `sales` | `listingid` (PK/FK → listings), saleprice, datesold, daysonmarket | 720 |
| `buyers` | `buyerid` (PK), `saleid` (FK → sales.listingid), buyertype, paymentmode, loantaken, loanprovider, loanamount | 20,000 |
| `property_attributes` | `attributeid` (PK), `listingid` (FK → listings), bedrooms, bathrooms, floornumber, totalfloors, yearbuilt, isrented, tenantcount, furnishingstatus, metrodistancekm, parkingavailable, powerbackup | 21,200 |

Foreign keys are enforced (`PRAGMA foreign_keys = ON`), so deleting a referenced row (e.g. an agent with active listings) is blocked at the database level.

## Project Structure

```
.
├── Home.py                  # Landing page: portfolio KPIs + navigation
├── pages/
│   ├── 1_Filters.py          # Interactive listing filters + KPIs + table
│   ├── 2_Visualizations.py   # Fixed 6-chart portfolio overview
│   ├── 3_CRUD_Operations.py  # View / Add / Update / Delete for every table
│   └── 4_SQL_Insights.py     # 30 curated SQL queries with live results
├── streamlit_db.py          # Database class: SQLite connection + run_query()
├── ui_helpers.py            # Shared UI helpers (sidebar footer, etc.)
├── queries.py                # SQL_QUERIES dict powering the SQL Insights page
├── project.db                # SQLite database used by the app
├── project.ipynb             # EDA + database build notebook
├── datasets/                  # Source/cleaned JSON & CSV datasets
└── requirements.txt
```

## Getting Started

### Prerequisites
- Python 3.10+
- `project.db` present in the project root (already included)

### Installation

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run Home.py
```

The app opens at `http://localhost:8501` with Home as the landing page and the other pages listed in the sidebar.

## Data Pipeline

The source data lives in `datasets/` (agent, listing, buyer, and property-attribute JSON/CSV files). `project.ipynb` contains the exploratory data analysis and the steps used to clean, join, and load that data into `project.db`. The Streamlit app itself only reads from and writes to `project.db` — it does not re-run the notebook.

## Notes

- All writes from the CRUD Operations page commit directly to `project.db`; there is no soft-delete or undo, so use the delete confirmation checkboxes carefully.
- The Visualizations page always reflects the full portfolio; use the Filters page for a scoped view.
