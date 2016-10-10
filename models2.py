import pickle
import inspect
import sys
from math import cos, sin, pi
from PyQt4 import QtCore, QtGui


def display_warning(title, message):
    error = QtGui.QMessageBox()
    error.setWindowTitle(title)
    error.setText(message)
    error.setIcon(QtGui.QMessageBox.Warning)
    error.exec_()


class GParam:
    # General parameters for graphicsScene object
    X_origin = 0.
    Y_origin = 0.
    W_scene = 2000.
    H_scene = 2000.
    rect_scene = QtCore.QRectF(X_origin, Y_origin, W_scene, H_scene)
    # Parameters for guest graphics
    W_rect = 25.
    H_rect = 25.
    X_rect = -W_rect / 2.
    Y_rect = -W_rect / 2.
    # Color for gender of a guest
    # M : male, F : female, C : child
    dict_map_color_gender = {'normal': {'': QtCore.Qt.gray,
                                        'M': QtCore.Qt.cyan,
                                        'F': QtCore.Qt.magenta,
                                        'C': QtCore.Qt.yellow},
                             'hovered': {'': QtCore.Qt.darkGray,
                                         'M': QtCore.Qt.darkCyan,
                                         'F': QtCore.Qt.darkMagenta,
                                         'C': QtCore.Qt.darkYellow}}
    # Parameters for table graphics
    W_table = 150.
    H_table = 150.
    X_table = -W_table / 2.
    Y_table = -H_table / 2.
    delta_chair = 5.
    W_tot_table = 2. * (W_rect + delta_chair) + W_table
    H_tot_table = 2. * (H_rect + delta_chair) + H_table

    def __init__(self):
        pass


class GraphicGuest(QtGui.QGraphicsItemGroup):
    def __init__(self, name='', surname='', gender=''):
        QtGui.QGraphicsItemGroup.__init__(self)
        self.gender = gender
        self.rect = QtGui.QGraphicsRectItem()
        # Accept hover event to color it darker.
        self.rect.setAcceptHoverEvents(True)
        self.text_name = QtGui.QGraphicsSimpleTextItem()
        self.text_surname = QtGui.QGraphicsSimpleTextItem()
        self.rect.setRect(GParam.X_rect, GParam.Y_rect,
                          GParam.W_rect, GParam.H_rect)
        self.text_name.setPos(GParam.X_rect, -GParam.Y_rect)
        self.text_surname.setPos(GParam.X_rect, -GParam.Y_rect + 10.)
        # Initialization with data :
        self.set_void_guest()
        self.set_text_name(name)
        self.set_text_surname(surname)
        self.set_color_gender(gender)
        # Grouping elements
        self.addToGroup(self.rect)
        self.addToGroup(self.text_name)
        self.addToGroup(self.text_surname)

    def set_void_guest(self, value=True):
        if value:
            pen = QtGui.QPen()
            pen.setStyle(QtCore.Qt.DashLine)
            self.rect.setPen(pen)
        else:
            'on passe la'
            pen = QtGui.QPen()
            pen.setStyle(QtCore.Qt.SolidLine)
            self.rect.setPen(pen)

    def set_text_name(self, name):
        if name != '':
            self.set_void_guest(False)
        self.text_name.setText(name)

    def set_text_surname(self, surname):
        if surname:
            self.set_void_guest(False)
        self.text_surname.setText(surname)

    def set_color_gender(self, gender):
        self.gender = gender
        if gender:
            self.set_void_guest(False)
        brush = QtGui.QBrush(
            GParam.dict_map_color_gender['normal'][str(gender)])
        self.rect.setBrush(brush)


    def set_data(self, i, value):
        if i == 0:
            self.set_text_name(value)
        elif i == 1:
            self.set_text_surname(value)
        elif i == 2:
            self.set_color_gender(value)

    def get_data(self, i):
        if i == 0:
            return self.text_name.text()
        elif i == 1:
            return self.text_surname.text()
        elif i == 2:
            return self.gender

    def hoverEnterEvent(self, event):
        brush = QtGui.QBrush(
            GParam.dict_map_color_gender['hovered'][str(self.gender)])
        self.rect.setBrush(brush)

    def hoverLeaveEvent(self, event):
        brush = QtGui.QBrush(
            GParam.dict_map_color_gender['normal'][str(self.gender)])
        self.rect.setBrush(brush)


class Guest:
    def __init__(self, name=None, surname=None, gender=None):
        self._graphic = GraphicGuest(name, surname, gender)
        self._data = [name, surname, gender]

    def get_data(self, i):
        return self._data[i]

    def __eq__(self, other):
        return all([self.get_data(i) == other.get_data(i)
                    for i in range(len(self._data))])

    def __ne__(self, other):
        return not self.__eq__(other)


class GraphicsTable(QtGui.QGraphicsItemGroup):
    def __init__(self, name, n_guest, guests=[]):
        QtGui.QGraphicsItemGroup.__init__(self)
        self.round = QtGui.QGraphicsEllipseItem()
        self.round.setRect(GParam.X_table, GParam.Y_table,
                           GParam.W_table, GParam.H_table)
        self.text = QtGui.QGraphicsSimpleTextItem()
        self.n_guest = n_guest
        self.name = name
        self._data = []
        self.set_text(self.name)
        if guests:
            if len(guests) == self.n_guest:
                for i in range(self.n_guest):
                    self._data.append(guests[i])
                    self.set_guest_to_table(guests[i], i)
        else:
            self._data = [None for _ in range(self.n_guest)]
            for i in range(self.n_guest):
                self.set_guest_to_table(GraphicGuest(), i)
        self.addToGroup(self.round)
        self.addToGroup(self.text)
        # self.setAcceptHoverEvents(True)
        self.setFlags(QtGui.QGraphicsItem.ItemIsMovable |
                      QtGui.QGraphicsItem.ItemIsSelectable)  # |
        # QtGui.QGraphicsItem.ItemSendsScenePositionChanges)

    def get_i_from_item(self, item):
        for item_ in self._data:
            if item_ == item:
                return self._data.index(item_)
        return None

    def set_void_table(self):
        pen = QtGui.QPen()
        pen.setStyle(QtCore.Qt.DashLine)
        self.round.setPen(pen)

    def set_text(self, name):
        pen = QtGui.QPen()
        pen.setStyle(QtCore.Qt.SolidLine)
        self.round.setPen(pen)
        self.text.setText(name)

    def set_guest(self, guest, i, pos=None):
        if not pos:
            guest.setPos((GParam.W_table / 2. + GParam.W_rect / 2.
                          + GParam.delta_chair)
                         * cos(2 * i * pi / self.n_guest),
                         (GParam.H_table / 2. + GParam.H_rect / 2.
                          + GParam.delta_chair)
                         * sin(2 * i * pi / self.n_guest))
        else:
            guest.setPos(pos)
        guest.rect.setRotation(360. * i / self.n_guest)
        self.addToGroup(guest)
        self._data[i] = guest

    def remove_guest(self, i):
        g = self._data[i]
        self.removeFromGroup(g)

    def reset_guest(self, i):
        self.remove_guest(i)
        self.set_guest(GraphicGuest(), i)

    def get_data(self, i):
        return self._data[i]

    def set_data(self, i, guest):
        self._data[i] = guest


class Table:
    def __init__(self, name, n_guest, guests=[]):
        self.graphics = GraphicsTable(name, n_guest, guests)
        self._data = [name, n_guest, guests]

    def get_data(self, i):
        return self._data[i]

    def __eq__(self, other):
        return self._data[0] == other.get_data(0)

    def __ne__(self, other):
        return not self.__eq__(other)

    def set_guest(self, guest, i):
        self.graphics.set_guest(guest, i)
        self._data[2][i] = guest


class GuestModel(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        QtGui.QStandardItemModel.__init__(self, parent)
        self._data = []
        self.itemChanged.connect(self._has_changed)

    def _has_changed(self, item):
        i, j = item.row(), item.column()
        value = item.data(QtCore.Qt.DisplayRole).toString()
        self._data[i].set_data(j, value)
        self.emit(QtCore.SIGNAL("guest changed"), item, value)

    def check_double(self, guest):
        return any([g == guest for g in self._data])

    def add_guest(self, name, surname, gender):
        g = Guest(name, surname, gender)
        if not self.check_double(g):
            self.appendRow([QtGui.QStandardItem(name),
                            QtGui.QStandardItem(surname),
                            QtGui.QStandardItem
                            (gender)])
            self._data.append(g)

    def delete_guest(self, row):
        self.removeRow(row)
        self._data.pop(row)


class TableModel(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self._data = []


class Controller:
    def __init__(self, guest_model, table_model):
        self.guest_model = guest_model
        self.table_model = table_model

    def add_guest(self, name, surname, gender):
        pass

    def delete_guest(self, name, surname, gender):
        pass

    def add_table(self, name, surname, gender):
        pass

    def delete_table(self, name, surname, gender):
        pass

    def update_guest(self, item, value):
        pass

    def update_table(self, event):
        pass


class SceneView(QtGui.QGraphicsView):
    def __init__(self, *args):
        QtGui.QGraphicsView.__init__(self, *args)
        self.setAcceptDrops(True)
        self._zoom = 0

    def wheelEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier:
            if event.delta() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView(GParam.rect_scene,
                               QtCore.Qt.KeepAspectRatioByExpanding)
            else:
                self._zoom = 0
        elif event.modifiers() == QtCore.Qt.NoModifier:
            super(SceneView, self).wheelEvent(event)


class TempWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        # Definition of the layouts
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
        self.graphic_view = SceneView()
        self.guest_view = QtGui.QTableView()
        # Definition of the models
        self.scene = QtGui.QGraphicsScene(GParam.X_origin, GParam.Y_origin,
                                          GParam.W_scene, GParam.H_scene)
        g1 = GraphicGuest('Philippe', 'JB', 'M')
        g2 = GraphicGuest('Esquevin', 'So', 'F')
        g3 = GraphicGuest('Bob', "Le ponge", 'C')
        g4 = GraphicGuest()
        g1.setPos(150., 150.)
        g2.setPos(300., 150.)
        g3.setPos(450., 150.)
        g4.setPos(600., 150.)
        self.scene.addItem(g1)
        self.scene.addItem(g2)
        self.scene.addItem(g3)
        self.scene.addItem(g4)
        self._guest_model = GuestModel()
        self._table_model = TableModel()
        # Linking model to controller
        self.controller = Controller(self._guest_model, self._table_model)
        # Linking model to view
        self.graphic_view.setScene(self.scene)
        self.graphic_view.fitInView(GParam.rect_scene,
                                    QtCore.Qt.KeepAspectRatioByExpanding)
        self.guest_view.setModel(self.controller.guest_model)
        # Adding elements to the layout
        h_layout.addWidget(self.btn_add_guest)
        h_layout.addWidget(self.btn_add_table)
        h_layout.addWidget(self.led)
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.guest_view)
        main_layout.addLayout(v_layout)
        main_layout.addWidget(self.graphic_view)
        self.setLayout(main_layout)

    def add_guest(self):
        pass

    def add_table(self):
        name = None
        while not name:
            name, n_guest, ok = NewTable.get_result()
            if name and ok == QtGui.QDialog.Accepted:
                pass
            elif ok == QtGui.QDialog.Rejected:
                break
            elif not name:
                display_warning('Empty name',
                                'The name of the table cannot be empty !')


class NewTable(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)
        self.setWindowTitle('New table...')
        self.setWindowFlags(QtCore.Qt.WindowTitleHint |
                            QtCore.Qt.WindowCloseButtonHint)
        self.setWindowIcon(QtGui.QIcon())
        self.lab_name = QtGui.QLabel('Name of the table')
        self.led = QtGui.QLineEdit()
        self.lab_n_guest = QtGui.QLabel('Number of guest around the table')
        self.cbx = QtGui.QComboBox()
        self.cbx.addItems(['10', '12'])
        btn = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                     QtGui.QDialogButtonBox.Cancel,
                                     QtCore.Qt.Horizontal, self)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        layout.addWidget(self.lab_name)
        layout.addWidget(self.led)
        layout.addWidget(self.lab_n_guest)
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
        return dialog.get_name(), dialog.get_n_guest(), result


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    view = TempWidget()
    view.show()
    sys.exit(app.exec_())
