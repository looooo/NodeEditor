from nodeeditor import SlotInput, SlotOutput


class ShapeInput(SlotInput):
    def __init__(self, scene):
        super(ShapeInput, self).__init__(scene=scene)

    def mouseMoveEvent(self, event):
        super(ShapeInput, self).mouseMoveEvent(event)
        # if not isinstance(self.connection_node, ShapeOutput):
        #     self.connection_node = None


class ShapeOutput(SlotOutput):
    def __init__(self, scene):
        super(ShapeOutput, self).__init__(scene=scene)

    def mouseMoveEvent(self, event):
        super(ShapeOutput, self).mouseMoveEvent(event)
        # if not isinstance(self.connection_node, ShapeInput):
        #     self.connection_node = None
