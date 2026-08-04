import sqlite3

DATABASE_PATH = "data/database/mnemosyne.db"


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# Document Operations
# -----------------------------

def add_document(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO documents (
            title,
            filename,
            filepath,
            file_type,
            category,
            pages,
            size_kb,
            uploaded_by,
            upload_date,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["title"],
        data["filename"],
        data["filepath"],
        data["file_type"],
        data["category"],
        data["pages"],
        data["size_kb"],
        data["uploaded_by"],
        data["upload_date"],
        data["status"]
    ))

    conn.commit()
    conn.close()


def get_all_documents():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM documents
        ORDER BY id DESC
    """)

    documents = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return documents


def get_document(document_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM documents
        WHERE id = ?
    """, (document_id,))

    row = cursor.fetchone()

    conn.close()

    if row:
        return dict(row)

    return None


def update_document(document_id, data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE documents
        SET
            title = ?,
            filename = ?,
            filepath = ?,
            file_type = ?,
            category = ?,
            pages = ?,
            size_kb = ?,
            uploaded_by = ?,
            upload_date = ?,
            status = ?
        WHERE id = ?
    """, (
        data["title"],
        data["filename"],
        data["filepath"],
        data["file_type"],
        data["category"],
        data["pages"],
        data["size_kb"],
        data["uploaded_by"],
        data["upload_date"],
        data["status"],
        document_id
    ))

    conn.commit()
    conn.close()


def delete_document(document_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM documents
        WHERE id = ?
    """, (document_id,))

    conn.commit()
    conn.close()


def search_documents(query):
    conn = get_connection()
    cursor = conn.cursor()

    search = f"%{query}%"

    cursor.execute("""
        SELECT *
        FROM documents
        WHERE
            title LIKE ?
            OR filename LIKE ?
            OR category LIKE ?
            OR uploaded_by LIKE ?
        ORDER BY id DESC
    """, (
        search,
        search,
        search,
        search
    ))

    results = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return results


def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM documents")
    total_documents = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(size_kb), 0) FROM documents")
    total_storage = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(pages), 0) FROM documents")
    total_pages = cursor.fetchone()[0]

    conn.close()

    return {
        "total_documents": total_documents,
        "total_storage": total_storage,
        "total_pages": total_pages
    }