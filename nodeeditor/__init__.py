from __future__ import division
import sys
from PySide import QtGui, QtCore
import math

class BaseNode(QtGui.QWidget):
    def __init__(self, scene, titel="base widget", color="red"):
        super(BaseNode, self).__init__()
        self.setObjectName("BaseWidget")
        self.scene = scene
        self.color=color
        self.layout = QtGui.QVBoxLayout(self)
        self.titel = QtGui.QLabel(titel)
        self.titel.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.titel)
        self.layout.setSpacing(0)
        self.setStyleSheet(
            """QWidget#BaseWidget {background-color:transparent};
            """)
        self.item = None

    def add_to_scene(self):
        self.item = NodeProxyWidget(self)
        self.scene.addItem(self.item)

    def delete(self):
        self.scene.removeItem(self.item)

    def paintEvent(self, ev):
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush(QtGui.QColor(self.color), QtCore.Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        pen = QtGui.QPen()
        pen.setColor(self.color)
        painter.setPen(pen)
        rect = painter.drawRoundedRect(self.rect(), 20, 20)

    def trigger(self):
        #find all outputs
        #call theire trigger 
        #so in the end the last element desides what is recomputed
        pass


class NodeScene(QtGui.QGraphicsScene):
    """A GraphicsScene which has a list of all the nodes"""
    def __init__(self):
        super(NodeScene, self).__init__()
        self.setSceneRect(-100, -100, 1000, 1000)
        self.node_list = []


class NodeView(QtGui.QGraphicsView):
    def wheelEvent(self, event):
        scale_value = 1 + (event.delta() / 5000)
        self.scale(scale_value, scale_value)


class NodeProxyWidget(QtGui.QGraphicsProxyWidget):
    """The QGraphicsProxyWidget allows to get the Widget on the scene"""
    def __init__(self, widget=None, parent=None):
        super(NodeProxyWidget, self).__init__(parent=parent)
        self.setWidget(widget)
        self.current_pos = None

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            self.current_pos = event.pos()
        else:
            super(NodeProxyWidget, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super(NodeProxyWidget, self).mouseMoveEvent(event)
        if event.buttons() == QtCore.Qt.RightButton:
            self.setPos(self.mapToParent(event.pos()) - self.current_pos)
            for i in range(2):
                for anchor_node in self.anchor_nodes:
                    for line in anchor_node.line:
                        line.update_line()

        else:
            super(NodeProxyWidget, self).mouseMoveEvent(event)

    @property
    def anchor_nodes(self):
        anchor_nodes = []
        self.find_anchor_nodes(self.widget(), arr=anchor_nodes)
        return(anchor_nodes)

    @staticmethod
    def find_anchor_nodes(widget, arr=[]):
        for child in widget.children():
            if isinstance(child, NodeAnchor):
                arr.append(child)
            else:
                NodeProxyWidget.find_anchor_nodes(child, arr=arr)

    def keyPressEvent(self, event):
        if event.key() == 16777223:
            for i in self.anchor_nodes:
                self.widget().scene.node_list.remove(i)
                i.delete_node()
            self.widget().delete()


class NodeAnchor(QtGui.QCheckBox):
    """a RadioButton which has some connection info and connections to other NodeAnchors
            make new connection with left click"""
    def __init__(self, parent=None, scene=None):
        super(NodeAnchor, self).__init__(parent)
        self.scene = scene
        self.line = []
        self.connection = False
        self.connection_node = None
        scene.node_list.append(self)

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
        if len(node1.line) == 0:
            node1.setChecked(0)
        if len(node2.line) == 0:
            node2.setChecked(0)

    def delete_node(self):
        for i in self.line:
            self.delete_line(i)


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


def PointNorm(p1, p2):
    return(math.sqrt((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2))


class NodeInput(NodeAnchor):
    """this node only accept one line"""
    def mousePressEvent(self, event):
        if len(self.line) == 0:
            super(NodeInput, self).mousePressEvent(event)
        else:
            self.delete_line(self.line[0])
            super(NodeInput, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super(NodeInput, self).mouseMoveEvent(event)
        if not isinstance(self.connection_node, NodeOutput):
            self.connection_node = None

    def get_connected_Node(self):
        if len(self.line) > 0:
            node1 = self.line[0].node1
            node2 = self.line[0].node2
            if node1 == self:
                return node2
            else:
                return node1
        return None


class NodeOutput(NodeAnchor):
    def mouseReleaseEvent(self, event):
        if self.connection:
            if self.connection_node is not None:
                if len(self.connection_node.line) != 0:
                    self.connection_node.delete_line(self.connection_node.line[0])
        super(NodeOutput, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        super(NodeOutput, self).mouseMoveEvent(event)
        if not isinstance(self.connection_node, NodeInput):
            self.connection_node = None


class ManipulatorNodeWidget(QtGui.QWidget):
    def __init__(self, widget=QtGui.QWidget(), inp=False, outp=False, scene=None, parent=None):
        super(ManipulatorNodeWidget, self).__init__(parent=parent)
        self.scene = scene
        self.layout = QtGui.QHBoxLayout(self)
        self.inp = None
        self.outp = None
        if inp:
            self.inp = NodeInput(self, self.scene)
            self.layout.addWidget(self.inp)
        else:
            self.layout.addWidget(QtGui.QWidget())
        self.base_widget = widget or QtGui.QWidget()
        self.base_widget.setParent(self)
        self.layout.addWidget(self.base_widget)
        if outp:
            self.outp = NodeOutput(self, self.scene)
            self.layout.addWidget(self.outp)
        else:
            self.layout.addWidget(QtGui.QWidget())
        self.output = self.fakefunc

    @property
    def input(self):
        """calls the o
        utput of connectet input"""
        print(self.inp)
        if self.inp:
            connected_node = self.inp.get_connected_Node()
            if connected_node:
                connected_manipulator_wid = connected_node.parent()
                return connected_manipulator_wid.output()
        return None

    @staticmethod
    def fakefunc():
        return None


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    scene = NodeScene()

    for i in range(2):
        wid = QtGui.QWidget()
        lay = QtGui.QHBoxLayout(wid)
        lay.addWidget(NodeInput(scene=scene))
        scene.addItem(NodeProxyWidget(wid))

    for i in range(2):
        wid = QtGui.QWidget()
        lay = QtGui.QHBoxLayout(wid)
        lay.addWidget(NodeOutput(scene=scene))
        scene.addItem(NodeProxyWidget(wid))

    view = NodeView()
    view.setScene(scene)
    view.show()
    sys.exit(app.exec_())
