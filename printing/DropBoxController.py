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
        self.layout = QGridLayout(self.control_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Left button - Empty Dropbox
        self.empty_button = QPushButton()
        self.empty_icon_normal = QIcon(resource_path("icons/emptyDropbox.png"))
        self.empty_icon_hovered = QIcon(resource_path("icons/emptyDropbox(Hovered).png"))
        self.empty_button.setIcon(self.empty_icon_normal)
        self.empty_button.setFlat(True)
        self.empty_button.setStyleSheet("background: transparent; border: none;")
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
        self.send_button.setStyleSheet("background: transparent; border: none;")
        self.send_button.clicked.connect(self.send_dropbox)

        # Hover events for Send button
        self.send_button.enterEvent = lambda event: self.send_button.setIcon(self.send_icon_hovered)
        self.send_button.leaveEvent = lambda event: self.send_button.setIcon(self.send_icon_normal)

        # Add buttons side-by-side
        self.layout.addWidget(self.empty_button, 0, 0, Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.send_button, 0, 1, Qt.AlignmentFlag.AlignCenter)

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

            # Compute available half width and height for each button
            half_width = new_rect.width() / 2
            available_height = new_rect.height()

            # Determine square side and enforce 1:1 aspect ratio
            square_side = int(min(half_width, available_height)) - 8
            square_side = max(32, square_side)

            for button in (self.empty_button, self.send_button):
                button.setFixedSize(square_side, square_side)
                button.setIconSize(QSize(square_side - 6, square_side - 6))

            # Keep layout centered and even
            self.layout.setColumnStretch(0, 1)
            self.layout.setColumnStretch(1, 1)
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
