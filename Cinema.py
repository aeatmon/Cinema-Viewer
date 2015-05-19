
#!/usr/bin/python

# Import PySide classes
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *

# import Python Image Library
import PIL.ImageFile

# Import cinema IO
import IO.cinema_store

import sys
import json

#open up a store
with open(sys.argv[1], mode="rb") as file:
    info_json = json.load(file)
storeType = "MFS"
try:
    if info_json["metadata"]["store_type"] == "SFS":
        cs = IO.cinema_store.SingleFileStore(sys.argv[1])
    else:
        raise TypeError
except(TypeError,KeyError):
    cs = IO.cinema_store.FileStore(sys.argv[1])

cs.load()

# Show it in Qt
app = QApplication(sys.argv)

# set up UI
from MainWindow import *
mainWindow = MainWindow()
mainWindow.setStore(cs)
mainWindow.show()

# Enter Qt application main loop
app.exec_()
sys.exit()
