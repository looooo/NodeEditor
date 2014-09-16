import Part
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
from nodeeditor import BaseNode
from nodeeditor.freecad import slots


#TOTO:
#SelectionNode
#RevolveNode
#FilletNode


class SketcherNode(BaseNode):
    """you have to connect this node to a document and thn click the button to create the sketch...."""
    def __init__(self, scene):
        super(SketcherNode, self).__init__(scene, "Sketch")
        self.sketch = None
        self.push = QtGui.QPushButton("Show Sketch")
        self.scetch_slot = slots.SlotOutput(scene)
        self.doc_slot = slots.DocumentInput(scene)
        self.addWidget(self.doc_slot, QtGui.QLabel("Document"))
        self.addWidget(self.scetch_slot, self.push)
        self.connect(self.push, QtCore.SIGNAL("clicked()"), self.show)
        self.scetch_slot.output = self.output

    def show(self):
        doc = self.doc_slot.input()
        if doc:
            if self.sketch is None:
                self.sketch = doc.addObject('Sketcher::SketchObject', 'Sketch')
            Gui.getDocument(doc.Name).setEdit(self.sketch.Name)
            Gui.activateWorkbench("SketcherWorkbench")

    def output(self):
        return self.sketch

    def delete(self):
        doc = self.doc_slot.input()
        if self.sketch:
            if doc:
                try:
                    doc.removeObject(self.sketch.Name)
                except Exception:
                    pass
        super(SketcherNode, self).delete()

class DocumentNode(BaseNode):
    """this is a document Node."""
    def __init__(self, scene):
        super(DocumentNode, self).__init__(scene, "document")
        self.doc = None
        self.output_slot = slots.DocumentOutput(scene)
        self.press = QtGui.QPushButton('show document')
        self.addWidget(self.output_slot)
        self.output_slot.output = self.output
        # self.connect(self.press, QtCore.SIGNAL('clicked()'), self.show_doc)

    def output(self):
        return self.doc

    def delete(self):
        super(DocumentNode, self).delete()
        if self.doc:
            App.closeDocument(self.doc.Name)

    def show_doc(self):
        print("haha") #TODO
        # Gui.ActiveDocument = Gui.getDocument(self.doc.Name).setEdit()

    def add_to_scene(self):
        super(DocumentNode, self).add_to_scene()
        self.doc = App.newDocument()
        self.back_to_nodes()


class ExtrudeNode(BaseNode):
    """extrudes a scetch by given value in Z-direction"""

    def __init__(self, scene):
        super(ExtrudeNode, self).__init__(scene, "extrude")
        self.height = QtGui.QDoubleSpinBox()
        self.height.setValue(10)
        self.sketch_slot = slots.SlotInput(scene)
        self.height_slot = slots.SlotInput(scene)
        self.shape_out = slots.ShapeOutput(scene)
        self.addWidget(self.height, self.height_slot)
        self.addWidget(self.sketch_slot, QtGui.QLabel("sketch"))
        self.addWidget(self.shape_out, QtGui.QLabel("shape"))
        self.shape_out.output = self.output

    def output(self):
        height = self.height_slot.input()
        if height:
            self.height.hide()
        sketch = self.sketch_slot.input()
        if sketch:
            face = Part.Face(sketch.Shape.Wires)
            h = height or self.height.value()
            self.height.setValue(h)
            shape = face.extrude(App.Vector(0, 0, h))
            return shape


class RevolveNode(BaseNode):
    """revolve the sketch"""
    def __init__(self, scene):
        super(RevolveNode, self).__init__(scene, "revolution")
        self.angle = QtGui.QDoubleSpinBox()
        self.angle.setMaximum(360)
        self.angle.setValue(360)
        self.sketch_slot = slots.SlotInput(scene)
        self.angle_slot = slots.SlotInput(scene)
        self.point_slot = slots.SlotInput(scene)
        self.vector_slot = slots.SlotInput(scene)
        self.shape_out = slots.ShapeOutput(scene)
        self.addWidget(self.angle, self.angle_slot)
        self.addWidget(self.point_slot, QtGui.QLabel("Point"))
        self.addWidget(self.vector_slot, QtGui.QLabel("Vector"))
        self.addWidget(self.sketch_slot, QtGui.QLabel("sketch"))
        self.addWidget(self.shape_out, QtGui.QLabel("shape"))
        self.shape_out.output = self.output

    def output(self):
        angle = self.angle_slot.input()
        sketch = self.sketch_slot.input()
        point = self.point_slot.input() or App.Vector(0, 0, 0)
        vector = self.vector_slot.input() or App.Vector(1, 0, 0)

        if angle:
            self.angle.hide()
        if sketch:
            face = Part.Face(sketch.Shape.Wires)
            alpha = angle or self.angle.value()
            shape = face.revolve(point, vector, alpha)
            return shape


class ViewerNode(BaseNode):
    """shows an object on the given document.
 if it is a list, the reference will be deleted"""

    def __init__(self, scene):
        super(ViewerNode, self).__init__(scene, "viewer")
        self.obj = None
        self.push = QtGui.QPushButton("show shape")
        self.shape_slot = slots.ShapeInput(scene)
        self.doc_slot = slots.DocumentInput(scene)
        self.addWidget(self.push)
        self.addWidget(self.shape_slot, QtGui.QLabel('shape'))
        self.addWidget(self.doc_slot, QtGui.QLabel('document'))
        self.connect(self.push, QtCore.SIGNAL("clicked()"), self.show)

    def show(self):
        doc = self.doc_slot.input()
        shape = self.shape_slot.input() 
        if doc:
            if shape:
                if not self.obj:
                    self.obj = doc.addObject("Part::Feature")
                if isinstance(shape, list):
                    for i in shape:
                        Part.show(i)
                self.obj.Shape = shape
            else:
                if self.obj:
                    doc.removeObject(self.obj.Name)
                    self.obj = None
        else:
            self.obj = None

    def delete(self):
        doc = self.doc_slot.input()
        if doc:
            if self.obj:
                doc.removeObject(self.obj.Name)
        super(ViewerNode, self).delete()


class CutNode(BaseNode):
    """Cut the second shape from the first"""

    def __init__(self, scene):
        super(CutNode, self).__init__(scene, "Cut")
        self.shape1_slot = slots.ShapeInput(scene)
        self.shape2_slot = slots.ShapeInput(scene)
        self.out_slot = slots.ShapeOutput(scene)
        self.addWidget(self.shape1_slot, QtGui.QLabel('shape'))
        self.addWidget(self.shape2_slot, QtGui.QLabel('shape'))
        self.addWidget(self.out_slot, QtGui.QLabel('shape'))
        self.out_slot.output = self.output

    def output(self):
        shp1 = self.shape1_slot.input()
        shp2 = self.shape2_slot.input()
        if None in (shp1, shp2):
            return None
        else:
            #both are shapes and have methode cut
            return shp1.cut(shp2)


class SelectionNode(BaseNode):
    """connect a document and a shape and select which element shold be passed to the next node"""
    def __init__(self, scene):
        super(SelectionNode, self).__init__(scene, "Selection")
        self.doc_in = slots.SlotInput(scene)
        self.shape_in = slots.ShapeInput(scene)
        self.shape_out = slots.ShapeOutput(scene)
        self.selection_out = slots.SlotOutput(scene)
        self.show = QtGui.QPushButton("Select")
        self.addWidget(self.shape_in, self.shape_out, QtGui.QLabel("Shape"))
        self.addWidget(self.doc_in, self.selection_out, self.show)


class ChamferNode(BaseNode):
    """chamfer on a edge"""
    pass

ButtonDict = {
    "Cut": CutNode,
    "Viewer": ViewerNode,
    "Sketch": SketcherNode,
    "Extrude": ExtrudeNode,
    "Revolve": RevolveNode,
    "Document": DocumentNode,
    "Chamfer": ChamferNode,
    "Selection": SelectionNode
}
