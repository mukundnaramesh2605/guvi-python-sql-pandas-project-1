"""Shared helper so every page connects to the same database."""

import streamlit as st
from db import Database


@st.cache_resource
def get_db():
    return Database()
