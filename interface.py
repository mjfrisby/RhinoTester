# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interface.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(502, 610)
        MainWindow.setMinimumSize(QtCore.QSize(502, 561))
        MainWindow.setMaximumSize(QtCore.QSize(502, 1000))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.cb_Periodic = QtWidgets.QCheckBox(self.centralwidget)
        self.cb_Periodic.setGeometry(QtCore.QRect(41, 81, 60, 17))
        self.cb_Periodic.setObjectName("cb_Periodic")
        self.cb_Constant = QtWidgets.QCheckBox(self.centralwidget)
        self.cb_Constant.setGeometry(QtCore.QRect(41, 204, 67, 17))
        self.cb_Constant.setObjectName("cb_Constant")
        self.cb_Friction = QtWidgets.QCheckBox(self.centralwidget)
        self.cb_Friction.setGeometry(QtCore.QRect(41, 407, 58, 17))
        self.cb_Friction.setObjectName("cb_Friction")
        self.cb_Inertia = QtWidgets.QCheckBox(self.centralwidget)
        self.cb_Inertia.setGeometry(QtCore.QRect(41, 350, 55, 17))
        self.cb_Inertia.setObjectName("cb_Inertia")
        self.layoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_2.setGeometry(QtCore.QRect(70, 370, 159, 22))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_9 = QtWidgets.QLabel(self.layoutWidget_2)
        self.label_9.setMinimumSize(QtCore.QSize(101, 0))
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_10.addWidget(self.label_9)
        self.txt_InertiaIntensity = QtWidgets.QLineEdit(self.layoutWidget_2)
        self.txt_InertiaIntensity.setMaximumSize(QtCore.QSize(50, 16777215))
        self.txt_InertiaIntensity.setObjectName("txt_InertiaIntensity")
        self.horizontalLayout_10.addWidget(self.txt_InertiaIntensity)
        self.button_Start = QtWidgets.QPushButton(self.centralwidget)
        self.button_Start.setGeometry(QtCore.QRect(40, 540, 121, 23))
        self.button_Start.setObjectName("button_Start")
        self.button_Stop = QtWidgets.QPushButton(self.centralwidget)
        self.button_Stop.setGeometry(QtCore.QRect(320, 540, 111, 23))
        self.button_Stop.setObjectName("button_Stop")
        self.cb_Damper = QtWidgets.QCheckBox(self.centralwidget)
        self.cb_Damper.setGeometry(QtCore.QRect(41, 290, 55, 17))
        self.cb_Damper.setObjectName("cb_Damper")
        self.layoutWidget_3 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_3.setGeometry(QtCore.QRect(70, 310, 159, 22))
        self.layoutWidget_3.setObjectName("layoutWidget_3")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout(self.layoutWidget_3)
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_10 = QtWidgets.QLabel(self.layoutWidget_3)
        self.label_10.setMinimumSize(QtCore.QSize(101, 0))
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_13.addWidget(self.label_10)
        self.txt_DamperIntensity = QtWidgets.QLineEdit(self.layoutWidget_3)
        self.txt_DamperIntensity.setMaximumSize(QtCore.QSize(50, 16777215))
        self.txt_DamperIntensity.setObjectName("txt_DamperIntensity")
        self.horizontalLayout_13.addWidget(self.txt_DamperIntensity)
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(10, 0, 91, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(10, 270, 91, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(70, 140, 371, 19))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.rb_Square = QtWidgets.QRadioButton(self.layoutWidget)
        self.rb_Square.setObjectName("rb_Square")
        self.bg_PeriodicType = QtWidgets.QButtonGroup(MainWindow)
        self.bg_PeriodicType.setObjectName("bg_PeriodicType")
        self.bg_PeriodicType.addButton(self.rb_Square)
        self.horizontalLayout.addWidget(self.rb_Square)
        self.rb_Sine = QtWidgets.QRadioButton(self.layoutWidget)
        self.rb_Sine.setObjectName("rb_Sine")
        self.bg_PeriodicType.addButton(self.rb_Sine)
        self.horizontalLayout.addWidget(self.rb_Sine)
        self.rb_Triangle = QtWidgets.QRadioButton(self.layoutWidget)
        self.rb_Triangle.setObjectName("rb_Triangle")
        self.bg_PeriodicType.addButton(self.rb_Triangle)
        self.horizontalLayout.addWidget(self.rb_Triangle)
        self.rb_SawtoothUp = QtWidgets.QRadioButton(self.layoutWidget)
        self.rb_SawtoothUp.setObjectName("rb_SawtoothUp")
        self.bg_PeriodicType.addButton(self.rb_SawtoothUp)
        self.horizontalLayout.addWidget(self.rb_SawtoothUp)
        self.rb_SawtoothDown = QtWidgets.QRadioButton(self.layoutWidget)
        self.rb_SawtoothDown.setObjectName("rb_SawtoothDown")
        self.bg_PeriodicType.addButton(self.rb_SawtoothDown)
        self.horizontalLayout.addWidget(self.rb_SawtoothDown)
        self.layoutWidget1 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(70, 100, 394, 35))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.dialPeriodic = QtWidgets.QDial(self.layoutWidget1)
        self.dialPeriodic.setMaximumSize(QtCore.QSize(31, 31))
        self.dialPeriodic.setMaximum(359)
        self.dialPeriodic.setProperty("value", 5)
        self.dialPeriodic.setSliderPosition(5)
        self.dialPeriodic.setWrapping(True)
        self.dialPeriodic.setObjectName("dialPeriodic")
        self.horizontalLayout_2.addWidget(self.dialPeriodic)
        self.horizontalLayout_6.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_5 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_5.setMinimumSize(QtCore.QSize(78, 0))
        self.label_5.setMaximumSize(QtCore.QSize(161, 16777215))
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_4.addWidget(self.label_5)
        self.txt_PeriodicFrequency = QtWidgets.QLineEdit(self.layoutWidget1)
        self.txt_PeriodicFrequency.setMaximumSize(QtCore.QSize(50, 16777215))
        self.txt_PeriodicFrequency.setObjectName("txt_PeriodicFrequency")
        self.horizontalLayout_4.addWidget(self.txt_PeriodicFrequency)
        self.horizontalLayout_6.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_6 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_6.setMinimumSize(QtCore.QSize(101, 0))
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_5.addWidget(self.label_6)
        self.txt_PeriodicIntensity = QtWidgets.QLineEdit(self.layoutWidget1)
        self.txt_PeriodicIntensity.setMaximumSize(QtCore.QSize(50, 16777215))
        self.txt_PeriodicIntensity.setObjectName("txt_PeriodicIntensity")
        self.horizontalLayout_5.addWidget(self.txt_PeriodicIntensity)
        self.horizontalLayout_6.addLayout(self.horizontalLayout_5)
        self.layoutWidget2 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget2.setGeometry(QtCore.QRect(70, 220, 252, 35))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_4 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.dialConstant = QtWidgets.QDial(self.layoutWidget2)
        self.dialConstant.setMaximumSize(QtCore.QSize(31, 31))
        self.dialConstant.setMaximum(359)
        self.dialConstant.setProperty("value", 5)
        self.dialConstant.setSliderPosition(5)
        self.dialConstant.setWrapping(True)
        self.dialConstant.setObjectName("dialConstant")
        self.horizontalLayout_3.addWidget(self.dialConstant)
        self.horizontalLayout_8.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_7 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_7.setMinimumSize(QtCore.QSize(101, 0))
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_7.addWidget(self.label_7)
        self.txt_ConstantIntensity = QtWidgets.QLineEdit(self.layoutWidget2)
        self.txt_ConstantIntensity.setMaximumSize(QtCore.QSize(50, 16777215))
        self.txt_ConstantIntensity.setObjectName("txt_ConstantIntensity")
        self.horizontalLayout_7.addWidget(self.txt_ConstantIntensity)
        self.horizontalLayout_8.addLayout(self.horizontalLayout_7)
        self.layoutWidget3 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget3.setGeometry(QtCore.QRect(70, 430, 159, 22))
        self.layoutWidget3.setObjectName("layoutWidget3")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.layoutWidget3)
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_8 = QtWidgets.QLabel(self.layoutWidget3)
        self.label_8.setMinimumSize(QtCore.QSize(101, 0))
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_9.addWidget(self.label_8)
        self.txt_FrictionIntensity = QtWidgets.QLineEdit(self.layoutWidget3)
        self.txt_FrictionIntensity.setMaximumSize(QtCore.QSize(50, 16777215))
        self.txt_FrictionIntensity.setObjectName("txt_FrictionIntensity")
        self.horizontalLayout_9.addWidget(self.txt_FrictionIntensity)
        self.layoutWidget4 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget4.setGeometry(QtCore.QRect(40, 20, 183, 46))
        self.layoutWidget4.setObjectName("layoutWidget4")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget4)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label = QtWidgets.QLabel(self.layoutWidget4)
        self.label.setMinimumSize(QtCore.QSize(47, 0))
        self.label.setObjectName("label")
        self.horizontalLayout_11.addWidget(self.label)
        self.text_PID = QtWidgets.QLineEdit(self.layoutWidget4)
        self.text_PID.setMinimumSize(QtCore.QSize(41, 0))
        self.text_PID.setMaximumSize(QtCore.QSize(41, 16777215))
        self.text_PID.setObjectName("text_PID")
        self.horizontalLayout_11.addWidget(self.text_PID)
        self.button_Connect = QtWidgets.QPushButton(self.layoutWidget4)
        self.button_Connect.setObjectName("button_Connect")
        self.horizontalLayout_11.addWidget(self.button_Connect)
        self.verticalLayout.addLayout(self.horizontalLayout_11)
        self.label_Connected = QtWidgets.QLabel(self.layoutWidget4)
        self.label_Connected.setObjectName("label_Connected")
        self.verticalLayout.addWidget(self.label_Connected)
        self.layoutWidget5 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget5.setGeometry(QtCore.QRect(70, 170, 334, 24))
        self.layoutWidget5.setObjectName("layoutWidget5")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout(self.layoutWidget5)
        self.horizontalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget5)
        self.label_2.setMaximumSize(QtCore.QSize(61, 16777215))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_12.addWidget(self.label_2)
        self.slider_PeriodicPhase = QtWidgets.QSlider(self.layoutWidget5)
        self.slider_PeriodicPhase.setMinimumSize(QtCore.QSize(241, 0))
        self.slider_PeriodicPhase.setMaximumSize(QtCore.QSize(241, 16777215))
        self.slider_PeriodicPhase.setMaximum(359)
        self.slider_PeriodicPhase.setOrientation(QtCore.Qt.Horizontal)
        self.slider_PeriodicPhase.setObjectName("slider_PeriodicPhase")
        self.horizontalLayout_12.addWidget(self.slider_PeriodicPhase)
        self.lab_PeriodicPhase = QtWidgets.QLabel(self.layoutWidget5)
        self.lab_PeriodicPhase.setMaximumSize(QtCore.QSize(31, 16777215))
        self.lab_PeriodicPhase.setObjectName("lab_PeriodicPhase")
        self.horizontalLayout_12.addWidget(self.lab_PeriodicPhase)
        self.cb_Spring = QtWidgets.QCheckBox(self.centralwidget)
        self.cb_Spring.setGeometry(QtCore.QRect(41, 467, 58, 17))
        self.cb_Spring.setObjectName("cb_Spring")
        self.layoutWidget_4 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_4.setGeometry(QtCore.QRect(70, 490, 235, 22))
        self.layoutWidget_4.setObjectName("layoutWidget_4")
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout(self.layoutWidget_4)
        self.horizontalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label_13 = QtWidgets.QLabel(self.layoutWidget_4)
        self.label_13.setMinimumSize(QtCore.QSize(101, 0))
        self.label_13.setObjectName("label_13")
        self.horizontalLayout_14.addWidget(self.label_13)
        self.txt_SpringIntensity = QtWidgets.QLineEdit(self.layoutWidget_4)
        self.txt_SpringIntensity.setMaximumSize(QtCore.QSize(50, 16777215))
        self.txt_SpringIntensity.setObjectName("txt_SpringIntensity")
        self.horizontalLayout_14.addWidget(self.txt_SpringIntensity)
        self.cb_SpringOverride = QtWidgets.QCheckBox(self.layoutWidget_4)
        self.cb_SpringOverride.setObjectName("cb_SpringOverride")
        self.horizontalLayout_14.addWidget(self.cb_SpringOverride)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 502, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Rhino Tester"))
        self.cb_Periodic.setText(_translate("MainWindow", "Periodic"))
        self.cb_Constant.setText(_translate("MainWindow", "Constant"))
        self.cb_Friction.setText(_translate("MainWindow", "Friction"))
        self.cb_Inertia.setText(_translate("MainWindow", "Inertia"))
        self.label_9.setText(_translate("MainWindow", "Intensity (0.0-1.0):"))
        self.button_Start.setText(_translate("MainWindow", "Start New Effect(s)"))
        self.button_Stop.setText(_translate("MainWindow", "Stop All Effects"))
        self.cb_Damper.setText(_translate("MainWindow", "Damper"))
        self.label_10.setText(_translate("MainWindow", "Intensity (0.0-1.0):"))
        self.label_11.setToolTip(_translate("MainWindow", "Additive effects will build on eachother as you start new effects"))
        self.label_11.setText(_translate("MainWindow", "Additive Effects"))
        self.label_12.setToolTip(_translate("MainWindow", "Singular effects will overwirte any previous effect setting with the new value"))
        self.label_12.setText(_translate("MainWindow", "Singular Effects"))
        self.rb_Square.setText(_translate("MainWindow", "Square"))
        self.rb_Sine.setText(_translate("MainWindow", "Sine"))
        self.rb_Triangle.setText(_translate("MainWindow", "Triangle"))
        self.rb_SawtoothUp.setText(_translate("MainWindow", "Sawtooth Up"))
        self.rb_SawtoothDown.setText(_translate("MainWindow", "Sawtooth Down"))
        self.label_3.setText(_translate("MainWindow", "Direction:"))
        self.label_5.setText(_translate("MainWindow", "Frequency (Hz):"))
        self.label_6.setText(_translate("MainWindow", "Intensity (0.0-1.0):"))
        self.label_4.setText(_translate("MainWindow", "Direction:"))
        self.label_7.setText(_translate("MainWindow", "Intensity (0.0-1.0):"))
        self.label_8.setText(_translate("MainWindow", "Intensity (0.0-1.0):"))
        self.label.setText(_translate("MainWindow", "Rhino PID:"))
        self.button_Connect.setText(_translate("MainWindow", "Connect"))
        self.label_Connected.setText(_translate("MainWindow", "DISCONNECTED"))
        self.label_2.setText(_translate("MainWindow", "Phase (deg):"))
        self.lab_PeriodicPhase.setText(_translate("MainWindow", "000"))
        self.cb_Spring.setText(_translate("MainWindow", "Spring"))
        self.label_13.setText(_translate("MainWindow", "Intensity (0.0-1.0):"))
        self.cb_SpringOverride.setText(_translate("MainWindow", "Override"))
