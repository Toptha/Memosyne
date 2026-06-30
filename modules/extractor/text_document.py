from modules.extractor.document import Document


class TextDocument(Document):

    def extract_text(self):

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as file:

            text = file.read()

        return [
            {
                "page": 1,
                "text": text
            }
        ]