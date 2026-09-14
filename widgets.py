import math
import sys
from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QPalette, QPen, QColor
from PyQt6.QtWidgets import QWidget, QApplication


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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # The light theme's greys and blue disappear on the dark theme's background
        dark = self.palette().color(QPalette.ColorRole.Window).lightness() < 128

        # Draw the static grid
        grid_color = QColor(90, 90, 90) if dark else QColor(211, 211, 211)
        center_line_color = QColor(140, 140, 140) if dark else QColor(169, 169, 169)
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
            crosshair_color = QColor(90, 150, 255) if dark else QColor(0, 0, 205)
        else:
            crosshair_color = QColor(110, 110, 110) if dark else self.disabled_color

        painter.setPen(QPen(crosshair_color, 2))
        painter.drawLine(self.center.x(), 0, self.center.x(), self.height())
        painter.drawLine(0, self.center.y(), self.width(), self.center.y())

        # Draw the dot at the intersection of the crosshairs
        painter.setBrush(crosshair_color)
        painter.drawEllipse(self.center, 3, 3)  # Radius of the dot

    def mousePressEvent(self, event):
        if self.movable and event.button() == Qt.MouseButton.LeftButton:
            self.update_center(event.pos())

    def mouseMoveEvent(self, event):
        if self.movable and event.buttons() & Qt.MouseButton.LeftButton:
            self.update_center(event.pos())


    def update_center(self, pos):
        # Ensure the new position is within bounds
        x = max(0, min(pos.x(), self.width()))
        y = max(0, min(pos.y(), self.height()))

        self.center = QPoint(x, y)
        self.x_pos = (self.center.x() / self.width()) * (self.max_val - self.min_val) + self.min_val
        self.y_pos = (self.center.y() / self.height()) * (self.max_val - self.min_val) + self.min_val
        self.update()
        # print(f"x: {self.x_pos:.2f}, y: {self.y_pos:.2f}")
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


class DirectionDial(QWidget):
    """Direction picker in the device's own degrees, 0-359, drawn where each
    one pushes the stick: 0 at the bottom (back), 90 left, 180 at the top
    (forward) and 270 right, increasing clockwise like the stock QDial.

    Click or drag to point it; Shift snaps to 15 degrees.  The mouse wheel
    and arrow keys step 1 degree, Page Up/Down step 15, and Home returns to 0.
    Offers QDial's value(), setValue() and valueChanged.
    """
    valueChanged = pyqtSignal(int)

    SNAP = 15
    SIZE = 72
    #: Screen angles, clockwise from the top
    CARDINALS = ((0, "F"), (90, "R"), (180, "B"), (270, "L"))
    #: Screen angle minus value: the device's 0 is at the bottom
    SCREEN_OFFSET = 180
    ACCENT = QColor("#ab37c8")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._hover = False
        self._wheel_remainder = 0
        self.setFixedSize(self.SIZE, self.SIZE)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Forward (F) 180°, right (R) 270°, back (B) 0°, left (L) 90°.\n"
                        "Click or drag to set the direction (Shift snaps to 15°).\n"
                        "Wheel or arrow keys: 1°   Page Up/Down: 15°   Home: 0°")

    def sizeHint(self):
        return QSize(self.SIZE, self.SIZE)

    def value(self):
        return self._value

    def setValue(self, value):
        value = int(round(value)) % 360
        if value != self._value:
            self._value = value
            self.update()
            self.valueChanged.emit(value)

    # --- input ------------------------------------------------------------------

    def _point_at(self, event):
        center = QRectF(self.rect()).center()
        dx = event.position().x() - center.x()
        dy = event.position().y() - center.y()
        if math.hypot(dx, dy) < 2:
            return  # the exact center has no direction
        angle = math.degrees(math.atan2(dx, -dy)) % 360
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            angle = round(angle / self.SNAP) * self.SNAP
        self.setValue(angle - self.SCREEN_OFFSET)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            self._point_at(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._point_at(event)

    def wheelEvent(self, event):
        # High-resolution wheels and touchpads send fractions of a notch
        self._wheel_remainder += event.angleDelta().y()
        notches = int(self._wheel_remainder / 120)
        if notches:
            self._wheel_remainder -= notches * 120
            step = self.SNAP if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else 1
            self.setValue(self._value + notches * step)
        event.accept()

    def keyPressEvent(self, event):
        steps = {
            Qt.Key.Key_Right: 1, Qt.Key.Key_Up: 1,
            Qt.Key.Key_Left: -1, Qt.Key.Key_Down: -1,
            Qt.Key.Key_PageUp: self.SNAP, Qt.Key.Key_PageDown: -self.SNAP,
        }
        if event.key() == Qt.Key.Key_Home:
            self.setValue(0)
        elif event.key() in steps:
            self.setValue(self._value + steps[event.key()])
        else:
            super().keyPressEvent(event)

    def enterEvent(self, event):
        self._hover = True
        self.update()

    def leaveEvent(self, event):
        self._hover = False
        self.update()

    def focusInEvent(self, event):
        self.update()

    def focusOutEvent(self, event):
        self.update()

    # --- painting ---------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        palette = self.palette()
        dark = palette.color(QPalette.ColorRole.Window).lightness() < 128
        enabled = self.isEnabled()
        text_color = palette.color(
            QPalette.ColorGroup.Normal if enabled else QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.WindowText)
        accent = self.ACCENT if enabled else text_color

        center = QRectF(self.rect()).center()
        radius = min(self.width(), self.height()) / 2 - 3

        def at(angle, distance):
            rad = math.radians(angle)
            return QPointF(center.x() + math.sin(rad) * distance, center.y() - math.cos(rad) * distance)

        active = enabled and (self._hover or self.hasFocus())
        rim = accent if active else (QColor(115, 115, 115) if dark else QColor(150, 150, 150))
        painter.setPen(QPen(rim, 2 if active else 1.5))
        painter.setBrush(palette.color(QPalette.ColorRole.Base))
        painter.drawEllipse(center, radius, radius)

        tick = QColor(text_color)
        tick.setAlpha(170)
        painter.setPen(QPen(tick, 1))
        for angle in (45, 135, 225, 315):
            painter.drawLine(at(angle, radius - 4), at(angle, radius - 1))

        letter_font = self.font()
        letter_font.setPointSizeF(max(6.0, letter_font.pointSizeF() * 0.65))
        letter_font.setBold(True)
        painter.setFont(letter_font)
        painter.setPen(tick)
        for angle, letter in self.CARDINALS:
            spot = at(angle, radius - 8)
            painter.drawText(QRectF(spot.x() - 7, spot.y() - 7, 14, 14), Qt.AlignmentFlag.AlignCenter, letter)

        # The pointer starts clear of the readout and runs over the ticks to the rim
        painter.setPen(QPen(accent, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        pointer = self._value + self.SCREEN_OFFSET
        painter.drawLine(at(pointer, radius * 0.55), at(pointer, radius - 2))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(accent)
        painter.drawEllipse(at(pointer, radius - 7), 4.5, 4.5)

        font = self.font()
        font.setPointSizeF(max(7.0, font.pointSizeF() * 0.8))
        painter.setFont(font)
        painter.setPen(text_color)
        painter.drawText(QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2),
                         Qt.AlignmentFlag.AlignCenter, f"{self._value}°")
