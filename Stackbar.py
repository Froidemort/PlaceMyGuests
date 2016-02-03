# coding=utf-8
"""Button bar which can hide button when dimensions are not sufficient to
make them appear."""

# imports
import sys
from PyQt4 import QtGui


# constants
# exception classes
# interface functions
# classes
class StackBar(QtGui.QWidget):
    def __init__(self, parent=None):
        super(StackBar, self).__init__(parent)


# internal functions & classes

def main():
    app = QtGui.QApplication(sys.argv)
    my_window = StackBar()
    my_window.show()
    app.exec_()


if __name__ == '__main__':
    main()
