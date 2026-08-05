from utils import *

import streamlit as st
from pathlib import Path
from datetime import datetime

from data.database.database import add_document

st.title("📤 Upload Document")

UPLOAD_DIR = ROOT / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

with st.form("upload_form"):

    title = st.text_input("Title")

    category = st.selectbox(
        "Category",
        [
            "Research Paper",
            "Assignment",
            "Notes",
            "Book",
            "Report",
            "Presentation",
            "Other"
        ]
    )

    uploaded_by = st.text_input("Uploaded By")

    uploaded_file = st.file_uploader(
        "Choose Document",
        type=["pdf", "docx", "txt"]
    )

    submit = st.form_submit_button("Upload")

    if submit:

        if not title.strip():
            st.error("Please enter a title.")

        elif not uploaded_by.strip():
            st.error("Please enter who uploaded the document.")

        elif uploaded_file is None:
            st.error("Please select a document.")

        else:

            save_path = UPLOAD_DIR / uploaded_file.name

            # Save uploaded file
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Prepare metadata
            document = {
                "title": title,
                "filename": uploaded_file.name,
                "filepath": str(save_path),
                "file_type": uploaded_file.name.split(".")[-1].lower(),
                "category": category,
                "pages": 0,
                "size_kb": round(uploaded_file.size / 1024, 2),
                "uploaded_by": uploaded_by,
                "upload_date": datetime.now().strftime("%Y-%m-%d"),
                "status": "Uploaded"
            }

            # Save metadata to database
            add_document(document)

            st.success("✅ Document uploaded successfully!")

            st.info(f"Saved to:\n{save_path}")

            st.balloons()