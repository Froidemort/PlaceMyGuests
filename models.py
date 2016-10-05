import pickle
import sys
from math import cos, sin, pi
from PyQt4 import QtCore, QtGui


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
    dict_map_color_gender = {'M': QtCore.Qt.blue,
                             'F': QtCore.Qt.red,
                             'C': QtCore.Qt.green}
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
    def __init__(self, data=None):
        QtGui.QGraphicsItemGroup.__init__(self)
        if data is None:
            data = ['', '', '']
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
        # print 'Calling set_void_guest in GraphicGuest class'
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
        self._data = [None for _ in range(self.n_guest)]
        self.set_text(self.name)
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

    def set_guest_to_table(self, guest, i, pos=None):
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
        self.set_guest_to_table(GraphicGuest(), i)


class GuestModel(QtGui.QStandardItemModel):
    def __init__(self, scene, parent=None):
        QtGui.QStandardItemModel.__init__(self, parent)
        self.scene = scene
        self._data = []
        self.itemChanged.connect(self._has_changed)
        self.setSupportedDragActions(QtCore.Qt.MoveAction)

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


class TableModel(QtCore.QObject):
    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        self._data = dict()
        self._placed_guest = []

    @staticmethod
    def _check_void_guest(l_in):
        return all([i == '' for i in l_in])

    def get_table(self, name):
        for key in self._data.keys():
            if key == name:
                return self._data[name]
        return None

    def rename_table(self, old_name, name):
        result = self.get_table(old_name)
        if result:
            self._data[name] = self._data[old_name]
            del self._data[old_name]

    def add_table(self, table):
        if table.name not in [t.name for t in self._data.keys()]:
            self._data[table] = [table.n_guest, [[''] * 3 for _ in range(table.n_guest)]]


class MyScene(QtGui.QGraphicsScene):
    def __init__(self, x, y, w, h):
        QtGui.QGraphicsScene.__init__(self, x, y, w, h)
        self.group = QtGui.QGraphicsItemGroup()
        pen = QtGui.QPen(QtCore.Qt.gray)
        for x_grid in xrange(0, int(w), int(GParam.W_tot_table)):
            for y_grid in xrange(0, int(h), int(GParam.H_tot_table)):
                l_h = QtGui.QGraphicsLineItem(float(x_grid), float(y_grid),
                                              w, float(y_grid))
                l_v = QtGui.QGraphicsLineItem(float(x_grid), float(y_grid),
                                              float(x_grid), h)
                l_h.setPen(pen)
                l_v.setPen(pen)
                self.group.addToGroup(l_h)
                self.group.addToGroup(l_v)
        self.addItem(self.group)
        self.data_table = TableModel()

    def get_parent(self, item):
        print type(item), 'from',
        if item.parentItem():
            parent = item.parentItem()
            self.get_parent(parent)
        else:
            print "MyScene"

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_A and event.modifiers() == QtCore.Qt.ControlModifier:
            for item in self.items():
                item.setSelected(True)
        if event.key() == QtCore.Qt.Key_Delete:
            print 'Deleting objects...'

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            print event.scenePos().x(), event.scenePos().y()
            if self.itemAt(event.scenePos()):
                print 'Item found !'
                g_g = self.itemAt(event.scenePos())
                self.get_parent(g_g)
                g_g.setSelected(True)
            else:
                print 'Nothing found !'
        super(MyScene, self).mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-person"):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-person"):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        item = self.itemAt(event.scenePos())
        if item:  # Checking existence of an item under the mouse
            if isinstance(item.parentItem(), GraphicGuest):
                # Checking if the item is a guest place.
                data = event.mimeData()
                b_stream = data.retrieveData("application/x-person",
                                             QtCore.QVariant.ByteArray)
                selected = pickle.loads(b_stream.toByteArray())
                print 'RECEIVED :', selected, event.scenePos().x(), event.scenePos().y()
                g = GraphicGuest()
                g.set_text_name(selected[0])
                g.set_text_surname(selected[1])
                g.set_color_gender(selected[2])
                g.setPos(event.scenePos())
                old_guest = item.parentItem()
                pos = old_guest.scenePos()
                table = old_guest.parentItem()
                i = table.get_i_from_item(old_guest)
                table.remove_guest(i)
                table.set_guest_to_table(g, i, pos)
                event.accept()


class MyView(QtGui.QGraphicsView):
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
                self.fitInView(GParam.rect_scene)
            else:
                self._zoom = 0
        elif event.modifiers() == QtCore.Qt.NoModifier:
            super(MyView, self).wheelEvent(event)


class CustomView(QtGui.QTableView):
    def __init__(self, parent=None):
        QtGui.QTableView.__init__(self, parent)
        self.setDragEnabled(True)
        # Graphical customization

        # Definition of selection mode, behavior and drag and drop mode.
        self.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self.setSelectionMode(QtGui.QTableView.SingleSelection)
        self.setDragDropMode(QtGui.QTableView.DragOnly)

    def startDrag(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return
        # selected is the relevant person object
        print index.row()
        selected = [self.model().index(index.row(), i).data().toString() for i
                    in range(3)]
        print 'EMITTED :', selected
        # convert to  a bytestream
        b_stream = pickle.dumps(selected)
        mime_data = QtCore.QMimeData()
        mime_data.setData("application/x-person", b_stream)
        # create the drag object
        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        drag.start(QtCore.Qt.MoveAction)

    def mouseMoveEvent(self, event):
        self.startDrag(event)
        super(CustomView, self).mouseMoveEvent(event)


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
        self.graphic_view = MyView()
        self.table_view = CustomView()
        # Definition of the models
        self.scene = MyScene(GParam.X_origin, GParam.Y_origin,
                             GParam.W_scene, GParam.H_scene)
        self.guest_model = GuestModel(self.scene)
        # Linking model to view
        self.graphic_view.setScene(self.scene)
        self.graphic_view.fitInView(GParam.rect_scene)
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
        name = None
        while not name:
            name, n_guest, ok = NewTable.get_result()
            if name and ok == QtGui.QDialog.Accepted:
                t = GraphicsTable([name, n_guest])
                self.scene.addItem(t)
                self.scene.data_table.add_table(t)
            elif ok == QtGui.QDialog.Rejected:
                break
            elif not name:
                display_error('The name of the table cannot be empty !')


class NewTable(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)
        self.setWindowTitle('New table...')
        self.setWindowFlags(QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
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


def display_error(message):
    error = QtGui.QMessageBox()
    error.setWindowTitle('Empty name')
    error.setText(message)
    error.setIcon(QtGui.QMessageBox.Warning)
    error.exec_()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    view = TempWidget()
    view.show()
    sys.exit(app.exec_())
