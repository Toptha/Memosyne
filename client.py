import streamlit as st
import requests
import pandas as pd
import json

BASE_URL = 'http://127.0.0.1:5000/documents'

st.set_page_config(page_title="Mnemosyne", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif !important;
}

/* Minimalist Dark Theme */
.stApp {
    background-color: #121212;
    color: #E2E8F0;
}

/* Clean Header */
.main-header {
    font-size: 2.2rem;
    font-weight: 600;
    color: #FFFFFF;
    margin-bottom: 2rem;
    border-bottom: 1px solid #333;
    padding-bottom: 1rem;
}

/* Clean Cards */
.clean-card {
    background: #1A1A1A;
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: none;
}

/* Metric text inside clean cards */
.metric-value {
    font-size: 2.5rem;
    font-weight: 600;
    color: #FFFFFF;
    line-height: 1.2;
}

.metric-label {
    font-size: 0.9rem;
    color: #888888;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 500;
}

/* Minimalist Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0px;
    background: transparent;
    border-bottom: 1px solid #333333;
}

.stTabs [data-baseweb="tab"] {
    height: 40px;
    background-color: transparent;
    color: #888888;
    font-weight: 500;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 0 15px;
    margin-right: 15px;
}

.stTabs [aria-selected="true"] {
    color: #FFFFFF !important;
    border-bottom: 2px solid #FFFFFF;
    background: transparent;
}

/* Professional Buttons */
.stButton > button {
    background-color: #FFFFFF;
    color: #000000;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: 500;
    transition: background-color 0.2s;
    width: 100%;
}
.stButton > button:hover {
    background-color: #E0E0E0;
    color: #000000;
}

/* Input Fields styling */
.stTextInput>div>div>input, .stNumberInput>div>div>input {
    background-color: #1A1A1A !important;
    color: #FFFFFF !important;
    border-radius: 4px !important;
    border: 1px solid #333333 !important;
    padding: 8px 12px !important;
}

.stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
    border-color: #666666 !important;
    box-shadow: none !important;
}

/* Dataframe styling */
.stDataFrame {
    border-radius: 4px;
    border: 1px solid #333333;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">Mnemosyne</div>', unsafe_allow_html=True)

def fetch_documents():
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching documents: {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to server. Is the Flask API running?")
        return []

def get_document(doc_id):
    try:
        response = requests.get(f"{BASE_URL}/{doc_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.ConnectionError:
        st.error("Connection Error.")
        return None

# Navigation via Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "View Document", "Upload", "Update", "Delete"])

documents = fetch_documents()

with tab1:
    st.markdown("#### Overview")
    if documents:
        df = pd.DataFrame(documents)
        columns_order = ['id', 'title', 'category', 'status', 'upload_date', 'filename', 'file_type', 'pages', 'size_kb', 'uploaded_by']
        columns_order = [col for col in columns_order if col in df.columns]
        df = df[columns_order]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'''
            <div class="clean-card">
                <div class="metric-label">Total Documents</div>
                <div class="metric-value">{len(documents)}</div>
            </div>
            ''', unsafe_allow_html=True)
        with col2:
            st.markdown(f'''
            <div class="clean-card">
                <div class="metric-label">Total Pages</div>
                <div class="metric-value">{df['pages'].sum() if 'pages' in df.columns else 0}</div>
            </div>
            ''', unsafe_allow_html=True)
        with col3:
            total_kb = df['size_kb'].sum() if 'size_kb' in df.columns else 0
            mb_val = round(total_kb / 1024, 1)
            st.markdown(f'''
            <div class="clean-card">
                <div class="metric-label">Storage Used</div>
                <div class="metric-value">{mb_val} MB</div>
            </div>
            ''', unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        # Add width parameter to resolve the deprecation warning
        st.dataframe(df, width='stretch', hide_index=True, height=400)
    else:
        st.info("No documents found. Start by uploading metadata.")

with tab2:
    st.markdown("#### Document Details")
    if documents:
        doc_map = {f"ID {d['id']} : {d['title']}": d['id'] for d in documents}
        selected = st.selectbox("Select document", options=list(doc_map.keys()), key="view_select")
        
        if selected:
            doc_id = doc_map[selected]
            doc = get_document(doc_id)
            if doc:
                st.markdown('<div class="clean-card">', unsafe_allow_html=True)
                st.json(doc)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("Failed to fetch document details.")
    else:
        st.info("No documents available.")

with tab3:
    st.markdown("#### Upload Metadata")
    with st.container():
        st.markdown('<div class="clean-card">', unsafe_allow_html=True)
        with st.form("upload_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Title*")
                filename = st.text_input("Filename*")
                file_type = st.selectbox("File Type*", ["pdf", "docx", "txt", "csv", "other"])
                category = st.text_input("Category*")
                
            with col2:
                pages = st.number_input("Pages*", min_value=1, step=1)
                size_kb = st.number_input("Size (KB)*", min_value=1, step=1)
                uploaded_by = st.text_input("Uploaded By*")
                upload_date = st.date_input("Upload Date")
                status = st.selectbox("Status", ["Uploaded", "Indexed"])
                
            submitted = st.form_submit_button("Submit")
            if submitted:
                if not (title and filename and category and uploaded_by):
                    st.error("Please fill in all required fields.")
                else:
                    data = {
                        "title": title,
                        "filename": filename,
                        "file_type": file_type,
                        "pages": pages,
                        "uploaded_by": uploaded_by,
                        "category": category,
                        "upload_date": upload_date.strftime("%Y-%m-%d"),
                        "size_kb": size_kb,
                        "status": status
                    }
                    try:
                        response = requests.post(BASE_URL, json=data)
                        if response.status_code == 201:
                            st.success(f"Document uploaded. ID: {response.json()['id']}")
                        else:
                            st.error(f"Error: {response.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to server.")
        st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown("#### Update Metadata")
    if documents:
        doc_map = {f"ID {d['id']} : {d['title']}": d['id'] for d in documents}
        selected = st.selectbox("Select document", options=list(doc_map.keys()), key="update_select")
        
        if selected:
            doc_id = doc_map[selected]
            doc = get_document(doc_id)
            if doc:
                st.markdown('<div class="clean-card">', unsafe_allow_html=True)
                with st.form("update_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        title = st.text_input("Title", value=doc.get("title", ""))
                        filename = st.text_input("Filename", value=doc.get("filename", ""))
                        ft_val = doc.get("file_type", "pdf")
                        ft_options = ["pdf", "docx", "txt", "csv", "other"]
                        ft_index = ft_options.index(ft_val) if ft_val in ft_options else 0
                        file_type = st.selectbox("File Type", ft_options, index=ft_index)
                        category = st.text_input("Category", value=doc.get("category", ""))
                        
                    with col2:
                        pages = st.number_input("Pages", min_value=1, step=1, value=doc.get("pages", 1))
                        size_kb = st.number_input("Size (KB)", min_value=1, step=1, value=doc.get("size_kb", 1))
                        uploaded_by = st.text_input("Uploaded By", value=doc.get("uploaded_by", ""))
                        st_val = doc.get("status", "Uploaded")
                        st_options = ["Uploaded", "Indexed"]
                        st_index = st_options.index(st_val) if st_val in st_options else 0
                        status = st.selectbox("Status", st_options, index=st_index)
                        
                    submitted = st.form_submit_button("Update")
                    if submitted:
                        update_data = {
                            "title": title,
                            "filename": filename,
                            "file_type": file_type,
                            "category": category,
                            "pages": pages,
                            "size_kb": size_kb,
                            "uploaded_by": uploaded_by,
                            "status": status
                        }
                        try:
                            response = requests.put(f"{BASE_URL}/{doc_id}", json=update_data)
                            if response.status_code == 200:
                                st.success("Document updated successfully.")
                            else:
                                st.error(f"Failed to update: {response.text}")
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot connect to server.")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No documents available.")

with tab5:
    st.markdown("#### Delete Document")
    if documents:
        doc_map = {f"ID {d['id']} : {d['title']}": d['id'] for d in documents}
        selected = st.selectbox("Select document", options=list(doc_map.keys()), key="delete_select")
        
        if selected:
            doc_id = doc_map[selected]
            st.markdown('<div class="clean-card">', unsafe_allow_html=True)
            st.warning(f"Are you sure you want to delete {selected}?")
            if st.button("Delete", type="primary"):
                try:
                    response = requests.delete(f"{BASE_URL}/{doc_id}")
                    if response.status_code == 204:
                        st.success("Document deleted.")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to server.")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No documents available.")
