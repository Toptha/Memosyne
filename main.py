from modules.extractor.pdf_document import PDFDocument
from modules.extractor.text_document import TextDocument
from modules.extractor.docx_document import DOCXDocument


documents = [

    PDFDocument(
        "test_docs/sample.pdf"
    ),

    TextDocument(
        "test_docs/sample.txt"
    ),

    DOCXDocument(
        "test_docs/sample.docx"
    )
]


for document in documents:

    print("=" * 50)

    print(
        "Class:",
        type(document).__name__
    )

    extracted_content = (
        document.extract_text()
    )

    print(
        "Pages:",
        len(extracted_content)
    )

    print("\nPreview:\n")

    print(
        extracted_content[0]["text"][:150]
    )

    print("=" * 50)