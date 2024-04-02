import sys

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QValidator
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QWidget, QRadioButton, QButtonGroup, QMessageBox

from interface import Ui_MainWindow
import utils
from typing import List, Dict
from ffb_rhino import HapticEffect
global dev

EFFECT_SQUARE = 3
EFFECT_SINE = 4
EFFECT_TRIANGLE = 5
EFFECT_SAWTOOTHUP = 6
EFFECT_SAWTOOTHDOWN = 7

effects: Dict[str, HapticEffect] = utils.Dispenser(HapticEffect)
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_ui()

        self.connected = False
        self.effect_index = 0

        # self.effects = {}

    def init_ui(self):
        self.label_Connected.setStyleSheet("color: red;")

        int_validator = QIntValidator()
        float_validator = QDoubleValidator(0.0,1.0, 3)
        float_validator.setNotation(QDoubleValidator.StandardNotation)
        self.bg_PeriodicType.setId(self.rb_Square, EFFECT_SQUARE)
        self.bg_PeriodicType.setId(self.rb_Sine, EFFECT_SINE)
        self.bg_PeriodicType.setId(self.rb_Triangle, EFFECT_TRIANGLE)
        self.bg_PeriodicType.setId(self.rb_SawtoothUp, EFFECT_SAWTOOTHUP)
        self.bg_PeriodicType.setId(self.rb_SawtoothDown, EFFECT_SAWTOOTHDOWN)
        self.rb_Sine.setChecked(True)


        self.text_PID.setValidator(int_validator)
        self.txt_PeriodicFrequency.setValidator(int_validator)
        self.txt_PeriodicFrequency.setValidator(int_validator)

        self.txt_PeriodicIntensity.setValidator(float_validator)
        self.txt_PeriodicIntensity.textChanged.connect(self.check_float)

        self.txt_ConstantIntensity.setValidator(float_validator)
        self.txt_ConstantIntensity.textChanged.connect(self.check_float)

        self.txt_DamperIntensity.setValidator(float_validator)
        self.txt_DamperIntensity.textChanged.connect(self.check_float)

        self.txt_InertiaIntensity.setValidator(float_validator)
        self.txt_InertiaIntensity.textChanged.connect(self.check_float)

        self.txt_FrictionIntensity.setValidator(float_validator)
        self.txt_FrictionIntensity.textChanged.connect(self.check_float)

        self.txt_SpringIntensity.setValidator(float_validator)
        self.txt_SpringIntensity.textChanged.connect(self.check_float)

        self.button_Connect.clicked.connect(self.connect_rhino)
        self.button_Start.clicked.connect(self.start_effects)
        self.button_Stop.clicked.connect(self.stop_effects)



        self.dialConstant.setValue(0)
        self.dialPeriodic.setValue(0)
        self.text_PID.setText("2055")
        self.txt_PeriodicFrequency.setText("10")
        self.txt_PeriodicIntensity.setText("0.15")
        self.slider_PeriodicPhase.setValue(0)
        self.lab_PeriodicPhase.setText("0")
        self.slider_PeriodicPhase.valueChanged.connect(self.update_phase_value)

        self.txt_ConstantIntensity.setText("0.5")
        self.txt_DamperIntensity.setText("0.5")
        self.txt_InertiaIntensity.setText("0.85")
        self.txt_FrictionIntensity.setText("0.5")
        self.txt_SpringIntensity.setText("0.5")

    def cleanup(self):
        # effects.foreach(lambda e: e.destroy())
        dev.resetEffects()

    def update_phase_value(self, value):
        self.lab_PeriodicPhase.setText(f"{value}")
    def check_float(self, text):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(text, 0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = 'white'
            sender.setStyleSheet('QLineEdit { background-color: %s }' % color)
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a'  # yellow
            sender.setStyleSheet('QLineEdit { background-color: %s }' % color)
        else:
            color = '#f6989d'  # red
            sender.setStyleSheet('QLineEdit { background-color: %s }' % color)

    def validate_float(self, widg):
        sender = widg
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state != QtGui.QValidator.Acceptable:
            return False
        else:
            return True

    def stop_button_clicked(self):
        """Placeholder function for the 'Stop' button."""
        self.effects["constant_force"].stop()
        # Replace this with your actual functionality
        print("Stop button pressed")

    def worker_finished(self):
        """Function to be executed when the worker thread finishes."""
        print("Worker thread finished")

    # def init_effects_dispenser(self):
    #     self.effects: Dict[str, HapticEffect] = utils.Dispenser(HapticEffect)

    def connect_rhino(self):
        global dev
        pid = self.text_PID.text()
        vid_pid = f"FFFF:{pid}"
        print(vid_pid)
        vid_pid = [int(x, 16) for x in vid_pid.split(":")]
        try:
            print("Connecting to Rhino")
            dev = HapticEffect.open(vid_pid[0], vid_pid[1])  # try to open RHINO
            # dev.resetEffects()
            self.label_Connected.setText("CONNECTED")
            self.label_Connected.setStyleSheet("color: green;")
            self.connected = True
            # self.button_Connect.setText("Disconnect")
            # self.button_Connect.clicked.connect(self.connect_rhino)
        except Exception as e:
            self.label_Connected.setText("DISCONNECTED")
            self.label_Connected.setStyleSheet("color: red;")
            QMessageBox.warning(None, "Cannot connect to Rhino", f"Unable to open device: {vid_pid}\nError: {e}\n\nPlease open the System Settings and verify the Master\ndevice PID is configured correctly")

    def stop_effects(self):
        effects.foreach(lambda e: e.destroy())
        self.effect_index = 0

    def start_effects(self):
        if not self.connected:
            QMessageBox.warning(self, "Error", "Please connect to a Rhino Device")
            return

        p_enabled = self.cb_Periodic.isChecked()
        if p_enabled:
            p_dir = self.dialPeriodic.value()
            p_freq = self.txt_PeriodicFrequency.text()
            p_phase = self.slider_PeriodicPhase.value()
            p_type = self.bg_PeriodicType.checkedId()

            if p_freq == '':
                QMessageBox.warning(self, "Periodic Settings Error", "Please enter a valid value for the periodic frequency")
                return
            p_intensity = self.txt_PeriodicIntensity.text()
            if p_intensity == '' or not self.validate_float(self.txt_PeriodicIntensity):
                QMessageBox.warning(self, "Periodic Settings Error", "Please enter a valid value for the periodic intensity")
                return
            self.effect_index += 1
            p_dir = int(p_dir)
            p_freq = int(p_freq)
            p_phase = int(p_phase)
            p_type = int(p_type)
            p_intensity = float(p_intensity)

            effects[f'periodic_{self.effect_index}'].periodic(p_freq, p_intensity, p_dir, p_type, phase=p_phase).start()

        c_enabled = self.cb_Constant.isChecked()
        if c_enabled:
            c_dir = self.dialConstant.value()
            c_intensity = self.txt_ConstantIntensity.text()
            if c_intensity == '' or not self.validate_float(self.txt_ConstantIntensity):
                QMessageBox.warning(self, "Constant Force Settings Error", "Please enter a valid value for the constant force intensity")
                return
            c_dir = int(c_dir)
            c_intensity = float(c_intensity)
            self.effect_index += 1
            effects[f'constant_{self.effect_index}'].constant(c_intensity, c_dir).start()

        d_enabled = self.cb_Damper.isChecked()
        if d_enabled:
            d_intensity = self.txt_DamperIntensity.text()
            if d_intensity == '' or not self.validate_float(self.txt_DamperIntensity):
                QMessageBox.warning(self, "Damper Force Settings Error", "Please enter a valid value for the damper force intensity")
                return
            d_intensity = float(d_intensity)
            d_coeff = int(d_intensity * 4096)
            self.effect_index += 1
            effects[f"damper_{self.effect_index}"].damper(d_coeff, d_coeff).start()

        i_enabled = self.cb_Inertia.isChecked()
        if i_enabled:
            i_intensity = self.txt_InertiaIntensity.text()
            if i_intensity == '' or not self.validate_float(self.txt_InertiaIntensity):
                QMessageBox.warning(self, "Inertia Force Settings Error", "Please enter a valid value for the inertia force intensity")
                return
            i_intensity = float(i_intensity)
            i_coeff = int(i_intensity*4096)
            effects["inertia"].inertia(i_coeff, i_coeff).start()

        f_enabled = self.cb_Friction.isChecked()
        if f_enabled:
            f_intensity = self.txt_FrictionIntensity.text()
            if f_intensity == '' or not self.validate_float(self.txt_FrictionIntensity):
                QMessageBox.warning(self, "Friction Force Settings Error", "Please enter a valid value for the friction force intensity")
                return
            f_intensity = float(f_intensity)
            f_coeff = int(f_intensity*4096)
            effects["friction"].friction(f_coeff, f_coeff).start()

        s_enabled = self.cb_Spring.isChecked()
        if s_enabled:
            s_intensity = self.txt_SpringIntensity.text()
            s_ovd = self.cb_SpringOverride.isChecked()
            if s_intensity == '' or not self.validate_float(self.txt_SpringIntensity):
                QMessageBox.warning(self, "Spring Force Settings Error", "Please enter a valid value for the spring force intensity")
                return
            s_intensity = float(s_intensity)
            s_coeff = int(s_intensity*4096)
            effects['spring'].spring(s_coeff, s_coeff).start(override=s_ovd)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.aboutToQuit.connect(main_window.cleanup)
    sys.exit(app.exec_())
