import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from ButtonsAndIcons import AnimatedButton
from ContainerWidgets import DraggableBoxContainer
from FileDropContainer import FileDropbox
from CoreFunctions import resource_path
from DropBoxController import DropBoxController
from loginContainer import LoginContainer
from DropBoxStatistics import DropBoxStatistics
from loggedInClock import DigitalClockContainer

class SandboxWindow(QMainWindow):
    def __init__(self, widgetData = None):
        super().__init__()

        self.setWindowTitle("Sandbox Environment")
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowSystemMenuHint | Qt.WindowType.WindowMinMaxButtonsHint)

        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background-color: #FCFCFC;")
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- Custom Top Bar ---
        self.top_bar = QWidget()
        self.top_bar.setStyleSheet("background-color: black;")
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.top_bar_layout.setContentsMargins(10, 5, 10, 5)
        self.top_bar_layout.setSpacing(10)

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        logo_path = resource_path("images/prodigiLogo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            self.logo_label.setPixmap(logo_pixmap.scaledToHeight(28, Qt.TransformationMode.SmoothTransformation))
        self.top_bar_layout.addWidget(self.logo_label)
        self.top_bar_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        try:
            self.min_button = AnimatedButton(resource_path("icons/minimiseWindow.png"))
            self.min_button.clicked.connect(self.showMinimized)

            self.max_button = AnimatedButton(resource_path("icons/maximiseWindow.png"))
            self.max_button.clicked.connect(self.toggle_max_restore)

            self.close_button = AnimatedButton(resource_path("icons/closeWindow.png"))
            self.close_button.clicked.connect(self.close)
        except Exception as e:
            print(f"[WARN] Could not load buttons: {e}")

        for btn in [getattr(self, name, None) for name in ["min_button", "max_button", "close_button"] if hasattr(self, name)]:
            self.top_bar_layout.addWidget(btn)

        self.main_layout.addWidget(self.top_bar)

        # --- Sandbox Area ---
        self.sandbox_container = DraggableBoxContainer(self.central_widget)
        self.main_layout.addWidget(self.sandbox_container)

        self.rect_items = []
        win_w = self.width()
        win_h = self.height()
        margin = 5

        widgetData = [
            {
                "container": None,
                "pos": (2 * margin + win_w * 0.32, margin),
                "rect_type": "DropBoxStatistics",
                "size": (win_w * 0.25, win_h * 0.2),
                "label": "Dropbox Stats"
            },
            {
                "container": None,
                "pos": (margin, margin + win_h * 0.2 + margin),
                "rect_type": "FileDropbox",
                "size": (win_w * 0.32, win_h - (margin+(win_h*0.28))),
                "label": "File Dropbox"
            },
            {
                "container": None,
                "pos": (margin, margin),
                "rect_type": "DropBoxController",
                "size": (win_w * 0.32, win_h * 0.2),
                "label": "File Box Remote"
            },
            {
                "container": None,
                # Below Login: start Y where login ends + margin
                "pos": (2 * margin + win_w * 0.32, margin + win_h * 0.2 + margin + win_h * 0.35 + margin),
                "rect_type": "DigitalClock",
                "size": (win_w * 0.25, (win_h - (margin+(win_h*0.28)))/2),
                "label": "Clock Display"
            },
            {
                "container": None,
                "pos": (2 * margin + win_w * 0.32, margin+win_h*0.2+margin),
                "rect_type": "LoginContainer",
                "size": (win_w * 0.25, (win_h - (margin+(win_h*0.28)))/2 - margin),
                "label": "User Login"
            }
        ]

        try:
            if not widgetData:
                raise ValueError("widgetData is None or empty. No widgets to load.")

            dropbox_stats_instance = None  # Track DropBoxStatistics instance for passing into FileDropbox
            login_container_instance = None

            for data in widgetData:
                x, y = data.get("pos", (0, 0))
                w, h = data.get("size", (200, 120))
                rect_type = data.get("rect_type", "ResizableRectItem")

                if rect_type == "DropBoxStatistics":
                    rect = DropBoxStatistics(
                        QRectF(0, 0, w, h),
                        self.sandbox_container,
                        data.get("label", "Dropbox Stats")
                    )
                    dropbox_stats_instance = rect  # Save for later use

                elif rect_type == "FileDropbox":
                    rect = FileDropbox(
                        QRectF(0, 0, w, h),
                        self.sandbox_container,
                        data.get("label", "Dropbox"),
                        statistics_view=dropbox_stats_instance  # Pass the stats instance here
                    )

                elif rect_type == "DropBoxController":
                    file_dropbox = next(
                        (r for r in self.rect_items if isinstance(r, FileDropbox)),
                        None
                    )
                    if not file_dropbox:
                        print("[WARNING] No FileDropbox found, creating a new one")
                        file_dropbox = FileDropbox(
                            QRectF(0, 0, w, h),
                            self.sandbox_container,
                            "File Dropbox",
                            statistics_view=dropbox_stats_instance
                        )

                    rect = DropBoxController(
                        QRectF(0, 0, w, h),
                        self.sandbox_container,
                        file_dropbox,
                        data.get("label", "File Box Remote")
                    )

                elif rect_type == "DigitalClock":
                    rect = DigitalClockContainer(
                        QRectF(0, 0, w, h),
                        self.sandbox_container,
                        data.get("label", "Digital Clock")
                    )
                    clock_instance = rect

                elif rect_type == "LoginContainer":
                    rect = LoginContainer(
                        QRectF(0, 0, w, h),
                        self.sandbox_container,
                        data.get("label", "User Login"),
                        text_list=[],
                        clock_container=locals().get("clock_instance", None)
                    )
                    login_container_instance = rect


                else:
                    rect = self.sandbox_container.ResizableRectItem(
                        QRectF(0, 0, w, h),
                        self.sandbox_container
                    )

                rect.setPos(x, y)
                self.sandbox_container.scene.addItem(rect)
                self.rect_items.append(rect)

            # Lock the scene rect to the window dimensions
            self.sandbox_container.scene.setSceneRect(0, 0, self.width(), self.height())


            # After the widget creation loop:
            file_dropbox = next((r for r in self.rect_items if isinstance(r, FileDropbox)), None)
            if file_dropbox and login_container_instance:
                file_dropbox.login_container = login_container_instance


        except ValueError as e:
            print(f"[Widget Loader] {e}")
        except Exception as e:
            print(f"[Widget Loader] Unexpected error: {e}")

        # Store geometry info per rect
        self.relative_states = {}

        self.is_maximized = False
        self.update_sizes()

        # Enable collision detection between boxes and resizing
        self.enable_box_collisions()
        self.enable_resize_collisions()

        self.top_bar.raise_()

    def enable_box_collisions(self):
        for rect in self.rect_items:
            if hasattr(rect, 'mouseMoveEvent'):
                original_mouse_move = rect.mouseMoveEvent

                def new_mouse_move(event, r=rect, orig=original_mouse_move):
                    prev_pos = r.pos()
                    orig(event)

                    overlaps = [o for o in self.rect_items if o is not r and r.collidesWithItem(o)]

                    for other in overlaps:
                        r_rect = r.sceneBoundingRect()
                        o_rect = other.sceneBoundingRect()

                        dx_left = o_rect.left() - r_rect.right()
                        dx_right = o_rect.right() - r_rect.left()
                        dy_top = o_rect.top() - r_rect.bottom()
                        dy_bottom = o_rect.bottom() - r_rect.top()

                        dx = dy = 0
                        if abs(dx_left) < abs(dx_right) and abs(dx_left) < abs(dy_top) and abs(dx_left) < abs(dy_bottom):
                            dx = dx_left
                        elif abs(dx_right) < abs(dy_top) and abs(dx_right) < abs(dy_bottom):
                            dx = dx_right
                        elif abs(dy_top) < abs(dy_bottom):
                            dy = dy_top
                        else:
                            dy = dy_bottom

                        r.setPos(r.pos() + QPointF(dx, dy))

                        for check_other in self.rect_items:
                            if check_other is not r and r.collidesWithItem(check_other):
                                r.setPos(prev_pos)
                                break

                rect.mouseMoveEvent = new_mouse_move

    def enable_resize_collisions(self):
        for rect in self.rect_items:
            if hasattr(rect, 'mouseMoveEvent'):
                original_mouse_move = rect.mouseMoveEvent

                def new_resize_move(event, r=rect, orig=original_mouse_move):
                    prev_rect = r.rect()
                    orig(event)

                    overlaps = [o for o in self.rect_items if o is not r and r.collidesWithItem(o)]
                    if overlaps:
                        current_rect = r.rect()
                        delta_w = current_rect.width() - prev_rect.width()
                        delta_h = current_rect.height() - prev_rect.height()

                        growing = False
                        if hasattr(r, 'resize_dir'):
                            if r.resize_dir in ('right', 'bottom', 'bottom_right'):
                                growing = (delta_w > 0 or delta_h > 0)
                            elif r.resize_dir in ('left', 'bottom_left'):
                                growing = (delta_w < 0 or delta_h > 0)

                        if growing:
                            r.setRect(prev_rect)
                            event.ignore()

                rect.mouseMoveEvent = new_resize_move

    def store_all_relative_positions(self):
        view_rect = self.sandbox_container.visible_scene_rect()
        self.relative_states.clear()
        for rect in self.rect_items:
            rect_pos = rect.pos()
            rect_geom = rect.rect()
            rel_x = (rect_pos.x() - view_rect.left()) / view_rect.width()
            rel_y = (rect_pos.y() - view_rect.top()) / view_rect.height()
            rel_w = rect_geom.width() / view_rect.width()
            rel_h = rect_geom.height() / view_rect.height()
            self.relative_states[rect] = (rel_x, rel_y, rel_w, rel_h)

    def restore_all_relative_positions(self):
        view_rect = self.sandbox_container.visible_scene_rect()
        if view_rect.width() <= 0 or view_rect.height() <= 0:
            return  # scene not ready yet

        for rect, (rel_x, rel_y, rel_w, rel_h) in list(self.relative_states.items()):
            try:
                new_w = max(1.0, rel_w * view_rect.width())
                new_h = max(1.0, rel_h * view_rect.height())
                new_x = view_rect.left() + rel_x * view_rect.width()
                new_y = view_rect.top()  + rel_y * view_rect.height()

                # Set rect then position; both can trigger itemChange
                rect.setRect(QRectF(0, 0, new_w, new_h))
                rect.setPos(QPointF(new_x, new_y))
            except RuntimeError:
                # The rect may have been deleted; drop its state
                self.relative_states.pop(rect, None)
            except Exception as e:
                print(f"[restore] rect error: {e}")

        # Bounded de-overlap pass to avoid infinite/expensive loops
        max_passes = 20
        for _ in range(max_passes):
            changed = False
            for i, r in enumerate(self.rect_items):
                for j, o in enumerate(self.rect_items):
                    if i != j and r.collidesWithItem(o):
                        r.setPos(r.pos() + QPointF(20, 20))
                        changed = True
            if not changed:
                break
            
    def toggle_max_restore(self):
        self.store_all_relative_positions()
        if self.is_maximized:
            self.showNormal()
        else:
            self.showMaximized()

        self.is_maximized = not self.is_maximized
        QTimer.singleShot(100, self.restore_all_relative_positions)

    def mousePressEvent(self, event):
        # Disable window dragging when maximized or fullscreen
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.top_bar.underMouse()
            and not self.isMaximized()
            and not self.isFullScreen()
        ):
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            self._drag_pos = None
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Only drag when not maximized or fullscreen
        if (
            event.buttons() == Qt.MouseButton.LeftButton
            and hasattr(self, "_drag_pos")
            and self._drag_pos is not None
            and not self.isMaximized()
            and not self.isFullScreen()
        ):
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            self.move(new_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_sizes()

    def update_sizes(self):
        bar_height = max(32, int(self.height() * 0.064))
        self.top_bar.setFixedHeight(bar_height)
        self.sandbox_container.set_top_inset(bar_height)

        # Dynamically scale logo based on bar height
        logo_path = resource_path("images/prodigiLogo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            # Use a fraction of the bar height for scaling (e.g., 70%)
            scaled_height = int(bar_height * 0.7)
            self.logo_label.setPixmap(
                logo_pixmap.scaledToHeight(scaled_height, Qt.TransformationMode.SmoothTransformation)
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SandboxWindow()
    window.show()
    sys.exit(app.exec())
