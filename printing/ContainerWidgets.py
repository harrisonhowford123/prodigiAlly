import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGridLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QListWidget, QAbstractItemView, QGraphicsProxyWidget
)
from PyQt6.QtGui import (
    QPixmap, QPen, QBrush, QColor, QPainter, QCursor, QFont, QFontDatabase, QIcon, QFontMetrics, QBrush
)
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from ButtonsAndIcons import AnimatedButton
from CoreFunctions import resource_path

class DraggableBoxContainer(QGraphicsView):
    class ResizableRectItem(QGraphicsRectItem):
        HANDLE_SIZE = 8
        TITLE_BAR_HEIGHT = 20
        TITLE_BAR_BUTTON_WIDTH = 16
        TITLE_BAR_BUTTON_SPACING = 4
        NUM_TITLE_BAR_BUTTONS = 2  # Minimize + Close
        MIN_CONTENT_WIDTH = 180
        MIN_WIDTH = MIN_CONTENT_WIDTH + (NUM_TITLE_BAR_BUTTONS * (TITLE_BAR_BUTTON_WIDTH + TITLE_BAR_BUTTON_SPACING))

        def __init__(self, rect, parent_view, title="Generic Container"):
            super().__init__(rect)
            self.parent_view = parent_view
            self.title = title
            self.is_minimized = False
            self._stored_rect_height = rect.height()

            # Pens and visuals
            self.default_pen = QPen(QColor(0, 0, 0))
            self.highlight_pen = QPen(QColor("#3F17BD"))
            for pen in [self.default_pen, self.highlight_pen]:
                pen.setWidth(2)
                pen.setCosmetic(True)

            self.setPen(self.default_pen)
            self.setBrush(QBrush(QColor("#FCFCFC")))
            self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
            self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, False)
            self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
            self.setAcceptHoverEvents(True)

            self.resizing = False
            self.dragging = False
            self.resize_dir = None
            self._allow_move = False

            # Font
            font_path = resource_path(os.path.join("fonts", "objektiv", "ObjektivMk2_Trial_Rg.ttf"))
            if os.path.exists(font_path):
                self.font_id = QFontDatabase.addApplicationFont(font_path)
                families = QFontDatabase.applicationFontFamilies(self.font_id)
                self.font_family = families[0] if families else "Objektiv Mk2 Trial"
            else:
                self.font_family = "Objektiv Mk2 Trial"

            # Minimize button
            self.min_button = QPushButton()
            self.min_button.setFixedSize(self.TITLE_BAR_BUTTON_WIDTH, self.TITLE_BAR_BUTTON_WIDTH)
            self.min_button.setIcon(QIcon(resource_path("icons/minimiseWindow.png")))
            self.min_button.setStyleSheet("border: none; background: transparent;")
            self.min_button.clicked.connect(self.toggle_minimize)

            self.button_proxy_min = QGraphicsProxyWidget(self)
            self.button_proxy_min.setWidget(self.min_button)

            # Close button
            self.close_button = QPushButton()
            self.close_button.setFixedSize(self.TITLE_BAR_BUTTON_WIDTH, self.TITLE_BAR_BUTTON_WIDTH)
            self.close_button.setIcon(QIcon(resource_path("icons/closeWindow.png")))
            self.close_button.setStyleSheet("border: none; background: transparent;")
            self.close_button.clicked.connect(self.delete_self)

            self.button_proxy_close = QGraphicsProxyWidget(self)
            self.button_proxy_close.setWidget(self.close_button)

            self.update_button_position()

        def update_button_position(self):
            rect = self.rect()
            btn_size = self.TITLE_BAR_BUTTON_WIDTH
            spacing = 6
            y = rect.top() + (self.TITLE_BAR_HEIGHT - btn_size) / 2

            x_close = rect.right() - btn_size - spacing
            x_min = x_close - btn_size - spacing

            self.button_proxy_close.setPos(x_close, y)
            self.button_proxy_min.setPos(x_min, y)

        def delete_self(self):
            # Disable interactions immediately
            self.setEnabled(False)
            self.setVisible(False)
            self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

            if hasattr(self, "proxy") and self.proxy is not None:
                try:
                    self.proxy.setWidget(None)
                except Exception:
                    pass

            if hasattr(self, "button_proxy_min") and self.button_proxy_min is not None:
                try:
                    self.button_proxy_min.setWidget(None)
                except Exception:
                    pass
            if hasattr(self, "button_proxy_close") and self.button_proxy_close is not None:
                try:
                    self.button_proxy_close.setWidget(None)
                except Exception:
                    pass

            # ContainerWidgets.py  (inside ResizableRectItem.delete_self)
            scene = self.scene()
            if scene:
                scene.removeItem(self)
                scene.update()
                scene.invalidate(scene.sceneRect(), QGraphicsScene.SceneLayer.AllLayers)
                scene.itemsBoundingRect()

            # Find the window and update its bookkeeping
            wnd = None
            try:
                p = self.parent_view.parent()
                wnd = p.parent() if p is not None else None
            except Exception:
                wnd = None

            if wnd is not None:
                # Remove from tracking lists/maps
                try:
                    if hasattr(wnd, "rect_items") and self in wnd.rect_items:
                        wnd.rect_items.remove(self)
                    if hasattr(wnd, "relative_states"):
                        wnd.relative_states.pop(self, None)
                except Exception:
                    pass

                # Rebuild collision handlers for remaining items (no args)
                try:
                    if hasattr(wnd, "enable_box_collisions"):
                        wnd.enable_box_collisions()
                    if hasattr(wnd, "enable_resize_collisions"):
                        wnd.enable_resize_collisions()
                except TypeError:
                    # Back-compat if older signatures exist somewhere
                    if hasattr(wnd, "enable_box_collisions"):
                        wnd.enable_box_collisions()
                    if hasattr(wnd, "enable_resize_collisions"):
                        wnd.enable_resize_collisions()

            self.resize_dir = None
            self.dragging = False
            self.resizing = False

            del self

        def toggle_minimize(self):
            if not self.is_minimized:
                self._stored_rect_height = self.rect().height()
                new_rect = QRectF(self.rect().x(), self.rect().y(), self.rect().width(), self.TITLE_BAR_HEIGHT)
                self.setRect(new_rect)
                self.is_minimized = True
                self.min_button.setIcon(QIcon(resource_path("icons/maximiseWindow.png")))
            else:
                new_rect = QRectF(self.rect().x(), self.rect().y(), self.rect().width(), self._stored_rect_height)
                self.setRect(new_rect)
                self.is_minimized = False
                self.min_button.setIcon(QIcon(resource_path("icons/minimiseWindow.png")))

            self.update_drop_geometry_if_any()
            self.update_button_position()
            self.update()

        def update_drop_geometry_if_any(self):
            if hasattr(self, "proxy"):
                if self.is_minimized:
                    self.proxy.setVisible(False)
                else:
                    self.proxy.setVisible(True)
                    rect = self.rect()
                    border_margin = 6
                    title_offset = self.TITLE_BAR_HEIGHT + border_margin
                    drop_rect = QRectF(border_margin, title_offset, rect.width() - border_margin * 2, rect.height() - title_offset - border_margin)
                    self.proxy.setGeometry(drop_rect)

        def _half_pen(self):
            return self.pen().widthF() / 2.0

        def hoverMoveEvent(self, event):
            rect = self.rect()
            pos = event.pos()
            margin = self.HANDLE_SIZE
            cursor = Qt.CursorShape.ArrowCursor

            if self.is_minimized:
                self.resize_dir = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
                super().hoverMoveEvent(event)
                return

            if abs(pos.x() - rect.right()) < margin and abs(pos.y() - rect.bottom()) < margin:
                cursor = Qt.CursorShape.SizeFDiagCursor
                self.resize_dir = 'bottom_right'
            elif abs(pos.x() - rect.right()) < margin and rect.top() < pos.y() < rect.bottom():
                cursor = Qt.CursorShape.SizeHorCursor
                self.resize_dir = 'right'
            elif abs(pos.y() - rect.bottom()) < margin and rect.left() < pos.x() < rect.right():
                cursor = Qt.CursorShape.SizeVerCursor
                self.resize_dir = 'bottom'
            else:
                self.resize_dir = None
                if pos.y() <= self.TITLE_BAR_HEIGHT:
                    cursor = Qt.CursorShape.SizeAllCursor

            self.setCursor(cursor)
            super().hoverMoveEvent(event)

        def mousePressEvent(self, event):
            if event.button() == Qt.MouseButton.LeftButton:
                pos = event.pos()
                if self.is_minimized:
                    self.resize_dir = None
                if pos.y() <= self.TITLE_BAR_HEIGHT and not self.resize_dir:
                    self._allow_move = True
                    self.dragging = True
                    self.drag_offset = pos
                elif self.resize_dir and not self.is_minimized:
                    self.resizing = True
                    self.start_pos = event.pos()
                else:
                    self._allow_move = False
            super().mousePressEvent(event)

        def mouseMoveEvent(self, event):
            if self.is_minimized:
                return super().mouseMoveEvent(event)

            if self.resizing and self.resize_dir:
                rect = self.rect()
                diff = event.pos() - self.start_pos

                if self.resize_dir == 'right':
                    rect.setWidth(max(self.MIN_WIDTH, rect.width() + diff.x()))
                elif self.resize_dir == 'bottom':
                    rect.setHeight(max(20, rect.height() + diff.y()))
                elif self.resize_dir == 'bottom_right':
                    rect.setWidth(max(self.MIN_WIDTH, rect.width() + diff.x()))
                    rect.setHeight(max(20, rect.height() + diff.y()))

                view_rect = self.parent_view.visible_scene_rect()
                half = self._half_pen()
                max_w = max(self.MIN_WIDTH, view_rect.right() - half - self.pos().x())
                max_h = max(20, view_rect.bottom() - half - self.pos().y())
                rect.setWidth(min(rect.width(), max_w))
                rect.setHeight(min(rect.height(), max_h))

                self.setRect(rect)
                self.start_pos = event.pos()
                self.update_button_position()
            elif self.dragging and self._allow_move:
                new_pos = self.pos() + (event.pos() - self.drag_offset)
                self.setPos(new_pos)
            else:
                super().mouseMoveEvent(event)

        def mouseReleaseEvent(self, event):
            self.resizing = False
            self.dragging = False
            self._allow_move = False
            self.resize_dir = None
            self.update_button_position()
            view_rect = self.parent_view.visible_scene_rect()
            item_rect = self.rect()
            pos = self.pos()

            # --- Adjust for top bar offset ---
            window = self.parent_view.parent()
            bar_height = window.top_bar.height() if hasattr(window, "top_bar") else 0

            # Compute relative coordinates including the bar offset
            rel_x = (pos.x() - view_rect.left()) / view_rect.width()
            rel_y = ((pos.y() - bar_height) - view_rect.top()) / view_rect.height()
            rel_w = item_rect.width() / view_rect.width()
            rel_h = item_rect.height() / view_rect.height()

            print(f"[{self.title}] Relative position/size (matching widgetData):")
            print(f"  X: {rel_x:.3f}, Y: {rel_y:.3f}, W: {rel_w:.3f}, H: {rel_h:.3f}")


            super().mouseReleaseEvent(event)

        def itemChange(self, change, value):
            if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionChange and self.scene():
                new_pos = QPointF(value)
                rect = self.rect()
                view_rect = self.parent_view.visible_scene_rect()
                half = self._half_pen()

                min_x = view_rect.left() + half
                min_y = view_rect.top() + half - self.parent_view.top_inset
                max_x = view_rect.right() - half - rect.width()
                max_y = view_rect.bottom() - half - rect.height()

                clamped_x = min(max(new_pos.x(), min_x), max_x)
                clamped_y = min(max(new_pos.y(), min_y), max_y)

                return QPointF(clamped_x, clamped_y)
            elif change == QGraphicsRectItem.GraphicsItemChange.ItemPositionHasChanged or change == QGraphicsRectItem.GraphicsItemChange.ItemTransformChange:
                self.update_button_position()
            return super().itemChange(change, value)

        def paint(self, painter, option, widget=None):
            super().paint(painter, option, widget)
            rect = self.rect()
            painter.setBrush(QBrush(QColor(0, 0, 0)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRectF(rect.left(), rect.top(), rect.width(), self.TITLE_BAR_HEIGHT))

            painter.setPen(QColor(255, 255, 255))
            font = QFont(self.font_family)
            font.setPointSize(10)
            painter.setFont(font)
            text_rect = QRectF(rect.left(), rect.top(), rect.width(), self.TITLE_BAR_HEIGHT)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter, self.title)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("border: none; background-color: #FCFCFC;")
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setBackgroundBrush(QBrush(Qt.GlobalColor.transparent))
        self.top_inset = 0
        self.top_inset_adjust = 0
        self._relative_x = 0.0
        self._relative_y = 0.0
        self._relative_w = 0.0
        self._relative_h = 0.0

    def set_top_inset(self, h: int):
        self.top_inset = max(0, int(h))
        self.top_inset_adjust = self.top_inset

    def visible_scene_rect(self) -> QRectF:
        vr = self.viewport().rect()
        scene_rect = self.mapToScene(vr).boundingRect()
        scene_rect.setTop(scene_rect.top() + self.top_inset)
        scene_rect.adjust(2, 2, -2, -2)
        return scene_rect

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.viewport().rect()
        self.setSceneRect(self.mapToScene(rect).boundingRect())
        for item in self.scene.items():
            if isinstance(item, self.ResizableRectItem):
                item.update_button_position()

