from __future__ import division
import sys
from PySide import QtGui, QtCore
import math


#TODO:
#dragging the sdene
#triggerfunc for dynamic update
#cached properties
#find bugs

class BaseNode(QtGui.QWidget):
    def __init__(self, scene, title="base widget", color="green"):
        super(BaseNode, self).__init__()
        self.setObjectName("BaseWidget")
        self.scene = scene
        self.color = color
        self.layout = QtGui.QGridLayout(self)
        self.title = QtGui.QLabel(title)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addItem(QtGui.QSpacerItem(10, 10), 0, 0)
        self.layout.addItem(QtGui.QSpacerItem(10, 10), 0, 2)
        self.layout.addWidget(self.title, 0, 1)
        self.layout.setSpacing(0)
        self.setStyleSheet(
            """QWidget#BaseWidget {background-color:transparent};
            """)
        self.item = None
        self.is_hidden = False

    def paintEvent(self, ev):
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush(QtGui.QColor(self.color), QtCore.Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        pen = QtGui.QPen()
        pen.setColor(self.color)
        painter.setPen(pen)
        rect = painter.drawRoundedRect(self.rect(), 20, 20)

    @property
    def slots(self):
        slots = []
        self.find_slots(self, arr=slots)
        return(slots)

    @staticmethod
    def find_slots(widget, arr=[]):
        for child in widget.children():
            if isinstance(child, Slot):
                arr.append(child)
            else:
                BaseNode.find_slots(child, arr=arr)

    def addWidget(self, *widgets):
        num_row = self.layout.rowCount()
        for wid in widgets:
            wid.setParent(self)
            if isinstance(wid, SlotInput):
                self.layout.addWidget(wid, num_row, 0)
            elif isinstance(wid, SlotOutput):
                self.layout.addWidget(wid, num_row, 2)
            else:
                self.layout.addWidget(wid, num_row, 1)

    def add_to_scene(self):
        self.item = NodeProxyWidget(self)
        self.scene.addItem(self.item)

    def delete(self):
        # add stuff you want to do before deleting the object
        self.scene.removeItem(self.item)

    def get_lower_connected(self):
        arr = [i.get_connected_nodes() for i in self.slots if isinstance(i, SlotOutput)]
        arr1 = []
        for a in arr:
            arr1 += a
        return(arr1)

    def trigger(self, nodes):
        for i in nodes:
            i.trigger(i.get_lower_connected())

    def get_view(self):
        try:
            return self.scene.views()[0]
        except:
            return None

    def get_mdi_sub_window(self):
        try:
            return self.get_view().parent()
        except:
            return None

    def get_mdi_widget(self):
        try:
            return self.get_mdi_sub_window().parent().parent()
        except:
            return None

    def back_to_nodes(self):
        self.get_mdi_widget().setActiveSubWindow(self.get_mdi_sub_window())


    def minimize(self):
        for i in self.children():
            if isinstance(i, QtGui.QWidget):
                if not isinstance(i, (Slot, QtGui.QLabel)):
                    if self.is_hidden:
                        i.show()
                    else:
                        i.hide()
        self.adjustSize()
        self.item.update_lines()
        self.is_hidden = not self.is_hidden

    def update_lines(self):
        for slot in self.slots:
            for line in slot.line:
                line.update_line()


class NodeProxyWidget(QtGui.QGraphicsProxyWidget):
    """The QGraphicsProxyWidget allows to get the Widget on the scene"""
    def __init__(self, widget=None, parent=None):
        super(NodeProxyWidget, self).__init__(parent=parent)
        self.setWidget(widget)
        self.setPos(200, 200)
        self.current_pos = None

    def mousePressEvent(self, event):
        # this node proxy widget deletes the handler from the widget
        # so there is the right mouse handling
        if event.buttons() == QtCore.Qt.RightButton:
            self.current_pos = event.pos()
        else:
            super(NodeProxyWidget, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super(NodeProxyWidget, self).mouseMoveEvent(event)
        if event.buttons() == QtCore.Qt.RightButton:
            self.setPos(self.mapToParent(event.pos()) - self.current_pos)
            for i in range(2):
                self.update_lines()
        else:
            super(NodeProxyWidget, self).mouseMoveEvent(event)

    def update_lines(self):
        self.widget().update_lines()

    def keyPressEvent(self, event):
        if event.key() == 88:
            self.widget().delete()
            for i in self.widget().slots:
                i.delete_node()
                self.widget().scene.node_list.remove(i)
        super(NodeProxyWidget, self).keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.widget().minimize()


class Slot(QtGui.QCheckBox):
    """a Checkbox which has some connection info and connections to other Slots
            make new connection with left click"""
    def __init__(self, scene=None, color='black'):
        super(Slot, self).__init__()
        self.color = color
        self.scene = scene
        self.line = []
        self.connection = False
        self.connection_node = None
        scene.node_list.append(self)

    def paintEvent(self, ev):
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush(QtGui.QColor(self.color), QtCore.Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        pen = QtGui.QPen()
        pen.setColor(self.color)
        painter.setPen(pen)
        rect = self.rect()
        rect.adjust(4,4,-4,-4)
        painter.drawRoundedRect(rect, 4, 4)

    @property
    def global_pos(self):
        temp = QtCore.QPointF(self.width() / 2, self.height() / 2)
        return QtCore.QPointF(self.parent().mapToGlobal(self.pos())) + temp

    def mousePressEvent(self, event):
        self.connection = True
        pos = self.global_pos
        line = QtCore.QLineF(pos.x(), pos.y(), pos.x(), pos.y())
        line_item = QtGui.QGraphicsLineItem(line, scene=self.scene)
        line_item.setZValue(0)
        self.line.append(line_item)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            if len(self.line) > 0:
                pos = self.mapToGlobal(event.pos())
                for node in self.scene.node_list:
                    node_pos = node.global_pos
                    if PointNorm(node_pos, pos) < 10 and node.parent() is not self.parent():
                        self.connection_node = node
                        pos = node_pos
                        break
                    else:
                        self.connection_node = None
                line = self.line[-1]
                l = line.line()
                x1 = l.x1()
                y1 = l.y1()
                line.setLine(x1, y1, pos.x(), pos.y())

    def mouseReleaseEvent(self, event):
        if self.connection:
            if self.connection_node is not None:
                line = NodeLine(self, self.connection_node, scene=self.scene)
                self.connection_node.line.append(line)
                self.line[-1] = line
                self.setChecked(1)
                self.connection_node.setChecked(1)
                self.got_connected()
                self.connection_node.got_connected()
                self.connection_node = None
            self.connection = False
        for i, p in enumerate(self.line):
            if not isinstance(p, NodeLine):
                self.line.pop(i)


    def delete_line(self, line):
        node1 = line.node1
        node2 = line.node2
        node1.line.remove(line)
        node2.line.remove(line)
        node1.got_unconnected()
        node2.got_unconnected()

    def delete_node(self):
        while self.line:
            self.delete_line(self.line[0])

    def got_connected(self):
        pass

    def got_unconnected(self):
        pass


class SlotInput(Slot):
    """this node only accept one line"""
    def mousePressEvent(self, event):
        if len(self.line) == 0:
            super(SlotInput, self).mousePressEvent(event)
        else:
            self.delete_line(self.line[0])
            super(SlotInput, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super(SlotInput, self).mouseMoveEvent(event)
        if not isinstance(self.connection_node, SlotOutput):
            self.connection_node = None

    def get_connected_node(self):
        if len(self.line) > 0:
            node1 = self.line[0].node1
            node2 = self.line[0].node2
            if node1 == self:
                return node2
            else:
                return node1
        return None

    def input(self):
        """calls the output of connectet input"""
        connected_node = self.get_connected_node()
        if connected_node:
            #it is not possible to connect to an input
            return connected_node.output()
        return None

    def help_(self):
        connected_node = self.get_connected_node()
        if connected_node:
            #it is not possible to connect to an input
            return connected_node.parent().__doc__
        return None


class SlotOutput(Slot):
    def __init__(self, scene, color="black"):
        super(SlotOutput, self).__init__(scene=scene, color=color)
        #set this output fuction to something else

    def mouseReleaseEvent(self, event):
        if self.connection:
            if self.connection_node is not None:
                if len(self.connection_node.line) != 0:
                    self.connection_node.delete_line(self.connection_node.line[0])
        super(SlotOutput, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        super(SlotOutput, self).mouseMoveEvent(event)
        if not isinstance(self.connection_node, SlotInput):
            self.connection_node = None

    def get_connected_nodes(self):
        arr = []
        for line in self.line:
            node1 = line.node1
            node2 = line.node2
            if node1 == self:
                arr.append(node2)
            else:
                arr.append(node1)
        return arr

    def output(self):
        return None

    def help_(self):
        return("connect me")


class NodeLine(QtGui.QGraphicsLineItem):
    """ a Line Element to connect Nodes"""
    def __init__(self, node1, node2, scene=None):
        super(NodeLine, self).__init__(scene=scene)
        self.node1 = node1
        self.node2 = node2
        self.linef = QtCore.QLineF(node1.global_pos, node2.global_pos)
        self.setZValue(-1)
        self.setLine(self.linef)
        self.delete_line = False

    def update_line(self):
        self.linef.setP1(self.node1.global_pos)
        self.linef.setP2(self.node2.global_pos)
        self.setLine(self.linef)


class NodeScene(QtGui.QGraphicsScene):
    """A GraphicsScene which has a list of all the nodes"""
    def __init__(self):
        super(NodeScene, self).__init__()
        self.setSceneRect(-0, 0, 2000, 2000)
        self.node_list = []


class NodeView(QtGui.QGraphicsView):
    def __init__(self, scene):
        super(NodeView, self).__init__()
        self.setScene(scene)
        self.setDragMode(QtGui.QGraphicsView.DragMode.ScrollHandDrag)
        self.add_item = None 
        self.setRenderHints(QtGui.QPainter.HighQualityAntialiasing)

    def mousePressEvent(self, event):
        if self.add_item:
            self.add_item.add_to_scene()
            self.add_item.item.setPos(self.mapToScene(event.pos()))
            self.add_item = None
        super(NodeView, self).mousePressEvent(event)

    def wheelEvent(self, event):
        scale_value = 1 + (event.delta() / 5000)
        self.scale(scale_value, scale_value)


def PointNorm(p1, p2):
    return(math.sqrt((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2))


from nodeeditor.python import value

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    scene = NodeScene()

    view = NodeView(scene)
    view.show()

    value.SliderNode(scene).add_to_scene()
    value.HelpNode(scene).add_to_scene()
    value.ListNode(scene).add_to_scene()



    sys.exit(app.exec_())
