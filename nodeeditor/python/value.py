from PySide import QtGui, QtCore
from nodeeditor import NodeProxyWidget, SlotOutput, SlotInput, BaseNode


class SliderNode(BaseNode):
    def __init__(self, scene):
        super(SliderNode, self).__init__(scene=scene, title="SliderNode")
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
    "Slider": SliderNode,
    "GetValue": GetValueNode,
    "Add": AddNode,
    "List": ListNode
}
