from nodeeditor import BaseNode
from nodeeditor.freecad.slots import SlotInput, SlotOutput, ShapeOutput, ShapeInput
from PySide import QtCore, QtGui
import FreeCAD as App


class VectorNode(BaseNode):
    def __init__(self, scene):
        super(VectorNode, self).__init__(scene=scene, title="Vector")
        self.x = QtGui.QDoubleSpinBox()
        self.y = QtGui.QDoubleSpinBox()
        self.z = QtGui.QDoubleSpinBox()
        self.slot_out = SlotOutput(scene)
        [self.addWidget(i) for i in (self.x, self.y, self.z)]
        self.addWidget(self.slot_out)
        self.slot_out.output = self.output

    def output(self):
        return App.Vector(self.x.value(), self.y.value(), self.z.value())


class MatrixNode(BaseNode):
    def __init__(self, scene):
        super(MatrixNode, self).__init__(scene=scene, title="Matrix")
        self.xx = QtGui.QDoubleSpinBox()
        self.xy = QtGui.QDoubleSpinBox()
        self.xz = QtGui.QDoubleSpinBox()
        self.xw = QtGui.QDoubleSpinBox()
        self.yx = QtGui.QDoubleSpinBox()
        self.yy = QtGui.QDoubleSpinBox()
        self.yz = QtGui.QDoubleSpinBox()
        self.yw = QtGui.QDoubleSpinBox()     
        self.zx = QtGui.QDoubleSpinBox()
        self.zy = QtGui.QDoubleSpinBox()
        self.zz = QtGui.QDoubleSpinBox()
        self.zw = QtGui.QDoubleSpinBox()
        self.wx = QtGui.QDoubleSpinBox()
        self.wy = QtGui.QDoubleSpinBox()
        self.wz = QtGui.QDoubleSpinBox()
        self.ww = QtGui.QDoubleSpinBox()
        self.xx.setValue(1)
        self.yy.setValue(1)
        self.zz.setValue(1)
        self.ww.setValue(1)
        self.Qmat = [[self.xx, self.xy, self.xz, self.xw],
                     [self.yx, self.yy, self.yz, self.yw],
                     [self.zx, self.zy, self.zz, self.zw],
                     [self.wx, self.wy, self.wz, self.ww]]
        self.slot_out = SlotOutput(scene)
        for i, row in enumerate(self.Qmat):
            for j, wid in enumerate(row):
                self.layout.addWidget(wid, i+1, j)
        self.layout.addWidget(self.slot_out, 6, 5)
        self.slot_out.output = self.output

    def output(self):
        return App.Matrix(*[j.value() for i in self.Qmat for j in i])


class apply_matrix(BaseNode):
    def __init__(self, scene):
        super(apply_matrix, self).__init__(scene=scene, title="apply matrix")
        self.mat_input = SlotInput(scene)
        self.shp_input = ShapeInput(scene)
        self.shp_output = ShapeOutput(scene)
        self.addWidget(self.mat_input, QtGui.QLabel("matrix"))
        self.addWidget(self.shp_input, QtGui.QLabel("shape"))
        self.addWidget(self.shp_output, QtGui.QLabel("shape"))
        self.shp_output.output = self.output


    def output(self):
        if self.shp_input is not None:
            mat = self.mat_input.input or App.Matrix()
            return self.shp_input.input.transformGeometry(mat)


class ListNode(BaseNode):
    def __init__(self, scene):
        super(ListNode, self).__init__(scene=scene, title="List")
        slot = SlotInput(scene)
        slot.setParent(self)
        self.push = QtGui.QPushButton()
        slot.got_connected = self.update_slots
        self.slot_list = [slot]
        self.slot_out = SlotOutput(scene)
        self.addWidget(self.push)
        self.addWidget(self.slot_out)
        self.layout.addWidget(self.slot_list[0], 3, 0)
        self.slot_out.output = self.output
        self.connect(self.push, QtCore.SIGNAL("clicked()"), self.update_slots)

    def update_slots(self):
        if len(self.slot_list) == 1 and self.slot_list[0].input is None:
            return
        else:
            for i in self.children():
                if isinstance(i, SlotInput):
                    print(i.input)
                    if i.input == None:
                        if i in self.scene.node_list:
                            self.scene.node_list.remove(i)
                        else:
                            print("jezt")
                        if i in self.slot_list:
                            self.slot_list.remove(i)
                        self.layout.removeWidget(i)
                        i.deleteLater()
            slot = SlotInput(self.scene)
            slot.got_connected = self.update_slots
            slot.setParent(self)
            self.slot_list.append(slot)
            self.layout.addWidget(slot, self.layout.rowCount() + 2, 0)
            self.adjustSize()
            self.update_lines()

    def output(self):
        return [i.input for i in self.slot_list if i.input is not None]


ButtonDict = {
    "Vector": VectorNode,
    "Matrix": MatrixNode,
    "Apply Matrix": apply_matrix,
    "List": ListNode
    }
