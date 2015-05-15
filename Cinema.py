
#!/usr/bin/python

# Import PySide classes
import sys
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *
import json

# import Python Image Library
import PIL.ImageFile

# Import cinema IO
import IO.cinema_store

#open up a store
with open(sys.argv[1], mode="rb") as file:
    info_json = json.load(file)
md = info_json["metadata"]
if md.has_key("store_type") and md["store_type"] == "SFS":
    cs = IO.cinema_store.SingleFileStore(sys.argv[1])
else:
    cs = IO.cinema_store.FileStore(sys.argv[1])
cs.load()

aselection = {}

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
