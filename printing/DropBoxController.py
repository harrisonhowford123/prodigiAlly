from ContainerWidgets import DraggableBoxContainer
from CoreFunctions import resource_path
from PyQt6.QtCore import QRectF, Qt, QSize, QEvent
from PyQt6.QtWidgets import QPushButton, QWidget, QGridLayout, QGraphicsProxyWidget
from PyQt6.QtGui import QIcon

class DropBoxController(DraggableBoxContainer.ResizableRectItem):
    def __init__(self, rect, parent_view, file_dropbox, title="File Box Remote"):
        super().__init__(rect, parent_view, title)

        self.file_dropbox = file_dropbox

        # Create a widget to hold buttons
        self.control_widget = QWidget()
        self.control_widget.setStyleSheet("background: white;")
        self.layout = QGridLayout(self.control_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Left button - Empty Dropbox
        self.empty_button = QPushButton()
        self.empty_icon_normal = QIcon(resource_path("icons/emptyDropbox.png"))
        self.empty_icon_hovered = QIcon(resource_path("icons/emptyDropbox(Hovered).png"))
        self.empty_button.setIcon(self.empty_icon_normal)
        self.empty_button.setFlat(True)
        self.empty_button.setStyleSheet("background: white; border: none;")
        self.empty_button.clicked.connect(self.empty_dropbox)

        # Hover events for Empty button
        self.empty_button.enterEvent = lambda event: self.empty_button.setIcon(self.empty_icon_hovered)
        self.empty_button.leaveEvent = lambda event: self.empty_button.setIcon(self.empty_icon_normal)

        # Right button - Process Dropbox
        self.send_button = QPushButton()
        self.send_icon_normal = QIcon(resource_path("icons/processDropbox.png"))
        self.send_icon_hovered = QIcon(resource_path("icons/processDropbox(Hovered).png"))
        self.send_button.setIcon(self.send_icon_normal)
        self.send_button.setFlat(True)
        self.send_button.setStyleSheet("background: white; border: none;")
        self.send_button.clicked.connect(self.send_dropbox)

        # Hover events for Send button
        self.send_button.enterEvent = lambda event: self.send_button.setIcon(self.send_icon_hovered)
        self.send_button.leaveEvent = lambda event: self.send_button.setIcon(self.send_icon_normal)

        # Third button - Example media button
        self.media_button = QPushButton()
        self.media_icon_normal = QIcon(resource_path("icons/mediaEx.png"))
        self.media_icon_hovered = QIcon(resource_path("icons/mediaEx(Hovered).png"))
        self.media_button.setIcon(self.media_icon_normal)
        self.media_button.setFlat(True)
        self.media_button.setStyleSheet("background: white; border: none;")
        self.media_button.clicked.connect(self.save_blank_pdf)

        # Hover events for Media button
        self.media_button.enterEvent = lambda event: self.media_button.setIcon(self.media_icon_hovered)
        self.media_button.leaveEvent = lambda event: self.media_button.setIcon(self.media_icon_normal)

        # Add all three buttons side-by-side
        self.layout.addWidget(self.empty_button, 0, 0, Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.send_button, 0, 1, Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.media_button, 0, 2, Qt.AlignmentFlag.AlignCenter)


        # Embed the control widget into the graphics container
        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(self.control_widget)

        self.update_geometry(rect.width(), rect.height())

    def send_dropbox(self):
        if self.file_dropbox and hasattr(self.file_dropbox, "processContainer"):
            self.file_dropbox.processContainer()
            print("[DEBUG] Triggered processContainer from controller.")
        else:
            print("[ERROR] file_dropbox does not have processContainer().")


    def empty_dropbox(self):
        if self.file_dropbox and hasattr(self.file_dropbox, "drop_widget"):
            drop = self.file_dropbox.drop_widget

            # Clear UI and internal file tracking
            drop.clear()
            drop.pdf_paths.clear()
            drop.placeholder.setVisible(True)

            # Update statistics (so zero counts show up)
            if hasattr(self.file_dropbox, "handle_drop_summary"):
                self.file_dropbox.handle_drop_summary()

            print("[DEBUG] Dropbox emptied and statistics updated.")


    def update_geometry(self, width, height):
        """Align control widget below title bar and enforce square buttons that resize dynamically."""
        if self.proxy:
            border_margin = 5
            title_offset = self.TITLE_BAR_HEIGHT + border_margin

            # Set proxy geometry below the title bar
            new_rect = QRectF(
                border_margin,
                title_offset,
                max(0, width - border_margin * 2),
                max(0, height - title_offset - border_margin)
            )
            self.proxy.setGeometry(new_rect)

            # Compute available width and height for each button
            third_width = new_rect.width() / 3
            available_height = new_rect.height()

            # Determine square side and enforce 1:1 aspect ratio
            square_side = int(min(third_width, available_height)) - 8
            square_side = max(32, square_side)

            for button in (self.empty_button, self.send_button, self.media_button):
                button.setFixedSize(square_side, square_side)
                button.setIconSize(QSize(square_side - 6, square_side - 6))

            # Keep layout centered and even
            self.layout.setColumnStretch(0, 1)
            self.layout.setColumnStretch(1, 1)
            self.layout.setColumnStretch(2, 1)
            self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.activate()
            self.control_widget.update()


    def setRect(self, rect):
        super().setRect(rect)
        if hasattr(self, "proxy"):
            self.update_geometry(rect.width(), rect.height())

    def itemChange(self, change, value):
        """Ensure buttons stay scaled correctly during parent or fullscreen resizing."""
        if change in (
            self.GraphicsItemChange.ItemPositionChange,
            self.GraphicsItemChange.ItemPositionHasChanged,
            self.GraphicsItemChange.ItemTransformChange,
            self.GraphicsItemChange.ItemSceneHasChanged,
        ):
            rect = self.rect()
            if hasattr(self, "proxy"):
                self.update_geometry(rect.width(), rect.height())
        return super().itemChange(change, value)


    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

    def save_blank_pdf(self):
        """Generate a PDF with centered logo at top and thumbnails arranged in 7 columns (no grid lines)."""
        from PyQt6.QtWidgets import QFileDialog, QApplication
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from CoreFunctions import resource_path
        import os
        from PIL import Image
        import fitz  # PyMuPDF for PDF thumbnails

        # Ask where to save
        file_path, _ = QFileDialog.getSaveFileName(None, "Save File Grid PDF", "", "PDF Files (*.pdf)")
        if not file_path:
            print("[INFO] Save canceled by user.")
            return
        if not file_path.lower().endswith(".pdf"):
            file_path += ".pdf"

        try:
            c = canvas.Canvas(file_path, pagesize=A4)
            page_width, page_height = A4

            # ---------------- Draw centered logo ----------------
            logo_path = resource_path("images/prodigiAllyLogo(Black).png")
            margin_y = 40
            logo_height = 0

            if os.path.exists(logo_path):
                logo_width = page_width * 0.3  # 30% of page width for balance
                with Image.open(logo_path) as img:
                    aspect_ratio = img.height / img.width
                    logo_height = logo_width * aspect_ratio

                x_centered = (page_width - logo_width) / 2
                y_position = page_height - margin_y - logo_height
                c.drawImage(
                    logo_path,
                    x_centered,
                    y_position,
                    width=logo_width,
                    height=logo_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
                print(f"[DEBUG] Centered logo drawn: {logo_path}")
            else:
                print(f"[WARNING] Logo not found: {logo_path}")

            # ---------------- Prepare grid geometry ----------------
            top_of_grid = page_height - (margin_y + logo_height + 30)  # small gap under logo
            bottom_of_grid = 40
            left_edge = 40
            right_edge = page_width - 40
            grid_width = right_edge - left_edge
            grid_height = top_of_grid - bottom_of_grid

            squares_per_row = 7
            square_size = grid_width / squares_per_row
            squares_per_col = int(grid_height // square_size)
            total_slots = squares_per_row * squares_per_col
            print(f"[DEBUG] Grid area: {squares_per_row}x{squares_per_col} (no lines drawn)")

            # ---------------- Collect files ----------------
            QApplication.processEvents()
            if not self.file_dropbox or not hasattr(self.file_dropbox, "drop_widget"):
                print("[ERROR] No dropbox found.")
                c.save()
                return

            files_dict = getattr(self.file_dropbox.drop_widget, "pdf_paths", {})
            files = list(files_dict.values())
            print(f"[DEBUG] Files found: {len(files)} -> {list(files_dict.keys())}")

            # ---------------- Draw thumbnails ----------------
            cell_index = 0
            for file_path in files:
                if cell_index >= total_slots:
                    print("[INFO] Grid full, remaining files skipped.")
                    break

                row = cell_index // squares_per_row
                col = cell_index % squares_per_row
                x = left_edge + col * square_size
                y = top_of_grid - (row + 1) * square_size

                try:
                    thumb_img = None

                    # Handle image files
                    if file_path.lower().endswith((".png", ".jpg", ".jpeg")):
                        thumb_img = Image.open(file_path)

                    # Handle PDFs with PyMuPDF
                    elif file_path.lower().endswith(".pdf"):
                        doc = fitz.open(file_path)
                        if len(doc) > 0:
                            page = doc.load_page(0)
                            pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
                            thumb_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        doc.close()

                    if thumb_img:
                        # Resize proportionally
                        thumb_img.thumbnail((square_size * 0.85, square_size * 0.85))
                        tmp_path = os.path.join(os.path.dirname(file_path), "_thumb_temp.png")
                        thumb_img.save(tmp_path)

                        img_w, img_h = thumb_img.size
                        img_x = x + (square_size - img_w) / 2
                        img_y = y + (square_size - img_h) / 2
                        c.drawImage(tmp_path, img_x, img_y, width=img_w, height=img_h)
                        os.remove(tmp_path)

                        # Draw filename label below image
                        name = os.path.basename(file_path)
                        if len(name) > 20:
                            name = name[:17] + "..."
                        c.setFont("Helvetica", 6)
                        c.setFillColor(colors.black)
                        c.drawCentredString(x + square_size / 2, y + 2, name)
                    else:
                        print(f"[WARN] Unsupported or unreadable file: {file_path}")

                except Exception as err:
                    print(f"[ERROR] Failed to render thumbnail for {file_path}: {err}")

                cell_index += 1

            # ---------------- Save PDF ----------------
            c.showPage()
            c.save()
            print(f"[DEBUG] Thumbnail grid PDF saved at: {file_path}")

        except Exception as e:
            print(f"[ERROR] Failed to create PDF: {e}")






