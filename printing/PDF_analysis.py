import PyPDF2
import re

def extract_pdf_info(pdf_path):
    orders = []
    leads = []
    isos = []  # 2D list per order
    quantities = []  # 2D list per order
    
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
            
            # --- Extract ISO barcodes: 11 chars starting with 'o', allow attached text ---
            iso_matches = re.findall(r'o[a-zA-Z0-9]{10}', text, re.IGNORECASE)
            
            # --- Skip pages without order or lead ---
            if not order_number or not lead_barcode:
                continue
            
            # --- Extract quantities for each ISO ---
            qty_list = []
            for iso in iso_matches:
                # Find the ISO position in text
                iso_pos = text.find(iso)
                if iso_pos != -1:
                    # Look at text before the ISO
                    text_before = text[:iso_pos]
                    # Try to find quantity pattern
                    qty_match = re.search(r'(?:Quantity|Qty)\s*[:\-]?\s*(\d+)', text_before, re.IGNORECASE)
                    qty = int(qty_match.group(1)) if qty_match else 1
                    qty_list.append(qty)
                else:
                    qty_list.append(1)
            
            # --- Check if this order/lead already exists ---
            if order_number in orders and lead_barcode in leads:
                idx = orders.index(order_number)
                isos[idx].extend(iso_matches)
                quantities[idx].extend(qty_list)
            else:
                orders.append(order_number)
                leads.append(lead_barcode)
                isos.append(iso_matches)
                quantities.append(qty_list)
    
    return orders, leads, isos, quantities
