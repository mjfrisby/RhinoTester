import ctypes
import logging
import os
import sys
import winreg

from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal, Qt, QThread, QTimer
from PyQt6.QtGui import QAction, QActionGroup, QColor, QFont, QIcon, QIntValidator, QPalette
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QListWidgetItem, QMessageBox,
    QPushButton, QVBoxLayout, QWidget,
)
from widgets import CrosshairWidget
from logwindow import LogWindow, install_logging

import styles
from interface import Ui_MainWindow
from telemffb import utils
from typing import Dict, List
from telemffb.hw.ffb_rhino import (
    HapticEffect, FFBReport_SetCondition, FFBRhino, DeviceInfo,
    EFFECT_SQUARE, EFFECT_SINE, EFFECT_TRIANGLE, EFFECT_SAWTOOTHUP,
    EFFECT_SAWTOOTHDOWN,
)
from telemffb.hw import ffb_dinput

global dev
dev = None

effects: Dict[str, HapticEffect] = utils.Dispenser(HapticEffect)

#: devpath prefix marking a DirectInput device (mirrors TelemFFB's
#: selector convention: 'dinput:{instance GUID}')
DINPUT_PREFIX = "dinput:"

#: Slider steps per 1.0 of intensity; the paired spin box shows the same value.
INTENSITY_STEPS = 1000

WAVEFORM_NAMES = {
    EFFECT_SQUARE: "Square",
    EFFECT_SINE: "Sine",
    EFFECT_TRIANGLE: "Triangle",
    EFFECT_SAWTOOTHUP: "Sawtooth Up",
    EFFECT_SAWTOOTHDOWN: "Sawtooth Down",
}


#: TelemFFB's app icon, for the window; the exe's own icon comes from the build spec
APP_ICON = os.path.join("image", "vpforceicon.png")

#: Windows groups taskbar buttons by this; without it a source run shows Python's icon
APP_USER_MODEL_ID = "VPforce.RhinoTester"


def resource_path(relative):
    """A file shipped with the tester: in the unpacked bundle when frozen,
    beside this script otherwise."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


#: Saved settings, beside the other VPforce apps' keys under HKEY_CURRENT_USER
SETTINGS_KEY = r"Software\VPforce\RhinoTester"

#: Theme choices, numbered as TelemFFB's themeId setting
THEME_LIGHT, THEME_DARK, THEME_SYSTEM = 0, 1, 2
THEME_NAMES = {THEME_SYSTEM: "System", THEME_LIGHT: "Light", THEME_DARK: "Dark"}
#: apply_theme's ``dark`` argument for each choice; None follows Windows
THEME_DARK_FLAG = {THEME_LIGHT: False, THEME_DARK: True, THEME_SYSTEM: None}


class Settings:
    """The tester's saved choices, as values under HKEY_CURRENT_USER\\<key>.
    Integers are stored as REG_DWORD and everything else as REG_SZ."""

    def __init__(self, key=SETTINGS_KEY):
        self.key = key

    def get(self, name, default=None):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.key) as key:
                return winreg.QueryValueEx(key, name)[0]
        except OSError:
            return default

    def set(self, name, value):
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.key) as key:
                kind = winreg.REG_DWORD if isinstance(value, int) else winreg.REG_SZ
                winreg.SetValueEx(key, name, 0, kind, value if kind == winreg.REG_DWORD else str(value))
        except OSError:
            logging.exception(f"Could not save {name} under HKEY_CURRENT_USER\\{self.key}")


def device_id(devinfo) -> str:
    """A name that finds the same device on a later run.  A HID path changes
    with the USB port, so VPforce devices go by serial number instead."""
    path = _devpath(devinfo)
    if path.startswith(DINPUT_PREFIX):
        return path
    return f"hid:{devinfo.vendor_id:04X}:{devinfo.product_id:04X}:{devinfo.serial_number}"


def apply_theme(app, dark=None):
    """TelemFFB's look: Fusion, Segoe UI, its accent color, and its dark
    palette and stylesheets.  ``dark`` of None follows the Windows setting.
    Can be called again to switch themes while running.

    Mirrors ``_setup_theme_and_styling`` in TelemFFB's main.py, and styles.py
    is copied from TelemFFB unchanged; update both together.
    """
    if app.style().name().lower() != 'fusion':
        app.setStyle('fusion')
    app.setFont(QFont('Segoe UI', 10))
    hints = app.styleHints()
    if dark is None:
        # a scheme set earlier hides the Windows setting until it is unset
        hints.unsetColorScheme()
        dark = hints.colorScheme() != Qt.ColorScheme.Light
    hints.setColorScheme(Qt.ColorScheme.Dark if dark else Qt.ColorScheme.Light)

    # Start from the style's own palette, or the previous theme's colors remain
    app.setPalette(QPalette())
    palette = app.palette()
    accent = QColor('#9430ad')
    palette.setColor(QPalette.ColorRole.Highlight, accent)
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor('white'))
    palette.setColor(QPalette.ColorRole.Link, accent)
    if dark:
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor('#dddddd'))
        palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.Text, QColor('#cccccc'))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor('#dddddd'))
        palette.setColor(QPalette.ColorRole.BrightText, QColor('red'))
        for role in (QPalette.ColorRole.WindowText, QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText):
            palette.setColor(QPalette.ColorGroup.Disabled, role, QColor(127, 127, 127))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(43, 43, 43))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor('#dddddd'))
    app.setPalette(palette)
    app.setStyleSheet(styles.DARK_MODE_STYLESHEET if dark else styles.LIGHT_MODE_STYLESHEET)
    return dark


def enumerate_devices() -> List[DeviceInfo]:
    """Every connectable device: VPforce hardware over HID, plus generic
    DirectInput FFB devices when the bridge DLL is present.

    VPforce devices also enumerate as DirectInput devices, so VID 0xFFFF
    is filtered from the DirectInput listing - those entries come from
    the native HID enumeration.
    """
    devs = list(FFBRhino.enumerate())
    logging.info("Available Rhino Devices:")
    logging.info("-------")
    for devinfo in devs:
        logging.info(
            f"* {devinfo.vendor_id:04X}:{devinfo.product_id:04X} - "
            f"{devinfo.product_string} - {devinfo.serial_number}")
        logging.info(f"* Path:{devinfo.path}")
    logging.info("-------")

    available, reason = ffb_dinput.bridge_availability()
    if not available:
        logging.info(f"DirectInput support not available: {reason}")
        return devs

    try:
        di_devs = ffb_dinput.DInputFFBDevice.enumerate()
    except Exception:
        logging.exception("DirectInput enumeration failed")
        return devs
    logging.info("Available DirectInput FFB Devices:")
    logging.info("-------")
    for devinfo in di_devs:
        if devinfo.vendor_id == 0xFFFF:
            continue
        devinfo.product_string = f"[DI] {devinfo.product_string}"
        devinfo.path = f"{DINPUT_PREFIX}{devinfo.guid}".encode()
        logging.info(
            f"* {devinfo.vendor_id:04X}:{devinfo.product_id:04X} - "
            f"{devinfo.product_string}")
        devs.append(devinfo)
    logging.info("-------")
    return devs


def _devpath(devinfo) -> str:
    path = devinfo.path
    return path.decode() if isinstance(path, bytes) else str(path)


class DeviceMonitorThread(QThread):
    positionChanged = pyqtSignal(float, float)

    def run(self):
        # Stopped by requestInterruption(), never terminate(): a thread killed
        # mid-call can leave a lock held and hang the process on exit
        while not self.isInterruptionRequested():
            if dev is not None:
                # a freshly opened device has no input snapshot until its
                # first report arrives; None until then
                input_data = dev.get_input()
                if input_data is not None:
                    x, y = input_data.axisXY()
                    self.positionChanged.emit(x, y)
            self.msleep(10)  # Adjust the interval as needed


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    _device_x = 0
    _device_y = 0
    cpOx = 0
    cpOy = 0

    def __init__(self, settings=None, theme=THEME_SYSTEM, log_handler=None):
        super().__init__()
        self.settings = settings if settings is not None else Settings()
        self.theme = theme
        self.log_handler = log_handler
        self.log_window = None
        #: Additive effects waiting for the next start, in the order queued.
        self.queue: List[dict] = []
        #: Running effects shown in the active list: effect name -> (row, label).
        self._active_rows: Dict[str, tuple] = {}
        #: Timed effects whose duration has run out; still listed, no longer playing.
        self._finished: set = set()
        #: The queued entry the periodic or constant controls are editing, or None.
        self._editing = None
        #: Set while an entry is loaded into the controls, so loading is not an edit.
        self._loading = False
        self.spring = None
        self.setupUi(self)
        self.init_ui()

        self.connected = False
        self.effect_index = 0

        # Create the device monitor thread
        self.device_thread = DeviceMonitorThread()
        self.device_thread.positionChanged.connect(self.update_reference_position)
        self.spring_x = FFBReport_SetCondition(parameterBlockOffset=0)
        self.spring_y = FFBReport_SetCondition(parameterBlockOffset=1)

        self._build_view_menu()
        # Once the event loop runs, so the window is up before any connection error dialog
        QTimer.singleShot(0, self._auto_connect)

    def init_ui(self):
        self.label_Connected.setStyleSheet("color: red;")

        int_validator = QIntValidator()
        self.bg_PeriodicType.setId(self.rb_Square, EFFECT_SQUARE)
        self.bg_PeriodicType.setId(self.rb_Sine, EFFECT_SINE)
        self.bg_PeriodicType.setId(self.rb_Triangle, EFFECT_TRIANGLE)
        self.bg_PeriodicType.setId(self.rb_SawtoothUp, EFFECT_SAWTOOTHUP)
        self.bg_PeriodicType.setId(self.rb_SawtoothDown, EFFECT_SAWTOOTHDOWN)
        self.rb_Sine.setChecked(True)

        self.txt_PeriodicFrequency.setValidator(int_validator)
        self.txt_Duration.setValidator(int_validator)
        self.txt_Duration.setText("0")

        self._bind_intensity(self.slider_PeriodicIntensity, self.spin_PeriodicIntensity, 0.15)
        self._bind_intensity(self.slider_ConstantIntensity, self.spin_ConstantIntensity, 0.5)
        self._bind_intensity(self.slider_DamperIntensity, self.spin_DamperIntensity, 0.5)
        self._bind_intensity(self.slider_InertiaIntensity, self.spin_InertiaIntensity, 0.85)
        self._bind_intensity(self.slider_FrictionIntensity, self.spin_FrictionIntensity, 0.5)
        self._bind_intensity(self.slider_SpringIntensity, self.spin_SpringIntensity, 0.5)

        self.button_Connect.clicked.connect(self.connect_device)
        self.button_Start.clicked.connect(self.start_effects)
        self.button_Stop.clicked.connect(self.stop_effects)
        self.button_QueuePeriodic.clicked.connect(self.queue_periodic)
        self.button_QueueConstant.clicked.connect(self.queue_constant)
        self.button_QueueRemove.clicked.connect(self.remove_queued)
        self.button_QueueClear.clicked.connect(self.clear_queue)
        self.list_Active.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.list_Queue.itemSelectionChanged.connect(self._queue_selection_changed)
        self.list_Queue.setToolTip("Select one entry to edit it with the controls on the left.\n"
                                   "Changes apply at once, even while the effect is playing.")
        for signal in (self.dialPeriodic.valueChanged, self.spin_PeriodicIntensity.valueChanged,
                       self.bg_PeriodicType.idClicked, self.slider_PeriodicPhase.valueChanged,
                       self.txt_PeriodicFrequency.textEdited, self.txt_Duration.textEdited):
            signal.connect(lambda *_: self._controls_changed("periodic"))
        for signal in (self.dialConstant.valueChanged, self.spin_ConstantIntensity.valueChanged):
            signal.connect(lambda *_: self._controls_changed("constant"))

        # Populate the device combobox: HID VPforce devices, then any
        # DirectInput FFB devices the bridge can see
        for devinfo in enumerate_devices():
            label = f"{devinfo.product_id:04X} - {devinfo.product_string}"
            self.cb_PID.addItem(label, userData=devinfo)

        self.dialConstant.setValue(0)
        self.dialPeriodic.setValue(0)
        self.txt_PeriodicFrequency.setText("10")
        self.slider_PeriodicPhase.setValue(0)
        self.lab_PeriodicPhase.setText("0")
        self.slider_PeriodicPhase.valueChanged.connect(self.update_phase_value)

        # Find the frame where the crosshair widget will be placed
        self.placeholder_frame = self.findChild(QWidget, 'crosshair_frame')

        # Create the crosshair widget
        self.crosshair_widget = CrosshairWidget()

        # Replace the frame with the crosshair widget
        layout = QVBoxLayout(self.placeholder_frame)
        layout.addWidget(self.crosshair_widget)
        self.placeholder_frame.setLayout(layout)

        self.crosshair_widget.setReferencePosition(0, 0)
        self.crosshair_widget.setDisabled(True)
        # Connected once: every connection runs the handler, so connecting
        # per spring start would send each drag's conditions several times.
        self.crosshair_widget.crosshairPositionChanged.connect(self.handle_crosshair_movement)

    @staticmethod
    def _bind_intensity(slider, spin, value):
        """Keep a slider and its spin box showing the same 0.0-1.0 intensity."""
        slider.setRange(0, INTENSITY_STEPS)
        spin.setRange(0.0, 1.0)
        spin.setDecimals(3)
        spin.setSingleStep(0.01)
        slider.valueChanged.connect(lambda v: spin.setValue(v / INTENSITY_STEPS))
        spin.valueChanged.connect(lambda v: slider.setValue(round(v * INTENSITY_STEPS)))
        spin.setValue(value)

    def _build_view_menu(self):
        view_menu = self.menubar.addMenu("&View")
        self.log_action = QAction("&Log…", self)
        self.log_action.setShortcut("Ctrl+L")
        self.log_action.triggered.connect(self.show_log)
        view_menu.addAction(self.log_action)
        view_menu.addSeparator()
        theme_menu = view_menu.addMenu("&Theme")
        group = QActionGroup(self)
        group.setExclusive(True)
        self.theme_actions: Dict[int, QAction] = {}
        for theme_id in (THEME_SYSTEM, THEME_LIGHT, THEME_DARK):
            action = QAction(THEME_NAMES[theme_id], self, checkable=True)
            action.setChecked(theme_id == self.theme)
            action.triggered.connect(lambda _checked=False, t=theme_id: self.set_theme(t))
            group.addAction(action)
            theme_menu.addAction(action)
            self.theme_actions[theme_id] = action

    def set_theme(self, theme_id):
        """Switch to a theme now and remember it for the next run."""
        self.theme = theme_id
        self.theme_actions[theme_id].setChecked(True)
        apply_theme(QApplication.instance(), THEME_DARK_FLAG[theme_id])
        self.settings.set("themeId", theme_id)

    def show_log(self):
        if self.log_window is None:
            if self.log_handler is None:
                self.log_handler = install_logging(redirect_std=False)
            self.log_window = LogWindow(self.log_handler, self)
        self.log_window.show()
        self.log_window.raise_()
        self.log_window.activateWindow()

    def _auto_connect(self):
        """Connect without a click when the choice is clear: the device used
        last time is present, or it is the only device found."""
        count = self.cb_PID.count()
        remembered = self.settings.get("lastDevice")
        index = -1
        if remembered:
            index = next((i for i in range(count) if device_id(self.cb_PID.itemData(i)) == remembered), -1)
        if index < 0 and count == 1:
            index = 0
        if index >= 0:
            self.cb_PID.setCurrentIndex(index)
            self.connect_device()

    def update_reference_position(self, x, y):
        self.crosshair_widget.setReferencePosition(x, y)

    def cleanup(self):
        # The monitor reads the device, so it stops before the device is shut down
        self.device_thread.requestInterruption()
        self.device_thread.wait()
        try:
            effects.clear()
        except Exception:
            pass
        try:
            if dev is not None:
                dev.reset_effects()
                dev.shutdown()
        except Exception:
            pass

    def update_phase_value(self, value):
        self.lab_PeriodicPhase.setText(f"{value}")

    def connect_device(self):
        global dev
        devinfo = self.cb_PID.currentData()
        if devinfo is None:
            QMessageBox.warning(
                self, "No Device Selected",
                "No device selected. Please select a device from the list.")
            return
        path = _devpath(devinfo)
        try:
            if path.startswith(DINPUT_PREFIX):
                print(f"Connecting to DirectInput device {devinfo.product_string}")
                dev = HapticEffect.open_dinput(path[len(DINPUT_PREFIX):])
            else:
                print(f"Connecting to VPforce device {devinfo.product_string}")
                # by exact path: two devices can share a PID
                dev = HapticEffect.open(
                    devinfo.vendor_id, devinfo.product_id, path=path)
            self.label_Connected.setText(f"CONNECTED: {devinfo.product_string}")
            self.label_Connected.setStyleSheet("color: green;")
            self.connected = True
            self.settings.set("lastDevice", device_id(devinfo))
        except Exception as e:
            self.label_Connected.setText("DISCONNECTED")
            self.label_Connected.setStyleSheet("color: red;")
            QMessageBox.warning(
                None, "Cannot connect to device",
                f"Unable to open device: {devinfo.product_string}\n"
                f"Error: {e}")
            return

        # Start the device monitor thread
        if not self.device_thread.isRunning():
            self.device_thread.start()

    def handle_crosshair_movement(self, x, y):
        # Handle the updated position of the moveable crosshairs
        if self.spring is None or not self.crosshair_widget.isEnabled():
            return
        # no console I/O here: this runs per mouse-move event, and a slow
        # print backlogs the event queue so the spring updates lag the drag
        logging.debug(f"New crosshair position: ({x}, {y})")
        self.cpOx = int(x * 4096)
        self.cpOy = int(y * 4096)
        self.spring_x.cpOffset = self.cpOx
        self.spring_y.cpOffset = self.cpOy
        self.spring.setCondition(self.spring_x)
        self.spring.setCondition(self.spring_y)

    # --- additive effect queue ------------------------------------------------

    def _periodic_spec(self, warn=True):
        """The periodic effect the controls describe, or None when the
        frequency or duration is empty (after a warning, if ``warn``)."""
        freq = self.txt_PeriodicFrequency.text()
        duration = self.txt_Duration.text()
        if freq == '':
            if warn:
                QMessageBox.warning(self, "Periodic Settings Error", "Please enter a valid value for the periodic frequency")
            return None
        if duration == '':
            if warn:
                QMessageBox.warning(self, "Periodic Settings Error", "Please enter a valid value for the periodic duration")
            return None
        return {
            "kind": "periodic",
            "frequency": int(freq),
            "intensity": self.spin_PeriodicIntensity.value(),
            "direction": self.dialPeriodic.value(),
            "waveform": self.bg_PeriodicType.checkedId(),
            "phase": self.slider_PeriodicPhase.value(),
            "duration": int(duration),
        }

    def _constant_spec(self):
        return {
            "kind": "constant",
            "intensity": self.spin_ConstantIntensity.value(),
            "direction": self.dialConstant.value(),
        }

    @staticmethod
    def _describe(spec):
        if spec["kind"] == "periodic":
            text = (f"{WAVEFORM_NAMES.get(spec['waveform'], 'Periodic')} {spec['frequency']} Hz, "
                    f"intensity {spec['intensity']:.3f}, direction {spec['direction']}, "
                    f"phase {spec['phase']}")
            if spec["duration"]:
                text += f", {spec['duration']} ms"
            return text
        return f"Constant, intensity {spec['intensity']:.3f}, direction {spec['direction']}"

    def _enqueue(self, spec):
        # The name is fixed when queued, so a later start can tell whether
        # this entry is already playing
        self.effect_index += 1
        spec["index"] = self.effect_index
        spec["name"] = f"{spec['kind']}_{self.effect_index}"
        spec["label"] = f"#{spec['index']} {self._describe(spec)}"
        self.queue.append(spec)
        self.list_Queue.addItem(spec["label"])

    def queue_periodic(self):
        spec = self._periodic_spec()
        if spec is not None:
            self._enqueue(spec)

    def queue_constant(self):
        self._enqueue(self._constant_spec())

    def remove_queued(self):
        rows = sorted((self.list_Queue.row(item) for item in self.list_Queue.selectedItems()), reverse=True)
        # Signals held off: mid-removal the list rows and the queue disagree
        self.list_Queue.blockSignals(True)
        try:
            for row in rows:
                self.list_Queue.takeItem(row)
                del self.queue[row]
        finally:
            self.list_Queue.blockSignals(False)
        self._queue_selection_changed()

    def clear_queue(self):
        self.list_Queue.blockSignals(True)
        try:
            self.queue.clear()
            self.list_Queue.clear()
        finally:
            self.list_Queue.blockSignals(False)
        self._queue_selection_changed()

    # --- editing a queued entry -------------------------------------------------

    def _queue_selection_changed(self):
        rows = [self.list_Queue.row(item) for item in self.list_Queue.selectedItems()]
        self._editing = self.queue[rows[0]] if len(rows) == 1 else None
        if self._editing is not None:
            self._load_spec(self._editing)
        self._show_editing()

    def _show_editing(self):
        spec = self._editing
        for kind, label in (("periodic", self.label_Periodic), ("constant", self.label_Constant)):
            text = f"<b>{kind.capitalize()}</b>"
            if spec is not None and spec["kind"] == kind:
                text += f"&nbsp;&nbsp;<span style='color:#ab37c8'>editing #{spec['index']}</span>"
            label.setText(text)

    def _load_spec(self, spec):
        self._loading = True
        try:
            if spec["kind"] == "periodic":
                self.dialPeriodic.setValue(spec["direction"])
                self.spin_PeriodicIntensity.setValue(spec["intensity"])
                self.txt_PeriodicFrequency.setText(str(spec["frequency"]))
                self.txt_Duration.setText(str(spec["duration"]))
                self.bg_PeriodicType.button(spec["waveform"]).setChecked(True)
                self.slider_PeriodicPhase.setValue(spec["phase"])
            else:
                self.dialConstant.setValue(spec["direction"])
                self.spin_ConstantIntensity.setValue(spec["intensity"])
        finally:
            self._loading = False

    def _controls_changed(self, kind):
        """Apply the controls to the queued entry being edited, and to its
        effect straight away if it is playing."""
        spec = self._editing
        if self._loading or spec is None or spec["kind"] != kind:
            return
        settings = self._periodic_spec(warn=False) if kind == "periodic" else self._constant_spec()
        if settings is None:
            return  # a frequency or duration box emptied mid-edit
        # a device effect cannot change its waveform, only be replaced
        new_waveform = kind == "periodic" and settings["waveform"] != spec["waveform"]
        spec.update(settings)
        spec["label"] = f"#{spec['index']} {self._describe(spec)}"
        row = next(i for i, queued in enumerate(self.queue) if queued is spec)
        self.list_Queue.item(row).setText(spec["label"])
        name = spec["name"]
        if not self._is_playing(name):
            return
        if new_waveform:
            self._restart(spec)
        else:
            self._apply(spec)
            self._active_rows[name][1].setText(spec["label"])

    # --- playing queued entries --------------------------------------------------

    def _is_playing(self, name):
        return name in self._active_rows and name not in self._finished

    @staticmethod
    def _apply(spec):
        """Send a queued entry's settings to its effect, creating it on first use."""
        effect = effects[spec["name"]]
        direction = spec["direction"]
        if spec["kind"] == "periodic":
            # effect_type is keyword-only in the current API: passed
            # positionally it lands in *args and is silently ignored
            effect.periodic(spec["frequency"], spec["intensity"], direction,
                            effect_type=spec["waveform"], phase=spec["phase"],
                            duration=spec["duration"])
        else:
            effect.constant(spec["intensity"], direction)
        return effect

    def _restart(self, spec):
        name = spec["name"]
        if name in effects:
            effects.dispose(name)
        self._apply(spec).start()
        self._show_active(name, spec["label"], spec.get("duration", 0))

    # --- active effects ---------------------------------------------------------

    def _show_active(self, name, text, duration_ms=0):
        """List a running effect with its own Stop button.  A singular effect
        started again updates its existing row rather than adding another."""
        self._finished.discard(name)
        entry = self._active_rows.get(name)
        if entry is None:
            item = QListWidgetItem()
            self.list_Active.addItem(item)
        else:
            item = entry[0]
        row = QWidget()
        box = QHBoxLayout(row)
        box.setContentsMargins(4, 1, 4, 1)
        # Stop first: a long description is cut off at the right edge, never the button
        stop = QPushButton("Stop")
        stop.clicked.connect(lambda _checked=False, n=name: self.stop_effect(n))
        box.addWidget(stop)
        label = QLabel(text)
        label.setToolTip(text)
        box.addWidget(label, 1)
        item.setSizeHint(row.sizeHint())
        self.list_Active.setItemWidget(item, row)
        self._active_rows[name] = (item, label)
        if duration_ms > 0:
            # A timed effect ends on the device by itself.  Its row stays, so
            # the effect can still be freed, but says it is no longer playing.
            QTimer.singleShot(duration_ms, lambda n=name, lab=label: self._mark_finished(n, lab))

    def _mark_finished(self, name, label):
        entry = self._active_rows.get(name)
        # the label identity check skips a row that was stopped or replaced
        # since the timer was set
        if entry is not None and entry[1] is label:
            self._finished.add(name)
            label.setText(label.text() + "  (finished)")

    def stop_effect(self, name):
        """Stop and free one effect, leaving the others playing."""
        effects.dispose(name)
        self._finished.discard(name)
        entry = self._active_rows.pop(name, None)
        if entry is not None:
            self.list_Active.takeItem(self.list_Active.row(entry[0]))
        if name == "spring":
            self.spring = None
            self.crosshair_widget.setDisabled(True)

    def stop_effects(self):
        # destroy AND forget: a destroyed HapticEffect must not be reused
        # from the dispenser (its lazy re-create asserts)
        effects.clear()
        self.spring = None
        # effect_index is not reset: queued entries keep the names they were given
        self._finished.clear()
        self._active_rows.clear()
        self.list_Active.clear()
        self.crosshair_widget.setDisabled(True)

    def start_effects(self):
        if not self.connected:
            QMessageBox.warning(self, "Error", "Please connect to a device")
            return
        input_data = dev.get_input()
        if input_data is not None:
            x, y = input_data.axisXY()
            self.crosshair_widget.setReferencePosition(x, y)

        # The queue is kept so it can be started again.  An entry still playing
        # is skipped; one stopped or finished is started afresh.
        for spec in self.queue:
            if not self._is_playing(spec["name"]):
                self._restart(spec)

        for name, checkbox, spin in (
                ("damper", self.cb_Damper, self.spin_DamperIntensity),
                ("inertia", self.cb_Inertia, self.spin_InertiaIntensity),
                ("friction", self.cb_Friction, self.spin_FrictionIntensity)):
            if checkbox.isChecked():
                coeff = int(spin.value() * 4096)
                getattr(effects[name], name)(coeff, coeff).start()
                self._show_active(name, f"{name.capitalize()}, intensity {spin.value():.3f}")

        if self.cb_Spring.isChecked():
            intensity = self.spin_SpringIntensity.value()
            override = self.cb_SpringOverride.isChecked()
            s_coeff = int(intensity * 4096)
            self.spring = effects["spring"].spring()
            self.spring_x.positiveCoefficient = self.spring_x.negativeCoefficient = s_coeff
            self.spring_y.positiveCoefficient = self.spring_y.negativeCoefficient = s_coeff
            self.spring.setCondition(self.spring_x)
            self.spring.setCondition(self.spring_y)
            self.spring.start(override=override)
            self.crosshair_widget.setEnabled(True)
            self._show_active("spring", f"Spring, intensity {intensity:.3f}"
                                        + (", override" if override else ""))


if __name__ == '__main__':
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
    except (AttributeError, OSError):
        pass
    app = QApplication(sys.argv)
    log_handler = install_logging()
    app.setWindowIcon(QIcon(resource_path(APP_ICON)))
    settings = Settings()
    # --darkmode and --lightmode override the saved choice, as in TelemFFB
    if '--darkmode' in sys.argv:
        theme = THEME_DARK
    elif '--lightmode' in sys.argv:
        theme = THEME_LIGHT
    else:
        theme = settings.get("themeId", THEME_SYSTEM)
        if theme not in THEME_NAMES:
            theme = THEME_SYSTEM
    apply_theme(app, THEME_DARK_FLAG[theme])
    main_window = MainWindow(settings, theme, log_handler)
    main_window.show()
    app.aboutToQuit.connect(main_window.cleanup)
    sys.exit(app.exec())
