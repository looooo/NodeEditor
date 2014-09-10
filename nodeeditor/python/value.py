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
        self.connect(self.press, QtCore.SIGNAL("clicked()"), self.set_value)
        self.outp_slot.output = self.output

    def set_value(self, val=None):
        val = val or self.inp_slot.input()
        self.val.setText(str(val))

    def output(self):
        inp = self.inp_slot.input()
        self.set_value(inp)
        return(inp)


class HelpNode(BaseNode):
    def __init__(self, scene):
        super(HelpNode, self).__init__(scene, "Help", "LightBlue")
        self.val = QtGui.QLabel()
        self.val.setAlignment(QtCore.Qt.AlignCenter)
        self.inp_slot = SlotInput(scene)
        self.press = QtGui.QPushButton()
        self.addWidget(self.press)
        self.addWidget(self.inp_slot, self.val)
        self.connect(self.press, QtCore.SIGNAL("clicked()"), self.set_value)

    def set_value(self, val=None):
        val = self.inp_slot.help_()
        self.val.setText(str(val))


class AddNode(BaseNode):
    def __init__(self, scene):
        super(AddNode, self).__init__(scene, "Add")
        self.val1_slot = SlotInput(scene)
        self.val2_slot = SlotInput(scene)
        self.out_slot = SlotOutput(scene)
        self.math = QtGui.QListWidget()
        self.addWidget(self.math)
        self.addWidget(self.val1_slot, QtGui.QLabel("value"))
        self.addWidget(self.val2_slot, QtGui.QLabel("value"))
        self.addWidget(self.out_slot, QtGui.QLabel("value"))
        self.out_slot.output = self.output

    def output(self):
        return self.val1_slot.input() + self.val2_slot.input()


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
                    if i.input() == None:
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
        arr = [i.input() for i in self.slot_list]
        return [i for i in arr if i is not None]


class LoopNode(BaseNode):
    def __init__(self, scene):
        super(LoopNode, self).__init__(scene, "Loop", "red")
        self.iter_max_slot = SlotInput(scene)
        self.iter_max = QtGui.QSpinBox()
        self.input_slot = SlotInput(scene)
        self.loop_input = SlotInput(scene)
        self.loop_output_slot = SlotOutput(scene)
        self.output_slot = SlotOutput(scene)

        self.iter_max = QtGui.QSpinBox()
        self.iter_max.setValue(0)

        self.addWidget(self.iter_max_slot, self.iter_max)
        self.addWidget(self.input_slot, QtGui.QLabel("object in"))
        self.addWidget(self.loop_output_slot, QtGui.QLabel("loop_object"), self.loop_input)
        self.addWidget(self.output_slot, QtGui.QLabel("object_out"))
        self.arr = []
        self.iter = 0
        self.output_slot.output = self.output
        self.loop_output_slot.output = self.loop_output

    def output(self):
        self.iter = 0
        print("enter loop")
        thing = self.loop_input.input()
        self.arr.append(thing)
        print("exit loop")
        return self.arr

    def loop_output(self):
        iter_max = self.iter_max_slot.input() or self.iter_max.value()
        print("iter_max", iter_max)
        print("iter", self.iter)
        if self.iter < iter_max:
            self.iter += 1
            thing = self.loop_input.input()
            self.arr.append(thing)
        else:
            # self.arr = []
            thing = self.input_slot.input()
            self.arr = []
            self.arr.append(thing)
        return thing


ButtonDict = {
    "Slider": SliderNode,
    "GetValue": GetValueNode,
    "Add": AddNode,
    "List": ListNode,
    "Loop": LoopNode,
    "Help": HelpNode    
}
