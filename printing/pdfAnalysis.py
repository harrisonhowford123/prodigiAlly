import re
import PyPDF2
import os

def extract_pdf_info(pdf_path):
    orders, leads, isos, quantities, sizes, prodtypes = [], [], [], [], [], []

    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text = page.extract_text() or ''

            # --- SIMPLE POSITION-BASED LEAD/ISO DETECTION ---
            order_match = re.findall(r'\b\d{8}\b', text)
            order_number = order_match[0] if order_match else None

            lead_matches = re.findall(r'B[a-zA-Z0-9]{8,10}', text)
            iso_matches = re.findall(r'[oO][0-9a-zA-Z]{10}', text)

            def has_three_digits(s):
                return sum(c.isdigit() for c in s) >= 3

            lead_matches = [m for m in lead_matches if has_three_digits(m)]
            iso_matches = [m for m in iso_matches if has_three_digits(m)]

            lead_barcode, isos_found = None, []

            # whichever appears first in text is the lead
            if lead_matches and iso_matches:
                lead_code = lead_matches[0]
                iso_code = iso_matches[0]
                lead_pos = text.find(lead_code)
                iso_pos = text.find(iso_code)

                if iso_pos != -1 and lead_pos != -1:
                    if iso_pos < lead_pos:
                        lead_barcode = iso_code
                        isos_found = [lead_code]
                    else:
                        lead_barcode = lead_code
                        isos_found = [iso_code]
                elif iso_pos != -1:
                    lead_barcode = iso_code
                    isos_found = [lead_code]
                elif lead_pos != -1:
                    lead_barcode = lead_code
                    isos_found = [iso_code]

            elif lead_matches:
                lead_barcode = lead_matches[0]
                isos_found = iso_matches
            elif iso_matches:
                lead_barcode = iso_matches[0]
                isos_found = lead_matches

            # --- END UPDATED SECTION ---

            prod_match = re.search(r'ITEMS\s*\d+\s*\[\d+\]\s*([^\n\r]+)', text)
            if prod_match:
                raw_type = prod_match.group(1).strip()
                raw_type = re.split(r'\b(DESTINATION|DATE|CUSTOMER|SHIPPING)\b', raw_type)[0].strip()
                raw_type = re.sub(r'[^A-Za-z\-\s]', '', raw_type).strip()
                page_prodType = re.sub(r'\s+', '-', raw_type.lower())
            else:
                page_prodType = 'unknown'

            special_size = None
            if page_prodType in ['float-framed-canvas', 'classic-slim-framed-canvas']:

                size_match = re.search(r'(\d+mm:\s*[0-9xX]+\")', text)
                depth_part, dimension_part = None, None
                if size_match:
                    special_size = size_match.group(1).replace(':', '/').replace(' ', '')
                    depth_part = re.search(r'(\d+)mm', special_size)
                    dimension_part = re.search(r'/([0-9xX]+\")', special_size)

                frame_match = re.findall(r'([A-Z][a-z]+)\s*(Float|Classic)', text, re.IGNORECASE)
                frame_color, frame_variant = None, None
                if frame_match:
                    last_color, last_variant = frame_match[-1]
                    frame_color = last_color.capitalize()
                    frame_variant = last_variant.capitalize()

                if depth_part and dimension_part:
                    size_core = f"{depth_part.group(1)}mm/{dimension_part.group(1)}"
                    if frame_color and frame_variant:
                        special_size = f"{size_core}/{frame_color} {frame_variant}"
                    else:
                        special_size = size_core
                elif not special_size:
                    special_size = 'Unknown'

            if page_prodType in ['stretched-canvas', 'slim-canvases', 'slim-canvas']:
                depth_match = re.search(r'(19|38)mm', text)
                size_match = re.search(r'Size\s*[:\-]?\s*([0-9xX]+)', text)
                if depth_match and size_match:
                    special_size = f"{depth_match.group(1)}mm/{size_match.group(1)}\""
                else:
                    alt_depth = re.search(r'(19|38)mm', text)
                    alt_size = re.search(r',\s*([0-9xX]+\")', text)
                    if alt_depth and alt_size:
                        special_size = f"{alt_depth.group(1)}mm/{alt_size.group(1).replace('"', '')}\""
                    else:
                        special_size = 'Unknown'

            if not order_number or not lead_barcode:
                continue

            qty_for_next_iso = 1
            iso_list, qty_list, size_list, prod_list = [], [], [], []

            # expanded to also detect B codes
            tokens = re.findall(
                r'(?:Quantity|Qty)\s*[:\-]?\s*(\d+)|([oO][0-9a-zA-Z]{10})|(B[a-zA-Z0-9]{8,10})',
                text,
                re.IGNORECASE
            )

            size_positions = [(m.start(), m.group(1)) for m in re.finditer(r'Size\s*[:\-]?\s*([0-9xX]+mm)', text)]

            for qty_token, iso_o, iso_b in tokens:
                iso_token = iso_o or iso_b
                if iso_token:
                    if has_three_digits(iso_token):
                        iso_pos = text.find(iso_token)
                        nearby_size = 'Unknown'

                        if special_size:
                            nearby_size = special_size
                        elif 'canvas' in page_prodType or 'canvases' in page_prodType:
                            for pos, size_val in size_positions:
                                if pos < iso_pos:
                                    nearby_size = size_val
                                else:
                                    break

                        if iso_token != lead_barcode:
                            iso_list.append(iso_token)
                            qty_list.append(qty_for_next_iso)
                            size_list.append(nearby_size)
                            prod_list.append(page_prodType)

                    qty_for_next_iso = 1
                elif qty_token:
                    qty_for_next_iso = int(qty_token)

            if order_number in orders and lead_barcode in leads:
                idx = orders.index(order_number)
                isos[idx].extend(iso_list)
                quantities[idx].extend(qty_list)
                sizes[idx].extend(size_list)
                prodtypes[idx].extend(prod_list)
            else:
                orders.append(order_number)
                leads.append(lead_barcode)
                isos.append(iso_list)
                quantities.append(qty_list)
                sizes.append(size_list)
                prodtypes.append(prod_list)

    return orders, leads, isos, quantities, sizes, prodtypes
