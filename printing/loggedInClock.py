from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QGraphicsProxyWidget
from PyQt6.QtGui import QFont, QFontDatabase, QFontMetrics, QIcon
from PyQt6.QtCore import Qt, QRectF, QTime, QSize
from ContainerWidgets import DraggableBoxContainer
from CoreFunctions import resource_path
from clientCalls import log_employee_time
from datetime import datetime, timedelta
import os

class DigitalClockContainer(DraggableBoxContainer.ResizableRectItem):
    MIN_VISIBLE_HEIGHT = 120

    def __init__(self, rect, parent_view, title="Digital Clock", employee_name=None):
        super().__init__(rect, parent_view, title)
        self.employee_name = employee_name
        self.current_employee = None  # Track current employee dynamically from LoginContainer

        font_path = resource_path(os.path.join("fonts", "objektiv", "ObjektivMk2_Trial_Rg.ttf"))
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            families = QFontDatabase.applicationFontFamilies(font_id)
            self.font_family = families[0] if families else "Objektiv Mk2 Trial"

        self.clock_widget = QWidget()
        self.clock_widget.setStyleSheet("background-color: transparent;")
        self.main_layout = QVBoxLayout(self.clock_widget)
        self.main_layout.setContentsMargins(8, 0, 8, 0)
        self.main_layout.setSpacing(0)

        self.time_row = QHBoxLayout()
        self.time_row.setContentsMargins(0, 0, 0, 0)
        self.time_row.setSpacing(40)
        self.time_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.start_label = QLabel("09:00")
        self.start_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.start_label.setStyleSheet("background-color: transparent; color: black;")

        self.end_label = QLabel("17:00")
        self.end_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.end_label.setStyleSheet("background-color: transparent; color: black;")

        self.time_row.addStretch(1)
        self.time_row.addWidget(self.start_label, 1)
        self.time_row.addStretch(1)
        self.time_row.addWidget(self.end_label, 1)
        self.time_row.addStretch(1)

        self.button_row = QHBoxLayout()
        self.button_row.setContentsMargins(0, 0, 0, 0)
        self.button_row.setSpacing(40)
        self.button_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.increase_start = QPushButton()
        self.decrease_start = QPushButton()
        self._setup_hover_button(self.increase_start, "increaseTime")
        self._setup_hover_button(self.decrease_start, "decreaseTime")
        self.increase_start.clicked.connect(lambda: self._on_time_changed(self.start_label, +15))
        self.decrease_start.clicked.connect(lambda: self._on_time_changed(self.start_label, -15))

        start_buttons_layout = QHBoxLayout()
        start_buttons_layout.setSpacing(6)
        start_buttons_layout.addWidget(self.increase_start)
        start_buttons_layout.addWidget(self.decrease_start)
        start_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        self.increase_end = QPushButton()
        self.decrease_end = QPushButton()
        self._setup_hover_button(self.increase_end, "increaseTime")
        self._setup_hover_button(self.decrease_end, "decreaseTime")
        self.increase_end.clicked.connect(lambda: self._on_time_changed(self.end_label, +15))
        self.decrease_end.clicked.connect(lambda: self._on_time_changed(self.end_label, -15))

        end_buttons_layout = QHBoxLayout()
        end_buttons_layout.setSpacing(6)
        end_buttons_layout.addWidget(self.increase_end)
        end_buttons_layout.addWidget(self.decrease_end)
        end_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        self.button_row.addStretch(1)
        self.button_row.addLayout(start_buttons_layout, 1)
        self.button_row.addStretch(1)
        self.button_row.addLayout(end_buttons_layout, 1)
        self.button_row.addStretch(1)

        self.send_row = QHBoxLayout()
        self.send_row.setContentsMargins(0, 0, 0, 0)
        self.send_row.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        self.send_button = QPushButton()
        self._setup_hover_button(self.send_button, "sendTimes(unActive)")
        self.send_row.addWidget(self.send_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.send_active = False
        self.send_button.clicked.connect(self._on_send_clicked)
        self.send_button.normal_icon_path = resource_path("icons/sendTimes(unActive).png")
        self.send_button.hover_icon_path = resource_path("icons/sendTimes(unActive).png")

        self.main_layout.addLayout(self.time_row, 25)
        self.main_layout.addLayout(self.button_row, 30)
        self.main_layout.addLayout(self.send_row, 45)

        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(self.clock_widget)
        self.update_geometry(rect.width(), rect.height())

    def _setup_hover_button(self, button, icon_base_name):
        normal_icon_path = resource_path(f"icons/{icon_base_name}.png")
        hover_icon_path = resource_path(f"icons/{icon_base_name}(Hovered).png")

        button.setIcon(QIcon(normal_icon_path))
        button.setFlat(True)
        button.setStyleSheet("background: transparent; border: none;")
        button.normal_icon_path = normal_icon_path
        button.hover_icon_path = hover_icon_path
        button.enterEvent = lambda event, b=button: b.setIcon(QIcon(b.hover_icon_path))
        button.leaveEvent = lambda event, b=button: b.setIcon(QIcon(b.normal_icon_path))

    def _on_time_changed(self, label, minutes_delta):
        current_time = QTime.fromString(label.text(), "HH:mm")
        if not current_time.isValid():
            return
        new_time = current_time.addSecs(minutes_delta * 60)
        label.setText(new_time.toString("HH:mm"))

        self._set_send_button_active(True)
        self.update_geometry(self.rect().width(), self.rect().height())

    def _set_send_button_active(self, active: bool):
        self.send_active = active
        if active:
            icon_name = "sendTimes"
            hover_icon_name = "sendTimes(Hovered)"
        else:
            icon_name = "sendTimes(unActive)"
            hover_icon_name = "sendTimes(unActive)"

        normal_icon_path = resource_path(f"icons/{icon_name}.png")
        hover_icon_path = resource_path(f"icons/{hover_icon_name}.png")

        self.send_button.setIcon(QIcon(normal_icon_path))
        self.send_button.normal_icon_path = normal_icon_path
        self.send_button.hover_icon_path = hover_icon_path

        self.send_button.enterEvent = lambda event: self.send_button.setIcon(QIcon(self.send_button.hover_icon_path))
        self.send_button.leaveEvent = lambda event: self.send_button.setIcon(QIcon(self.send_button.normal_icon_path))

    def _on_send_clicked(self):
        if not self.send_active:
            print("[DEBUG] Send button inactive, click ignored.")
            return

        start_text = self.start_label.text()
        end_text = self.end_label.text()

        employee = self.current_employee or self.employee_name
        if not employee:
            print("[DEBUG] No employee name set — cannot send times.")
            return

        today = datetime.now().date()
        start_dt = datetime.combine(today, datetime.strptime(start_text, "%H:%M").time())
        end_dt = datetime.combine(today, datetime.strptime(end_text, "%H:%M").time())

        # Handle overnight wrap
        if end_dt < start_dt:
            end_dt += timedelta(days=1)

        result = log_employee_time(employee, start_dt, end_dt)
        print(f"[DEBUG] Sent time data for {employee}: {result}")


        self._set_send_button_active(False)
        self.update_geometry(self.rect().width(), self.rect().height())

    def update_geometry(self, width, height):
        if not self.proxy or width <= 0 or height <= 0:
            return

        border_margin = 8
        title_offset = self.TITLE_BAR_HEIGHT + border_margin
        content_width = max(0, width - border_margin * 2)
        content_height = max(0, height - title_offset - border_margin)

        self.proxy.setGeometry(QRectF(border_margin, title_offset, content_width, content_height))

        aspect_ratio = content_width / max(content_height, 1)
        balanced_scale = min(1.0, aspect_ratio * 1.0) if aspect_ratio < 1.5 else 1.0

        base_font_size = int(min(content_height, content_width) * 0.17 * balanced_scale)
        font_size = max(8, min(base_font_size, int(content_width * 0.1)))

        font = QFont(self.font_family, font_size)
        metrics = QFontMetrics(font)

        total_text_width = metrics.horizontalAdvance(self.start_label.text()) + metrics.horizontalAdvance(self.end_label.text()) + self.time_row.spacing() + 40
        while total_text_width > content_width and font_size > 6:
            font_size -= 1
            font.setPointSize(font_size)
            metrics = QFontMetrics(font)
            total_text_width = metrics.horizontalAdvance(self.start_label.text()) + metrics.horizontalAdvance(self.end_label.text()) + self.time_row.spacing() + 40

        self.start_label.setFont(font)
        self.end_label.setFont(font)

        btn_size = int(min(content_height * 0.28, content_width * 0.18))
        btn_size = max(20, btn_size)

        for btn in [self.increase_start, self.decrease_start, self.increase_end, self.decrease_end, self.send_button]:
            btn.setFixedSize(btn_size, btn_size)
            btn.setIconSize(QSize(btn_size - 2, btn_size - 2))

        self.main_layout.activate()

    def setRect(self, rect):
        min_w = getattr(self, 'MIN_WIDTH', 200)
        width = max(rect.width(), min_w)

        if rect.height() <= self.TITLE_BAR_HEIGHT + 0.5:
            height = self.TITLE_BAR_HEIGHT
        else:
            height = max(rect.height(), self.MIN_VISIBLE_HEIGHT)

        clamped = QRectF(rect.x(), rect.y(), width, height)
        super().setRect(clamped)
        self.update_geometry(width, height)

    def itemChange(self, change, value):
        if change in (
            self.GraphicsItemChange.ItemPositionChange,
            self.GraphicsItemChange.ItemPositionHasChanged,
            self.GraphicsItemChange.ItemTransformChange,
            self.GraphicsItemChange.ItemSceneHasChanged,
        ):
            r = self.rect()
            self.update_geometry(r.width(), r.height())
        return super().itemChange(change, value)

    def get_times(self):
        return self.start_label.text(), self.end_label.text()

    def set_times(self, start_str: str, end_str: str):
        self.start_label.setText(start_str)
        self.end_label.setText(end_str)
        self._set_send_button_active(False)
        self.update_geometry(self.rect().width(), self.rect().height())

    def set_current_employee(self, employee_name: str):
        self.current_employee = employee_name
        print(f"[DEBUG] Current employee set to: {employee_name}")
