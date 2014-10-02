from PySide import QtGui, QtCore
from nodeeditor import SlotOutput, SlotInput, BaseNode
from nodeeditor import Gui


class SliderNode(BaseNode):
    "Returns a single value"
    def __init__(self, scene):
        super(SliderNode, self).__init__(scene=scene, title="SliderNode")
        self.slider = Gui.Slider(QtCore.Qt.Horizontal)
        self.outp_slot = SlotOutput(scene)
        self.value = Gui.Label(str(self.slider.value()))
        self.addItem(self.slider)
        self.addItem(self.value, self.outp_slot)
        self.slider.valueChanged.connect(self.set_value)
        self.outp_slot.output = self.output

    def output(self):
        return self.slider.value()

    def set_value(self, val):
        self.value.setText(str(val))


class GetValueNode(BaseNode):
    """Shows the output of the connected Node."""

    def __init__(self, scene):
        super(GetValueNode, self).__init__(scene, "GetValue")
        self.val = Gui.Label()
        self.inp_slot = SlotInput(scene)
        self.outp_slot = SlotOutput(scene)
        self.press = Gui.PushButton("press")
        self.addItem(self.press)
        self.addItem(self.inp_slot, self.val, self.outp_slot)
        self.press.clicked.connect(self.set_value)
        self.outp_slot.output = self.output

    def set_value(self, val=None):
        val = val or self.inp_slot.input()
        self.val.setText(str(val))

    def output(self):
        inp = self.inp_slot.input()
        self.set_value(inp)
        return inp or 0


class HelpNode(BaseNode):
    """This Node provides some information if
 you connect it to a Nodes output."""

    def __init__(self, scene):
        super(HelpNode, self).__init__(scene, "Help", "LightBlue")
        self.val = Gui.TextEdit()
        self.val.sizeHint = self.text_sizeHint
        self.val.setMinimumSize(200, 50)
        self.val.setReadOnly(True)
        self.val.setAlignment(QtCore.Qt.AlignCenter)
        self.inp_slot = SlotInput(scene)
        self.press = Gui.PushButton()
        self.addItem(self.press)
        self.addItem(self.inp_slot, self.val)
        self.press.clicked.connect(self.set_value)
        self.set_value()

    def set_value(self, val=None):
        val = self.inp_slot.help_() or self.__doc__
        self.val.setText(str(val))
        self.adjustSize()
        self.update()

    def text_sizeHint(self, *args):
        return QtCore.QSize(10, 10)


# class AddNode(BaseNode):
#     "simple math Node"
#     def __init__(self, scene):
#         super(AddNode, self).__init__(scene, "Add")
#         self.val1_slot = SlotInput(scene)
#         self.val2_slot = SlotInput(scene)
#         self.out_slot = SlotOutput(scene)
#         self.math = QtGui.SpinBox()
#         self.addWidget(self.math)
#         self.addWidget(self.val1_slot, Label("value"))
#         self.addWidget(self.val2_slot, Label("value"))
#         self.addWidget(self.out_slot, Label("value"))
#         self.out_slot.output = self.output

#     def output(self):
#         return self.val1_slot.input() + self.val2_slot.input()


class ListNode(BaseNode):
    """joins all kind of objects, but you have to care
 where to put the output in"""

    def __init__(self, scene):
        super(ListNode, self).__init__(scene=scene, title="List")
        slot = SlotInput(scene)
        slot.setParent(self)
        self.push = Gui.PushButton()
        slot.got_connected = self.update_slots
        self.slot_list = [slot]
        self.slot_out = SlotOutput(scene)
        self.addItem(self.slot_out)
        self.layout().addItem(self.slot_list[0], 3, 0)
        self.slot_out.output = self.output

    def update_slots(self):
        if len(self.slot_list) == 1 and self.slot_list[0].input is None:
            return
        else:
            for i in self.children():
                if isinstance(i, SlotInput):
                    if i.input() == None:
                        if i in self._scene.node_list:
                            self._scene.node_list.remove(i)
                        if i in self.slot_list:
                            self.slot_list.remove(i)
                        self.layout().removeItem(i)
                        i.deleteLater()
            slot = SlotInput(self._scene)
            slot.got_connected = self.update_slots
            slot.setParent(self)
            self.slot_list.append(slot)
            self.layout().addItem(slot, self.layout().rowCount() + 2, 0)
            self.adjustSize()
            self.update_lines()

    def output(self):
        arr = [i.input() for i in self.slot_list]
        return [i for i in arr if i is not None]


# class LoopNode(BaseNode):
#     """make an array of objects"""
#     def __init__(self, scene):
#         super(LoopNode, self).__init__(scene, "Loop", "red")
#         self.iter_max_slot = SlotInput(scene)
#         self.iter_max = QtGui.QSpinBox()
#         self.input_slot = SlotInput(scene)
#         self.loop_input = SlotInput(scene)
#         self.loop_output_slot = SlotOutput(scene)
#         self.output_slot = SlotOutput(scene)

#         self.iter_max = QtGui.QSpinBox()
#         self.iter_max.setValue(0)

#         self.addWidget(self.iter_max_slot, self.iter_max)
#         self.addWidget(self.input_slot, Label("object in"))
#         self.addWidget(self.loop_output_slot, Label("loop_object"), self.loop_input)
#         self.addWidget(self.output_slot, Label("object_out"))
#         self.arr = []
#         self.iter = 0
#         self.output_slot.output = self.output
#         self.loop_output_slot.output = self.loop_output

#     def output(self):
#         self.iter = 0
#         print("enter loop")
#         thing = self.loop_input.input()
#         self.arr.append(thing)
#         print("exit loop")
#         return self.arr

#     def loop_output(self):
#         iter_max = self.iter_max_slot.input() or self.iter_max.value()
#         print("iter_max", iter_max)
#         print("iter", self.iter)
#         if self.iter < iter_max:
#             self.iter += 1
#             thing = self.loop_input.input()
#             self.arr.append(thing)
#         else:
#             # self.arr = []
#             thing = self.input_slot.input()
#             self.arr = []
#             self.arr.append(thing)
#         return thing


ButtonDict = {
    "Slider": SliderNode,
    "GetValue": GetValueNode,
    # "Add": AddNode,
    "List": ListNode,
    # "Loop": LoopNode,
    "Help": HelpNode    
}
