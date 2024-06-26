import fitz
import re
import argparse
import os

class PDFRedactor:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.patterns = {
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'PHONE': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'NAME': r'\b[A-Z][a-z]*\s[A-Z][a-z]*\b'
        }

    def redact_pdf(self):
        try:
            print(f"Opening: {self.input_path}")
            doc = fitz.open(self.input_path)
            print(f"Doc opened successfully. Number of pages: {len(doc)}")

            for page_num, page in enumerate(doc):
                print(f"Processing page {page_num + 1}")
                blocks = page.get_text("dict")["blocks"]
                
                for block in blocks:
                    if block['type'] == 0:  # text block
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"]
                                
                                for pattern_name, pattern in self.patterns.items():
                                    matches = re.finditer(pattern, text)
                                    for match in matches:
                                        start, end = match.span()
                                        matched_text = text[start:end]
                                        inst = page.search_for(matched_text, quads=True)
                                        for quad in inst:
                                            print(f"Redacting {pattern_name}: '{matched_text}' at {quad}")
                                            page.add_redact_annot(quad, fill=(0, 0, 0))
                
                page.apply_redactions()
                print(f"Redactions applied to page {page_num + 1}")

            print(f"Saving document to: {self.output_path}")
            doc.save(self.output_path, garbage=4, deflate=True)
            doc.close()
            print(f"Redacted PDF saved as {self.output_path}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Redact sensitive information from PDF files.")
    parser.add_argument("input_pdf", help="Path to the input PDF file")
    parser.add_argument("output_pdf", help="Path to save the redacted PDF file")
    args = parser.parse_args()

    if not os.path.exists(args.input_pdf):
        print(f"Error: Input file '{args.input_pdf}' does not exist.")
        return

    redactor = PDFRedactor(args.input_pdf, args.output_pdf)
    redactor.redact_pdf()

if __name__ == "__main__":
    main()
