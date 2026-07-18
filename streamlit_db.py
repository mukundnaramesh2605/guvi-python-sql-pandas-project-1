import pandas as pd
import sqlite3
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')
class Database:
    def __init__(self, db_path="project.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def close(self):
        self.conn.close()
    
    def run_query(self, query):
        return pd.read_sql(query, self.conn)      

    def close(self):
        self.conn.close()
        