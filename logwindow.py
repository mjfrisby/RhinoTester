"""The tester's log: captured from startup and shown in View > Log.

A build without a console has nowhere else to put logging, print() output or
the traceback of an unhandled exception, so install_logging() collects all
three into a bounded history that the log window shows when it opens.
"""
import collections
import html
import logging
import sys
import threading

from PyQt6.QtCore import QEvent, QObject, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QHBoxLayout, QLabel,
    QMessageBox, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
)

LOG_FORMAT = "%(asctime)s.%(msecs)03d %(levelname)-8s %(name)s: %(message)s"
DATE_FORMAT = "%H:%M:%S"

_handler = None


class _Emitter(QObject):
    record = pyqtSignal(int, str)


class BufferedLogHandler(logging.Handler):
    """Keeps the most recent formatted records, since the log window may open
    long after they were logged, and signals each new one.  Records logged
    from other threads reach the window through Qt's queued signal delivery."""

    CAPACITY = 5000

    def __init__(self):
        super().__init__()
        self.records = collections.deque(maxlen=self.CAPACITY)
        self.emitter = _Emitter()

    def emit(self, record):
        try:
            text = self.format(record)
        except Exception:
            self.handleError(record)
            return
        self.records.append((record.levelno, text))
        self.emitter.record.emit(record.levelno, text)


class StreamToLog:
    """Stands in for sys.stdout or sys.stderr, logging each complete line."""

    encoding = "utf-8"
    _busy = threading.local()

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self._partial = ""
        self._lock = threading.Lock()

    def write(self, text):
        if getattr(self._busy, "active", False):
            # logging reporting a failure of its own; logging that would recurse
            if sys.__stderr__ is not None:
                sys.__stderr__.write(text)
            return len(text)
        self._busy.active = True
        try:
            with self._lock:
                lines = (self._partial + text).split("\n")
                self._partial = lines.pop()
            for line in lines:
                if line.strip():
                    self.logger.log(self.level, line.rstrip())
        finally:
            self._busy.active = False
        return len(text)

    def flush(self):
        pass

    def isatty(self):
        return False


def _log_unhandled(exc_type, exc, tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc, tb)
        return
    logging.getLogger("unhandled").critical("Unhandled exception", exc_info=(exc_type, exc, tb))


def install_logging(redirect_std=True, level=logging.INFO):
    """Route logging to the log window's history, and to the console when
    there is one.  Safe to call again; later calls return the same handler.

    With ``redirect_std``, print() output and anything written to stderr are
    logged too.  Unhandled exceptions are always logged; with this hook in
    place PyQt reports an exception raised in a slot instead of aborting.
    Call after the QApplication exists.
    """
    global _handler
    if _handler is not None:
        return _handler
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    root = logging.getLogger()
    # A module-level logging.info() before this point adds a default stderr
    # handler.  Without a console that handler has no stream, and each failed
    # write would put a "Logging error" traceback into the log.
    for existing in list(root.handlers):
        root.removeHandler(existing)
    root.setLevel(level)
    _handler = BufferedLogHandler()
    _handler.setFormatter(formatter)
    root.addHandler(_handler)
    # The original stream, not sys.stderr: that may be redirected into logging below
    if sys.__stderr__ is not None:
        console = logging.StreamHandler(sys.__stderr__)
        console.setFormatter(formatter)
        root.addHandler(console)
    if redirect_std:
        sys.stdout = StreamToLog(logging.getLogger("stdout"), logging.INFO)
        sys.stderr = StreamToLog(logging.getLogger("stderr"), logging.ERROR)
    sys.excepthook = _log_unhandled
    return _handler


class LogWindow(QWidget):
    """Records since startup and new ones as they arrive, with a level filter,
    copy, save and clear."""

    LEVELS = (("Debug", logging.DEBUG), ("Info", logging.INFO),
              ("Warning", logging.WARNING), ("Error", logging.ERROR))

    def __init__(self, handler, parent=None):
        super().__init__(parent, Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        self.setWindowTitle("Rhino Tester Log")
        self.resize(900, 450)
        self.handler = handler

        self.level_box = QComboBox()
        for name, level in self.LEVELS:
            self.level_box.addItem(name, level)
        self.level_box.setCurrentIndex(self.level_box.findData(logging.INFO))
        self.follow = QCheckBox("Follow new messages")
        self.follow.setChecked(True)
        copy_button = QPushButton("Copy All")
        save_button = QPushButton("Save…")
        clear_button = QPushButton("Clear")

        self.view = QPlainTextEdit()
        self.view.setReadOnly(True)
        self.view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.view.setMaximumBlockCount(handler.CAPACITY)
        font = QFont("Consolas")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFixedPitch(True)
        self.view.setFont(font)

        bar = QHBoxLayout()
        bar.addWidget(QLabel("Show:"))
        bar.addWidget(self.level_box)
        bar.addStretch(1)
        bar.addWidget(self.follow)
        bar.addWidget(copy_button)
        bar.addWidget(save_button)
        bar.addWidget(clear_button)
        layout = QVBoxLayout(self)
        layout.addLayout(bar)
        layout.addWidget(self.view)

        self.level_box.currentIndexChanged.connect(self._level_changed)
        copy_button.clicked.connect(self.copy_all)
        save_button.clicked.connect(self._save_clicked)
        clear_button.clicked.connect(self.clear)

        # Under the handler's lock, so no record lands between the history and the connection
        handler.acquire()
        try:
            self._render()
            handler.emitter.record.connect(self._append)
        finally:
            handler.release()

    def min_level(self):
        return self.level_box.currentData()

    def _level_changed(self):
        # Debug records are only captured while asked for; some are logged per mouse move
        logging.getLogger().setLevel(logging.DEBUG if self.min_level() <= logging.DEBUG else logging.INFO)
        self._render()

    def _color(self, level):
        palette = self.palette()
        dark = palette.color(QPalette.ColorRole.Window).lightness() < 128
        if level >= logging.ERROR:
            return "#ff6b6b" if dark else "#a02020"
        if level >= logging.WARNING:
            return "#e5b454" if dark else "#8a5a00"
        if level < logging.INFO:
            return "#8c8c8c" if dark else "#6e6e6e"
        return palette.color(QPalette.ColorRole.Text).name()

    def _insert(self, level, text):
        body = html.escape(text).replace("\n", "<br>")
        self.view.appendHtml(f'<span style="white-space:pre; color:{self._color(level)};">{body}</span>')

    def _render(self):
        self.view.clear()
        for level, text in list(self.handler.records):
            if level >= self.min_level():
                self._insert(level, text)
        bar = self.view.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _append(self, level, text):
        if level < self.min_level():
            return
        self._insert(level, text)
        if self.follow.isChecked():
            bar = self.view.verticalScrollBar()
            bar.setValue(bar.maximum())

    def copy_all(self):
        QApplication.clipboard().setText(self.view.toPlainText())

    def save_to(self, path):
        """Write every captured record, whatever the filter shows."""
        with open(path, "w", encoding="utf-8") as fh:
            for _level, text in list(self.handler.records):
                fh.write(text + "\n")

    def _save_clicked(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Log", "rhino-tester.log",
                                              "Log files (*.log *.txt);;All files (*)")
        if not path:
            return
        try:
            self.save_to(path)
        except OSError as exc:
            QMessageBox.warning(self, "Save Log", f"Could not save the log:\n{exc}")

    def clear(self):
        self.handler.acquire()
        try:
            self.handler.records.clear()
        finally:
            self.handler.release()
        self.view.clear()

    def changeEvent(self, event):
        # Level colors follow the theme
        if event.type() in (QEvent.Type.PaletteChange, QEvent.Type.ApplicationPaletteChange) \
                and hasattr(self, "view"):
            self._render()
        super().changeEvent(event)
