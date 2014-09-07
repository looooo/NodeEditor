import Part
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
from nodeeditor import BaseNode, SlotInput, SlotOutput
from nodeeditor.freecad.slots import ShapeInput, ShapeOutput


#TOTO:
#SelectionNode
#RevolveNode
#FilletNode


class SketcherNode(BaseNode):
    def __init__(self, scene):
        super(SketcherNode, self).__init__(scene, "Sketch", "pink")
        self.sketch = None
        self.push = QtGui.QPushButton("Show Sketch")
        self.scetch_slot = SlotOutput(scene)
        self.doc_slot = SlotInput(scene)
        self.addWidget(self.doc_slot, QtGui.QLabel("Document"))
        self.addWidget(self.scetch_slot, self.push)
        self.connect(self.push, QtCore.SIGNAL("clicked()"), self.show)
        self.scetch_slot.output = self.output

    def show(self):
        if self.doc_slot.input:
            doc = self.doc_slot.input
            if self.sketch is None:
                self.sketch = doc.addObject('Sketcher::SketchObject', 'Sketch')
            Gui.getDocument(doc.Name).setEdit(self.sketch.Name)
            Gui.activateWorkbench("SketcherWorkbench")

    def output(self):
        return(self.sketch)

    def delete(self):
        if self.sketch:
            if self.doc_slot.input:
                self.doc_slot.input.removeObject(self.sketch.Name)
        super(SketcherNode, self).delete()


class DocumentNode(BaseNode):
    def __init__(self, scene):
        super(DocumentNode, self).__init__(scene, "document", "green")
        self.doc = None
        self.output_slot = SlotOutput(scene)
        self.press = QtGui.QPushButton('show document')
        # self.addWidget(self.output_slot, self.press)
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
        self.doc = App.newDocument()
        super(DocumentNode, self).add_to_scene()
        self.back_to_nodes()


class ExtrudeNode(BaseNode):
    def __init__(self, scene):
        super(ExtrudeNode, self).__init__(scene, "extrude", "blue")
        self.height = QtGui.QDoubleSpinBox()
        self.height.setValue(10)
        self.sketch_slot = SlotInput(scene)
        self.height_slot = SlotInput(scene)
        self.shape_out = ShapeOutput(scene)
        self.addWidget(self.height, self.height_slot)
        self.addWidget(self.sketch_slot, QtGui.QLabel("sketch"))
        self.addWidget(self.shape_out, QtGui.QLabel("shape"))
        self.shape_out.output = self.output

    def output(self):
        if self.height_slot.input:
            self.height.hide()
        sketch = self.sketch_slot.input
        if sketch:
            face = Part.Face(sketch.Shape.Wires)
            h = self.height_slot.input or self.height.value()
            self.height.setValue(h)
            shape = face.extrude(App.Vector(0, 0, h))
            return shape


class RevolveNode(BaseNode):
    def __init__(self, scene):
        super(RevolveNode, self).__init__(scene, "revolution", "blue")
        self.angle = QtGui.QDoubleSpinBox()
        self.angle.setMaximum(360)
        self.angle.setValue(360)
        self.sketch_slot = SlotInput(scene)
        self.angle_slot = SlotInput(scene)
        self.point_slot = SlotInput(scene)
        self.vector_slot = SlotInput(scene)
        self.shape_out = ShapeOutput(scene)
        self.addWidget(self.angle, self.angle_slot)
        self.addWidget(self.point_slot, QtGui.QLabel("Point"))
        self.addWidget(self.vector_slot, QtGui.QLabel("Vector"))
        self.addWidget(self.sketch_slot, QtGui.QLabel("sketch"))
        self.addWidget(self.shape_out, QtGui.QLabel("shape"))
        self.shape_out.output = self.output

    def output(self):
        if self.angle_slot.input:
            self.angle.hide()
        sketch = self.sketch_slot.input
        if sketch:
            face = Part.Face(sketch.Shape.Wires)
            alpha = self.angle_slot.input or self.angle.value()
            self.angle.setValue(alpha)
            p = self.point_slot.input or App.Vector(0, 0, 0)
            v = self.vector_slot.input or App.Vector(0, 1, 0)
            shape = face.revolve(p, v, alpha)
            return shape


class ViewerNode(BaseNode):
    def __init__(self, scene):
        super(ViewerNode, self).__init__(scene, "viewer", "yellow")
        self.obj = None
        self.push = QtGui.QPushButton("show shape")
        self.shape_slot = ShapeInput(scene)
        self.doc_slot = SlotInput(scene)
        self.addWidget(self.push)
        self.addWidget(self.shape_slot, QtGui.QLabel('shape'))
        self.addWidget(self.doc_slot, QtGui.QLabel('document'))
        self.connect(self.push, QtCore.SIGNAL("clicked()"), self.show)

    def show(self):
        if self.doc_slot.input is not None:
            if self.shape_slot.input is not None:
                if not self.obj:
                    self.obj = self.doc_slot.input.addObject("Part::Feature", "item")
                self.obj.Shape = self.shape_slot.input
            else:
                if self.obj:
                    self.doc_slot.input.removeObject(self.obj.Name)
                    self.obj = None
        else:
            self.obj = None

    def delete(self):
        print("loeschen startet")
        if self.doc_slot.input is not None:
            print(1)
            if self.obj is not None:
                print("jskdfnskjfn")
                self.doc_slot.input.removeObject(self.obj.Name)
        super(ViewerNode, self).delete()


class CutNode(BaseNode):
    def __init__(self, scene):
        super(CutNode, self).__init__(scene, "Cut", "blue")
        self.shape1_slot = ShapeInput(scene)
        self.shape2_slot = ShapeInput(scene)
        self.out_slot = ShapeOutput(scene)
        self.addWidget(self.shape1_slot, QtGui.QLabel('shape'))
        self.addWidget(self.shape2_slot, QtGui.QLabel('shape'))
        self.addWidget(self.out_slot, QtGui.QLabel('shape'))
        self.out_slot.output = self.output

    def output(self):
        if None in (self.shape1_slot.input, self.shape2_slot.input):
            return None
        else:
            #both are shapes and have methode cut
            return self.shape1_slot.input.cut(self.shape2_slot.input)
            

ButtonDict = {
    "Cut": CutNode,
    "Viewer": ViewerNode,
    "Sketch": SketcherNode,
    "Extrude": ExtrudeNode,
    "Revolve": RevolveNode,
    "Document": DocumentNode
}
