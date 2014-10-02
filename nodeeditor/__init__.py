from __future__ import division
import sys
from PySide import QtGui, QtCore
import math
from Gui import *


class BaseNode(QtGui.QGraphicsWidget):
    def __init__(self, scene=None, title="BASE ITEM", color="green"):
        super(BaseNode, self).__init__()
        self._scene = scene
        self.color = color
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        layout = QtGui.QGraphicsGridLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setVerticalSpacing(1)
        self.setLayout(layout)
        self.setMinimumWidth(10)
        self.setMinimumHeight(10)
        self.setMaximumWidth(500)
        self.addItem(SlotFakeOutput(), Label(title), SlotFakeInput())

    @property
    def brush(self):
        return QtGui.QBrush(QtGui.QColor(self.color), QtCore.Qt.BrushStyle.SolidPattern)

    @property
    def pen(self):
        col = 'yellow' if self.selected else 'black'  
        self.setZValue(10) if self.selected else self.setZValue(self.zValue() - 1)
        pen = QtGui.QPen()
        pen.setColor(col)
        return(pen)

    @property
    def selected(self):
        return self.isSelected()

    def paint(self, painter, option, widget):
        shape = QtGui.QPainterPath()
        rect = self.rect()
        rect.adjust(7, 0, -7, 0)
        shape.addRoundedRect(rect, 10, 10)
        opt = 0.7
        painter.setOpacity(opt)
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawPath(shape)

    def mouseMoveEvent(self, event):
        super(BaseNode, self).mouseMoveEvent(event)
        if event.buttons() == QtCore.Qt.LeftButton:
            for i in range(2):
                self.update_lines()

    def update_lines(self):
        for slot in self.slots:
            for line in slot.line:
                line.update_line()

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

    def addItem(self, *items):
        num_row = self.layout().rowCount()
        for item in items:
            item.setParent(self)
            if isinstance(item, (SlotInput, SlotFakeInput)):
                self.layout().addItem(item, num_row, 0, QtCore.Qt.AlignCenter)
            elif isinstance(item, (SlotOutput, SlotFakeOutput)):
                self.layout().addItem(item, num_row, 2, QtCore.Qt.AlignCenter)
            else:
                self.layout().addItem(item, num_row, 1, QtCore.Qt.AlignCenter)

    def removeWidget(self, widget):
        # parent has to be set!
        self.layout.removeWidget(widget)
        if widget in self._scene.node_list:
            self._scene.node_list.remove(widget)
        if isinstance(widget, Slot):
            for l in widget.line:
                widget.delete_line(l)
        widget.setParent(None)
        widget.deleteLater()

    def add_to_scene(self):
        self._scene.addItem(self)



class Slot(QtGui.QGraphicsWidget):
    def __init__(self, scene, parent=None, color = 'yellow'):
        super(Slot, self).__init__()
        self.setParent(parent)
        self.width = 10
        self.height = 10
        self._color = color
        self.setMaximumSize(self.width, self.height)
        self._scene = scene
        self.line = []
        self.connection = False
        self.connection_node = None
        scene.node_list.append(self)

    @property
    def color(self):
        return QtGui.QColor(self._color)

    @property
    def selected(self):
        return self.parent().selected

    @property
    def pen(self):
        col = 'yellow' if self.connection else 'black'
        pen = QtGui.QPen()
        pen.setColor(col)
        return(pen)
    
    @property
    def brush(self):
        return QtGui.QBrush(QtGui.QColor(self.color), QtCore.Qt.BrushStyle.SolidPattern)
    
    def paint(self, painter=None, option=None, widget=None):
        shape = QtGui.QPainterPath()
        shape.addEllipse(0, 0, self.width, self.height)
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawPath(shape)

    @property
    def global_pos(self):
        temp = QtCore.QPointF(self.width / 2, self.height / 2)
        return QtCore.QPointF(self.mapToScene(temp))

    def mousePressEvent(self, event):
        self.update()
        self.connection = True
        pos = self.global_pos
        line = QtCore.QLineF(pos.x(), pos.y(), pos.x(), pos.y())
        line_item = QtGui.QGraphicsLineItem(line, scene=self._scene)
        line_item.setZValue(0)
        self.line.append(line_item)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            if len(self.line) > 0:
                pos = self.mapToScene(event.pos())
                for node in self._scene.node_list:
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
                line = NodeLine(self, self.connection_node, scene=self._scene)
                self.connection_node.line.append(line)
                self.line[-1] = line
                self.got_connected()
                self.connection_node.got_connected()
                self.connection_node = None
            self.connection = False
        for i, p in enumerate(self.line):
            if not isinstance(p, NodeLine):
                self.line.pop(i)
        self.update()

    def delete_line(self, line):
        node1 = line.node1
        node2 = line.node2
        node1.line.remove(line)
        node2.line.remove(line)
        node1.got_unconnected()
        node2.got_unconnected()

    def delete_Slot(self):
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
        if not isinstance(self.connection_node, self.accepted_slots):
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

    @property
    def accepted_slots(self):
        return (SlotOutput)


class SlotOutput(Slot):
    def mouseReleaseEvent(self, event):
        if self.connection:
            if self.connection_node is not None:
                if len(self.connection_node.line) != 0:
                    self.connection_node.delete_line(self.connection_node.line[0])
        super(SlotOutput, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        super(SlotOutput, self).mouseMoveEvent(event)
        if not isinstance(self.connection_node, self.accepted_slots):
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

    @property
    def accepted_slots(self):
        return SlotInput


class SlotFakeInput(QtGui.QGraphicsWidget):
    def setGeometry(self, rect):
        pass

    def sizeHint(self, *args):
        return QtCore.QSizeF(10, 10)


class SlotFakeOutput(QtGui.QGraphicsWidget):
    def setGeometry(self, rect):
        pass

    def sizeHint(self, *args):
        return QtCore.QSizeF(10, 10)


class NodeLine(QtGui.QGraphicsLineItem):
    """ a Line Element to connect Nodes"""
    def __init__(self, node1, node2, scene=None):
        super(NodeLine, self).__init__(scene=scene)
        self.node1 = node1
        self.node2 = node2
        self.linef = QtCore.QLineF(node1.global_pos, node2.global_pos)
        self.setZValue(11)
        self.setLine(self.linef)
        self.delete_line = False

    def update_line(self):
        self.linef.setP1(self.node1.global_pos)
        self.linef.setP2(self.node2.global_pos)
        self.setLine(self.linef)


class NodeScene(QtGui.QGraphicsScene):
    """A GraphicsScene which has a list of all the nodes"""
    def __init__(self, color="grey"):
        super(NodeScene, self).__init__()
        self.setSceneRect(-0, 0, 500, 500)
        self._color = color
        self.node_list = []
        self.setBackgroundBrush(self.color)

    @property
    def color(self):
        return QtGui.QColor(self._color)

    def drawBackground(self, painter, rect):
        super(NodeScene, self).drawBackground(painter, rect)
        painter.setPen(QtGui.QPen(self.color.lighter(90)))
        gridSize = 50
        left = int(rect.left()) - (int(rect.left()) % gridSize)
        top = int(rect.top()) - (int(rect.top()) % gridSize)
        x = left
        while x < rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += gridSize
        y = top
        while y < rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
            y += gridSize


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
            self.add_item.setPos(self.mapToScene(event.pos()))
            self.add_item = None
        super(NodeView, self).mousePressEvent(event)

    def wheelEvent(self, event):
        scale_value = 1 + (event.delta() / 5000)
        self.scale(scale_value, scale_value)

def PointNorm(p1, p2):
    return(math.sqrt((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2))


if __name__ == "__main__":
    from nodeeditor.python import value
    app = QtGui.QApplication(sys.argv)
    app.setOverrideCursor(QtCore.Qt.ArrowCursor)
    scene = NodeScene()
    item = value.SliderNode(scene)
    value.SliderNode(scene).add_to_scene()
    value.GetValueNode(scene).add_to_scene()
    value.HelpNode(scene).add_to_scene()
    value.ListNode(scene).add_to_scene()


    view = NodeView(scene)
    view.show()

    sys.exit(app.exec_())
