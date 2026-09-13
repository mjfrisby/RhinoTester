import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from widgets import CrosshairWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Crosshair Widget Example")

        # Create the crosshair widget
        self.crosshair_widget = CrosshairWidget()

        # Create the enable/disable button
        self.toggle_button = QPushButton("Disable Crosshairs")
        self.toggle_button.setCheckable(True)
        self.toggle_button.toggled.connect(self.toggle_crosshairs)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.crosshair_widget)
        layout.addWidget(self.toggle_button)

        # Set the central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def toggle_crosshairs(self, checked):
        if checked:
            self.crosshair_widget.setMovable(False)
            self.toggle_button.setText("Enable Crosshairs")
        else:
            self.crosshair_widget.setMovable(True)
            self.toggle_button.setText("Disable Crosshairs")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
