import Part
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
from nodeeditor import NodeProxyWidget, ManipulatorNodeWidget, BaseNode


class SketcherNode(BaseNode):
    def __init__(self, scene):
        super(SketcherNode, self).__init__(scene, "Sketch")
        self.sketch = None
        self.push = QtGui.QPushButton("Show Sketch")
        self.manipulator = ManipulatorNodeWidget(widget=self.push, outp=True,  scene=scene)
        self.document = ManipulatorNodeWidget(widget=QtGui.QLabel("document"), inp=True,  scene=scene)
        self.layout.addWidget(self.document)
        self.layout.addWidget(self.manipulator)
        self.add_to_scene()
        self.connect(self.push, QtCore.SIGNAL("clicked()"), self.show)
        self.manipulator.output = self.output

    def show(self):
        if self.document.input:
            doc = self.document.input
            if self.sketch is None:
                self.sketch = doc.addObject('Sketcher::SketchObject', 'Sketch')
            Gui.getDocument(doc.Name).setEdit(self.sketch.Name)
            Gui.activateWorkbench("SketcherWorkbench")

    def output(self):
        return(self.sketch)


class DocumentNode(BaseNode):
    def __init__(self, scene):
        super(DocumentNode, self).__init__(scene, "Document", "yellow")
        self.doc = None
        self.manipulator = ManipulatorNodeWidget(outp=True,  scene=scene)
        self.layout.addWidget(self.manipulator)
        self.add_to_scene()
        self.manipulator.output = self.output

    def output(self):
        if not self.doc:
            self.doc = App.newDocument()
        return self.doc


class ExtrudeNode(BaseNode):
    def __init__(self, scene):
        super(ExtrudeNode, self).__init__(scene, "Extrude", "blue")
        self.height = QtGui.QDoubleSpinBox()
        self.height.setValue(10)
        self.manipulator = ManipulatorNodeWidget(inp=True, outp=True, scene=scene)
        self.height_man =  ManipulatorNodeWidget(widget=self.height, inp=True, scene=scene)
        self.layout.addWidget(self.manipulator)
        self.layout.addWidget(self.height_man)
        self.add_to_scene()
        self.manipulator.output = self.output

    def output(self):
        sketch = self.manipulator.input
        if sketch:
            face =  Part.Face(sketch.Shape.Wires)
            h = self.height_man.input
            if h is None:
                h = self.height.value()
            self.height.setValue(h)
            shape = face.extrude(App.Vector(0,0,h))
            return shape


class SphereNode(BaseNode):
    def __init__(self, scene):
        super(SphereNode, self).__init__(scene=scene, titel="Sphere", color="yellow")
        self.radius = QtGui.QDoubleSpinBox()
        self.radius.setValue(3)
        self.sphere_manipulator = ManipulatorNodeWidget(widget=self.radius, outp=True,  scene=scene)
        self.radius.setValue(10.)
        self.layout.addWidget(self.sphere_manipulator)
        self.add_to_scene()
        self.sphere_manipulator.output = self.output

    def output(self):
        return Part.makeSphere(self.radius.value())

    def add_to(self, scene):
        item = NodeProxyWidget(self)
        scene.addItem(item)


class CylinderNode(SphereNode):
    def __init__(self, scene):
        super(CylinderNode, self).__init__(scene)
        self.titel.setText("Cylinder")
        self.c_height = QtGui.QDoubleSpinBox()
        self.c_height.setValue(10.)
        self.layout.addWidget(ManipulatorNodeWidget(widget=self.c_height))

    def output(self):
        return Part.makeCylinder(self.radius.value(), self.c_height.value())


class ViewerNode(BaseNode):
    def __init__(self, scene):
        super(ViewerNode, self).__init__(scene=scene, titel="Viewer", color="yellow")
        self.obj = None
        self.push = QtGui.QPushButton("show shape")
        self.manipulator = ManipulatorNodeWidget(widget=self.push, inp=True,  scene=scene)
        self.document = ManipulatorNodeWidget(widget=QtGui.QLabel("document"), inp=True,  scene=scene)
        self.layout.addWidget(self.manipulator)
        self.layout.addWidget(self.document)
        self.add_to_scene()
        self.connect(self.push, QtCore.SIGNAL("clicked()"), self.show)

    def show(self):
        if self.manipulator.input is not None:
            if self.document.input is not None:
                if not self.obj:
                    self.obj = self.document.input.addObject("Part::Feature", "item")
                self.obj.Shape = self.manipulator.input


class CutNode(BaseNode):
    def __init__(self, scene):
        super(CutNode, self).__init__(scene=scene, titel="Cut", color="blue")
        self.shape1 = ManipulatorNodeWidget(inp=True, outp=True,  scene=scene)
        self.shape2 = ManipulatorNodeWidget(inp=True,  scene=scene)
        self.layout.addWidget(self.shape1)
        self.layout.addWidget(self.shape2)
        self.shape1.output = self.output
        self.add_to_scene()

    def output(self):
        if None in (self.shape1.input, self.shape2.input):
            return None
        else:
            #both are shapes and have methode cut
            return self.shape1.input.cut(self.shape2.input)

ButtonDict = {
    "Sphere": SphereNode,
    "Cylinder": CylinderNode,
    "Cut": CutNode,
    "Viewer": ViewerNode,
    "Sketch": SketcherNode,
    "Extrude": ExtrudeNode,
    "Document": DocumentNode
}
