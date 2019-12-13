# -*- coding: utf-8 -*-
"""
@author: Sam Schott  (ss2151@cam.ac.uk)

(c) Sam Schott; This work is licensed under a Creative Commons
Attribution-NonCommercial-NoDerivs 2.0 UK: England & Wales License.

"""

from PyQt5 import QtGui, QtWidgets


class ListValidator(QtGui.QValidator):
    """
    This is a validator for a list of float values.
    """

    accepted_strings = []

    def validate(self, string, position):
        """
        This is the actual validator. It checks whether the current user input is a valid string
        every time the user types a character. There are 3 states that are possible.
        1) Invalid: The current input string is invalid. The user input will not accept the last
                    typed character.
        2) Acceptable: The user input in conform with the regular expression and will be accepted.
        3) Intermediate: The user input is not a valid string yet but on the right track. Use this
                         return value to allow the user to type fill-characters needed in order to
                         complete an expression (i.e. the decimal point of a float value).
        :param string: The current input string (from a QLineEdit for example)
        :param position: The current position of the text cursor
        :return: enum QValidator::State: the returned validator state,
                 str: the input string, int: the cursor position
        """

        string_list = string.split(',')
        validated_list = [self.validate_string(x) for x in string_list]

        if self.Invalid in validated_list:
            return self.Invalid, string, position
        elif self.Intermediate in validated_list:
            return self.Intermediate, string, position
        else:
            return self.Acceptable, string, position

    def validate_string(self, text):

        text = text.strip()
        text = text.rstrip()

        try:
            float(text)
            return self.Acceptable
        except ValueError:

            if text in ['', '-', '+']:
                return self.Intermediate

            for string in self.accepted_strings:
                if string == text:
                    return self.Acceptable
                elif string.startswith(text):
                    return self.Intermediate

            return self.Invalid


class FloatListWidget(QtWidgets.QLineEdit):

    _accepted_strings = []

    def __init__(self, *args, **kwargs):
        """"
        A QLineEdit which only allows comma separated lists to be entered. By default, the
        values must be numeric but :func:`setAcceptedStrings` allows the user to set a
        list of string values which will also be accepted.
        """
        super(FloatListWidget, self).__init__(*args, **kwargs)

        self.validator_ = ListValidator()
        self.validator_.accepted_strings = self._accepted_strings
        self.setValidator(self.validator_)

    def value(self):
        """
        Return the current list of values.

        :return: List of values.
        :rtype: list
        """
        text = self.text()
        string_list = text.split(',')

        return [self._string_to_value(x) for x in string_list]

    def setValue(self, value_list):
        """
        Set the current value.

        :param list value_list: List of values.
        """

        string_list = []

        for value in value_list:
            if value in self._accepted_strings:
                string_list.append(value)
            elif isinstance(value, float) and value.is_integer():
                string_list.append(str(int(value)))
            else:
                string_list.append(str(value))

        string = ', '.join(string_list)

        string = string.replace('  ', ' ')
        string = string.strip()

        self.setText(string)

    def acceptedStrings(self):
        """
        Returns a list of accepted strings.

        :return: List of accepted strings.
        :rtype: list
        """
        return self._accepted_strings

    def setAcceptedStrings(self, string_list):
        """
        Accepts the string given in :param:`string_list` as input values.

        :param list string_list: list of strings.
        """

        if not all([isinstance(x, str) for x in string_list]):
            raise ValueError('Input must be a list of strings.')

        self._accepted_strings = string_list
        self.validator_.accepted_strings = string_list

    def _string_to_value(self, string):
        try:
            return float(string)
        except ValueError:
            if string in self._accepted_strings:
                return string
            else:
                raise ValueError('Invalid drain voltage.')
