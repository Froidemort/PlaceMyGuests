# coding=utf-8
"""Main program :
TO DO : Explanations !"""

# imports
import sys

from PyQt4 import QtGui

import Stackbar


# constants
# exception classes
# interface functions
# classes
class MainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.stack_bar = Stackbar.StackBar()


# internal functions & classes

def main():
    app = QtGui.QApplication(sys.argv)
    my_window = MainWindow()
    my_window.show()
    app.exec_()


if __name__ == '__main__':
    main()
