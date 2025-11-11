import sys
import os
import re
from PyPDF2 import PdfReader
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGridLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QListWidget, QAbstractItemView, QGraphicsProxyWidget
)
from PyQt6.QtGui import (
    QPixmap, QPen, QBrush, QColor, QPainter, QCursor, QFont, QFontDatabase, QIcon, QFontMetrics,
    QDrag, QMouseEvent, QGuiApplication
)
from PyQt6.QtCore import (
    Qt, QRectF, QPointF, QTimer, QUrl, QMimeData, QPoint,
    QVariantAnimation, QEasingCurve
)

from ButtonsAndIcons import AnimatedButton
from CoreFunctions import resource_path
from ContainerWidgets import DraggableBoxContainer


class PdfDropArea(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.DropAction.CopyAction)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._base_style = ("""QListWidget {
            border: 2px dashed #555;
            border-radius: 10px;
            background-color: #fafafa;
            color: #000;
            font-size: 14px;
        }
        QListWidget::item:hover {
            background-color: #DCD1FD;
            color: #000;
        }
        QListWidget::item:selected {
            background-color: #3F17BD;
            color: #fff;
            outline: none;
            border: none;
        }
        QListWidget::item:focus {
            outline: none;
            border: none;
        }
        QListWidget::focus {
            outline: none;
            border: none;
        }""")

        self._highlight_style = ("""QListWidget {
            border: 2px solid #6D05FF;
            border-radius: 10px;
            background-color: #F6F2FF;
            color: #000;
            font-size: 14px;
        }
        QListWidget::item:hover {
            background-color: #DCD1FD;
            color: #000;
        }
        QListWidget::item:selected {
            background-color: #3F17BD;
            color: #fff;
            outline: none;
            border: none;
        }
        QListWidget::item:focus {
            outline: none;
            border: none;
        }
        QListWidget::focus {
            outline: none;
            border: none;
        }""")

        self.setStyleSheet(self._base_style)
        self.setSpacing(4)

        # Centered label for placeholder text
        self.placeholder = QLabel("Drop Files Here...", self)
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color: #bbb; font-size: 14px;")
        self.placeholder.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Dictionary to store display name -> full path mapping
        self.pdf_paths = {}

        # Load and apply Objektiv font if available
        font_path = resource_path(os.path.join("fonts", "objektiv", "ObjektivMk2_Trial_Rg.ttf"))
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                objektiv_font = QFont(families[0], 11)
                self.setFont(objektiv_font)
                self.placeholder.setFont(objektiv_font)

        # Initialize drag tracking variable
        self.drag_start_pos = QPoint()


    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep placeholder centered
        self.placeholder.setGeometry(0, 0, self.width(), self.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()
            item = self.itemAt(event.pos())
            modifiers = QApplication.keyboardModifiers()

            if not item:
                self.clearSelection()
                return super().mousePressEvent(event)

            # --- Handle manual toggling (disable Qt’s default range selection) ---
            if modifiers & (Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.ControlModifier):
                item.setSelected(not item.isSelected())
                return

            # --- Handle dragging from existing selection ---
            if item.isSelected():
                # Don't change anything, we're probably starting a drag
                return

            # --- Normal click: clear others and select this one ---
            self.clearSelection()
            item.setSelected(True)
            return
        else:
            super().mousePressEvent(event)

    def leaveEvent(self, event):
        # Deselect when mouse leaves the drop area
        self.clearSelection()
        super().leaveEvent(event)

    def keyPressEvent(self, event):
        # Delete selected item on Backspace
        if event.key() == Qt.Key.Key_Backspace:
            for item in self.selectedItems():
                row = self.row(item)
                name = item.text()
                if name in self.pdf_paths:
                    del self.pdf_paths[name]
                self.takeItem(row)
            self.placeholder.setVisible(self.count() == 0)
            if hasattr(self, "on_files_changed"):
                self.on_files_changed()
        else:
            super().keyPressEvent(event)

    def _is_pdf_drop(self, event):
        if not event.mimeData().hasUrls():
            return False
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path:
                return True
        return False

    def dragEnterEvent(self, event):
        if self._is_pdf_drop(event):
            self.setStyleSheet(self._highlight_style)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if self._is_pdf_drop(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(self._base_style)
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if (event.pos() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return

        items = self.selectedItems()
        if not items:
            return

        urls = []
        for item in items:
            path = self.pdf_paths.get(item.text())
            if path and os.path.exists(path):
                urls.append(QUrl.fromLocalFile(path))

        if not urls:
            return

        mime_data = QMimeData()
        mime_data.setUrls(urls)

        drag = QDrag(self)
        drag.setMimeData(mime_data)

        count = len(urls)
        pixmap = QPixmap(120, 40)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#3F17BD"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 120, 40, 10, 10)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter,
                         f"{count} file{'s' if count != 1 else ''}")
        painter.end()

        drag.setPixmap(pixmap)
        drag.setHotSpot(pixmap.rect().center())

        drag.exec(Qt.DropAction.CopyAction)


    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.drag_start_pos = QPoint()

    def dropEvent(self, event):
        added = False
        for url in event.mimeData().urls():
            try:
                path = url.toLocalFile()
                if not path:
                    print("[DEBUG] Skipping empty path")
                    continue

                filename = os.path.basename(path)
                lowercase = filename.lower()
                print(f"[DEBUG] Dropped file: {filename}")

                # Skip duplicates by full path
                if path in self.pdf_paths.values():
                    print(f"[DEBUG] Duplicate file ignored: {path}")
                    continue


                # --- PDF Handling ---
                if lowercase.endswith(".pdf"):
                    match = re.search(r"po00(\d+)_li(\d+)_?", lowercase)
                    if match:
                        order_number = match.group(1)
                        file_number = match.group(2).lstrip("0") or "0"
                        display_name = f"Image File {order_number} - File Number {file_number}"
                        print(f"[DEBUG] Detected image-style PDF -> {display_name}")
                    else:
                        display_name = f"Order Form: {filename}"
                        print(f"[DEBUG] Detected order form PDF -> {display_name}")

                    self.addItem(display_name)
                    self.pdf_paths[display_name] = path
                    added = True

                # --- Image Handling (JPG/PNG) ---
                elif lowercase.endswith((".jpg", ".png")):
                    match = re.search(r"po00(\d+)_li(\d+)_?", lowercase)
                    if match:
                        order_number = match.group(1)
                        file_number = match.group(2).lstrip("0") or "0"
                        display_name = f"Image File {order_number} - File Number {file_number}"

                        self.addItem(display_name)
                        self.pdf_paths[display_name] = path
                        added = True
                    else:
                        print(f"[DEBUG] Ignored image without pattern: {filename}")

                # --- Excel/CSV Handling ---
                elif lowercase.endswith((".xlsx", ".xls", ".csv")):
                    display_name = f"Warehouse Inventory Transfer: {filename}"
                    print(f"[DEBUG] Detected Excel/CSV file -> {display_name}")

                    self.addItem(display_name)
                    self.pdf_paths[display_name] = path
                    added = True

            except Exception as e:
                import traceback
                print(f"[ERROR] dropEvent crashed for {url}: {e}\n{traceback.format_exc()}")

        # Reset visuals
        self.setStyleSheet(self._base_style)
        self.placeholder.setVisible(self.count() == 0)

        if added:
            event.acceptProposedAction()
        else:
            event.ignore()

    def get_file_path(self, name):
        return self.pdf_paths.get(name, None)

class FileDropbox(DraggableBoxContainer.ResizableRectItem):
    def __init__(self, rect, parent_view, title="File Dropbox", statistics_view=None, login_container=None):
        super().__init__(rect, parent_view, title)

        self.minimized = False
        self.statistics_view = statistics_view  # Reference to DropBoxStatistics instance
        self.login_container = login_container

        self.proxy = QGraphicsProxyWidget(self)
        self.drop_widget = PdfDropArea()

        self.drop_widget.on_files_changed = self.handle_drop_summary

        # Hook drop event to call handle_drop_summary
        original_drop_event = self.drop_widget.dropEvent

        def wrapped_drop_event(event):
            original_drop_event(event)
            self.handle_drop_summary()

        self.drop_widget.dropEvent = wrapped_drop_event

        self.proxy.setWidget(self.drop_widget)

        self.update_drop_geometry(rect.width(), rect.height())

    def update_drop_geometry(self, width, height):
        border_margin = 6
        title_offset = self.TITLE_BAR_HEIGHT + border_margin
        drop_rect = QRectF(
            border_margin,
            title_offset,
            max(0, width - border_margin * 2),
            max(0, height - title_offset - border_margin)
        )
        self.proxy.setGeometry(drop_rect)

    def setRect(self, rect):
        MIN_WIDTH = 200
        MIN_HEIGHT = 150

        width = max(rect.width(), MIN_WIDTH)
        height = self.TITLE_BAR_HEIGHT if self.minimized else max(rect.height(), MIN_HEIGHT)

        clamped_rect = QRectF(rect.x(), rect.y(), width, height)
        super().setRect(clamped_rect)

        if hasattr(self, "proxy"):
            self.update_drop_geometry(width, height)

    def toggle_minimize(self):
        self.minimized = not self.minimized
        rect = self.rect()

        if self.minimized:
            self.drop_widget.setVisible(False)
            self.setRect(QRectF(rect.x(), rect.y(), rect.width(), self.TITLE_BAR_HEIGHT))
        else:
            self.drop_widget.setVisible(True)
            self.setRect(QRectF(rect.x(), rect.y(), rect.width(), 150))

        if self.statistics_view:
            self.statistics_view.update_geometry(self.rect().width(), self.rect().height())

    def itemChange(self, change, value):
        if change in (
            QGraphicsRectItem.GraphicsItemChange.ItemPositionChange,
            QGraphicsRectItem.GraphicsItemChange.ItemTransformChange,
        ):
            rect = self.rect()
            if hasattr(self, "proxy"):
                self.update_drop_geometry(rect.width(), rect.height())
        return super().itemChange(change, value)

    def paint(self, painter, option, widget=None):
        rect = self.rect()
        painter.setPen(self.pen())

        if self.minimized:
            painter.setBrush(QBrush(QColor(0, 0, 0)))
            painter.drawRect(QRectF(rect.left(), rect.top(), rect.width(), self.TITLE_BAR_HEIGHT))

            painter.setPen(QColor(255, 255, 255))
            font = QFont(self.font_family)
            font.setPointSize(10)
            painter.setFont(font)
            text_rect = QRectF(rect.left(), rect.top(), rect.width(), self.TITLE_BAR_HEIGHT)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.title)
        else:
            super().paint(painter, option, widget)

    def handle_drop_summary(self):
        if not self.statistics_view:
            print("[DEBUG] No statistics view linked, skipping summary.")
            return

        # Create a 2D counting list: [[order_count], [image_count], [misc_count]]
        file_counts = [[0], [0], [0]]

        for i in range(self.drop_widget.count()):
            item_name = self.drop_widget.item(i).text()
            if item_name.startswith("Order"):
                file_counts[0][0] += 1
            elif item_name.startswith("Image"):
                file_counts[1][0] += 1
            else:
                file_counts[2][0] += 1

        self.statistics_view.display_file_categories(file_counts)

    def processContainer(self):
        import re, os, PyPDF2, requests
        from PyQt6.QtCore import QVariantAnimation, QEasingCurve, QTimer, Qt
        from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGraphicsOpacityEffect
        from PyQt6.QtGui import QPixmap
        from pdfAnalysis import extract_pdf_info
        from clientCalls import send_print_data, fetch_next_container_id
        from CoreFunctions import resource_path

        parent_window = QApplication.activeWindow() or self.drop_widget.window()
        if not parent_window:
            return

        # ---------------- shared helpers ----------------
        def update_opacity(value):
            if not parent_window or not parent_window.isVisible():
                return
            for widget in parent_window.findChildren(QWidget):
                if widget is not self.drop_widget and not widget.isHidden():
                    effect = widget.graphicsEffect() or QGraphicsOpacityEffect(widget)
                    effect.setOpacity(value)
                    widget.setGraphicsEffect(effect)

            if hasattr(self, "_processing_icon") and self._processing_icon:
                icon_effect = self._processing_icon.graphicsEffect() or QGraphicsOpacityEffect(self._processing_icon)
                icon_effect.setOpacity((1.0 - value) * 2 if value >= 0.5 else 1.0)
                self._processing_icon.setGraphicsEffect(icon_effect)

        def cleanup_effects():
            if hasattr(self, "_processing_icon") and self._processing_icon:
                self._processing_icon.deleteLater()
                self._processing_icon = None
            if parent_window and parent_window.isVisible():
                for w in parent_window.findChildren(QWidget):
                    if w is not self.drop_widget and w.graphicsEffect():
                        w.setGraphicsEffect(None)

        # ---------------- fade in ----------------
        def fade_in_then_process():
            icon_path = resource_path("icons/processDropbox(Hovered).png")
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                label = QLabel(parent_window)
                label.setPixmap(pixmap)
                label.setStyleSheet("background: transparent;")
                label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                win_size, icon_size = parent_window.size(), pixmap.size()
                center_x = (win_size.width() - icon_size.width()) // 2
                center_y = (win_size.height() - icon_size.height()) // 2
                label.setGeometry(center_x, center_y, icon_size.width(), icon_size.height())

                eff = QGraphicsOpacityEffect(label)
                eff.setOpacity(0.0)
                label.setGraphicsEffect(eff)
                label.show()
                label.raise_()
                self._processing_icon = label

            fade_in = QVariantAnimation(parent_window)
            fade_in.setDuration(600)
            fade_in.setStartValue(1.0)
            fade_in.setEndValue(0.5)
            fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
            fade_in.valueChanged.connect(update_opacity)
            fade_in.finished.connect(lambda: QTimer.singleShot(100, do_processing))
            fade_in.start()
            self._fade_in_ref = fade_in

        # ---------------- main file processing ----------------
        def do_processing():
            try:
                employee_name = ""
                if getattr(self, "login_container", None) and getattr(self.login_container, "text_list", None):
                    if self.login_container.text_list:
                        employee_name = self.login_container.text_list[-1]

                pdf_files = [
                    path for name, path in self.drop_widget.pdf_paths.items()
                    if path.lower().endswith('.pdf') and name.lower().startswith('order form')
                ]
                image_files = [
                    path for name, path in self.drop_widget.pdf_paths.items()
                    if path.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')) and name.lower().startswith('image file')
                ]

                today_str = datetime.now().strftime('%d-%m-%y')

                if pdf_files:
                    orders_all, leads_all, isos_all, quantities_all, sizes_all, prodtypes_all = [], [], [], [], [], []
                    for pdf in pdf_files:
                        o, l, i, q, s, p = extract_pdf_info(pdf)
                        orders_all.extend(o)
                        leads_all.extend(l)
                        isos_all.extend(i)
                        quantities_all.extend(q)
                        sizes_all.extend(s)
                        prodtypes_all.extend(p)

                    for idx, order in enumerate(orders_all):
                        isos = isos_all[idx] if idx < len(isos_all) else []
                        for iso_index, iso in enumerate(isos):
                            prodType = prodtypes_all[idx][iso_index] if idx < len(prodtypes_all) and iso_index < len(prodtypes_all[idx]) else 'Unknown'
                            size = sizes_all[idx][iso_index] if idx < len(sizes_all) and iso_index < len(sizes_all[idx]) else 'Unknown'

                            if size and isinstance(size, str):
                                size = f"{today_str}/{size}"

                            quantity = quantities_all[idx][iso_index] if idx < len(quantities_all) and iso_index < len(quantities_all[idx]) else 1

                            for q_num in range(1, quantity + 1):
                                iso_name = iso if q_num == 1 else f"{iso}_{q_num}"

                                print("Sending to server with attributes:")
                                print({
                                    'containerID': "",
                                    'orderNumber': order,
                                    'leadBarcode': leads_all[idx] if idx < len(leads_all) else None,
                                    'isoBarcode': iso_name,
                                    'workstation': 'Printing Station: Order File Processed',
                                    'employeeName': employee_name,
                                    'prodType': prodType,
                                    'size': size
                                })

                                response = send_print_data(
                                    containerID="",
                                    orderNumber=order,
                                    leadBarcode=leads_all[idx] if idx < len(leads_all) else None,
                                    isoBarcode=iso_name,
                                    workstation='Printing Station: Order File Processed',
                                    employeeName=employee_name,
                                    prodType=prodType,
                                    size=size
                                )

                                print("Server response:", response)

                if image_files:
                    container_id = fetch_next_container_id()
                    for image_path in image_files:
                        image_name = os.path.basename(image_path)
                        m = re.search(r"po00(\d+)_li(\d+)_?", image_name.lower())
                        order_number = m.group(1) if m else None
                        item_num = f"li{m.group(2).lstrip('0')}" if m else None

                        print("Sending to server with attributes:")
                        print({
                            'containerID': container_id,
                            'orderNumber': order_number,
                            'leadBarcode': None,
                            'isoBarcode': image_name,
                            'workstation': "Printing Station: Image File Processed",
                            'employeeName': employee_name,
                            'prodType': None,
                            'size': None,
                            'itemNum': item_num
                        })

                        response = send_print_data(
                            containerID=container_id,
                            orderNumber=order_number,
                            leadBarcode=None,
                            isoBarcode=image_name,
                            workstation="Printing Station: Image File Processed",
                            employeeName=employee_name,
                            prodType=None,
                            size=None,
                            itemNum=item_num
                        )

                        print("Server response:", response)

                self.drop_widget.pdf_paths.clear()
                if hasattr(self.drop_widget, 'clear'):
                    self.drop_widget.clear()
                if hasattr(self, 'statistics_view') and self.statistics_view:
                    self.statistics_view.display_file_categories([[0], [0], [0]])

                QTimer.singleShot(150, fade_out)

            except Exception:
                import traceback
                print(traceback.format_exc())
                fade_out()

        # ---------------- fade out ----------------
        def fade_out():
            fade_out_anim = QVariantAnimation(parent_window)
            fade_out_anim.setDuration(600)
            fade_out_anim.setStartValue(0.5)
            fade_out_anim.setEndValue(1.0)
            fade_out_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
            fade_out_anim.valueChanged.connect(update_opacity)
            fade_out_anim.finished.connect(cleanup_effects)
            fade_out_anim.start()
            self._fade_out_ref = fade_out_anim

        fade_in_then_process()










