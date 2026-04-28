import sys
import os
import pdfplumber
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bank Statement Extractor")
        self.resize(700, 500)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Sidebar setup
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar.setFixedWidth(200)

        self.logo_label = QLabel("PDF Extractor")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        sidebar_layout.addWidget(self.logo_label)

        self.select_file_btn = QPushButton("Select File")
        self.select_file_btn.clicked.connect(self.select_file)
        sidebar_layout.addWidget(self.select_file_btn)

        self.extract_btn = QPushButton("Extract Data")
        self.extract_btn.clicked.connect(self.extract_data)
        self.extract_btn.setEnabled(False)
        sidebar_layout.addWidget(self.extract_btn)

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # Main content setup
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        self.file_label = QLabel("Selected: No file selected")
        self.file_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        content_layout.addWidget(self.file_label)

        self.log_textbox = QTextEdit()
        self.log_textbox.setReadOnly(True)
        content_layout.addWidget(self.log_textbox)

        main_layout.addWidget(content_widget)

        self.pdf_file = ""

    def log(self, message):
        self.log_textbox.append(message)
        # Force UI update
        QApplication.processEvents()

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.set_file(file_path)

    def set_file(self, file_path):
        self.pdf_file = file_path
        self.file_label.setText(f"Selected: {os.path.basename(self.pdf_file)}")
        self.log(f"Selected file: {self.pdf_file}")
        
        if self.pdf_file:
            self.extract_btn.setEnabled(True)
        else:
            self.extract_btn.setEnabled(False)

    def extract_data(self):
        if not self.pdf_file:
            return
            
        self.log("\nStarting extraction...")
        self.extract_btn.setEnabled(False)
        self.select_file_btn.setEnabled(False)
        
        output_folder = os.path.join(os.path.dirname(self.pdf_file), "extracted_output")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        pdf_file = os.path.basename(self.pdf_file)
        pdf_path = self.pdf_file
        self.log(f"Processing {pdf_file}...")
        
        def save_styled_excel(dataframe, path):
            with pd.ExcelWriter(path, engine='openpyxl') as writer:
                dataframe.to_excel(writer, index=False, header=False, sheet_name='Transactions')
                worksheet = writer.sheets['Transactions']
                
                from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
                header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
                header_font = Font(color="FFFFFF", bold=True)
                thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
                
                for row in worksheet.iter_rows():
                    for cell in row:
                        cell.border = thin_border
                        if cell.row == 1:
                            cell.fill = header_fill
                            cell.font = header_font
                            cell.alignment = Alignment(horizontal="center", vertical="center")
                        else:
                            cell.alignment = Alignment(vertical="center", wrap_text=True)
                
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    worksheet.column_dimensions[column_letter].width = min(max_length + 2, 50)

        try:
            import re
            
            date_pattern = re.compile(r'(\d{2}[-/]\w{3}[-/]\d{2,4}|\d{2}[-/]\d{2}[-/]\d{2,4}|\d{4}[-/]\d{2}[-/]\d{2})')
            
            skip_keywords = [
                'your bank statement', 'account summary', 'opening balance',
                'closing balance', 'total deposits', 'total withdrawals',
                'interest rate', 'overdue charges', 'interest type',
                'please see', 'important information', 'the national bank',
                '"rakbank"', 'central bank of', 'page [', 'page ', 'disclaimer',
                'end of day', 'summary ', 'payments in', 'payments out',
                'get in touch', 'for queries', 'for complaints', 'call 04',
                'we aim', 'this is a digitally', 'accrued interest',
                'account number:', 'branch:', 'currency:', 'iban:',
                'account type:', 'statement period:', 'date issued:',
                '24hr customer service', 'www.starling', 'sort code:',
                'account name:', 'financial services', 'your deposit',
                '© 2025', 'wio bank', 'this bank is regulated',
                'please review', 'within 30 days', 'correct (subject',
                'to raise a complaint', 'summary of accounts',
                'account statement', 'account holder',
                'the items and balance', 'verified. report any',
                'of the statement date', 'accurate.', 'all charges, terms',
                'please note that for foreign', 'indicative only',
                'mashreqbank psc', 'it is the policy', 'full compliance',
                'with iran, syria', 'dear customer', 'statement for period',
                'customer number', 'account currency', 'account number ',
                'يكنبلا', 'يراجلا', 'خيراتلا', 'فصولا', 'كيشلا',
                'بحسلا', 'ةعيدولا', 'ديصرلا', 'باسحلا', 'ةدئافلا',
                'ةرخأتملا', 'ةفاضملا', '.ةمهم', 'ينطولا', 'يزكرملا',
                'تامولعم', 'فشكلا', 'رادصإلا',
            ]
            
            def is_skip_line(line):
                lower = line.lower()
                for kw in skip_keywords:
                    if kw in lower:
                        return True
                ascii_chars = sum(1 for c in line if ord(c) < 128 and c.isalpha())
                has_digits = any(c.isdigit() for c in line)
                if ascii_chars == 0 and len(line) > 5 and not has_digits:
                    return True
                # Skip "page1 of4", "page 2 of 4" etc.
                if re.match(r'^page\s*\d+\s*of\s*\d+$', lower.strip()):
                    return True
                return False
            
            # Step 1: Extract text and find header line
            all_lines = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        for line in text.split('\n'):
                            all_lines.append(line.strip())
            
            if not all_lines:
                self.log(f"  -> No text found in {pdf_file}.")
                self.extract_btn.setEnabled(True)
                self.select_file_btn.setEnabled(True)
                return
            
            header_kws_detect = ['date', 'description', 'balance', 'amount', 'withdrawal', 
                                 'deposit', 'credit', 'debit', 'transaction', 'type', 'ref.', 'reference']
            header_line = None
            for i, line in enumerate(all_lines):
                lower = line.lower().strip()
                if 'date' not in lower:
                    continue
                matches = sum(1 for kw in header_kws_detect if kw in lower)
                if matches >= 2:
                    header_line = line.strip()
                    break
            
            if not header_line:
                self.log(f"  -> Could not detect table header in {pdf_file}.")
                self.extract_btn.setEnabled(True)
                self.select_file_btn.setEnabled(True)
                return
            
            # Step 2: Use word-level extraction to find header column positions
            known_multi_word = {
                'reference number': 'Reference Number',
                'account balance': 'Account Balance',
                'ref. number': 'Ref. Number',
            }
            
            with pdfplumber.open(pdf_path) as pdf:
                # Find header words on the page
                header_words_found = []
                header_top = None
                header_page_idx = None
                
                for page_idx, page in enumerate(pdf.pages):
                    words = page.extract_words()
                    # Look for a line with at least 3 header keywords
                    # Group words by y position
                    y_groups = {}
                    for w in words:
                        y_key = round(w['top'] / 4) * 4
                        if y_key not in y_groups:
                            y_groups[y_key] = []
                        y_groups[y_key].append(w)
                    
                    sorted_y_keys = sorted(y_groups.keys())
                    for y_idx, y_key in enumerate(sorted_y_keys):
                        line_words = y_groups[y_key]
                        line_text = ' '.join([w['text'].lower() for w in line_words])
                        kw_matches = sum(1 for kw in header_kws_detect if kw in line_text)
                        if kw_matches >= 3 and 'date' in line_text:
                            header_top = line_words[0]['top']
                            header_page_idx = page_idx
                            
                            # Collect header words from this line AND adjacent lines (±10 y)
                            for adj_y in sorted_y_keys:
                                if abs(adj_y - y_key) <= 12:  # Within ~12 px
                                    for w in y_groups[adj_y]:
                                        wt = w['text'].lower()
                                        if wt in header_kws_detect or wt in ('in', 'out', 'number', 'cheque', 'ref.', 'reference', 'account'):
                                            header_words_found.append(w)
                                    # Update header_top to the latest line if it's after
                                    if adj_y > y_key:
                                        header_top = max(header_top, max(w['top'] for w in y_groups[adj_y]))
                            break
                    if header_words_found:
                        break
                
                if not header_words_found:
                    self.log(f"  -> Could not locate header positions in {pdf_file}.")
                    self.extract_btn.setEnabled(True)
                    self.select_file_btn.setEnabled(True)
                    return
                
                # Sort by x position and merge multi-word columns
                header_words_found.sort(key=lambda w: w['x0'])
                
                merged_cols = []
                i = 0
                while i < len(header_words_found):
                    w = header_words_found[i]
                    # Skip Arabic words
                    if any(ord(c) > 127 for c in w['text']):
                        i += 1
                        continue
                    if i + 1 < len(header_words_found):
                        nw = header_words_found[i + 1]
                        two = (w['text'] + ' ' + nw['text']).lower()
                        if two in known_multi_word:
                            merged_cols.append({
                                'text': known_multi_word[two],
                                'x0': w['x0'], 'x1': nw['x1']
                            })
                            i += 2
                            continue
                    merged_cols.append({'text': w['text'].capitalize(), 'x0': w['x0'], 'x1': w['x1']})
                    i += 1
                
                col_names = [c['text'] for c in merged_cols]
                
                # Build column boundaries (midpoints between adjacent columns)
                col_ranges = []
                for ci, col in enumerate(merged_cols):
                    x_start = 0 if ci == 0 else (merged_cols[ci - 1]['x1'] + col['x0']) / 2
                    x_end = 9999 if ci == len(merged_cols) - 1 else (col['x1'] + merged_cols[ci + 1]['x0']) / 2
                    col_ranges.append((x_start, x_end))
                
                self.log(f"  -> Detected columns: {col_names}")
                
                # Step 3: Extract all data words and assign to columns by x-position
                all_word_rows = []
                
                for page_idx, page in enumerate(pdf.pages):
                    words = page.extract_words()
                    
                    # Skip words above header on the header page
                    if page_idx == header_page_idx and header_top is not None:
                        words = [w for w in words if w['top'] > header_top + 10]
                    elif page_idx < header_page_idx:
                        continue
                    
                    # Group words by y position (same visual line)
                    y_groups = {}
                    for w in words:
                        y_key = round(w['top'] / 4) * 4
                        if y_key not in y_groups:
                            y_groups[y_key] = []
                        y_groups[y_key].append(w)
                    
                    for y_key in sorted(y_groups.keys()):
                        all_word_rows.append(y_groups[y_key])
                
                # Step 4: Build structured rows from word positions
                raw_rows = []
                for words_in_line in all_word_rows:
                    row = [''] * len(col_names)
                    for w in sorted(words_in_line, key=lambda x: x['x0']):
                        word_center = (w['x0'] + w['x1']) / 2
                        best_col = 0
                        for ci, (x_start, x_end) in enumerate(col_ranges):
                            if x_start <= word_center <= x_end:
                                best_col = ci
                                break
                        if row[best_col]:
                            row[best_col] += ' ' + w['text']
                        else:
                            row[best_col] = w['text']
                    
                    # Skip boilerplate rows
                    row_text = ' '.join(row)
                    if is_skip_line(row_text):
                        continue
                    if not any(cell.strip() for cell in row):
                        continue
                    
                    raw_rows.append(row)
            
            # Step 5: Merge multi-line transactions
            # A new transaction starts when the Date column has a date
            transactions = []
            current_txn = None
            
            for row in raw_rows:
                has_date = date_pattern.search(row[0]) if row[0] else False
                
                if has_date:
                    if current_txn:
                        transactions.append(current_txn)
                    current_txn = [list(row)]
                else:
                    if current_txn:
                        current_txn.append(list(row))
            
            if current_txn:
                transactions.append(current_txn)
            
            if not transactions:
                self.log(f"  -> No transactions found in {pdf_file}.")
            else:
                # Merge multi-row transactions into single rows
                output_data = [col_names]
                
                for txn_rows in transactions:
                    merged = [''] * len(col_names)
                    for row in txn_rows:
                        for ci, cell in enumerate(row):
                            if cell.strip():
                                if merged[ci]:
                                    merged[ci] += '\n' + cell.strip()
                                else:
                                    merged[ci] = cell.strip()
                    output_data.append(merged)
                
                df = pd.DataFrame(output_data)
                base_name = os.path.splitext(pdf_file)[0]
                excel_path = os.path.join(output_folder, f"{base_name}.xlsx")
                
                save_styled_excel(df, excel_path)
                self.log(f"  -> Extracted {len(transactions)} transactions. Saved to {excel_path}")
                    
        except Exception as e:
            import traceback
            self.log(f"  -> Error processing {pdf_file}: {str(e)}")
            self.log(traceback.format_exc())
            
        self.log("\nExtraction complete! File saved in:")
        self.log(output_folder)
        
        QMessageBox.information(self, "Success", "Extraction complete!\nFile saved in the extracted_output folder.")
        
        self.extract_btn.setEnabled(True)
        self.select_file_btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = App()
    window.show()
    sys.exit(app.exec())
