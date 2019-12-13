# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 16:23:13 2018

@author: samschott
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QBrush, QImage, QPainter, QPixmap, QWindow


_USER_DIALOG_ICON_SIZE = 70


def elide_string(string, font=None, pixels=200, side="right"):
    """
    Elides a string to fit into the given width.

    :param str string: String to elide.
    :param font: Font to calculate size. If not given, the current style's default font
        for a QLabel is used.
    :param int pixels: Maximum width in pixels.
    :param str side: Side to truncate. Can be "right" or "left", defaults to "right".
    :return: Truncated string.
    :rtype: str
    """

    if not font:
        font = QtWidgets.QLabel().font()

    metrics = QtGui.QFontMetrics(font)
    mode = Qt.ElideRight if side is "right" else Qt.ElideLeft

    return metrics.elidedText(string, mode, pixels)


def get_scaled_font(scaling=1.0, bold=False, italic=False):
    """
    Returns the current style's default font for a QLabel but scaled by the given factor.

    :param float scaling: Scaling factor.
    :param bool bold: Sets the returned font to bold (defaults to ``False``)
    :param bool italic: Sets the returned font to italic (defaults to ``False``)
    :return: `QFont`` instance.
    """
    label = QtWidgets.QLabel()
    font = label.font()
    font.setBold(bold)
    font.setItalic(italic)
    font_size = round(font.pointSize()*scaling)
    # noinspection PyTypeChecker
    font.setPointSize(font_size)

    return font


def icon_to_pixmap(icon, width, height=None):
    """Converts a given icon to a pixmap. Automatically adjusts to high-DPI scaling.

    :param icon: Icon to convert.
    :param int width: Target point height.
    :param int height: Target point height.
    :return: ``QPixmap`` instance.
    """
    if not height:
        height = width

    is_hidpi = QtCore.QCoreApplication.testAttribute(Qt.AA_UseHighDpiPixmaps)
    pr = QWindow().devicePixelRatio()

    if not is_hidpi:
        width = width*pr
        height = height*pr
    px = icon.pixmap(width, height)
    if not is_hidpi:
        px.setDevicePixelRatio(pr)

    return px


class Worker(QtCore.QObject):
    """A worker object. To be used in QThreads."""

    sig_done = QtCore.pyqtSignal(object)

    def __init__(self, target=None, args=None, kwargs=None):
        QtCore.QObject.__init__(self)
        self._target = target
        self._args = args or ()
        self._kwargs = kwargs or {}

    def start(self):
        res = self._target(*self._args, **self._kwargs)
        self.sig_done.emit(res)


class BackgroundTask(QtCore.QObject):
    """A utility class to manage a worker thread."""

    sig_done = QtCore.pyqtSignal(object)

    def __init__(self, parent=None, target=None, args=None, kwargs=None, autostart=True):
        QtCore.QObject.__init__(self, parent)
        self._target = target
        self._args = args or ()
        self._kwargs = kwargs or {}

        if autostart:
            self.start()

    def start(self):

        self.thread = QtCore.QThread(self)
        self.worker = Worker(target=self._target, args=self._args, kwargs=self._kwargs)
        self.worker.sig_done.connect(self.sig_done.emit)
        self.worker.sig_done.connect(self.thread.quit)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.start)
        self.thread.start()

    def wait(self, timeout=None):
        if timeout:
            self.thread.wait(msecs=timeout)
        else:
            self.thread.wait()


class BackgroundTaskProgressDialog(QtWidgets.QDialog):
    """A progress dialog to show during long-running background tasks."""

    def __init__(self, icon, title, message="", cancel=True, parent=None, width=450, icon_size=_USER_DIALOG_ICON_SIZE):
        super(self.__class__, self).__init__(parent=parent)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Sheet | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("")
        self.setFixedWidth(width)

        self.gridLayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridLayout)

        self.iconLabel = QtWidgets.QLabel(self)
        self.titleLabel = QtWidgets.QLabel(self)
        self.infoLabel = QtWidgets.QLabel(self)
        self.progressBar = QtWidgets.QProgressBar()
        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel)

        self.iconLabel.setMinimumSize(icon_size, icon_size)
        self.iconLabel.setMaximumSize(icon_size, icon_size)
        self.iconLabel.setAlignment(Qt.AlignTop)
        self.titleLabel.setFont(get_scaled_font(bold=True))
        self.infoLabel.setFont(get_scaled_font(scaling=0.9))
        self.infoLabel.setFixedWidth(width-150)
        self.infoLabel.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.infoLabel.setWordWrap(True)
        self.infoLabel.setOpenExternalLinks(True)

        self.iconLabel.setPixmap(icon_to_pixmap(icon, icon_size))
        self.titleLabel.setText(title)
        self.infoLabel.setText(message)

        self.buttonBox.rejected.connect(self.reject)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)

        self.gridLayout.addWidget(self.iconLabel, 0, 0, 3, 1)
        self.gridLayout.addWidget(self.titleLabel, 0, 1, 1, 1)

        if message:
            self.gridLayout.addWidget(self.infoLabel, 1, 1, 1, 1)
            self.gridLayout.addWidget(self.progressBar, 2, 1, 1, 1)
        else:
            self.gridLayout.addWidget(self.progressBar, 1, 1, 1, 1)

        if message and cancel:
            self.gridLayout.addWidget(self.buttonBox, 3, 1, -1, -1)
        elif cancel:
            self.gridLayout.addWidget(self.buttonBox, 2, 1, -1, -1)

        self.adjustSize()


class UserDialog(QtWidgets.QDialog):
    """A template user dialog. Shows a traceback if given in constructor."""

    def __init__(self, icon, title, message, details=None, parent=None, icon_size=_USER_DIALOG_ICON_SIZE):
        super(self.__class__, self).__init__(parent=parent)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Sheet | Qt.WindowTitleHint |
                            Qt.CustomizeWindowHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("")
        width = 550 if details else 450
        self.setFixedWidth(width)

        self.gridLayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridLayout)

        self.iconLabel = QtWidgets.QLabel(self)
        self.titleLabel = QtWidgets.QLabel(self)
        self.infoLabel = QtWidgets.QLabel(self)

        self.iconLabel.setMinimumSize(icon_size, icon_size)
        self.iconLabel.setMaximumSize(icon_size, icon_size)
        self.titleLabel.setFont(get_scaled_font(bold=True))
        self.infoLabel.setFont(get_scaled_font(scaling=0.9))
        self.infoLabel.setFixedWidth(width-150)
        self.infoLabel.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                     QtWidgets.QSizePolicy.MinimumExpanding)
        self.infoLabel.setWordWrap(True)
        self.infoLabel.setOpenExternalLinks(True)

        self.iconLabel.setPixmap(icon_to_pixmap(icon, icon_size))
        self.titleLabel.setText(title)
        self.infoLabel.setText(message)

        if details:
            self.details = QtWidgets.QTextBrowser(self)
            self.details.setText("".join(details))
            self.details.setOpenExternalLinks(True)

        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)

        self.gridLayout.addWidget(self.iconLabel, 0, 0, 2, 1)
        self.gridLayout.addWidget(self.titleLabel, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.infoLabel, 1, 1, 1, 1)
        if details:
            self.gridLayout.addWidget(self.details, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.buttonBox, 3, 1, -1, -1)

        self.adjustSize()

    def setAcceptButtonName(self, name):
        self.buttonBox.buttons()[0].setText(name)

    def addCancelButton(self, name="Cancel"):
        self._cancelButton = self.buttonBox.addButton(QtWidgets.QDialogButtonBox.Cancel)
        self._cancelButton.setText(name)
        self._cancelButton.clicked.connect(self.close)

    def setCancelButtonName(self, name):
        self._cancelButton.setText(name)

    def addSecondAcceptButton(self, name, icon="dialog-ok"):
        self._acceptButton2 = self.buttonBox.addButton(QtWidgets.QDialogButtonBox.Ignore)
        self._acceptButton2.setText(name)
        if isinstance(icon, QtGui.QIcon):
            self._acceptButton2.setIcon(icon)
        elif isinstance(icon, str):
            self._acceptButton2.setIcon(QtGui.QIcon.fromTheme(icon))
        self._acceptButton2.clicked.connect(lambda: self.setResult(2))
        self._acceptButton2.clicked.connect(self.close)

    def setSecondAcceptButtonName(self, name):
        self._acceptButton2.setText(name)


def get_masked_image(path, size=64, overlay_text=""):
    """
    Returns a ``QPixmap`` from an image file masked with a smooth circle.
    The returned pixmap will have a size of *size* × *size* pixels.

    :param str path: Path to image file.
    :param int size: Target size. Will be the diameter of the masked image.
    :param overlay_text: Overlay text. This will be shown in white sans-serif on top of
        the image.
    :return: `QPixmap`` instance.
    """

    with open(path, "rb") as f:
        imgdata = f.read()

    imgtype = path.split(".")[-1]

    # Load image and convert to 32-bit ARGB (adds an alpha channel):
    image = QImage.fromData(imgdata, imgtype)
    image.convertToFormat(QImage.Format_ARGB32)

    # Crop image to a square:
    imgsize = min(image.width(), image.height())
    rect = QRect(
        (image.width() - imgsize) / 2,
        (image.height() - imgsize) / 2,
        imgsize,
        imgsize,
    )
    image = image.copy(rect)

    # Create the output image with the same dimensions and an alpha channel
    # and make it completely transparent:
    out_img = QImage(imgsize, imgsize, QImage.Format_ARGB32)
    out_img.fill(Qt.transparent)

    # Create a texture brush and paint a circle with the original image onto
    # the output image:
    brush = QBrush(image)        # Create texture brush
    painter = QPainter(out_img)  # Paint the output image
    painter.setBrush(brush)      # Use the image texture brush
    painter.setPen(Qt.NoPen)     # Don't draw an outline
    painter.setRenderHint(QPainter.Antialiasing, True)  # Use AA
    painter.drawEllipse(0, 0, imgsize, imgsize)  # Actually draw the circle

    if overlay_text:
        # draw text
        font = QtGui.QFont("Arial Rounded MT Bold")
        font.setPointSize(imgsize * 0.4)
        painter.setFont(font)
        painter.setPen(Qt.white)
        painter.drawText(QRect(0, 0, imgsize, imgsize), Qt.AlignCenter, overlay_text)

    painter.end()                # We are done (segfault if you forget this)

    # Convert the image to a pixmap and rescale it.  Take pixel ratio into
    # account to get a sharp image on retina displays:
    pr = QWindow().devicePixelRatio()
    pm = QPixmap.fromImage(out_img)
    pm.setDevicePixelRatio(pr)
    size *= pr
    pm = pm.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    return pm
