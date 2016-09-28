import sys
from PyQt4 import QtCore, QtGui
from math import cos, sin, pi
from collections import OrderedDict as ordict

class GParam:
    # General parameters for graphicsScene object
    X_origin = 0.
    Y_origin = 0.
    W_scene = 1024.
    H_scene = 1024.
    # Parameters for guest graphics
    W_rect = 25.
    H_rect = 25.
    X_rect = -W_rect / 2.
    Y_rect = -W_rect / 2.
    # Color for gender of a guest
    # M : male, F : female, C : child
    dict_map_color_gender = {'M': QtCore.Qt.blue,
                             'F': QtCore.Qt.red,
                             'C': QtCore.Qt.green}
    # Parameters for table graphics
    W_table = 150.
    H_table = 150.
    X_table = -W_table / 2.
    Y_table = -H_table / 2.


class GraphicGuest(QtGui.QGraphicsItemGroup):
    def __init__(self, data=['', '', '']):
        QtGui.QGraphicsItemGroup.__init__(self)
        self.rect = QtGui.QGraphicsRectItem()
        self.text_name = QtGui.QGraphicsSimpleTextItem()
        self.text_surname = QtGui.QGraphicsSimpleTextItem()
        self.rect.setRect(GParam.X_rect, GParam.Y_rect,
                          GParam.W_rect, GParam.H_rect)
        self.text_name.setPos(GParam.X_rect, -GParam.Y_rect)
        self.text_surname.setPos(GParam.X_rect, -GParam.Y_rect + 10.)
        # Initialization with data :
        self.set_text_name(data[0])
        self.set_text_surname(data[1])
        self.set_color_gender(data[2])
        self.set_void_guest()
        # Grouping elements
        self.addToGroup(self.rect)
        self.addToGroup(self.text_name)
        self.addToGroup(self.text_surname)
        # Set this group movable
        self.setFlags(QtGui.QGraphicsItem.ItemIsMovable)

    def set_void_guest(self):
        print 'Calling set_void_guest in GraphicGuest class'
        pen = QtGui.QPen()
        pen.setStyle(QtCore.Qt.DashLine)
        self.rect.setPen(pen)

    def set_text_name(self, name):
        pen = QtGui.QPen()
        pen.setStyle(QtCore.Qt.SolidLine)
        self.rect.setPen(pen)
        self.text_name.setText(name)

    def set_text_surname(self, surname):
        pen = QtGui.QPen()
        pen.setStyle(QtCore.Qt.SolidLine)
        self.rect.setPen(pen)
        self.text_surname.setText(surname)

    def set_color_gender(self, gender):
        if gender:
            pen = QtGui.QPen()
            pen.setStyle(QtCore.Qt.SolidLine)
            self.rect.setPen(pen)
            brush = QtGui.QBrush(GParam.dict_map_color_gender[str(gender)])
            self.rect.setBrush(brush)
        else:
            brush = QtGui.QBrush(QtCore.Qt.gray)
            self.rect.setBrush(brush)


class GraphicsTable(QtGui.QGraphicsItemGroup):
    def __init__(self, data):
        QtGui.QGraphicsItemGroup.__init__(self)
        self.round = QtGui.QGraphicsEllipseItem()
        self.round.setRect(GParam.X_table, GParam.Y_table,
                           GParam.W_table, GParam.H_table)
        self.text = QtGui.QGraphicsSimpleTextItem()
        print 'data : ', data
        self.n_guest = data[1]
        self.name = data[0]
        self.set_text(self.name)
        for i in range(self.n_guest):
            g = GraphicGuest()
            g.setPos((GParam.W_table / 2. + GParam.W_rect / 2. + 5.) * cos(2 * i * pi / self.n_guest),
                     (GParam.H_table / 2. + GParam.H_rect / 2. + 5.) * sin(2 * i * pi / self.n_guest))
            g.setRotation(360. * i / self.n_guest)
            self.addToGroup(g)
        self.addToGroup(self.round)
        self.addToGroup(self.text)
        self.setFlags(QtGui.QGraphicsItem.ItemIsMovable | QtGui.QGraphicsItem.ItemIsSelectable)

    def set_void_table(self):
        pen = QtGui.QPen()
        pen.setStyle(QtCore.Qt.DashLine)
        self.round.setPen(pen)

    def set_text(self, name):
        pen = QtGui.QPen()
        pen.setStyle(QtCore.Qt.SolidLine)
        self.round.setPen(pen)
        self.text.setText(name)


class GuestModel(QtGui.QStandardItemModel):
    def __init__(self, scene, parent=None):
        QtGui.QStandardItemModel.__init__(self, parent)
        self.scene = scene
        self._data = []
        self.itemChanged.connect(self._has_changed)

    @staticmethod
    def get_data_to_graphics(l_in):
        return [i.data().toString() for i in l_in]

    @staticmethod
    def _check_and_store(arg, l_out):
        if arg:
            l_out.append(QtGui.QStandardItem(arg))
        else:
            l_out.append(QtGui.QStandardItem())

    def add_guest(self, name=None, surname=None, gender=None):
        l_out = []
        self._check_and_store(name, l_out)
        self._check_and_store(surname, l_out)
        self._check_and_store(gender, l_out)
        self.appendRow(l_out)
        data = self.get_data_to_graphics(l_out)
        g_g = GraphicGuest(data)
        l_out.append(g_g)
        # self.scene.addItem(g_g)
        self._data.append(l_out)

    def _has_changed(self, item):
        data_changed = item.data(QtCore.Qt.DisplayRole).toString()
        print 'Un item a change en', item.row(), item.column(), \
            data_changed
        if item.column() == 0:
            self._data[item.row()][3].set_text_name(data_changed)
        elif item.column() == 1:
            self._data[item.row()][3].set_text_surname(data_changed)
        elif item.column() == 2:
            self._data[item.row()][3].set_color_gender(data_changed)
        if all([self._data[item.row()][i].data(
                QtCore.Qt.DisplayRole).toString() == ''
                for i in range(3)]):
            self._data[item.row()][3].set_void_guest()


class TableModel(QtGui.QStandardItemModel):
    def __init__(self, scene, parent=None):
        QtGui.QStandardItemModel.__init__(self, parent)
        self.scene = scene
        self._data = ordict()
        self._data['root'] = ordict()
        self._placed_guest = []

    @staticmethod
    def get_graphics_to_data(l_in):
        return None

    @staticmethod
    def _check_void_guest(self, l_in):
        return all([i=='' for i in l_in])

    @staticmethod
    def _check_and_store(arg, l_out):
        if arg:
            l_out.append(QtGui.QStandardItem(arg))
        else:
            l_out.append(QtGui.QStandardItem())

    def add_table(self, name, n_guest):
        l_out = []
        self._check_and_store(name, l_out)
        self._check_and_store(n_guest, l_out)
        item = QtGui.QStandardItem(l_out[0])
        [item.appendRow([QtGui.QStandardItem('') for _ in range(3)]) for _ in range(n_guest)]
        self.appendRow([item, l_out[1]])


class TempWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        h_layout = QtGui.QHBoxLayout()
        v_layout = QtGui.QVBoxLayout()
        main_layout = QtGui.QHBoxLayout()
        # Definition of Buttons and LineEdit
        self.btn_add_guest = QtGui.QPushButton("Add guest")
        self.btn_add_table = QtGui.QPushButton("Add table")
        self.btn_add_guest.clicked.connect(self.add_guest)
        self.btn_add_table.clicked.connect(self.add_table)
        self.led = QtGui.QLineEdit()
        # Definition of the views
        self.table_view = QtGui.QTableView()
        self.graphic_view = QtGui.QGraphicsView()
        self.graphic_view.setAcceptDrops(True)
        # Definition of the models
        self.scene = QtGui.QGraphicsScene(GParam.X_origin, GParam.Y_origin,
                                          GParam.W_scene, GParam.H_scene)
        self.guest_model = GuestModel(self.scene)
        self.table_model = TableModel(self.scene)
        # Linking model to view
        self.graphic_view.setScene(self.scene)
        self.table_view.setModel(self.guest_model)
        # Adding elements to the layout
        h_layout.addWidget(self.btn_add_guest)
        h_layout.addWidget(self.btn_add_table)
        h_layout.addWidget(self.led)
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.table_view)
        main_layout.addLayout(v_layout)
        main_layout.addWidget(self.graphic_view)
        self.setLayout(main_layout)

    def add_guest(self):
        self.guest_model.add_guest()

    def add_table(self):
        print 'calling add_table from TempWidget class'
        name, n_guest, ok = NewTable.get_result()
        if ok:
            t = GraphicsTable([name, n_guest])
            self.scene.addItem(t)
            self.table_model.add_table(name, n_guest)


class NewTable(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)
        self.led = QtGui.QLineEdit()
        self.cbx = QtGui.QComboBox()
        self.cbx.addItems(['10', '12'])
        btn = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                     QtGui.QDialogButtonBox.Cancel,
                                     QtCore.Qt.Horizontal, self)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        layout.addWidget(self.led)
        layout.addWidget(self.cbx)
        layout.addWidget(btn)

    def get_name(self):
        return self.led.text()

    def get_n_guest(self):
        return int(self.cbx.currentText())

    @staticmethod
    def get_result():
        dialog = NewTable()
        result = dialog.exec_()
        return dialog.get_name(), \
               dialog.get_n_guest(), \
               result == QtGui.QDialog.Accepted


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    view = TempWidget()
    view.show()
    sys.exit(app.exec_())
