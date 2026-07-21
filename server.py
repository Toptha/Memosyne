import json
import os
from flask import Flask, request, jsonify

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'documents.json')

def load_documents():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_documents(documents):
    with open(DATA_FILE, 'w') as f:
        json.dump(documents, f, indent=4)

@app.route('/documents', methods=['GET'])
def get_documents():
    documents = load_documents()
    return jsonify(documents), 200

@app.route('/documents/<int:doc_id>', methods=['GET'])
def get_document_by_id(doc_id):
    documents = load_documents()
    for doc in documents:
        if doc['id'] == doc_id:
            return jsonify(doc), 200
    return jsonify({"error": "Document Not Found"}), 404

@app.route('/documents', methods=['POST'])
def add_document():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    required_fields = ['title', 'filename', 'file_type', 'pages', 'uploaded_by', 'category', 'upload_date', 'size_kb', 'status']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    documents = load_documents()
    
    # Generate new ID
    new_id = 1
    if documents:
        new_id = max(doc['id'] for doc in documents) + 1
        
    new_document = {
        "id": new_id,
        "title": data['title'],
        "filename": data['filename'],
        "file_type": data['file_type'],
        "pages": data['pages'],
        "uploaded_by": data['uploaded_by'],
        "category": data['category'],
        "upload_date": data['upload_date'],
        "size_kb": data['size_kb'],
        "status": data['status']
    }
    
    documents.append(new_document)
    save_documents(documents)
    
    return jsonify(new_document), 201

@app.route('/documents/<int:doc_id>', methods=['PUT'])
def update_document(doc_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
        
    documents = load_documents()
    for doc in documents:
        if doc['id'] == doc_id:
            # Update fields
            for key, value in data.items():
                if key != 'id': # Prevent ID modification
                    doc[key] = value
            
            save_documents(documents)
            return jsonify(doc), 200
            
    return jsonify({"error": "Document Not Found"}), 404

@app.route('/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    documents = load_documents()
    
    for i, doc in enumerate(documents):
        if doc['id'] == doc_id:
            del documents[i]
            save_documents(documents)
            return '', 204
            
    return jsonify({"error": "Document Not Found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
