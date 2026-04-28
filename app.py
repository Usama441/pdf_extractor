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

        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        sidebar_layout.addWidget(self.select_folder_btn)

        self.extract_btn = QPushButton("Extract Data")
        self.extract_btn.clicked.connect(self.extract_data)
        self.extract_btn.setEnabled(False)
        sidebar_layout.addWidget(self.extract_btn)

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # Main content setup
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        self.folder_label = QLabel("Selected: No folder selected")
        self.folder_label.setStyleSheet("font-size: 14px;")
        content_layout.addWidget(self.folder_label)

        self.files_label = QLabel("Found PDF Files:")
        self.files_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        content_layout.addWidget(self.files_label)

        self.log_textbox = QTextEdit()
        self.log_textbox.setReadOnly(True)
        content_layout.addWidget(self.log_textbox)

        main_layout.addWidget(content_widget)

        self.pdf_files = []
        self.folder_path = ""

        # Check default 'pdf' folder
        default_folder = os.path.join(os.getcwd(), "pdf")
        if os.path.isdir(default_folder):
            self.set_folder(default_folder)

    def log(self, message):
        self.log_textbox.append(message)
        # Force UI update
        QApplication.processEvents()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.set_folder(folder)

    def set_folder(self, folder):
        self.folder_path = folder
        self.folder_label.setText(f"Selected: {self.folder_path}")
        self.log(f"Selected folder: {self.folder_path}")
        
        # Find PDFs
        self.pdf_files = [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]
        
        self.log(f"Found {len(self.pdf_files)} PDF files.")
        for f in self.pdf_files:
            self.log(f" - {f}")
            
        if self.pdf_files:
            self.extract_btn.setEnabled(True)
        else:
            self.extract_btn.setEnabled(False)

    def extract_data(self):
        if not self.pdf_files:
            return
            
        self.log("\nStarting extraction...")
        self.extract_btn.setEnabled(False)
        self.select_folder_btn.setEnabled(False)
        
        output_folder = os.path.join(self.folder_path, "extracted_output")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        for pdf_file in self.pdf_files:
            pdf_path = os.path.join(self.folder_path, pdf_file)
            self.log(f"Processing {pdf_file}...")
            
            try:
                all_data = []
                with pdfplumber.open(pdf_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        tables = page.extract_tables()
                        for table in tables:
                            all_data.extend(table)
                
                if all_data:
                    cleaned_data = [row for row in all_data if any(cell is not None and str(cell).strip() != "" for cell in row)]
                    
                    if cleaned_data:
                        df = pd.DataFrame(cleaned_data)
                        base_name = os.path.splitext(pdf_file)[0]
                        excel_path = os.path.join(output_folder, f"{base_name}.xlsx")
                        csv_path = os.path.join(output_folder, f"{base_name}.csv")
                        
                        df.to_excel(excel_path, index=False, header=False)
                        df.to_csv(csv_path, index=False, header=False)
                        self.log(f"  -> Extracted {len(cleaned_data)} rows. Saved to {excel_path} and .csv")
                    else:
                        self.log(f"  -> No data found in {pdf_file} after cleaning.")
                else:
                    text_data = []
                    with pdfplumber.open(pdf_path) as pdf:
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                lines = text.split('\n')
                                for line in lines:
                                    if line.strip():
                                        text_data.append([line.strip()])
                    
                    if text_data:
                        df = pd.DataFrame(text_data)
                        base_name = os.path.splitext(pdf_file)[0]
                        excel_path = os.path.join(output_folder, f"{base_name}_text.xlsx")
                        csv_path = os.path.join(output_folder, f"{base_name}_text.csv")
                        df.to_excel(excel_path, index=False, header=False)
                        df.to_csv(csv_path, index=False, header=False)
                        self.log(f"  -> No tabular data found. Extracted text lines instead. Saved to {excel_path}")
                    else:
                        self.log(f"  -> No tabular or text data found in {pdf_file}.")
                        
            except Exception as e:
                self.log(f"  -> Error processing {pdf_file}: {str(e)}")
                
        self.log("\nExtraction complete! Files saved in:")
        self.log(output_folder)
        
        QMessageBox.information(self, "Success", "Extraction complete!\nFiles saved in the extracted_output folder.")
        
        self.extract_btn.setEnabled(True)
        self.select_folder_btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = App()
    window.show()
    sys.exit(app.exec())
