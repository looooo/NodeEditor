import Part
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
from nodeeditor import NodeProxyWidget, BaseNode, SlotInput, SlotOutput


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
        self.addWidget(self.output_slot, self.press)
        self.output_slot.output = self.output
        self.connect(self.press, QtCore.SIGNAL('clicked()'), self.show_doc)

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
        self.shape_out = SlotOutput(scene)
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


class SphereNode(BaseNode):
    def __init__(self, scene):
        super(SphereNode, self).__init__(scene, "sphere", "yellow")
        self.radius = QtGui.QDoubleSpinBox()
        self.radius.setValue(3)
        self.radius_slot = SlotInput(scene)
        self.shape_out = SlotOutput(scene)
        self.addWidget(self.radius, self.radius_slot)
        self.addWidget(self.shape_out, QtGui.QLabel('shape'))
        self.shape_out.output = self.output

    def output(self):
        r = self.radius_slot.input or self.radius.value()
        self.radius.setValue(r)
        return Part.makeSphere(r)


class CylinderNode(BaseNode):
    def __init__(self, scene):
        super(CylinderNode, self).__init__(scene, "cylinder", "yellow")
        self.height = QtGui.QDoubleSpinBox()
        self.height.setValue(10.)
        self.height_slot = SlotInput(scene)
        self.radius = QtGui.QDoubleSpinBox()
        self.radius.setValue(3)
        self.radius_slot = SlotInput(scene)
        self.shape_out = SlotOutput(scene)
        self.addWidget(self.height, self.height_slot)
        self.addWidget(self.radius, self.radius_slot)
        self.addWidget(self.shape_out, QtGui.QLabel('shape'))
        self.shape_out.output = self.output

    def output(self):
        h = self.height_slot.input or self.height.value()
        r = self.radius_slot.input or self.radius.value()
        self.height.setValue(h)
        self.radius.setValue(r)
        return Part.makeCylinder(r, h)


class ViewerNode(BaseNode):
    def __init__(self, scene):
        super(ViewerNode, self).__init__(scene, "viewer", "yellow")
        self.obj = None
        self.push = QtGui.QPushButton("show shape")
        self.shape_slot = SlotInput(scene)
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
        self.shape1_slot = SlotInput(scene)
        self.shape2_slot = SlotInput(scene)
        self.out_slot = SlotOutput(scene)
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
    "Sphere": SphereNode,
    "Cylinder": CylinderNode,
    "Cut": CutNode,
    "Viewer": ViewerNode,
    "Sketch": SketcherNode,
    "Extrude": ExtrudeNode,
    "Document": DocumentNode
}
