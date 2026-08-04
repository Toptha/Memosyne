from utils import *
import streamlit as st

from data.database.database import get_dashboard_stats

st.set_page_config(
    page_title="Mnemosyne",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📚 Mnemosyne")
st.subheader("Document Management System")

stats = get_dashboard_stats()

col1, col2, col3 = st.columns(3)

col1.metric("Documents", stats["total_documents"])
col2.metric("Pages", stats["total_pages"])
col3.metric("Storage", f"{round(stats['total_storage']/1024,2)} MB")