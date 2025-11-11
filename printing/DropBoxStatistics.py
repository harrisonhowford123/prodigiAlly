import sys
import os
from PyQt6.QtGui import QFont, QPen, QPainter
from PyQt6.QtCore import Qt, QRectF, QPointF
from ContainerWidgets import DraggableBoxContainer


class DropBoxStatistics(DraggableBoxContainer.ResizableRectItem):
    def __init__(self, rect, parent_view, title="Dropbox Statistics", stats_data=None):
        super().__init__(rect, parent_view, title)
        self.stats_data = stats_data or {}

        # Counters
        self.order_count = 0
        self.image_count = 0
        self.misc_count = 0

        # Headers for columns
        self.headers = ["Order Files", "Image Files", "Misc Files"]

    def update_geometry(self, width, height):
        # Trigger a repaint when resized
        self.prepareGeometryChange()
        self.update()

    def display_file_categories(self, file_list_2d):
        """Update displayed values."""
        if not file_list_2d or len(file_list_2d) < 3:
            print("Invalid file list structure. Expected 3 sublists.")
            return

        self.order_count = file_list_2d[0][0]
        self.image_count = file_list_2d[1][0]
        self.misc_count = file_list_2d[2][0]
        self.update()

    def paint(self, painter: QPainter, option, widget=None):
        # Draw parent container (title bar, borders, etc.)
        super().paint(painter, option, widget)

        # Pen for grid lines
        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(1)
        painter.setPen(pen)

        # Geometry
        border_margin = 5
        title_offset = self.TITLE_BAR_HEIGHT + border_margin
        rect = QRectF(border_margin, title_offset,
                      self.rect().width() - border_margin * 2,
                      self.rect().height() - title_offset - border_margin)

        # Grid math
        cell_width = rect.width() / 3
        cell_height = rect.height() / 2

        # Draw grid
        for i in range(1, 3):
            x = rect.left() + cell_width * i
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))

        y = rect.top() + cell_height
        painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))

        # Font sizing with vertical cap
        max_header_size = int(cell_width * 0.15)
        max_value_size = int(cell_width * 0.25)

        header_font = QFont("Arial", max(10, min(max_header_size, int(cell_height * 0.25))))
        value_font = QFont("Arial", max(10, min(max_value_size, int(cell_height * 0.35))))

        painter.setPen(Qt.GlobalColor.black)

        # Draw headers and numbers
        counts = [self.order_count, self.image_count, self.misc_count]
        padding = cell_width * 0.05  # horizontal padding inside each cell

        # --- Determine smallest header font that fits all labels WITH padding ---
        test_font = QFont(header_font)
        min_point_size = test_font.pointSize()

        for header in self.headers:
            font = QFont(test_font)
            painter.setFont(font)
            fm = painter.fontMetrics()

            available_width = cell_width - padding * 2  # usable text area inside padding
            # Shrink font until the text fits within the available space
            while fm.horizontalAdvance(header) > available_width and font.pointSize() > 8:
                font.setPointSize(font.pointSize() - 1)
                painter.setFont(font)
                fm = painter.fontMetrics()

            min_point_size = min(min_point_size, font.pointSize())

        # Apply that minimum size to all headers
        header_font.setPointSize(min_point_size)
        painter.setFont(header_font)

        # --- Draw all headers and values ---
        for i, header in enumerate(self.headers):
            x = rect.left() + i * cell_width
            text_rect_top = QRectF(x + padding, rect.top(), cell_width - padding * 2, cell_height)
            text_rect_bottom = QRectF(x + padding, rect.top() + cell_height, cell_width - padding * 2, cell_height)

            # Header text (top row)
            painter.setFont(header_font)
            painter.drawText(text_rect_top, Qt.AlignmentFlag.AlignCenter, header)

            # Value text (bottom row)
            painter.setFont(value_font)
            painter.drawText(text_rect_bottom, Qt.AlignmentFlag.AlignCenter, str(counts[i]))






