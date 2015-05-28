"""
A struct to hold layer and fields together.
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

    def setDepth(self, image):
        self.depth = image
        #print "SETDEPTH"
        #print image
        #print self.depth

    def getDepth(self):
        return self.depth

    def addColor(self, image):
        self.colors.append(image)
        #print "ADDCOLOR"
        #print image
        #print self.colors

    def getColor1(self):
        return self.colors[0]

    def addValues(self, image):
        self.values.append(image)
        #print "ADDVALUE"
        #print image
        #print self.values

    def getValues1(self, image):
        return self.values[1]

    def setLuminance(self, image):
        self.luminance = image

    def getLuminance(self, image):
        return self.luminance

    def addToBaseQuery(self, query):
        self.dict.update(query)

    def addQuery(self, img_type, fieldname, fieldchoice):
        #print "ADDQUERY", img_type, fieldname, fieldchoice
        self._fields[img_type] = {fieldname:fieldchoice}

    def loadImages(self, store):
        #convert the set of queries I've been set up with to images
        nfields = len(self._fields)
        if nfields == 0:
            img = list(store.find(self.dict))[0].data
            self.addColor(img)
            #print "FALLBACK RGB"
        else:
            for f in self._fields.keys():
                query = copy.deepcopy(self.dict)
                query.update(self._fields[f])
                #print f
                #print "Q", query
                img = list(store.find(query))[0].data
                #print "I", img
                if f == 'rgb':
                    #print "ADD RGB"
                    self.addColor(img)
                elif f == 'depth':
                    #print "ADD DEPTH"
                    self.setDepth(img)
                elif f == 'value':
                    #print "ADD VALUES"
                    self.addColor(img) #TODO: change to addValues when renderer can handle
                elif f == 'luminance':
                    self.setLuminance(img)
