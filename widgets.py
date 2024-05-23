import sys
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QWidget, QApplication


class CrosshairWidget(QWidget):
    crosshairPositionChanged = pyqtSignal(float, float)
    def __init__(self, min_val=-1.0, max_val=1.0):
        super().__init__()
        self.setMinimumSize(200, 200)
        self.center = QPoint(self.width() // 2, self.height() // 2)
        self.min_val = min_val
        self.max_val = max_val
        self.x_pos = 0.0
        self.y_pos = 0.0
        self.movable = True
        self.disabled_color = QColor(211, 211, 211)  # Light grey

        # Reference crosshair position
        self.ref_x_pos = 0.0
        self.ref_y_pos = 0.0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the static grid
        grid_color = QColor(211, 211, 211)  # Light grey
        center_line_color = QColor(169, 169, 169)  # Slightly darker grey
        painter.setPen(QPen(grid_color, 1))

        # Draw vertical grid lines
        num_lines = 10
        for i in range(num_lines + 1):
            x = i * self.width() // num_lines
            painter.drawLine(x, 0, x, self.height())

        # Draw horizontal grid lines
        for i in range(num_lines + 1):
            y = i * self.height() // num_lines
            painter.drawLine(0, y, self.width(), y)

        # Draw center lines
        painter.setPen(QPen(center_line_color, 1))
        painter.drawLine(self.width() // 2, 0, self.width() // 2, self.height())
        painter.drawLine(0, self.height() // 2, self.width(), self.height() // 2)

        # Draw the reference crosshairs
        ref_color = QColor(255, 0, 0)  # Red
        ref_x_pos = (self.ref_x_pos + 1) / 2 * self.width()
        ref_y_pos = (self.ref_y_pos + 1) / 2 * self.height()
        painter.setPen(QPen(ref_color, 2))
        painter.drawLine(int(ref_x_pos), 0, int(ref_x_pos), self.height())
        painter.drawLine(0, int(ref_y_pos), self.width(), int(ref_y_pos))

        # Draw the movable crosshairs
        if self.movable:
            crosshair_color = QColor(0, 0, 205)  # Medium blue
        else:
            crosshair_color = self.disabled_color

        painter.setPen(QPen(crosshair_color, 2))
        painter.drawLine(self.center.x(), 0, self.center.x(), self.height())
        painter.drawLine(0, self.center.y(), self.width(), self.center.y())

        # Draw the dot at the intersection of the crosshairs
        painter.setBrush(crosshair_color)
        painter.drawEllipse(self.center, 3, 3)  # Radius of the dot

    def mousePressEvent(self, event):
        if self.movable and event.button() == Qt.LeftButton:
            self.update_center(event.pos())

    def mouseMoveEvent(self, event):
        if self.movable and event.buttons() & Qt.LeftButton:
            self.update_center(event.pos())


    def update_center(self, pos):
        # Ensure the new position is within bounds
        x = max(0, min(pos.x(), self.width()))
        y = max(0, min(pos.y(), self.height()))

        self.center = QPoint(x, y)
        self.x_pos = (self.center.x() / self.width()) * (self.max_val - self.min_val) + self.min_val
        self.y_pos = (self.center.y() / self.height()) * (self.max_val - self.min_val) + self.min_val
        self.update()
        print(f"x: {self.x_pos:.2f}, y: {self.y_pos:.2f}")
        self.crosshairPositionChanged.emit(self.x_pos, self.y_pos)

    def resizeEvent(self, event):
        # Ensure center remains at the current logical position when resized
        self.center = QPoint(
            int((self.x_pos - self.min_val) / (self.max_val - self.min_val) * self.width()),
            int((self.y_pos - self.min_val) / (self.max_val - self.min_val) * self.height())
        )
        self.update()

    def setMovable(self, movable):
        self.movable = movable
        self.update()

    def setReferencePosition(self, x, y):
        """
        Set the position of the reference crosshairs.
        :param x: The x-coordinate position (between -1 and 1).
        :param y: The y-coordinate position (between -1 and 1).
        """
        # Ensure the provided positions are within the valid range
        x = max(min(x, 1), -1)
        y = max(min(y, 1), -1)

        # Update the reference positions
        self.ref_x_pos = x
        self.ref_y_pos = y

        # Request a repaint to update the widget
        self.update()
