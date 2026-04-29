import pdfplumber
import os

pdf_path = "/home/infiniti/Projects/Pdf_extrector/pdf/ADCBStmt01Jan25to31Jan25.pdf"
password = "enter_password_here" # I don't know the password, but the user does.
# Wait, I can't run it with the password if I don't know it.

# I'll try to extract the first few pages and see the raw text if I can.
# Actually, I'll just ask the user for some examples or try to guess based on common ADCB formats.
# But better: I can try to find a way to analyze without password if possible? No.

# Wait, the user successfully extracted it! So they entered the password.
# I can't rerun extraction here without the password.

# However, I can look at the TEXT that pdfplumber might be seeing if I could.
# Since I can't, I'll ask the user for a screenshot of the "extra text" or I'll try to find common ADCB boilerplate.

# Common ADCB boilerplate:
# - "Abu Dhabi Commercial Bank PJSC"
# - "Head Office"
# - "Page X of Y"
# - "Summary of Accounts"
# - "Transaction Details"
# - "Value Date"
# - "Balance"
# - "Serial No"
# - "Description"

# Let's look at the ADCB PDF name: ADCBStmt01Jan25to31Jan25.pdf
# I'll create a scratch script that the user can run to SHOW me the extra text? 
# Or I'll just add common ADCB keywords.
