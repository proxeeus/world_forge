from panda3d.core import CollisionNode
from pandac.PandaModules import CollisionSphere
import globals

class Spawn:

    id = 0
    name = ""
    modelname = "models/arrow.egg"
    model = ""

    def __init__(self, dbid, name):
        self.id = dbid
        self.name = name
        #self.model.setScale(50, 50, 50)
        #self.model.setColor(0.6, 0.6, 1.0, 1.0)

    def initmodel(self):
        self.model.setScale(50, 50, 50)
        self.model.setColor(0.6, 0.6, 1.0, 1.0)

    # Initializes the spawn's heading from the EQEmu db value into the 360-based value
    def initheadingfromdb(self, dbheading):
        self.model.setH(dbheading / 512 * 360 - 90)

    def placeintoworld(self, x, y, z):
        self.model.setPos(x, y, z)

    def addnewspawntoworld(self, thePoint, picker):
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
        self.model.setTag("name", self.name)
        picker.makePickable(self.model)
        # TODO : ADD A WAY TO KEEP ADDED SPAWNS AS A GLOBAL LIST
        #globals.spawn_list.append(self)
        #globals.addspawntolist(self)
        # spawn_coords.append(point)
