import pandas as pd
import json
import sqlite3
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

class Database:
    EXPECTED_TABLES = {"agents", "listings", "sales", "buyers", "property_attributes"}

    def __init__(self, db_path="project.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.conn.execute("PRAGMA foreign_keys = ON;")
        if not self._has_all_tables():
            self.build_database()

    def _has_all_tables(self):
        existing = {
            row[0]
            for row in self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            )
        }
        return self.EXPECTED_TABLES.issubset(existing)

    def close(self):
        self.conn.close()

    def load_dataset(self, path, rename_map, date_columns=None, file_format="json"):
        if file_format == "csv":
            df = pd.read_csv(path)
        else:
            df = pd.read_json(path)

        df.rename(columns=rename_map, inplace=True)

        for column in date_columns or []:
            df[column] = pd.to_datetime(df[column])

        return df

    def run_query(self, query):
        return pd.read_sql(query, self.conn)

    def create_table(self, table_name, create_query, df):
        self.cursor.execute(create_query)
        df.to_sql(table_name, self.conn, if_exists="append", index=False)
        self.conn.commit()

    def create_index(self, index_name, table, column):
        self.cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column});")
        self.conn.commit()

    def build_database(self):
        agents_df = self.load_dataset("datasets/agents_cleaned.json",
        rename_map={
            "Agent_ID": "agentid",
            "Name": "name",
            "Phone": "phone",
            "Email": "email",
            "commission_rate": "commissionrate",
            "deals_closed": "dealsclosed",
            "rating": "rating",
            "experience_years": "experienceyears",
            "avg_closing_days": "avgclosingdays",
            },
        )
        buyers_df = self.load_dataset("datasets/buyers_cleaned.json",
        rename_map={
            "buyer_id": "buyerid",
            "sale_id": "saleid",
            "buyer_type": "buyertype",
            "payment_mode": "paymentmode",
            "loan_taken": "loantaken",
            "loan_provider": "loanprovider",
            "loan_amount": "loanamount",
            },
        )
        listings_df = self.load_dataset("datasets/listings_final_expanded.json",
        rename_map={
            "Listing_ID": "listingid",
            "City": "city",
            "Property_Type": "propertytype",
            "Price": "price",
            "Sqft": "sqft",
            "Date_Listed": "datelisted",
            "Agent_ID": "agentid",
            "Latitude": "latitude",
            "Longitude": "longitude",
            },
        date_columns=["datelisted"],
        )
        sales_df = self.load_dataset("datasets/sales_cleaned.csv",
        rename_map={
            "Listing_ID": "listingid",
            "Sale_Price": "saleprice",
            "Date_Sold": "datesold",
            "Days_on_Market": "daysonmarket",
            },
        date_columns=["datesold"],
        file_format="csv",
        )
        property_df = self.load_dataset("datasets/property_attributes_final_expanded.json",
        rename_map={
            "attribute_id": "attributeid",
            "listing_id": "listingid",
            "floor_number": "floornumber",
            "total_floors": "totalfloors",
            "year_built": "yearbuilt",
            "is_rented": "isrented",
            "tenant_count": "tenantcount",
            "furnishing_status": "furnishingstatus",
            "metro_distance_km": "metrodistancekm",
            "parking_available": "parkingavailable",
            "power_backup": "powerbackup",
            },
        )
        agents_table_query = """
        CREATE TABLE IF NOT EXISTS agents(
            agentid TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            commissionrate REAL NOT NULL,
            dealsclosed INTEGER NOT NULL,
            rating REAL NOT NULL,
            experienceyears INTEGER NOT NULL,
            avgclosingdays INTEGER NOT NULL
        );
        """
        listings_table_query = """
        CREATE TABLE IF NOT EXISTS listings(
            listingid TEXT PRIMARY KEY,
            city TEXT NOT NULL,
            propertytype TEXT NOT NULL,
            price REAL NOT NULL,
            sqft REAL NOT NULL,
            datelisted DATE NOT NULL,
            agentid TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,

            FOREIGN KEY(agentid)
                REFERENCES agents(agentid)
        );
        """
        sales_table_query = """
        CREATE TABLE IF NOT EXISTS sales(
            listingid TEXT PRIMARY KEY,
            saleprice REAL NOT NULL,
            datesold DATE NOT NULL,
            daysonmarket INTEGER NOT NULL,

            FOREIGN KEY(listingid)
                REFERENCES listings(listingid)
        );
        """
        buyers_table_query = """
        CREATE TABLE IF NOT EXISTS buyers(
            buyerid INTEGER PRIMARY KEY,
            saleid TEXT NOT NULL,

            buyertype TEXT NOT NULL,
            paymentmode TEXT NOT NULL,
            loantaken BOOLEAN NOT NULL,
            loanprovider TEXT,
            loanamount REAL NOT NULL,

            FOREIGN KEY(saleid)
                REFERENCES sales(listingid)
        );
        """
        property_attributes_table_query = """
        CREATE TABLE IF NOT EXISTS property_attributes(
            attributeid INTEGER PRIMARY KEY,
            listingid TEXT UNIQUE,
            bedrooms INTEGER NOT NULL,
            bathrooms INTEGER NOT NULL,
            floornumber INTEGER NOT NULL,
            totalfloors INTEGER NOT NULL,
            yearbuilt INTEGER NOT NULL,
            isrented BOOLEAN NOT NULL,
            tenantcount INTEGER NOT NULL,
            furnishingstatus TEXT NOT NULL,
            metrodistancekm REAL NOT NULL,
            parkingavailable BOOLEAN NOT NULL,
            powerbackup BOOLEAN NOT NULL,

            FOREIGN KEY(listingid)
                REFERENCES listings(listingid)
        );
        """
        
        self.create_table("agents", agents_table_query, agents_df)
        self.create_table("listings", listings_table_query, listings_df)
        self.create_table("sales", sales_table_query, sales_df)
        self.create_table("buyers", buyers_table_query, buyers_df)
        self.create_table("property_attributes", property_attributes_table_query, property_df)
        indexes = [
            ("idx_agents_rating", "agents", "rating"),
            ("idx_agents_experience", "agents", "experienceyears"),
            ("idx_listings_city", "listings", "city"),
            ("idx_listings_propertytype", "listings", "propertytype"),
            ("idx_listings_price", "listings", "price"),
            ("idx_listings_agentid", "listings", "agentid"),
            ("idx_sales_datesold", "sales", "datesold"),
            ("idx_sales_saleprice", "sales", "saleprice"),
            ("idx_buyers_saleid", "buyers", "saleid"),
            ("idx_buyers_buyertype", "buyers", "buyertype"),
            ("idx_buyers_paymentmode", "buyers", "paymentmode"),
            ("idx_property_bedrooms", "property_attributes", "bedrooms"),
            ("idx_property_yearbuilt", "property_attributes", "yearbuilt"),
            ("idx_property_metrodistance", "property_attributes", "metrodistancekm"),
            ("idx_property_listingid", "property_attributes", "listingid"),
        ]

        for index_name, table, column in indexes:
            self.create_index(index_name, table, column)

        self.conn.commit()
