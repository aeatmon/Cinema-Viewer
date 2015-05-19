from PySide import QtCore
from PySide.QtCore import *
from PySide.QtGui import *

import numpy as np
import PIL

from QRenderView import *
from RenderViewMouseInteractor import *

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()

        # Set title
        self.setWindowTitle('Cinema Desktop')

        # Set up UI
        self._mainWidget = QSplitter(Qt.Horizontal, self)
        self.setCentralWidget(self._mainWidget)

        self._displayWidget = QRenderView(self)
        self._displayWidget.setRenderHints(QPainter.SmoothPixmapTransform)
        self._displayWidget.setAlignment(Qt.AlignCenter)
        self._displayWidget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self._parametersWidget = QWidget(self)
        self._parametersWidget.setMinimumSize(QSize(200, 100))
        self._parametersWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self._mainWidget.addWidget(self._displayWidget)
        self._mainWidget.addWidget(self._parametersWidget)

        layout = QVBoxLayout()
        self._parametersWidget.setLayout(layout)

        #keep track of widgets that depend on others for easy updating
        self._dependent_widgets = {}

        self.createMenus()

        # Set up render view interactor
        self._mouseInteractor = RenderViewMouseInteractor()

    # Create the menu bars
    def createMenus(self):
        # File menu
        self._exitAction = QAction('E&xit', self, statusTip='Exit the application',
                                   triggered=self.close)
        self._fileToolBar = self.menuBar().addMenu('&File')
        self._fileToolBar.addAction(self._exitAction)

    # Set the store currently being displayed
    def setStore(self, store):
        self._store = store
        self._initializeCurrentQuery()

        # Disconnect all mouse signals in case the store has no phi or theta values
        self._disconnectMouseSignals()

        if ('phi' in store.parameter_list):
            self._mouseInteractor.setPhiValues(store.parameter_list['phi']['values'])

        if ('theta' in store.parameter_list):
            self._mouseInteractor.setThetaValues(store.parameter_list['theta']['values'])

        if ('phi' in store.parameter_list or 'theta' in store.parameter_list):
            self._connectMouseSignals()

        # Display the default image
        self.render()
        # Make the GUI
        self._createParameterUI()

    # Disconnect mouse signals
    def _disconnectMouseSignals(self):
        try:
            dw = self._displayWidget
            dw.mousePressSignal.disconnect(self._initializeCamera)
            dw.mousePressSignal.disconnect(self._mouseInteractor.onMousePress)
            dw.mouseMoveSignal.disconnect(self._mouseInteractor.onMouseMove)
            dw.mouseReleaseSignal.disconnect(self._mouseInteractor.onMouseRelease)
            dw.mouseWheelSignal.disconnect(self._mouseInteractor.onMouseWheel)

            # Update camera phi-theta if mouse is dragged
            self._displayWidget.mouseMoveSignal.disconnect(self._updateCamera)

            # Update camera if mouse wheel is moved
            self._displayWidget.mouseWheelSignal.disconnect(self._updateCamera)
        except:
            # No big deal if we can't disconnect
            pass

    # Connect mouse signals
    def _connectMouseSignals(self):
        dw = self._displayWidget
        dw.mousePressSignal.connect(self._initializeCamera)
        dw.mousePressSignal.connect(self._mouseInteractor.onMousePress)
        dw.mouseMoveSignal.connect(self._mouseInteractor.onMouseMove)
        dw.mouseReleaseSignal.connect(self._mouseInteractor.onMouseRelease)
        dw.mouseWheelSignal.connect(self._mouseInteractor.onMouseWheel)

        # Update camera phi-theta if mouse is dragged
        self._displayWidget.mouseMoveSignal.connect(self._updateCamera)

        # Update camera if mouse wheel is moved
        self._displayWidget.mouseWheelSignal.connect(self._updateCamera)

    # Initializes image store query.
    def _initializeCurrentQuery(self):
        self._currentQuery = dict()
        dd = self._store.parameter_list

        for name, properties in dd.items():
            if properties['type'] == 'option':
                v = set()
                v.add(str(dd[name]['default']))
                self._currentQuery[name] = v
            else:
                self._currentQuery[name] = dd[name]['default']

    # Create a slider for a 'range' parameter
    def _createRangeSlider(self, name, properties):
        labelValueWidget = QWidget(self)
        labelValueWidget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        labelValueWidget.setLayout(QHBoxLayout())
        labelValueWidget.layout().setContentsMargins(0, 0, 0, 0)
        self._parametersWidget.layout().addWidget(labelValueWidget)

        textLabel = QLabel(properties['label'], self)
        labelValueWidget.layout().addWidget(textLabel)

        valueLabel = QLabel('0', self)
        valueLabel.setAlignment(Qt.AlignRight)
        valueLabel.setObjectName(name + "ValueLabel")
        labelValueWidget.layout().addWidget(valueLabel)

        controlsWidget = QWidget(self)
        controlsWidget.setSizePolicy(QSizePolicy.MinimumExpanding,
                                           QSizePolicy.Fixed)
        controlsWidget.setLayout(QHBoxLayout())
        controlsWidget.layout().setContentsMargins(0, 0, 0, 0)
        #controlsWidget.setContentsMargins(0, 0, 0, 0)
        self._parametersWidget.layout().addWidget(controlsWidget)

        flat = False
        width = 25

        skipBackwardIcon = self.style().standardIcon(QStyle.SP_MediaSkipBackward)
        skipBackwardButton = QPushButton(skipBackwardIcon, '', self)
        skipBackwardButton.setObjectName("SkipBackwardButton." + name)
        skipBackwardButton.setFlat(flat)
        skipBackwardButton.setMaximumWidth(width)
        skipBackwardButton.clicked.connect(self.onSkipBackward)
        controlsWidget.layout().addWidget(skipBackwardButton)

        seekBackwardIcon = self.style().standardIcon(QStyle.SP_MediaSeekBackward)
        seekBackwardButton = QPushButton(seekBackwardIcon, '', self)
        seekBackwardButton.setObjectName("SeekBackwardButton." + name)
        seekBackwardButton.setFlat(flat)
        seekBackwardButton.setMaximumWidth(width)
        seekBackwardButton.clicked.connect(self.onSeekBackward)
        controlsWidget.layout().addWidget(seekBackwardButton)

        slider = QSlider(Qt.Horizontal, self)
        slider.setObjectName(name)
        controlsWidget.layout().addWidget(slider);

        seekForwardIcon = self.style().standardIcon(QStyle.SP_MediaSeekForward)
        seekForwardButton = QPushButton(seekForwardIcon, '', self)
        seekForwardButton.setObjectName("SeekForwardButton." + name)
        seekForwardButton.setFlat(flat)
        seekForwardButton.setMaximumWidth(width)
        seekForwardButton.clicked.connect(self.onSeekForward)
        controlsWidget.layout().addWidget(seekForwardButton)

        skipForwardIcon = self.style().standardIcon(QStyle.SP_MediaSkipForward)
        skipForwardButton = QPushButton(skipForwardIcon, '', self)
        skipForwardButton.setObjectName("SkipForwardButton." + name)
        skipForwardButton.setFlat(flat)
        skipForwardButton.setMaximumWidth(width)
        skipForwardButton.clicked.connect(self.onSkipForward)
        controlsWidget.layout().addWidget(skipForwardButton)

        playIcon = self.style().standardIcon(QStyle.SP_MediaPlay)
        playButton = QPushButton(playIcon, '', self)
        playButton.setObjectName("PlayButton." + name)
        playButton.setFlat(flat)
        playButton.setMaximumWidth(width)
        playButton.clicked.connect(self.onPlay)
        controlsWidget.layout().addWidget(playButton)

        # Configure the slider
        default   = properties['default']
        values    = properties['values']
        typeValue = properties['type']
        label     = properties['label']
        slider.setMinimum(0)
        slider.setMaximum(len(values)-1)
        slider.setPageStep(1)
        slider.valueChanged.connect(self.onSliderMoved)

        self._updateSlider(properties['label'], properties['default'])
        return controlsWidget

    # Create a slider for a 'list' parameter
    def _createListPulldown(self, name, properties):
        labelValueWidget = QWidget(self)
        labelValueWidget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        labelValueWidget.setLayout(QHBoxLayout())
        labelValueWidget.layout().setContentsMargins(0, 0, 0, 0)
        self._parametersWidget.layout().addWidget(labelValueWidget)

        textLabel = QLabel(properties['label'], self)
        labelValueWidget.layout().addWidget(textLabel)

        controlsWidget = QWidget(self)
        controlsWidget.setSizePolicy(QSizePolicy.MinimumExpanding,
                                           QSizePolicy.Fixed)
        controlsWidget.setLayout(QHBoxLayout())
        controlsWidget.layout().setContentsMargins(0, 0, 0, 0)
        #controlsWidget.setContentsMargins(0, 0, 0, 0)
        self._parametersWidget.layout().addWidget(controlsWidget)

        menu = QComboBox(self)
        menu.setObjectName(name)
        controlsWidget.layout().addWidget(menu);

        found = -1
        for entry in properties['values']:
            if entry == properties['default']:
                found = menu.count()
            menu.addItem(str(entry))
        menu.setCurrentIndex(found)
        menu.currentIndexChanged.connect(self.onChosen)
        return controlsWidget

    # Create a slider for an 'option' parameter
    def _createOptionCheckbox(self, name, properties):
        labelValueWidget = QWidget(self)
        labelValueWidget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        labelValueWidget.setLayout(QHBoxLayout())
        labelValueWidget.layout().setContentsMargins(0, 0, 0, 0)
        self._parametersWidget.layout().addWidget(labelValueWidget)

        textLabel = QLabel(properties['label'], self)
        labelValueWidget.layout().addWidget(textLabel)

        controlsWidget = QWidget(self)
        controlsWidget.setSizePolicy(QSizePolicy.MinimumExpanding,
                                           QSizePolicy.Fixed)
        controlsWidget.setLayout(QHBoxLayout())
        controlsWidget.layout().setContentsMargins(0, 0, 0, 0)
        #controlsWidget.setContentsMargins(0, 0, 0, 0)
        self._parametersWidget.layout().addWidget(controlsWidget)

        for entry in properties['values']:
           cb = QCheckBox(str(entry), self)
           cb.setObjectName(name)
           cb.value = entry
           if entry == properties['default']:
               cb.setChecked(True)

           cb.stateChanged.connect(self.onChecked)
           controlsWidget.layout().addWidget(cb)
        return controlsWidget

    # Create property UI
    def _createParameterUI(self):
        keys = sorted(self._store.parameter_list)
        dependencies = self._store.parameter_associations

        for name in keys:
            properties = self._store.parameter_list[name]
            widget = None

            if len(properties['values']) == 1:
                #don't have widget if no choice possible
                continue

            if properties['type'] == 'range':
                widget = self._createRangeSlider(name, properties)

            if properties['type'] == 'list':
                widget = self._createListPulldown(name, properties)

            if properties['type'] == 'option':
                widget = self._createOptionCheckbox(name, properties)

            if properties['type'] == 'hidden':
                continue

            if widget and name in dependencies:
                # disable widgets that depend on settings of others
                widget.setEnabled(False)
                self._dependent_widgets[name] = widget

        self._parametersWidget.layout().addStretch()
        self._updateDependentWidgets()

    # Update enable state of all dependent widgets
    # Current logic says enable the depender if ANY of its dependees
    # are have a state that the depender likes.
    # TODO: doesn't handle recursive dependencies correctly
    def _updateDependentWidgets(self):
        dependencies = self._store.parameter_associations
        cq, ignored, opts = self._getCurrentQuery()
        for name, widget in self._dependent_widgets.iteritems():
            ok = False
            for parent, okvals in dependencies[name].iteritems():
                if parent in cq:
                    val = cq[parent]
                    if val in okvals:
                        ok = True
                if parent in opts:
                    vals = opts[parent]
                    for x in vals:
                        if x in okvals:
                            ok = True
            if ok:
                widget.setEnabled(True)
            else:
                widget.setEnabled(False)

    # Respond to a slider movement
    def onSliderMoved(self):
        parameterName = self.sender().objectName()
        sliderIndex = self.sender().value()
        pl = self._store.parameter_list
        parameterValue = pl[parameterName]['values'][sliderIndex]
        self._currentQuery[parameterName] = parameterValue
        # Update value label
        valueLabel = self._parametersWidget.findChild(QLabel, parameterName + "ValueLabel")
        valueLabel.setText(self._formatText(parameterValue))

        self._updateDependentWidgets()
        self.render()

    # Respond to a combobox change
    def onChosen(self, index):
        parameterName = self.sender().objectName()
        pl = self._store.parameter_list
        parameterValue = pl[parameterName]['values'][index]
        self._currentQuery[parameterName] = parameterValue

        self._updateDependentWidgets()
        self.render()

    # Respond to a checkbox change
    def onChecked(self, state):
        parameterName = self.sender().objectName()
        parameterValue = self.sender().value
        currentValues = self._currentQuery[parameterName]
        if state:
            currentValues.add(str(parameterValue))
        else:
            currentValues.remove(str(parameterValue))
        self._currentQuery[parameterName] = currentValues

        self._updateDependentWidgets()
        self.render()

    # Back up slider all the way to the left
    def onSkipBackward(self):
        parameterName = self.sender().objectName().replace("SkipBackwardButton.", "")
        slider = self._parametersWidget.findChild(QSlider, parameterName)
        slider.setValue(0)

    # Back up slider one step to the left
    def onSeekBackward(self):
        parameterName = self.sender().objectName().replace("SeekBackwardButton.", "")
        slider = self._parametersWidget.findChild(QSlider, parameterName)
        slider.setValue(0 if slider.value() == 0 else slider.value() - 1)

    # Forward slider one step to the right
    def onSeekForward(self):
        parameterName = self.sender().objectName().replace("SeekForwardButton.", "")
        slider = self._parametersWidget.findChild(QSlider, parameterName)
        maximum = slider.maximum()
        slider.setValue(maximum if slider.value() == maximum else slider.value() + 1)

    # Forward the slider all the way to the right
    def onSkipForward(self):
        parameterName = self.sender().objectName().replace("SkipForwardButton.", "")
        slider = self._parametersWidget.findChild(QSlider, parameterName)
        slider.setValue(slider.maximum())

    # Play forward through the parameters
    def onPlay(self):
        parameterName = self.sender().objectName().replace("PlayButton.", "")
        timer = QTimer(self)
        timer.setObjectName("Timer." + parameterName)
        timer.setInterval(200)
        timer.timeout.connect(self.onPlayTimer)
        timer.start()

    def onPlayTimer(self):
        parameterName = self.sender().objectName().replace("Timer.", "")

        slider = self._parametersWidget.findChild(QSlider, parameterName)
        maximum = slider.maximum()
        if (slider.value() == slider.maximum()):
            self.sender().stop()
        else:
            slider.setValue(maximum if slider.value() == maximum else slider.value() + 1)

    # Format string from number
    def _formatText(self, value):
        try:
            intValue = int(value)
            return '{0}'.format(intValue)
        except:
            pass

        try:
            floatValue = float(value)
            return '{0}'.format(floatValue)
        except:
            pass

        # String
        return value

    # Update slider from value
    def _updateSlider(self, parameterName, value):
        pl = self._store.parameter_list
        index = pl[parameterName]['values'].index(value)
        slider = self._parametersWidget.findChild(QSlider, parameterName)
        slider.setValue(index)

    # Initialize the angles for the camera
    def _initializeCamera(self):
        self._mouseInteractor.setPhi(self._currentQuery['phi'])
        self._mouseInteractor.setTheta(self._currentQuery['theta'])

    # Update the camera angle
    def _updateCamera(self):
        # Set the camera settings if available
        phi   = self._mouseInteractor.getPhi()
        theta = self._mouseInteractor.getTheta()

        if ('phi' in self._currentQuery):
            self._currentQuery['phi']   = phi

        if ('theta' in self._currentQuery):
            self._currentQuery['theta'] = theta

        # Update the sliders for phi and theta
        self._updateSlider('phi', phi)
        self._updateSlider('theta', theta)

        scale = self._mouseInteractor.getScale()
        self._displayWidget.resetTransform()
        self._displayWidget.scale(scale, scale)

        self.render()

    # look at state of all widgesseparate option types with multiple values out into their own dict
    def _getCurrentQuery(self):
        def _isfield(self, n):
            if ('isfield' in self._store.parameter_list[n] and
                self._store.parameter_list[n]['isfield'] == 'yes'):
                return True
            return False
        def _islayer(self, n):
            if ('islayer' in self._store.parameter_list[n] and
                self._store.parameter_list[n]['islayer'] == 'yes'):
                #print n, "is a layer"
                return True
            #print n, "is not a layer"
            return False
        def _getdepender(self, n):
            for depender, dependees in self._store.parameter_associations.iteritems():
                if n in dependees:
                    #print "FOUND DEPENDER", depender
                    return depender
            return None
        def _getcolorvalue(self, n):
            #print "N",n
            param = self._store.parameter_list[n]
            #print "PARAM", param
            #print "CQ", self._currentQuery
            v = self._currentQuery[n]
            #print "FIELD VALUE IS", v
            return v

        cQuery = dict()
        dQuery = dict()
        opts = dict()
        hasLayer = False
        for n,v in self._currentQuery.items():
            if _isfield(self, n):
                #handle with layer below
                continue
            if _islayer(self, n):
                opts[n] = v
                layern = []
                fieldname = _getdepender(self, n)
                colorchoice = _getcolorvalue(self, fieldname)
                cQuery[fieldname] = colorchoice
                dQuery[fieldname] = u'depth'
                hasLayer = True
                continue
            if type(v) == type(set()):
                cQuery[n] = list(v)[0] #TODO: other than for layers/fields we don't know how to do these
                dQuery[n] = list(v)[0]
            else:
                cQuery[n] = v
                dQuery[n] = v
        #print "CQ", cQuery
        #print "DQ", dQuery
        if not hasLayer:
            dQuery = dict()
        return cQuery, dQuery, opts

    # Perform query requested of the UI
    # retrieve documents that go into the result,
    # display the retrieved image.
    def render(self):
        # Retrieve image from data store with the current query.
        cq, dq, opts = self._getCurrentQuery()
        docs = [doc for doc in self._store.find(cq)]
        doComposite = False
        if len(dq):
            doComposite = True
            ddocs = [doc for doc in self._store.find(dq)]
        layers = [] #ends up with color and depth information for each selected layer
        if len(docs) > 0:
            for dix in range(0,len(docs)):
                doc = docs[dix]
                if doComposite:
                    ddoc = ddocs[dix]
                for n, vs in opts.items():
                    if doc.descriptor[n] in vs:
                        layers.append(doc)
                        if doComposite:
                            layers.append(ddoc)
                    else:
                        pass

        if len(layers) == 0 and len(dq) == 0:
            layers.append(docs[0])

        self.displayDocument(layers)

    # Given a document, read the data into an image that can be displayed in Qt
    def displayDocument(self, layers):

        if len(layers) == 0 or layers[0] == None or layers[0].data == None:
            self._displayWidget.setPixmap(None)
            self._displayWidget.setAlignment(Qt.AlignCenter)
            return

        c0 = np.copy(layers[0].data)

        d0 = None
        if len(layers)>1:
            d0 = np.copy(layers[1].data)

        # composite in the rest of the layers, picking color of nearest pixel
        for idx in range(2,len(layers),2):
            cnext = layers[idx].data
            dnext = layers[idx+1].data
            indxarray = np.where(dnext<d0)
            c0[indxarray[0],indxarray[1],:] = cnext[indxarray[0],indxarray[1],:]
            d0[indxarray[0],indxarray[1],:] = dnext[indxarray[0],indxarray[1],:]

        pimg = PIL.Image.fromarray(c0)
        imageString = pimg.tostring('raw', 'RGB')
        qimg = QImage(imageString, pimg.size[0], pimg.size[1], QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)

        # Try to resize the display widget
        self._displayWidget.sizeHint = pix.size
        self._displayWidget.setPixmap(pix)
