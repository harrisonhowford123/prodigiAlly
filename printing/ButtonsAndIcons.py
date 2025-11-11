import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QSpacerItem, QSizePolicy, QPushButton, QFrame
)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QMouseEvent, QTransform
from PyQt6.QtCore import Qt, QSize, QPoint, QPropertyAnimation, QRect, QEasingCurve

from PyQt6.QtCore import QRectF, Qt, QSize, QPropertyAnimation, QEasingCurve, QPoint, QVariantAnimation, QParallelAnimationGroup
from PyQt6.QtWidgets import QPushButton, QWidget, QLabel, QGridLayout, QGraphicsProxyWidget, QApplication, QGraphicsOpacityEffect, QLineEdit, QFrame, QCompleter, QListView
from PyQt6.QtGui import QIcon, QFont, QGuiApplication, QPixmap, QColor

class AnimatedButtonFade(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.default_color = QColor("black")
        self.hover_color = QColor("#3F17BD")
        self.text_default = QColor("#3F17BD")
        self.text_hover = QColor("white")
        self.animation = QVariantAnimation(self)
        self.animation.setDuration(150)
        self.animation.valueChanged.connect(self.update_color)
        self.setFont(QFont("Objektiv Mk2 XBold", 10, QFont.Weight.Bold))
        self.setStyleSheet(f"border: 2px solid #3F17BD; border-radius: 0px; padding: 6px 12px;")
        self._bg_progress = 0.0
        self.update_color()

    def enterEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self._bg_progress)
        self.animation.setEndValue(1.0)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self._bg_progress)
        self.animation.setEndValue(0.0)
        self.animation.start()
        super().leaveEvent(event)

    def update_color(self, value=None):
        if value is not None:
            self._bg_progress = value
        bg_color = self._interpolate_color(self.default_color, self.hover_color, self._bg_progress)
        text_color = self._interpolate_color(self.text_default, self.text_hover, self._bg_progress)
        self.setStyleSheet(f"background-color: {bg_color.name()}; border: 2px solid #3F17BD; color: {text_color.name()}; border-radius: 0px; padding: 6px 12px;")

    def _interpolate_color(self, start, end, progress):
        r = start.red() + (end.red() - start.red()) * progress
        g = start.green() + (end.green() - start.green()) * progress
        b = start.blue() + (end.blue() - start.blue()) * progress
        return QColor(int(r), int(g), int(b))

class AnimatedButton(QPushButton):
    """Custom QPushButton that animates icon size on hover and ensures consistent brightness across icons."""

    def __init__(self, icon_path: str, size: int = 16, parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.normal_size = QSize(size, size)
        self.hover_size = QSize(int(size * 1.15), int(size * 1.15))
        self.setIcon(QIcon(icon_path))
        self.setIconSize(self.normal_size)
        self.setStyleSheet("background: transparent; border: none;")
        self.animation = QPropertyAnimation(self, b"iconSize")
        self.animation.setDuration(150)

    def enterEvent(self, event):
        self.repaint()
        self.animation.stop()
        self.animation.setStartValue(self.iconSize())
        self.animation.setEndValue(self.hover_size)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.iconSize())
        self.animation.setEndValue(self.normal_size)
        self.animation.start()
        super().leaveEvent(event)


