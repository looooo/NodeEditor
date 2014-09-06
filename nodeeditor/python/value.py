from PySide import QtGui, QtCore
from nodeeditor import NodeProxyWidget, SlotOutput, SlotInput, BaseNode


class SliderNode(BaseNode):
    def __init__(self, scene):
        super(SliderNode, self).__init__(scene=scene, titel="SliderNode")
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.outp_slot = SlotOutput(scene)
        self.value = QtGui.QLabel(str(self.slider.value()))
        self.value.setAlignment(QtCore.Qt.AlignCenter)
        self.addWidget(self.slider)
        self.addWidget(self.value, self.outp_slot)
        self.connect(self.slider, QtCore.SIGNAL("valueChanged(int)"), self.set_value)
        self.outp_slot.output = self.output

    def output(self):
        return self.slider.value()

    def set_value(self, val):
        self.value.setText(str(val))


class GetValueNode(BaseNode):
    def __init__(self, scene):
        super(GetValueNode, self).__init__(scene, "GetValue")
        self.val = QtGui.QLabel()
        self.val.setAlignment(QtCore.Qt.AlignCenter)
        self.inp_slot = SlotInput(scene)
        self.outp_slot = SlotOutput(scene)
        self.press = QtGui.QPushButton()
        self.addWidget(self.press)
        self.addWidget(self.inp_slot, self.val, self.outp_slot)
        self.set_value()
        self.connect(self.press, QtCore.SIGNAL("clicked()"), self.set_value)
        self.outp_slot.output = self.output

    def set_value(self):
        self.val.setText(str(self.inp_slot.input))

    def output(self):
        self.set_value()
        return(self.inp_slot.input)


class AddNode(BaseNode):
    def __init__(self, scene):
        super(AddNode, self).__init__(scene, "Add")
        self.val1_slot = SlotInput(scene)
        self.val2_slot = SlotInput(scene)
        self.out_slot = SlotOutput(scene)
        self.addWidget(self.val1_slot, QtGui.QLabel("value"))
        self.addWidget(self.val2_slot, QtGui.QLabel("value"))
        self.addWidget(self.out_slot, QtGui.QLabel("value"))
        self.out_slot.output = self.output

    def output(self):
        if self.val1_slot.input is not None and self.val2_slot.input is not None:
            return self.val1_slot.input + self.val2_slot.input
        return 0.


ButtonDict = {
    "Slider": SliderNode,
    "GetValue": GetValueNode,
    "Add": AddNode
}
