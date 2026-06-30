from modules.extractor.pdf_document import PDFDocument
from modules.extractor.text_document import TextDocument
from modules.extractor.docx_document import DOCXDocument


class DocumentFactory:

    @staticmethod
    def create_document(file_path):

        file_path = file_path.lower()

        if file_path.endswith(".pdf"):
            return PDFDocument(file_path)

        elif file_path.endswith(".txt"):
            return TextDocument(file_path)

        elif file_path.endswith(".docx"):
            return DOCXDocument(file_path)

        raise ValueError(
            "Unsupported file format"
        )