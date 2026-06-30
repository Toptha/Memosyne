import os
import streamlit as st

from modules.extractor import DocumentFactory

UPLOAD_DIR = "data/uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

st.set_page_config(
    page_title="Mnemosyne",
    layout="wide"
)

st.title("Mnemosyne")
st.subheader(
    "Semantic Document Search System"
)

uploaded_file = st.file_uploader(
    "Upload Document",
    type=["pdf", "txt", "docx"]
)

if uploaded_file:

    file_path = os.path.join(
        UPLOAD_DIR,
        uploaded_file.name
    )

    with open(file_path, "wb") as file:
        file.write(
            uploaded_file.getbuffer()
        )

    document = (
        DocumentFactory.create_document(
            file_path
        )
    )

    extracted_pages = (
        document.extract_text()
    )

    st.success(
        "Document processed successfully"
    )

    st.write(
        f"Pages Extracted: {len(extracted_pages)}"
    )

    st.subheader("Preview")

    st.text(
        extracted_pages[0]["text"][:1000]
    )