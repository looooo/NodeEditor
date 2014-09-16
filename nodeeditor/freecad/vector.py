from nodeeditor import BaseNode
from nodeeditor.freecad import slots
from PySide import QtCore, QtGui
import FreeCAD as App


class VectorNode(BaseNode):
    def __init__(self, scene):
        super(VectorNode, self).__init__(scene=scene, title="Vector")
        self.x = QtGui.QDoubleSpinBox()
        self.y = QtGui.QDoubleSpinBox()
        self.z = QtGui.QDoubleSpinBox()
        self.slot_out = slots.SlotOutput(scene)
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
        self.slot_out = slots.SlotOutput(scene)
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
        self.mat_input = slots.SlotInput(scene)
        self.shp_input = slots.ShapeInput(scene)
        self.shp_output = slots.ShapeOutput(scene)
        self.addWidget(self.mat_input, QtGui.QLabel("matrix"))
        self.addWidget(self.shp_input, QtGui.QLabel("shape"))
        self.addWidget(self.shp_output, QtGui.QLabel("shape"))
        self.shp_output.output = self.output


    def output(self):
        shp = self.shp_input.input()
        if shp:
            mat = self.mat_input.input() or App.Matrix()
            return shp.transformGeometry(mat)



ButtonDict = {
    "Vector": VectorNode,
    "Matrix": MatrixNode,
    "Apply Matrix": apply_matrix,
    }
