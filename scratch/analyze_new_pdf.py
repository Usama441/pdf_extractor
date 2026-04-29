import pdfplumber
import os

pdf_path = "/home/infiniti/Projects/Pdf_extrector/pdf/E-STATEMENT_02JUL2025_3601_unlocked.pdf"

if not os.path.exists(pdf_path):
    print(f"File not found: {pdf_path}")
    exit(1)

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    for i, page in enumerate(pdf.pages[:3]):
        print(f"\n--- Page {i+1} ---")
        text = page.extract_text()
        print("TEXT PREVIEW:")
        if text:
            lines = text.split('\n')
            for line in lines[:30]:
                print(line)
        else:
            print("No text extracted.")
        
        print("\nWORD SAMPLE (First 20 words):")
        words = page.extract_words()
        for w in words[:20]:
            print(f"Text: {w['text']:20} x0: {w['x0']:<10.2f} x1: {w['x1']:<10.2f} top: {w['top']:<10.2f} bottom: {w['bottom']:<10.2f}")
