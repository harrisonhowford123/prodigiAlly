from ContainerWidgets import DraggableBoxContainer
from CoreFunctions import resource_path
from ButtonsAndIcons import AnimatedButton, AnimatedButtonFade
from clientCalls import fetch_all_employees, fetch_employee_times
from PyQt6.QtCore import QRectF, Qt, QSize, QPropertyAnimation, QEasingCurve, QPoint, QVariantAnimation, QParallelAnimationGroup, QTimer
from PyQt6.QtWidgets import QPushButton, QWidget, QLabel, QGridLayout, QGraphicsProxyWidget, QApplication, QGraphicsOpacityEffect, QLineEdit, QFrame
from PyQt6.QtGui import QIcon, QFont, QGuiApplication, QPixmap, QColor

class BlackWindow(QWidget):
    def __init__(self, parent=None, on_success=None):
        super().__init__(None)
        self._center_parent = parent
        self.on_success = on_success
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.setStyleSheet("""
            QWidget { background-color: black; }
            QLineEdit {
                border: 2px solid white;
                border-radius: 0px;
                color: white;
                background: transparent;
                padding: 6px;
                font-family: 'Objektiv Mk2 XBold';
                selection-background-color: #3F17BD;
                selection-color: white;
            }
            QLineEdit::placeholder { color: grey; }
        """)

        self.overlay = QFrame(self)
        self.overlay.setStyleSheet("background-color: black;")
        self.overlay.lower()

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(600)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)

        self.slide_animation = QPropertyAnimation(self, b"pos")
        self.slide_animation.setDuration(600)
        self.slide_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.logo_label = QLabel(self)
        self.logo_pixmap = QPixmap(resource_path("images/prodigiAllyLogo.png"))
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        self.input1 = QLineEdit(self)
        self.input2 = QLineEdit(self)
        self.input1.setPlaceholderText("Username...")
        self.input2.setPlaceholderText("Password...")
        self.input2.setEchoMode(QLineEdit.EchoMode.Password)

        for input_box in [self.input1, self.input2]:
            input_box.setFont(QFont("Objektiv Mk2 XBold", 10))

        try:
            self.employees = fetch_all_employees()
            self.employee_names = [emp.employeeName for emp in self.employees]
        except Exception:
            self.employees = []
            self.employee_names = []

        self.input1.textEdited.connect(self._update_inline_suggestion)

        self.close_btn = AnimatedButton(resource_path("icons/closeWindow.png"))
        self.close_btn.setParent(self)
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.clicked.connect(self.close_with_animation)

        self.login_btn = AnimatedButtonFade("Login", self)
        self.login_btn.clicked.connect(self.verify_login)

        self.background_anim = QVariantAnimation()
        self.background_anim.setDuration(500)
        self.background_anim.setStartValue(1.0)
        self.background_anim.setEndValue(0.5)
        self.background_anim.valueChanged.connect(self._update_parent_opacity)

        self.popup_anim = QParallelAnimationGroup()
        self.popup_anim.addAnimation(self.slide_animation)
        self.popup_anim.addAnimation(self.fade_animation)

    def _update_inline_suggestion(self, text):
        if not text:
            return
        for name in self.employee_names:
            if name.lower().startswith(text.lower()):
                suggestion = name[len(text):]
                self.input1.blockSignals(True)
                self.input1.setText(text + suggestion)
                self.input1.setSelection(len(text), len(suggestion))
                self.input1.blockSignals(False)
                return

    def verify_login(self):
        username = self.input1.text().strip()
        password = self.input2.text().strip()

        for emp in self.employees:
            if emp.employeeName.lower() == username.lower() and getattr(emp, 'password', None) == password:
                if callable(self.on_success):
                    self.on_success(emp.employeeName)
                self.close_with_animation()
                return

        # Wrong password animation (red shake)
        red_color = "#FF5555"
        anim = QPropertyAnimation(self.input2, b"pos", self)
        original_pos = self.input2.pos()
        anim.setDuration(150)
        anim.setKeyValueAt(0, original_pos)
        anim.setKeyValueAt(0.25, original_pos + QPoint(-5, 0))
        anim.setKeyValueAt(0.5, original_pos + QPoint(5, 0))
        anim.setKeyValueAt(0.75, original_pos + QPoint(-5, 0))
        anim.setKeyValueAt(1, original_pos)
        anim.start()

        # Red border
        self.input2.setStyleSheet("""
            QLineEdit {
                border: 2px solid #FF5555;
                border-radius: 0px;
                color: white;
                background: transparent;
                padding: 6px;
                font-family: 'Objektiv Mk2 XBold';
                selection-background-color: #3F17BD;
                selection-color: white;
            }
            QLineEdit::placeholder { color: grey; }
        """)

        self.input2.clear()
        self.input2.setPlaceholderText("Password")

        # Reset border after 0.5s
        def reset_border():
            self.input2.setStyleSheet("""
                QLineEdit {
                    border: 2px solid white;
                    border-radius: 0px;
                    color: white;
                    background: transparent;
                    padding: 6px;
                    font-family: 'Objektiv Mk2 XBold';
                    selection-background-color: #3F17BD;
                    selection-color: white;
                }
                QLineEdit::placeholder { color: grey; }
            """)

        QTimer.singleShot(500, reset_border)


    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.input2.hasFocus():
                self.verify_login()
                return

            cursor_pos = self.input1.cursorPosition()
            selected_text = self.input1.selectedText()
            if selected_text:
                self.input1.setCursorPosition(cursor_pos + len(selected_text))
                self.input1.deselect()
                self.input2.setFocus()
            else:
                text = self.input1.text()
                for name in self.employee_names:
                    if name.lower().startswith(text.lower()):
                        self.input1.setText(name)
                        self.input2.setFocus()
                        break
        else:
            super().keyPressEvent(event)

    def resize_relative_to_parent(self):
        if self._center_parent and self._center_parent.isVisible():
            parent_width = self._center_parent.width()
            parent_height = self._center_parent.height()
            new_height = int(parent_height * (2/3))
            new_width = int(new_height / 1.5)
            self.setFixedSize(new_width, new_height)

    def resizeEvent(self, event):
        self.resize_relative_to_parent()
        super().resizeEvent(event)

        self.overlay.setGeometry(0, 0, self.width(), self.height())

        new_width = int(self.width() * 0.85)
        scaled_logo = self.logo_pixmap.scaledToWidth(new_width, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(scaled_logo)

        self.close_btn.move(self.width() - self.close_btn.width() - 10, 10)

        logo_x = (self.width() - scaled_logo.width()) // 2
        logo_y = int(self.height() * 0.15)
        self.logo_label.move(logo_x, logo_y)

        input_width = int(self.width() * 0.8)
        input_height = 36
        spacing = int(self.height() * 0.075)

        start_y = logo_y + scaled_logo.height() + 40
        input_x = (self.width() - input_width) // 2

        self.input1.setGeometry(input_x, start_y, input_width, input_height)
        self.input2.setGeometry(input_x, start_y + input_height + spacing, input_width, input_height)

        login_y = start_y + (input_height + spacing) * 2
        self.login_btn.setGeometry(input_x, login_y, int(input_width * 0.4), input_height)

    def _update_parent_opacity(self, value):
        if self._center_parent and self._center_parent.isVisible():
            for widget in self._center_parent.findChildren(QWidget):
                if widget is not self:
                    effect = widget.graphicsEffect() or QGraphicsOpacityEffect(widget)
                    effect.setOpacity(value)
                    widget.setGraphicsEffect(effect)

    def showEvent(self, event):
        super().showEvent(event)
        self.resize_relative_to_parent()
        parent = self._center_parent
        try:
            if parent is None:
                parent = QApplication.activeWindow()
            if parent and parent.isVisible():
                center_global = parent.mapToGlobal(parent.rect().center())
                target_point = center_global
            else:
                target_point = QGuiApplication.primaryScreen().availableGeometry().center()
        except Exception:
            target_point = QGuiApplication.primaryScreen().availableGeometry().center()

        start_y = int(target_point.y() - self.height() / 2 - 50)
        end_y = int(target_point.y() - self.height() / 2)
        main_x = int(target_point.x() - self.width() / 2)

        self.move(main_x, start_y)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.activateWindow()
        self.raise_()

        self.slide_animation.setStartValue(QPoint(main_x, start_y))
        self.slide_animation.setEndValue(QPoint(main_x, end_y))
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)

        self.background_anim.start()
        self.popup_anim.start()

    def close_with_animation(self):
        # --- Check if linked LoginContainer has empty text_list ---
        container = getattr(self, "login_container_ref", None)
        if container and not container.text_list:
            print("No active users — exiting application.")
            QApplication.quit()
            return

        # --- Otherwise, just close as normal ---
        self.hide()
        if self._center_parent and self._center_parent.isVisible():
            self.reverse_background = QVariantAnimation(self)
            self.reverse_background.setDuration(600)
            self.reverse_background.setStartValue(0.5)
            self.reverse_background.setEndValue(1.0)
            self.reverse_background.valueChanged.connect(self._update_parent_opacity)
            self.reverse_background.finished.connect(self._finish_close)
            self.reverse_background.start()
        else:
            self._finish_close()


    def _finish_close(self):
        if self._center_parent and self._center_parent.isVisible():
            for widget in self._center_parent.findChildren(QWidget):
                widget.setGraphicsEffect(None)
        super().close()

    def closeEvent(self, event):
        if self._center_parent and self._center_parent.isVisible():
            for widget in self._center_parent.findChildren(QWidget):
                widget.setGraphicsEffect(None)
        super().closeEvent(event)


# In loginContainer.py

class LoginContainer(DraggableBoxContainer.ResizableRectItem):
    def __init__(self, rect, parent_view, title="Login Box", text_list=None, clock_container=None):
        super().__init__(rect, parent_view, title)
        self.text_list = text_list or []
        self.clock_container = clock_container

        self.control_widget = QWidget()
        self.layout = QGridLayout(self.control_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)

        # --- Sign Out button setup ---
        self.signout_button = QPushButton()
        self.signout_icon_normal = QIcon(resource_path("icons/signOut.png"))
        self.signout_icon_hovered = QIcon(resource_path("icons/signOut(Hovered).png"))
        self.signout_button.setIcon(self.signout_icon_normal)
        self.signout_button.setFlat(True)
        self.signout_button.setStyleSheet("background: transparent; border: none;")
        self.signout_button.clicked.connect(self._on_signout_click)
        self.signout_button.enterEvent = lambda event: self.signout_button.setIcon(self.signout_icon_hovered)
        self.signout_button.leaveEvent = lambda event: self.signout_button.setIcon(self.signout_icon_normal)

        # --- User button setup ---
        self.add_user_button = QPushButton()
        self.icon_normal = QIcon(resource_path("icons/userIcon.png"))
        self.icon_hovered = QIcon(resource_path("icons/userIcon(Hovered).png"))
        self.add_user_button.setIcon(self.icon_normal)
        self.add_user_button.setFlat(True)
        self.add_user_button.setStyleSheet("background: transparent; border: none;")
        self.add_user_button.clicked.connect(self.open_black_window)
        self.add_user_button.enterEvent = lambda event: self.add_user_button.setIcon(self.icon_hovered)
        self.add_user_button.leaveEvent = lambda event: self.add_user_button.setIcon(self.icon_normal)

        # --- Switch button setup ---
        self.switch_button = QPushButton()
        self.switch_icon_normal = QIcon(resource_path("icons/switchUser.png"))
        self.switch_icon_hovered = QIcon(resource_path("icons/switchUser(Hovered).png"))
        self.switch_button.setIcon(self.switch_icon_normal)
        self.switch_button.setFlat(True)
        self.switch_button.setStyleSheet("background: transparent; border: none;")
        self.switch_button.clicked.connect(self._on_switch_click)
        self.switch_button.enterEvent = lambda event: self.switch_button.setIcon(self.switch_icon_hovered)
        self.switch_button.leaveEvent = lambda event: self.switch_button.setIcon(self.switch_icon_normal)

        # --- Label setup ---
        label_text = f"  {self.text_list[0]}  " if self.text_list else ""
        self.text_label = QLabel(label_text)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setStyleSheet("color: #333; font-weight: 500; background: transparent; font-family: 'Objektiv Mk2 XBold';")
        self.text_label.setWordWrap(True)
        self.text_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        if label_text:
            self.text_label.setText(f"<div style='text-align: center;'>{label_text}</div>")

        # --- Layout structure: 2 rows ---
        self.layout.addWidget(self.signout_button, 0, 0, Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.add_user_button, 0, 1, Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.switch_button, 0, 2, Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.text_label, 1, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)

        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(self.control_widget)

        self.update_geometry(rect.width(), rect.height())
        self._check_and_open_popup()

    def _check_and_open_popup(self):
        """Check if text_list is empty and reopen popup if needed."""
        if not self.text_list:
            # Add a small delay to avoid reopening too early (Qt cleanup timing)
            QTimer.singleShot(300, self.open_black_window)

    def _on_signout_click(self):
        if self.text_list:
            removed = self.text_list.pop()  # remove the end value
            print(f"Signed out: {removed}")
            if self.text_list:
                new_end_entry = self.text_list[-1]
                self.text_label.setText(f"<div style='text-align: center;'>{new_end_entry}</div>")
            else:
                self.text_label.setText("")
                # If list is now empty, open login popup
                self.open_black_window()
            print("Updated text_list after sign out:", self.text_list)

    def _on_switch_click(self):
        # Skip if text_list is empty or only has one entry
        if not self.text_list:
            print("[DEBUG] text_list is empty — skipping rotation and time fetch.")
            return
        if len(self.text_list) == 1:
            print("[DEBUG] Only one employee in text_list — skipping rotation and time fetch.")
            return

        # Rotate list
        last_item = self.text_list.pop()
        self.text_list.insert(0, last_item)
        new_end_entry = self.text_list[-1]
        self.text_label.setText(f"<div style='text-align: center;'>{new_end_entry}</div>")
        print("Rotated text_list:", self.text_list)

        # --- Update current employee in clock container ---
        if self.clock_container:
            self.clock_container.set_current_employee(new_end_entry)

        # Only fetch times if name is valid (non-empty string)
        if new_end_entry and new_end_entry.strip():
            try:
                start_time, end_time = fetch_employee_times(new_end_entry)
                if start_time or end_time:
                    start_str = start_time.strftime("%H:%M") if start_time else "—"
                    end_str = end_time.strftime("%H:%M") if end_time else "—"

                    if self.clock_container:
                        self.clock_container.set_times(start_str, end_str)
                        print(f"[DEBUG] Updated clock for {new_end_entry} → {start_str} - {end_str}")
                    else:
                        print("[DEBUG] No clock container attached; cannot update times.")
                else:
                    print(f"[DEBUG] {new_end_entry} has no recorded start/end times.")
            except Exception as e:
                print(f"[DEBUG] Failed to fetch times for {new_end_entry}: {e}")
        else:
            print("[DEBUG] Skipping time fetch — invalid or blank employee name.")


    def open_black_window(self):
        parent_window = QApplication.activeWindow() or self.control_widget.window()
        self.black_window = BlackWindow(
            parent_window,
            on_success=self._on_login_success
        )
        self.black_window.login_container_ref = self  # pass reference to container
        original_close = self.black_window._finish_close
        def wrapped_close():
            original_close()
            self._check_and_open_popup()
        self.black_window._finish_close = wrapped_close
        self.black_window.show()

    def _on_login_success(self, employee_name):
        if employee_name in self.text_list:
            self.text_list.remove(employee_name)
        self.text_list.append(employee_name)
        print("Updated text_list:", self.text_list)
        self.text_label.setText(f"<div style='text-align: center;'>{employee_name}</div>")
        self.update_geometry(self.rect().width(), self.rect().height())

        # --- Update clock times and current employee ---
        if self.clock_container:
            self.clock_container.set_current_employee(employee_name)

        if self.text_list and employee_name and employee_name.strip():
            try:
                start_time, end_time = fetch_employee_times(employee_name)
                if start_time or end_time:
                    start_str = start_time.strftime("%H:%M") if start_time else "—"
                    end_str = end_time.strftime("%H:%M") if end_time else "—"

                    if self.clock_container:
                        self.clock_container.set_times(start_str, end_str)
                        print(f"[DEBUG] Updated clock for {employee_name} → {start_str} - {end_str}")
                    else:
                        print("[DEBUG] No clock container attached; cannot update times.")
                else:
                    print(f"[DEBUG] {employee_name} has no recorded start/end times.")
            except Exception as e:
                print(f"[DEBUG] Failed to fetch times for {employee_name}: {e}")
        else:
            print("[DEBUG] Skipping time fetch — text_list empty or invalid employee name.")



    def update_geometry(self, width, height):
        if not self.proxy or width <= 0 or height <= 0:
            return

        border_margin = 5
        title_offset = self.TITLE_BAR_HEIGHT + border_margin
        new_rect = QRectF(border_margin, title_offset, max(0, width - border_margin * 2), max(0, height - title_offset - border_margin))
        self.proxy.setGeometry(new_rect)

        third_width = new_rect.width() / 3
        available_height = new_rect.height() / 2
        square_side = int(min(third_width, available_height)) - 8
        square_side = max(32, square_side)

        for btn in [self.signout_button, self.add_user_button, self.switch_button]:
            btn.setFixedSize(square_side, square_side)
            btn.setIconSize(QSize(square_side - 6, square_side - 6))

        font_size = int(new_rect.height() * 0.15)
        max_font_size = int(new_rect.width() * 0.08)
        font_size = max(10, min(font_size, max_font_size))

        self.text_label.setStyleSheet(
            f"color: #333; font-size: {font_size}px; font-weight: 500; background: transparent; text-align: center; font-family: 'Objektiv Mk2 XBold';"
        )

        self.layout.setRowStretch(0, 2)
        self.layout.setRowStretch(1, 1)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.activate()
        self.control_widget.update()

    def setRect(self, rect):
        super().setRect(rect)
        if hasattr(self, "proxy"):
            self.update_geometry(rect.width(), rect.height())

    def itemChange(self, change, value):
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
