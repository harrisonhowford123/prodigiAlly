import re
import PyPDF2
import os

def extract_pdf_info(pdf_path):
            orders, leads, isos, quantities, sizes, prodtypes = [], [], [], [], [], []

            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text() or ''

                    # Extract order, lead, ISOs
                    order_match = re.findall(r'\b\d{8}\b', text)
                    order_number = order_match[0] if order_match else None

                    lead_matches = re.findall(r'B[a-zA-Z0-9]{9}', text)
                    iso_matches = re.findall(r'[oO][0-9a-zA-Z]{10}', text)

                    # Detect page-level product type (e.g. '6 [9] posters')
                    prod_match = re.search(r'ITEMS\s*\d+\s*\[\d+\]\s*([A-Za-z]+)', text)
                    page_prodType = prod_match.group(1) if prod_match else 'Unknown'

                    def has_three_digits(s):
                        return sum(c.isdigit() for c in s) >= 3

                    lead_matches = [m for m in lead_matches if has_three_digits(m)]
                    iso_matches = [m for m in iso_matches if has_three_digits(m)]

                    if len(iso_matches) > 1:
                        isos_found = iso_matches
                        lead_barcode = lead_matches[0] if lead_matches else None
                    elif len(lead_matches) > 1:
                        isos_found = lead_matches
                        lead_barcode = iso_matches[0] if iso_matches else None
                    elif len(iso_matches) == 1 and len(lead_matches) == 1:
                        iso_pos = text.find(iso_matches[0])
                        lead_pos = text.find(lead_matches[0])
                        if iso_pos < lead_pos:
                            lead_barcode = iso_matches[0]
                            isos_found = lead_matches
                        else:
                            lead_barcode = lead_matches[0]
                            isos_found = iso_matches
                    else:
                        isos_found, lead_barcode = [], None

                    if not order_number or not lead_barcode:
                        continue

                    qty_for_next_iso = 1
                    iso_list, qty_list, size_list, prod_list = [], [], [], []

                    tokens = re.findall(
                        r'(?:Quantity|Qty)\s*[:\-]?\s*(\d+)|([oO][0-9a-zA-Z]{10})',
                        text,
                        re.IGNORECASE
                    )

                    # Pre-extract all size markers with their positions
                    size_positions = [(m.start(), m.group(1)) for m in re.finditer(r'Size\s*[:\-]?\s*([0-9xX]+mm)', text)]

                    for qty_token, iso_token in tokens:
                        if iso_token:
                            if has_three_digits(iso_token):
                                iso_pos = text.find(iso_token)
                                nearby_size = 'Unknown'
                                for pos, size_val in size_positions:
                                    if pos < iso_pos:
                                        nearby_size = size_val
                                    else:
                                        break
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
