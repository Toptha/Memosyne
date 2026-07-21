import requests
import json

BASE_URL = 'http://127.0.0.1:5000/documents'

def print_menu():
    print("\n==========================")
    print("Mnemosyne Client")
    print("==========================")
    print("1 View Documents")
    print("2 View Document")
    print("3 Upload Metadata")
    print("4 Update Metadata")
    print("5 Delete Document")
    print("6 Exit")
    print("==========================")

def view_documents():
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            docs = response.json()
            if not docs:
                print("No documents found.")
            else:
                for doc in docs:
                    print(f"[{doc['id']}] {doc['title']} ({doc['status']})")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Server Down (ConnectionError). Is the Flask server running?")
    except requests.exceptions.JSONDecodeError:
        print("Error: Invalid JSON response.")

def view_document():
    try:
        doc_id = input("Enter Document ID to view: ")
        response = requests.get(f"{BASE_URL}/{doc_id}")
        if response.status_code == 200:
            doc = response.json()
            print(json.dumps(doc, indent=4))
        elif response.status_code == 404:
            print(f"404 Not Found: {response.json().get('error', 'Document Not Found')}")
        else:
            print(f"Error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Error: Server Down (ConnectionError).")
    except requests.exceptions.JSONDecodeError:
        print("Error: Invalid JSON response.")

def upload_metadata():
    print("Enter Document Metadata:")
    title = input("Title: ")
    filename = input("Filename: ")
    file_type = input("File Type (e.g., pdf, docx, txt): ")
    try:
        pages = int(input("Pages: "))
        size_kb = int(input("Size (KB): "))
    except ValueError:
        print("Error: Pages and Size must be integers.")
        return
        
    uploaded_by = input("Uploaded By: ")
    category = input("Category: ")
    upload_date = input("Upload Date (YYYY-MM-DD): ")
    status = input("Status (Uploaded / Indexed): ")
    
    data = {
        "title": title,
        "filename": filename,
        "file_type": file_type,
        "pages": pages,
        "uploaded_by": uploaded_by,
        "category": category,
        "upload_date": upload_date,
        "size_kb": size_kb,
        "status": status
    }
    
    try:
        response = requests.post(BASE_URL, json=data)
        if response.status_code == 201:
            print(f"201 Created: Successfully added document. New ID: {response.json()['id']}")
        elif response.status_code == 400:
            print(f"400 Bad Request: {response.json().get('error', 'Invalid Request')}")
        else:
            print(f"Error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Error: Server Down (ConnectionError).")
    except requests.exceptions.JSONDecodeError:
        print("Error: Invalid JSON response.")

def update_metadata():
    try:
        doc_id = input("Enter Document ID to update: ")
        
        # Check if doc exists
        get_resp = requests.get(f"{BASE_URL}/{doc_id}")
        if get_resp.status_code == 404:
            print(f"404 Not Found: {get_resp.json().get('error', 'Document Not Found')}")
            return
        elif get_resp.status_code != 200:
            print(f"Error: {get_resp.status_code}")
            return
            
        print("Enter new values (leave blank to keep current):")
        doc = get_resp.json()
        
        data = {}
        status = input(f"Status [{doc.get('status')}]: ")
        if status.strip():
            data['status'] = status.strip()
            
        title = input(f"Title [{doc.get('title')}]: ")
        if title.strip():
            data['title'] = title.strip()
            
        if not data:
            print("No changes specified.")
            return
            
        response = requests.put(f"{BASE_URL}/{doc_id}", json=data)
        if response.status_code == 200:
            print("200 OK: Successfully updated document.")
        elif response.status_code == 404:
            print("404 Not Found.")
        elif response.status_code == 400:
            print(f"400 Bad Request: {response.json().get('error', 'Invalid Request')}")
        else:
            print(f"Error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Error: Server Down (ConnectionError).")
    except requests.exceptions.JSONDecodeError:
        print("Error: Invalid JSON response.")

def delete_document():
    try:
        doc_id = input("Enter Document ID to delete: ")
        response = requests.delete(f"{BASE_URL}/{doc_id}")
        if response.status_code == 204:
            print("204 No Content: Successfully deleted document.")
        elif response.status_code == 404:
            print("404 Not Found.")
        else:
            print(f"Error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Error: Server Down (ConnectionError).")

def main():
    while True:
        print_menu()
        choice = input("Enter choice: ")
        
        if choice == '1':
            view_documents()
        elif choice == '2':
            view_document()
        elif choice == '3':
            upload_metadata()
        elif choice == '4':
            update_metadata()
        elif choice == '5':
            delete_document()
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
