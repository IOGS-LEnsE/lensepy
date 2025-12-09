from PyQt6.QtWidgets import QFrame

def rgb255_to_float(c):
    return tuple(x/255 for x in c)

def make_hline():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    return line

def make_vline():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.VLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    return line