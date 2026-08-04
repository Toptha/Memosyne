from utils import *

import streamlit as st
import pandas as pd

from data.database.database import get_all_documents

st.title("📚 Document Library")

documents = get_all_documents()

if not documents:
    st.info("No documents have been uploaded yet.")
else:
    df = pd.DataFrame(documents)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )