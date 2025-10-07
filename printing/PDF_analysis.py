import PyPDF2
import re

def extract_pdf_info(pdf_path):
    orders = []
    leads = []
    isos = []  # 2D list per order

    # Open the PDF
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        num_pages = len(reader.pages)

        for page_index, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if not text:
                text = ""

            # --- Extract order number: first 8-digit numeric ---
            order_match = re.findall(r'\b\d{8}\b', text)
            order_number = order_match[0] if order_match else None

            # --- Extract lead barcode: 10 chars starting with B ---
            lead_match = re.findall(r'\bB[a-zA-Z0-9]{9}\b', text)
            lead_barcode = lead_match[0] if lead_match else None

            # --- Extract ISObarcodes: 11 chars starting with 'o', allow attached text ---
            iso_matches = re.findall(r'o[a-zA-Z0-9]{10}', text, re.IGNORECASE)

            # --- Skip pages without order or lead ---
            if not order_number or not lead_barcode:
                continue

        
            # --- Check if this order/lead already exists ---
            if order_number in orders and lead_barcode in leads:
                idx = orders.index(order_number)
                isos[idx].extend(iso_matches)
            else:
                orders.append(order_number)
                leads.append(lead_barcode)
                isos.append(iso_matches)

    return orders, leads, isos
