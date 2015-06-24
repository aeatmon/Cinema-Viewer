"""
Manages the set of one or more fields that go into a layer.
"""

import copy

class LayerSpec(object):
    def __init__(self):
        self.depth = None
        self.luminance = None
        self.colors = []
        self.values = []
        self.dict = {}
        self._fields = {}

    def addToBaseQuery(self, query):
        """ add queries that together define the layer """
        self.dict.update(query)

    def addQuery(self, img_type, fieldname, fieldchoice):
        """ add a query for a particular field of the layer """
        #print "ADDQUERY", img_type, fieldname, fieldchoice
        self._fields[img_type] = {fieldname:fieldchoice}

    def loadImages(self, store):
        """
        Take the queries we've been given and get images for them.
        Later call get* to get the images out.
        """
        nfields = len(self._fields)
        if nfields == 0:
            img = list(store.find(self.dict))[0].data
            self._addColor(img)
            #print "FALLBACK RGB"
        else:
            for f in self._fields.keys():
                query = copy.deepcopy(self.dict)
                query.update(self._fields[f])
                #print f
                #print "Q", query
                img = list(store.find(query))[0].data
                #print "I", img
                if f == 'RGB':
                    #print "ADD RGB"
                    self._addColor(img)
                elif f == 'Z':
                    #print "ADD DEPTH"
                    self._setDepth(img)
                elif f == 'VALUE':
                    #print "ADD VALUES"
                    self._addColor(img) #TODO: change to addValues when renderer can handle
                elif f == 'LUMINANCE':
                    self._setLuminance(img)

    def _setDepth(self, image):
        self.depth = image
        #print "SETDEPTH"
        #print image
        #print self.depth

    def getDepth(self):
        return self.depth

    def _addColor(self, image):
        self.colors.append(image)
        #print "ADDCOLOR"
        #print image
        #print self.colors

    def getColor1(self):
        return self.colors[0]

    def _addValues(self, image):
        self.values.append(image)
        #print "ADDVALUE"
        #print image
        #print self.values

    def getValues1(self, image):
        return self.values[1]

    def _setLuminance(self, image):
        self.luminance = image

    def getLuminance(self, image):
        return self.luminance
