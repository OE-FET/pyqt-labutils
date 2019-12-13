# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Sam Schott  (ss2151@cam.ac.uk)

(c) Sam Schott; This work is licensed under a Creative Commons
Attribution-NonCommercial-NoDerivs 2.0 UK: England & Wales License.

"""

from PyQt5 import QtCore, QtWidgets


from .scientific_spinbox import ScienSpinBox, ScienDSpinBox
from .list_entry_widget import FloatListWidget


class SettingsWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        """
        A widget to group settings for a scientific instrument or measurement.

        Settings are ordered on a grid with a QLabel which describes the setting on the
        left and a widget to modify the setting on the right. Currently supported fields
        are given below.
        """
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setVerticalSpacing(5)
        self.gridLayout.setColumnStretch(0, 1)  # first column has relative size 1
        self.gridLayout.setColumnStretch(1, 2)  # second column has relative size 2

    def addDoubleField(self, name, value, unit=None, limits=None):
        """
        Adds a setting to modify a float number.

        :param str name: Setting title. Will be displayed as label next to the spin box.
        :param float value: Initial value.
        :param str unit: Unit.
        :param limits: Tuple or list with maximum and minimum value.
        :return: Instance of :class:`scientific_spinbox.ScienDSpinBox`.
        """

        label = QtWidgets.QLabel(self)
        label.setText(name)

        spinbox = ScienDSpinBox(self)
        spinbox.setMinimumWidth(90)
        spinbox.setMaximumWidth(90)
        spinbox.setValue(value)
        if unit:
            spinbox.setSuffix(unit)
        if limits:
            spinbox.setRange(*limits)

        n_rows = self.gridLayout.rowCount()
        self.gridLayout.addWidget(label, n_rows, 0, 1, 1, alignment=QtCore.Qt.AlignRight)
        self.gridLayout.addWidget(spinbox, n_rows, 1, 1, 1, alignment=QtCore.Qt.AlignLeft)

        return spinbox

    def addIntField(self, name, value, unit=None, limits=None):
        """
        Adds a setting to modify an integer number.

        :param str name: Setting title. Will be displayed as label next to the spin box.
        :param int value: Initial value.
        :param str unit: Unit.
        :param limits: Tuple or list with maximum and minimum value.
        :return: Instance of :class:`scientific_spinbox.ScienSpinBox`.
        """
        label = QtWidgets.QLabel(self)
        label.setText(name)

        spinbox = ScienSpinBox(self)
        spinbox.setMinimumWidth(90)
        spinbox.setMaximumWidth(90)
        spinbox.setValue(value)
        if unit:
            spinbox.setSuffix(unit)
        if limits:
            spinbox.setRange(*limits)

        n_rows = self.gridLayout.rowCount()
        self.gridLayout.addWidget(label, n_rows, 0, 1, 1, alignment=QtCore.Qt.AlignRight)
        self.gridLayout.addWidget(spinbox, n_rows, 1, 1, 1, alignment=QtCore.Qt.AlignLeft)

        return spinbox

    def addSelectionField(self, name, choices, index=0):
        """
        Adds a setting to select a value from a combobox. Use this if you want to
        change the available choices programmatically at a later point.

        :param str name: Setting title. Will be displayed as label next to the combobox.
        :param list choices: List of strings that indicate choices.
        :param int index: Index of default choice.
        :return: Instance of :class:`PyQt5.QWidgets.QComboBox`.
        """
        label = QtWidgets.QLabel(self)
        label.setText(name)

        combobox = QtWidgets.QComboBox(self)
        combobox.setMinimumWidth(150)
        combobox.setMaximumWidth(150)
        combobox.addItems(choices)
        combobox.setCurrentIndex(index)

        n_rows = self.gridLayout.rowCount()
        self.gridLayout.addWidget(label, n_rows, 0, 1, 1, alignment=QtCore.Qt.AlignRight)
        self.gridLayout.addWidget(combobox, n_rows, 1, 1, 1, alignment=QtCore.Qt.AlignLeft)

        return combobox

    def addSelectionBoxes(self, name, choices, index=0):
        """
        Adds a setting to select values from mutually exclusive radio buttons. Use this if
        the set of choices will not change in the future. Use multiple checkboxes through
        :func:`addCheckBox` instead if you want to allow multiple choices to be selected.

        :param str name: Setting title. Will be displayed as label next to the combobox.
        :param list choices: List of strings that indicate choices.
        :param int index: Index of default choice.
        :return: Instance of :class:`PyQt5.QWidgets.QButtonGroup`.
        """
        label = QtWidgets.QLabel(self)
        label.setAlignment(QtCore.Qt.AlignTop)
        label.setText(name)

        button_group = QtWidgets.QButtonGroup(self)
        button_group.setExclusive(True)

        box = QtWidgets.QVBoxLayout()

        for choice, i in zip(choices, range(len(choices))):
            rb = QtWidgets.QRadioButton(choice, parent=self)
            rb.setChecked(index == i)
            button_group.addButton(rb)
            box.addWidget(rb)

        n_rows = self.gridLayout.rowCount()
        self.gridLayout.addWidget(label, n_rows, 0, 1, 1, alignment=QtCore.Qt.AlignRight)
        self.gridLayout.addLayout(box, n_rows, 1, 1, 1, alignment=QtCore.Qt.AlignLeft)

        return button_group

    def addListField(self, name, value_list):
        """
        Adds a setting to enter a list of values.

        :param name: Setting title. Will be displayed as label next to the entry widget.
        :param list value_list: Initial list of values.
        :return: Instance of :class:`list_entry_widget.FloatListWidget`.
        """

        label = QtWidgets.QLabel(self)
        label.setText(name)

        list_field = FloatListWidget(self)
        list_field.setMinimumWidth(150)
        list_field.setMaximumWidth(150)
        list_field.setValue(value_list)

        n_rows = self.gridLayout.rowCount()
        self.gridLayout.addWidget(label, n_rows, 0, 1, 1, alignment=QtCore.Qt.AlignRight)
        self.gridLayout.addWidget(list_field, n_rows, 1, 1, 1, alignment=QtCore.Qt.AlignLeft)

        return list_field

    def addCheckBox(self, name, checked=True):
        """
        Adds a check box setting.

        :param name: Setting title. Will be displayed to the right of the checkbox.
        :param bool checked: Initial checked state.
        :return: Instance of :class:`PyQt5.QWidgets.QCheckBox`.
        """

        checkbox = QtWidgets.QCheckBox(name, parent=self)
        checkbox.setChecked(checked)

        n_rows = self.gridLayout.rowCount()
        self.gridLayout.addWidget(checkbox, n_rows, 1, 1, 1, alignment=QtCore.Qt.AlignLeft)

        return checkbox

    def addSeparator(self, width=350):
        """
        Adds a horizontal line to separate sections.

        :param int width: Width in pixels.
        :return: Instance of :class:`PyQt5.QtWidgets.QFrame`.
        """

        h_line = QtWidgets.QFrame(self)
        h_line.setFrameShape(QtWidgets.QFrame.HLine)
        h_line.setFixedWidth(width)
        h_line.setStyleSheet("color: rgb(205, 203, 205)")

        n_rows = self.gridLayout.rowCount()
        self.gridLayout.addWidget(h_line, n_rows, 0, 1, -1, alignment=QtCore.Qt.AlignHCenter)

        return h_line
