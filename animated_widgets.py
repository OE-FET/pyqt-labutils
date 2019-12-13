# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Sam Schott  (ss2151@cam.ac.uk)

(c) Sam Schott; This work is licensed under a Creative Commons
Attribution-NonCommercial-NoDerivs 2.0 UK: England & Wales License.

"""
# external packages
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap, QWindow


class FaderWidget(QtWidgets.QWidget):

    pixmap_opacity = 1.0

    def __init__(self, old_widget, new_widget, duration=300):
        QtWidgets.QWidget.__init__(self, new_widget)

        pr = QWindow().devicePixelRatio()
        self.old_pixmap = QPixmap(new_widget.size()*pr)
        self.old_pixmap.setDevicePixelRatio(pr)
        old_widget.render(self.old_pixmap)

        self.timeline = QtCore.QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(duration)
        self.timeline.start()

        self.resize(new_widget.size())
        self.show()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmap_opacity)
        painter.drawPixmap(0, 0, self.old_pixmap)
        painter.end()

    def animate(self, value):
        self.pixmap_opacity = 1.0 - value
        self.repaint()


class AnimatedStackedWidget(QtWidgets.QStackedWidget):
    """
    A subclass of ``QStackedWidget`` with sliding or fading animations between stacks.
    """

    def __init__(self, parent=None):
        super(AnimatedStackedWidget, self).__init__(parent)

        self.m_direction = Qt.Horizontal
        self.m_speed = 300
        self.m_animationtype = QtCore.QEasingCurve.OutCubic
        self.m_now = 0
        self.m_next = 0
        self.m_wrap = False
        self.m_pnow = QtCore.QPoint(0, 0)
        self.m_active = False

    def setDirection(self, direction):
        self.m_direction = direction

    def setSpeed(self, speed):
        self.m_speed = speed

    def setAnimation(self, animationtype):
        self.m_animationtype = animationtype

    def setWrap(self, wrap):
        self.m_wrap = wrap

    @QtCore.pyqtSlot()
    def slideInPrev(self):
        now = self.currentIndex()
        if self.m_wrap or now > 0:
            self.slideInIdx(now - 1)

    @QtCore.pyqtSlot()
    def slideInNext(self):
        now = self.currentIndex()
        if self.m_wrap or now < (self.count() - 1):
            self.slideInIdx(now + 1)

    def slideInIdx(self, idx):
        if idx > (self.count() - 1):
            idx = idx % self.count()
        elif idx < 0:
            idx = (idx + self.count()) % self.count()
        self.slideInWgt(self.widget(idx))

    def slideInWgt(self, newwidget):
        if self.m_active:
            return

        self.m_active = True

        _now = self.currentIndex()
        _next = self.indexOf(newwidget)

        if _now == _next:
            self.m_active = False
            return

        offsetx, offsety = self.frameRect().width(), self.frameRect().height()
        self.widget(_next).setGeometry(self.frameRect())

        if not self.m_direction == Qt.Horizontal:
            if _now < _next:
                offsetx, offsety = 0, -offsety
            else:
                offsetx = 0
        else:
            if _now < _next:
                offsetx, offsety = -offsetx, 0
            else:
                offsety = 0

        pnext = self.widget(_next).pos()
        pnow = self.widget(_now).pos()
        self.m_pnow = pnow

        offset = QtCore.QPoint(offsetx, offsety)
        self.widget(_next).move(pnext - offset)
        self.widget(_next).show()
        self.widget(_next).raise_()

        anim_group = QtCore.QParallelAnimationGroup(
            self, finished=self.animationDoneSlot
        )

        for index, start, end in zip((_now, _next), (pnow, pnext - offset), (pnow + offset, pnext)):
            animation = QtCore.QPropertyAnimation(
                self.widget(index),
                b"pos",
                duration=self.m_speed,
                easingCurve=self.m_animationtype,
                startValue=start,
                endValue=end,
            )
            anim_group.addAnimation(animation)

        self.m_next = _next
        self.m_now = _now
        self.m_active = True
        anim_group.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    @QtCore.pyqtSlot()
    def animationDoneSlot(self):
        self.setCurrentIndex(self.m_next)
        self.widget(self.m_now).hide()
        self.widget(self.m_now).move(self.m_pnow)
        self.m_active = False

    def fadeInIdx(self, index):
        self.fader_widget = FaderWidget(self.currentWidget(), self.widget(index),
                                        self.m_speed)
        self.setCurrentIndex(index)


class AnimatedResizeWidget(QtWidgets.QWidget):

    def adjustSize(self):
        self.animatedResize()

    def animatedResize(self, newGeometry=None, ms_time=200):
        currentGeometry = self.geometry()
        if not newGeometry:
            newSize = self._adjustedSize()
            newGeometry = QtCore.QRect(currentGeometry.topLeft(), newSize)

        self.animation = QtCore.QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(ms_time)
        self.animation.setStartValue(currentGeometry)
        self.animation.setEndValue(newGeometry)
        self.animation.start()

    def _adjustedSize(self):

        s = self.sizeHint()

        if self.isWindow():
            layout = self.layout()

            if layout:
                if layout.hasHeightForWidth():
                    s.setHeight(layout.totalHeightForWidth(s.width()))
                exp = layout.expandingDirections()
            else:
                if self.sizePolicy().hasHeightForWidth():
                    s.setHeight(self.heightForWidth(s.width()))
                exp = self.sizePolicy().expandingDirections()

            if int(exp) & QtCore.Qt.Horizontal:
                s.setWidth(max(s.width(), 200))
            if int(exp) & QtCore.Qt.Vertical:
                s.setHeight(max(s.height(), 100))

            screen = QtWidgets.QDesktopWidget().screenGeometry(self.pos())

            s.setWidth(min(s.width(), screen.width()*2/3))
            s.setHeight(min(s.height(), screen.height()*2/3))

        if not s.isValid():
            r = self.childrenRect()
            if r.isNull():
                return r
            s = r.size() + QtCore.QSize(2 * r.x(), 2 * r.y())

        return s
