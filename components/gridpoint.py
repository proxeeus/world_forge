from panda3d.core import CollisionNode
from pandac.PandaModules import CollisionSphere
import globals

class Gridpoint:

    gridid = 0
    zoneid = 0
    type = 0
    type2 = 0
    number = 0
    x = 0
    y = 0
    z = 0
    heading = -1
    pause = 0

    # other members
    modelname = "models/arrow.egg"
    model = ""
    newdbentry = False

    def initmodel(self):
        self.model.setScale(50, 50, 50)
        self.model.setColor(83, 51, 237, 1, True)

    # Initializes the spawn's heading from the EQEmu db value into the 360-based value
    def initheadingfromdb(self, dbheading):
        self.model.setH(dbheading / 512 * 360 - 90)

    # Does the exact opposite of initheadingfromdb
    def setheadingfromworld(self, worldheading):
        # ((Orientation B + 90)/360)*520
        self.spawnentry_heading = ((worldheading + 90) / 360) * 520

    # Renders the spawn's model in the 3D view
    def placeintoworld(self, x, y, z):
        self.model.setPos(x, y, z)

    # Creates a brand new model (unexisting gridpoint) and renders it in the 3D view
    def addnewgridpointtoworld(self, thePoint, picker):
        self.model = loader.loadModel(self.modelname)
        self.initmodel()
        self.model.reparentTo(render)
        self.initheadingfromdb(0)
        self.placeintoworld(thePoint[1].getX(), thePoint[1].getY(), thePoint[1].getZ())
        print thePoint[1].getY(), thePoint[1].getX(), thePoint[1].getZ()
        min, macks = self.model.getTightBounds()
        radius = max([macks.getY() - min.getY(), macks.getX() - min.getX()]) / 2
        cs = CollisionSphere(thePoint[1].getX(), thePoint[1].getY(), thePoint[1].getZ(), radius)
        csNode = self.model.attachNewNode(CollisionNode("modelCollide"))
        csNode.node().addSolid(cs)
        # TODO: determine a correct tagging mechanism
        #self.model.setTag("name", self.spawngroup_name)
        picker.makePickable(self.model)

    def deletemodel(self):
        loader.unloadModel(self.modelname)
        self.model.removeNode()