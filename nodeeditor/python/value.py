from PySide import QtGui, QtCore
from nodeeditor import NodeProxyWidget, ManipulatorNodeWidget, BaseNode


class SliderNode(BaseNode):
    def __init__(self, scene):
        super(SliderNode, self).__init__(scene=scene, titel="SliderNode")
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider_manipulator = ManipulatorNodeWidget(widget=self.slider, outp=True,  scene=scene)
        self.value = QtGui.QLabel(str(self.slider.value()))
        self.value.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.slider_manipulator)
        self.layout.addWidget(self.value)
        self.connect(self.slider, QtCore.SIGNAL("valueChanged(int)"), self.set_value)
        self.slider_manipulator.output = self.output
        self.add_to_scene()

    def output(self):
        return self.slider.value()

    def set_value(self, val):
        self.value.setText(str(val))


class GetValueNode(BaseNode):
    def __init__(self, scene):
        super(GetValueNode, self).__init__(scene, "GetValue")
        self.val = QtGui.QLabel()
        self.inp = ManipulatorNodeWidget(widget=self.val, inp=True, scene=scene)
        self.press = QtGui.QPushButton("Calculate Value")
        self.layout.addWidget(self.val)
        self.layout.addWidget(self.inp)
        self.layout.addWidget(self.press)
        self.val.setAlignment(QtCore.Qt.AlignCenter)
        self.connect(self.press, QtCore.SIGNAL("clicked()"), self.set_value)
        self.add_to_scene()

    def set_value(self):
        self.val.setText(str(self.inp.input))


class AddNode(BaseNode):
    def __init__(self, scene):
        super(AddNode, self).__init__(scene, "Add")
        self.val1 = ManipulatorNodeWidget(inp=True, scene=scene)
        self.val2 = ManipulatorNodeWidget(inp=True, scene=scene)
        self.out = ManipulatorNodeWidget(outp=True, scene=scene)
        self.layout.addWidget(self.val1)
        self.layout.addWidget(self.val2)
        self.layout.addWidget(self.out)
        self.out.output = self.output
        self.add_to_scene()

    def output(self):
        if self.val1.input is not None and self.val2.input is not None:
            return self.val1.input + self.val2.input
        return 0.


class MultNode(AddNode):
    def __init__(self, scene):
        super(MultNode, self).__init__(scene)
        self.titel.setText("Multply")

    def output(self):
        if self.val1.input is not None and self.val2.input is not None:
            return self.val1.input * self.val2.input
        return 0.


ButtonDict = {
    "Slider": SliderNode,
    "GetValue": GetValueNode,
    "Add": AddNode
}
