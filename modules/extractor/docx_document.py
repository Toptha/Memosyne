from docx import Document as DocxReader

from modules.extractor.document import Document


class DOCXDocument(Document):

    def extract_text(self):

        doc = DocxReader(self.file_path)

        text = "\n".join(
            paragraph.text
            for paragraph in doc.paragraphs
        )

        return [
            {
                "page": 1,
                "text": text
            }
        ]