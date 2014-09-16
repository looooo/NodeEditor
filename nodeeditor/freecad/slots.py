from nodeeditor import SlotInput, SlotOutput


class ShapeInput(SlotInput):
    color = "green"

    @property
    def accepted_slots(self):
        return (ShapeOutput)


class ShapeOutput(SlotOutput):
    color = "green"

    @property
    def accepted_slots(self):
        return (ShapeInput)


class DocumentInput(SlotInput):
    color = "yellow"

    @property
    def accepted_slots(self):
        return (DocumentOutput)


class DocumentOutput(SlotOutput):
    color = "yellow"

    @property
    def accepted_slots(self):
        return (DocumentInput)
