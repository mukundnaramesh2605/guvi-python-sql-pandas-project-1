import os
import shutil
import tempfile

import pandas as pd
import sqlite3
import streamlit as st
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')
class Database:
    def __init__(self, db_path="project.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def run_query(self, query):
        return pd.read_sql(query, self.conn)

    def close(self):
        self.conn.close()


def _writable_db_copy(source_path):
    # Streamlit Community Cloud's app directory is read-only, so CRUD writes
    # need a copy in the writable temp dir instead of the checked-out repo file.
    writable_path = os.path.join(tempfile.gettempdir(), f"brickview_{os.path.basename(source_path)}")
    if not os.path.exists(writable_path):
        shutil.copy(source_path, writable_path)
    return writable_path


@st.cache_resource # to reuse connection throughout the session.
def get_db(db_path="project.db"):
    return Database(_writable_db_copy(db_path))
        