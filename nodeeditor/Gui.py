from PySide import QtGui, QtCore


class Label(QtGui.QGraphicsLayoutItem):
    def __init__(self, text="None"):
        super(Label, self).__init__()
        self.text_item = QtGui.QGraphicsSimpleTextItem(text)
        self.setGraphicsItem(self.text_item)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

    def setText(self, text):
        self.text_item.setText(text)
        self.updateGeometry()

    def setGeometry(self, rect):
        self.text_item.setPos(rect.topLeft())

    def updateGeometry(self):
        print(self.text_item.boundingRect())

    def sizeHint(self, *args):
        rect = self.text_item.boundingRect()
        return rect.size()

    def setParent(self, *args):
        self.setParentLayoutItem(args[0])


class Label1(QtGui.QGraphicsWidget):
    def __init__(self, text="None"):
        super(Label1, self).__init__()
        self.text_item = QtGui.QGraphicsSimpleTextItem(text)
        self.setLayout(QtGui.QGraphicsLinearLayout())
        self.layout().addItem(self.text_item)

    def setGeometry(self, rect):
        self.text_item.setPos(rect.topLeft())


class PushButton(QtGui.QGraphicsProxyWidget):
    def __init__(self, text=""):
        super(PushButton, self).__init__()
        self.button = QtGui.QPushButton(text)
        self.setWidget(self.button)
        self.clicked = self.button.clicked


class Slider(QtGui.QGraphicsProxyWidget):
    def __init__(self, orientation=QtCore.Qt.Horizontal):
        super(Slider, self).__init__()
        self.slider = QtGui.QSlider()
        self.slider.setOrientation(orientation)
        self.setWidget(self.slider)
        self.valueChanged = self.slider.valueChanged
        self.value = self.slider.value


class CheckBox(QtGui.QGraphicsProxyWidget):
    def __init__(self):
        super(CheckBox, self).__init__()
        self.checkbox = QtGui.QCheckBox()
        self.setWidget(self.checkbox)


class SpinBox(QtGui.QGraphicsProxyWidget):
    def __init__(self):
        super(SpinBox, self).__init__()
        self.spinbox = QtGui.QSpinBox()
        self.setWidget(self.spinbox)


class DoubleSpinBox(QtGui.QGraphicsProxyWidget):
    def __init__(self):
        super(DoubleSpinBox, self).__init__()
        self.spinbox = QtGui.QDoubleSpinBox()
        self.setWidget(self.spinbox)
        self.setValue = self.spinbox.setValue
        self.value = self.spinbox.value
        self.setMaximum = self.spinbox.setMaximum


class TextEdit(QtGui.QGraphicsProxyWidget):
    def __init__(self):
        super(TextEdit, self).__init__()
        self.textedit = QtGui.QTextEdit()
        self.setWidget(self.textedit)
        self.sizeHint = self.textedit.sizeHint
        self.setReadOnly = self.textedit.setReadOnly
        self.setAlignment = self.textedit.setAlignment
        self.setText = self.textedit.setText
