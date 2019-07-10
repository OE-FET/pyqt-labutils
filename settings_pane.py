# -*- coding: utf-8 -*-
"""
@author: Sam Schott  (ss2151@cam.ac.uk)

(c) Sam Schott; This work is licensed under a Creative Commons
Attribution-NonCommercial-NoDerivs 2.0 UK: England & Wales License.

"""

from __future__ import division, print_function, absolute_import
from qtpy import QtCore, QtWidgets


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

    def addDoubleField(self, name, value, unit=None, limits=None):
        """
        Adds a setting to modify a decimal number.

        :param str name: Setting title. Will be displayed as label next to the spin box.
        :param float value: Initial value.
        :param str unit: Unit.
        :param limits: Tuple or list with maximum and minimum value.
        :return: Instance of :class:`scientific_spinbox.ScienDSpinBox`.
        """

        label = QtWidgets.QLabel(self)
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        label.setText(name)

        spinbox = ScienDSpinBox(self)
        spinbox.setMinimumWidth(90)
        spinbox.setMaximumWidth(90)
        spinbox.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        spinbox.setValue(value)
        if unit:
            spinbox.setSuffix(unit)
        if limits:
            spinbox.setRange(*limits)

        n_rows = self.gridLayout.rowCount()

        self.gridLayout.addWidget(label, n_rows, 0, 1, 1)
        self.gridLayout.addWidget(spinbox, n_rows, 1, 1, 1)

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
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        label.setText(name)

        spinbox = ScienSpinBox(self)
        spinbox.setMinimumWidth(90)
        spinbox.setMaximumWidth(90)
        spinbox.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        spinbox.setValue(value)
        if unit:
            spinbox.setSuffix(unit)
        if limits:
            spinbox.setRange(*limits)

        n_rows = self.gridLayout.rowCount()

        self.gridLayout.addWidget(label, n_rows, 0, 1, 1)
        self.gridLayout.addWidget(spinbox, n_rows, 1, 1, 1)

        return spinbox

    def addSelectionField(self, name, choices, index=0):
        """
        Adds a setting to select a value from a combobox.

        :param str name: Setting title. Will be displayed as label next to the combobox.
        :param list choices: List of strings that indicate choices.
        :param int index: Default choice.
        :return: Instance of :class:`PyQt5.QWidgets.QComboBox`.
        """
        label = QtWidgets.QLabel(self)
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        label.setText(name)

        combobox = QtWidgets.QComboBox(self)
        combobox.setMinimumWidth(150)
        combobox.setMaximumWidth(150)
        combobox.addItems(choices)
        combobox.setCurrentIndex(index)

        n_rows = self.gridLayout.rowCount()

        self.gridLayout.addWidget(label, n_rows, 0, 1, 1)
        self.gridLayout.addWidget(combobox, n_rows, 1, 1, 2)

        return combobox

    def addListField(self, name, value_list):
        """
        Adds a setting to enter a list of values.

        :param name: Setting title. Will be displayed as label next to the entry widget.
        :param list value_list: Initial list of values.
        :return: Instance of :class:`list_entry_widget.FloatListWidget`.
        """

        label = QtWidgets.QLabel(self)
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        label.setText(name)

        list_field = FloatListWidget(self)
        list_field.setMinimumWidth(150)
        list_field.setMaximumWidth(150)
        list_field.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        list_field.setValue(value_list)

        n_rows = self.gridLayout.rowCount()

        self.gridLayout.addWidget(label, n_rows, 0, 1, 1)
        self.gridLayout.addWidget(list_field, n_rows, 1, 1, 2)

        return list_field
