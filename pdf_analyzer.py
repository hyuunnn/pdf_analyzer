from pypdf import PdfReader
from pypdf.errors import FileNotDecryptedError
import argparse
import os
import io
import logging

logger = logging.getLogger("pypdf._reader")
log_capture = io.StringIO()
handler = logging.StreamHandler(log_capture)
handler.setLevel(logging.WARNING)
logger.addHandler(handler)

def check_warnings(log_lines):
    for log_line in log_lines:
        if "Ignoring wrong pointing" in log_line:
            return True
    return False

def print_structure(pdf):
    num_pages = len(pdf.pages)
    print(f"Total number of pages: {num_pages}\n")

    for page_number, page in enumerate(pdf.pages):
        print(f"Page {page_number + 1} Structure:")
        print(page)
        for key, value in page.items():
            print(f"Key: {key}, Value: {value}")
        print("\n--\n")

def analyze_pdf(path):
    pdf_files = [i for i in os.listdir(path) if i.endswith(".pdf")]
    results = []

    for pdf_file in pdf_files:
        log_capture.truncate(0)
        
        pdf = PdfReader(os.path.join(path, pdf_file))
        is_corrupted = check_warnings(log_capture.getvalue().split("\n"))
        is_encrypted = pdf.is_encrypted
        print(f"File: {pdf_file}")
        print(f"  - Corrupted: {is_corrupted}")
        print(f"  - Encrypted: {is_encrypted}")

        # Determine the PDF type
        if is_corrupted and not is_encrypted:
            pdf_type = "Corrupted PDF"
        elif not is_corrupted and is_encrypted:
            pdf_type = "Encrypted PDF"
        elif not is_corrupted and not is_encrypted:
            pdf_type = "Normal PDF"
        else:
            pdf_type = "Unknown PDF Type"

        results.append({
            "File": pdf_file,
            "Corrupted": is_corrupted,
            "Encrypted": is_encrypted,
            "Type": pdf_type
        })

        try:
            print_structure(pdf)
        except FileNotDecryptedError:
            print("The file is encrypted and cannot be analyzed.\n")

    # Print the summary results
    print("\n--- Summary Results ---")
    for result in results:
        print(f"File: {result['File']}, Corrupted: {result['Corrupted']}, Encrypted: {result['Encrypted']}, Type: {result['Type']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze PDF files")
    parser.add_argument("--path", help="Path to the PDF file", required=True)
    args = parser.parse_args()
    analyze_pdf(args.path)
