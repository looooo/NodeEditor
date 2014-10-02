import Part
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
from nodeeditor import BaseNode
from nodeeditor.freecad import slots
from nodeeditor import Gui as gui


#TOTO:
#SelectionNode
#RevolveNode
#FilletNode


class SketcherNode(BaseNode):
    """you have to connect this node to a document and thn click the button to create the sketch...."""
    def __init__(self, scene):
        super(SketcherNode, self).__init__(scene, "Sketch")
        self.sketch = None
        self.push = gui.PushButton("Show Sketch")
        self.scetch_slot = slots.SlotOutput(scene)
        self.doc_slot = slots.DocumentInput(scene)
        self.addItem(self.doc_slot, gui.Label("Document"))
        self.addItem(self.scetch_slot, self.push)

        # show constraint-properties:
        self.constraints = []   #widget_pos_list
        self.show_constraints = gui.PushButton("show constraints")
        self.addItem(self.show_constraints)
        self.show_constraints.clicked.connect(self.add_constraint_slots)
        self.push.clicked.connect(self.show)
        self.scetch_slot.output = self.output

    def show(self):
        self.update_constraints()
        doc = self.doc_slot.input()
        if doc:
            if self.sketch is None:
                self.sketch = doc.addObject('Sketcher::SketchObject', 'Sketch')
            Gui.getDocument(doc.Name).setEdit(self.sketch.Name)
            Gui.activateWorkbench("SketcherWorkbench")

    def output(self):
        self.update_constraints()
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

    def add_constraint_slots(self):
        if self.sketch:
            del_pos = []
            constraints = [i for i in self.sketch.getPropertyByName("Constraints") if i.Name != ""]
            constraints_names = [i.Name for i in constraints]
            for i_pos, i in enumerate(self.constraints):
                if i[0].Name in constraints_names:
                    ind = constraints_names.index(i[0].Name)
                    constraints.pop(ind)
                    constraints_names.pop(ind)
                    # update upstream
                else:
                    self.removeWidget(i[1])
                    self.removeWidget(i[2])
                    del_pos.append(i_pos)
            for i in del_pos:
                self.constraints.pop(i)
            for i in constraints:
                label = gui.Label(i.Name)
                slot = slots.SlotInput(self.scene)
                slot.setParent(self)
                self.constraints.append([i, label, slot])
                self.addItem(label, slot)

    def update_constraints(self):
        doc = self.doc_slot.input()
        for constraint, label, slot in self.constraints:
            inp = slot.input()
            print(constraint.Name, inp)
            if inp is not None:
                self.sketch.setDatum(constraint.Name, inp)
        if doc is not None:
            doc.recompute()


class DocumentNode(BaseNode):
    """this is a document Node."""
    def __init__(self, scene):
        super(DocumentNode, self).__init__(scene, "document")
        self.doc = None
        self.output_slot = slots.DocumentOutput(scene)
        self.press = gui.PushButton('show document')
        self.addItem(self.output_slot)
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
        # self.back_to_nodes()


class ExtrudeNode(BaseNode):
    """extrudes a scetch by given value in Z-direction"""

    def __init__(self, scene):
        super(ExtrudeNode, self).__init__(scene, "extrude")
        self.height = gui.DoubleSpinBox()
        self.height.setValue(10)
        self.sketch_slot = slots.SlotInput(scene)
        self.height_slot = slots.SlotInput(scene)
        self.shape_out = slots.ShapeOutput(scene)
        self.addItem(self.height, self.height_slot)
        self.addItem(self.sketch_slot, gui.Label("sketch"))
        self.addItem(self.shape_out, gui.Label("shape"))
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
        self.angle = gui.DoubleSpinBox()
        self.angle.setMaximum(360)
        self.angle.setValue(360)
        self.sketch_slot = slots.SlotInput(scene)
        self.angle_slot = slots.SlotInput(scene)
        self.point_slot = slots.SlotInput(scene)
        self.vector_slot = slots.SlotInput(scene)
        self.shape_out = slots.ShapeOutput(scene)
        self.addItem(self.angle, self.angle_slot)
        self.addItem(self.point_slot, gui.Label("Point"))
        self.addItem(self.vector_slot, gui.Label("Vector"))
        self.addItem(self.sketch_slot, gui.Label("sketch"))
        self.addItem(self.shape_out, gui.Label("shape"))
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
        self.push = gui.PushButton("show shape")
        self.shape_slot = slots.ShapeInput(scene)
        self.doc_slot = slots.DocumentInput(scene)
        self.addItem(self.push)
        self.addItem(self.shape_slot, gui.Label('shape'))
        self.addItem(self.doc_slot, gui.Label('document'))
        self.push.clicked.connect(self.show)

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
        self.addItem(self.shape1_slot, gui.Label('shape'))
        self.addItem(self.shape2_slot, gui.Label('shape'))
        self.addItem(self.out_slot, gui.Label('shape'))
        self.out_slot.output = self.output

    def output(self):
        shp1 = self.shape1_slot.input()
        shp2 = self.shape2_slot.input()
        if None in (shp1, shp2):
            return None
        else:
            #both are shapes and have methode cut
            return shp1.cut(shp2)


# class SelectionNode(BaseNode):
#     """connect a document and a shape and select which element shold be passed to the next node"""
#     def __init__(self, scene):
#         super(SelectionNode, self).__init__(scene, "Selection")
#         self.doc_in = slots.SlotInput(scene)
#         self.shape_in = slots.ShapeInput(scene)
#         self.shape_out = slots.ShapeOutput(scene)
#         self.selection_out = slots.SlotOutput(scene)
#         self.show = QtGui.QPushButton("Select")
#         self.addItem(self.shape_in, self.shape_out, QtGui.QLabel("Shape"))
#         self.addItem(self.doc_in, self.selection_out, self.show)


# class ChamferNode(BaseNode):
#     """chamfer on a edge"""
#     pass

ButtonDict = {
    "Cut": CutNode,
    "Viewer": ViewerNode,
    "Sketch": SketcherNode,
    "Extrude": ExtrudeNode,
    "Revolve": RevolveNode,
    "Document": DocumentNode,
    # "Chamfer": ChamferNode,
    # "Selection": SelectionNode
}
