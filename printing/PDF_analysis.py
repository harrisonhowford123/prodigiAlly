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
            
            # --- Extract all potential lead and ISO barcodes ---
            lead_matches = re.findall(r'B[a-zA-Z0-9]{9}', text)
            iso_matches = re.findall(r'o[a-zA-Z0-9]{10}', text, re.IGNORECASE)

            # --- Filter out barcodes that don't have at least 2 digits ---
            def has_two_digits(s):
                return sum(c.isdigit() for c in s) >= 2

            lead_matches = [m for m in lead_matches if has_two_digits(m)]
            iso_matches = [m for m in iso_matches if has_two_digits(m)]

            # DEBUG: Print info for first 4 orders
            if order_number in ['13565721', '13565755', '13565810', '13565866']:
                print(f"\n{'='*60}")
                print(f"[DEBUG] Page {page_index} - Order: {order_number}")
                print(f"  Lead matches (B...): {lead_matches}")
                print(f"  ISO matches (o...): {iso_matches}")
                print(f"  len(lead_matches): {len(lead_matches)}")
                print(f"  len(iso_matches): {len(iso_matches)}")

            # --- Determine which group is lead vs ISO based on count ---
            if len(iso_matches) > 1:
                if order_number in ['13565721', '13565755', '13565810', '13565866']:
                    print(f"  → Branch: len(iso_matches) > 1")
                isos_found = iso_matches
                lead_barcode = lead_matches[0] if lead_matches else None
            elif len(lead_matches) > 1:
                if order_number in ['13565721', '13565755', '13565810', '13565866']:
                    print(f"  → Branch: len(lead_matches) > 1")
                isos_found = lead_matches
                lead_barcode = iso_matches[0] if iso_matches else None
            elif len(iso_matches) == 1 and len(lead_matches) == 1:
                if order_number in ['13565721', '13565755', '13565810', '13565866']:
                    print(f"  → Branch: Single ISO and single lead")
                # Single ISO and single lead case - determine by position
                iso_pos = text.find(iso_matches[0])
                lead_pos = text.find(lead_matches[0])
                
                if order_number in ['13565721', '13565755', '13565810', '13565866']:
                    print(f"  iso_pos: {iso_pos}, lead_pos: {lead_pos}")
                
                if iso_pos < lead_pos:
                    # ISO format appears first, so it's the lead
                    if order_number in ['13565721', '13565755', '13565810', '13565866']:
                        print(f"  → ISO appears first, using as lead")
                    lead_barcode = iso_matches[0]
                    isos_found = lead_matches
                else:
                    # Lead format appears first, so it's the lead
                    if order_number in ['13565721', '13565755', '13565810', '13565866']:
                        print(f"  → Lead appears first, using as lead")
                    lead_barcode = lead_matches[0]
                    isos_found = iso_matches
            else:
                if order_number in ['13565721', '13565755', '13565810', '13565866']:
                    print(f"  → Branch: ELSE (fallback)")
                # fallback if structure doesn't fit expected pattern
                isos_found = []
                lead_barcode = None

            # DEBUG: Print results
            if order_number in ['13565721', '13565755', '13565810', '13565866']:
                print(f"  Final lead_barcode: {lead_barcode}")
                print(f"  Final isos_found: {isos_found}")
                print(f"  Will skip? {not order_number or not lead_barcode}")
                print(f"{'='*60}\n")

            # --- Skip pages without order or lead ---
            if not order_number or not lead_barcode:
                continue
            
            # --- Extract quantities for each ISO ---
            qty_list = []
            for iso in isos_found:
                iso_pos = text.find(iso)
                if iso_pos != -1:
                    text_before = text[:iso_pos]
                    qty_match = re.search(r'(?:Quantity|Qty)\s*[:\-]?\s*(\d+)', text_before, re.IGNORECASE)
                    qty = int(qty_match.group(1)) if qty_match else 1
                    qty_list.append(qty)
                else:
                    qty_list.append(1)
            
            # --- Check if this order/lead already exists ---
            if order_number in orders and lead_barcode in leads:
                idx = orders.index(order_number)
                isos[idx].extend(isos_found)
                quantities[idx].extend(qty_list)
            else:
                orders.append(order_number)
                leads.append(lead_barcode)
                isos.append(isos_found)
                quantities.append(qty_list)
    
    return orders, leads, isos, quantities
