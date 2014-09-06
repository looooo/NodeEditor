__ALL__ = ["part", "value", "NodeWindow"]

from PySide import QtGui, QtCore
from nodeeditor import NodeView, NodeScene
from nodeeditor.python import value
from nodeeditor.freecad import part
import FreeCADGui as Gui


ButtonDict = {
    "Value": value.ButtonDict,
    "Part": part.ButtonDict
}

class NodeWindow(object):
    def __init__(self, winTitle="NodeView"):
        mainwindow = Gui.getMainWindow() #!!!! PySide returne a widget with self.getMainWIndow() !!!
        mdi = self.getMdiArea()

        self.scene = NodeScene()
        self.view = NodeView()
        self.view.setScene(self.scene)
        self.view.setWindowTitle(winTitle)
        self.sub = mdi.addSubWindow(self.view)
        self.NodeWidget = QtGui.QTabWidget()
        mainwindow.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockWidget)
        self.sub.show()

    def getMdiArea(self):
        """ Return FreeCAD MdiArea. """
        mw = self.getMainWindow()
        if not mw:
            return None
        childs = mw.children()
        for c in childs:
            if isinstance(c, QtGui.QMdiArea):
                return c
        return None

    def getMainWindow(self):
        """ Return the FreeCAD main window. """
        toplevel = QtGui.qApp.topLevelWidgets()
        for i in toplevel:
            if i.metaObject().className() == "Gui::MainWindow":
                return i
        return None

    @property
    def dockWidget(self):
        self.NodeWidget.setTabPosition(QtGui.QTabWidget.East)
        dockWidget = QtGui.QDockWidget()
        dockWidget.setWidget(self.NodeWidget)
        for category in ButtonDict:
            widget = QtGui.QWidget()
            layout = QtGui.QVBoxLayout(widget)
            layout.setAlignment(QtCore.Qt.AlignTop)
            layout.setSpacing(0)
            self.NodeWidget.addTab(widget, category)
            for node in ButtonDict[category]:
                layout.addWidget(BaseNodeButton(name=node, scene=self.scene, view=self.view, Node=ButtonDict[category][node]))
        return dockWidget

    def clean(self):
        self.scene = NodeScene()
        self.view.setScene(self.scene)

    def addToScene(self, object_class):
        object_class(self.scene)



class BaseNodeButton(QtGui.QPushButton):
    def __init__(self, name="BaseNode", scene=None, view=None, Node=value.BaseNode):
        super(BaseNodeButton, self).__init__(name)
        self.scene = scene
        self.view = view
        self.Node = Node
        self.clicked.connect(self.add)

    def add(self):
        add_item = self.Node(self.scene)
        self.view.add_item = add_item

