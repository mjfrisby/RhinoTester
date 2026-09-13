# -*- mode: python ; coding: utf-8 -*-
# One-file build: Rhino Tester.exe carries everything it needs, including the
# Visual C++ runtime.  DirectLink is deliberately not bundled; the tester loads
# it from the location its installer records in the registry.
#
# Build with:  python -m PyInstaller "Rhino Tester.spec"
# Running PyInstaller on "Rhino Tester.py" instead overwrites this file with a
# generic one-folder spec.

import os

import PyQt6

QT_BIN = os.path.join(os.path.dirname(PyQt6.__file__), 'Qt6', 'bin')

a = Analysis(
    ['Rhino Tester.py'],
    pathex=[],
    # Both at the bundle root, which is on the DLL search path; a subfolder is not.
    # ffb_rhino loads hidapi.dll by name.  Qt's MSVCP140 delay-loads concrt140,
    # which PyQt6's hook leaves out, so without it the exe would depend on the
    # Visual C++ runtime being installed.
    binaries=[('dll/hidapi.dll', '.'),
              (os.path.join(QT_BIN, 'concrt140.dll'), '.')],
    # The window icon; the exe's own icon is set on EXE below
    datas=[('image/vpforceicon.png', 'image')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt6.QtQuick', 'PyQt6.QtQuickWidgets', 'PyQt6.QtQuick3D', 'PyQt6.QtQml', 'PyQt6.QtOpenGL',
              'PyQt6.QtTest'],
    noarchive=False,
)
# Qt and Windows libraries a widgets-only app does not use.  Matched as
# substrings of the bundled file name, so keep entries specific.  The Visual
# C++ runtime (vcruntime, msvcp, concrt) must never be listed: the exe would
# then only start where that runtime happens to be installed.  The Universal
# CRT (ucrtbase, api-ms-win-*) is part of Windows 10 and later.
exclude_bin = ["QtWebEngineProcess.exe",
               "Quick.dll",
               "QuickWidgets.dll",
               "Qt6Xml",
               "Qt6Sql",
               "PositioningQuick",
               "Qt6Positioning",
               "Qt6Bluetooth",
               "Qt6Network",
               # these two import Qt6Network; PDF images and TUIO touch are unused
               "Qt6Pdf",
               "qpdf.dll",
               "qtuiotouchplugin",
               "Qt6Test",
               "Qt6Nfc",
               "Qt6WebChannel",
               "Qt6WebSockets",
               "Qt6RemoteObjects",
               "Qt6PrintSupport",
               "Qt6TextToSpeech",
               "QmlModels",
               "Qt6Help",
               "api-ms-win",
               "ucrtbase.dll",
               "opengl32sw.dll",
               "Qt6Qml",
               "Qt6WebEngineCore.dll",
               "d3dcompiler_47.dll",
               "qsqlite.dll",
               "dbghelp.dll",
               "dbgcore.dll",
               "Qt6Sensors",
               "WebEngine",
               "Qt6Location",
               "Qt6Multimedia",
               "Qt6DBus",
               "geoservices",
               "sensorgestures",
               "dsengine",
               "qtmedia",
               "wmfengine",
               "qwebp"]

exclude_data = ["qtwebengine", "translations", "icudtl"]


def filter_bin(entry):
    keep = not any(x in entry[0] for x in exclude_bin)
    if not keep:
        print("EXCL", entry[0])
    return keep


def filter_data(entry):
    keep = not any(x in entry[0] for x in exclude_data)
    if not keep:
        print("EXCL", entry[0])
    return keep


a.binaries = list(filter(filter_bin, a.binaries))
a.datas = list(filter(filter_data, a.datas))
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Rhino Tester',
    icon='image/vpforceicon.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    # No console window: output and errors go to View > Log instead
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
