from panda3d.core import CollisionNode
from pandac.PandaModules import CollisionSphere
import globals

class Spawn:

    # db-related members
    spawngroup_id = 0
    spawngroup_name = ""
    spawngroup_minx = 0
    spawngroup_maxx = 0
    spawngroup_miny = 0
    spawngroup_maxy = 0
    spawngroup_dist = 0
    spawngroup_mindelay = 0
    spawngroup_delay = 0
    spawngroup_despawn = 0
    spawngroup_despawntimer = 0
    spawngroup_spawnlimit = 0
    spawngroup_chance = 0

    spawnentry_id = 0
    spawnentry_npcid = 0
    spawnentry_npcname = ""
    spawnentry_x = 0
    spawnentry_y = 0
    spawnentry_z = 0
    spawnentry_heading = 0
    spawnentry_respawn = 600
    spawnentry_variance = 0
    spawnentry_pathgrid = 0
    spawnentry_condition = 0
    spawnentry_condvalue = 0
    spawnentry_version = 0
    spawnentry_enabled = 1
    spawnentry_animation = 0
    spawnentry_zone = ""

    # The very base, original coordinates, useful for reference
    spawnentry_originalx = 0
    spawnentry_originaly = 0
    spawnentry_originalz = 0
    spawnentry_originalheading = 0

    # other members
    modelname = "models/arrow.egg"
    model = ""
    newdbentry = False

    #def __init__(self, spawngroup_id, spawngroup_name):
     #   self.spawngroup_id = spawngroup_id
     #   self.spawngroup_name = spawngroup_name

    def initmodel(self):
        self.model.setScale(50, 50, 50)
        self.model.setColor(0.6, 0.6, 1.0, 1.0)

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

    # Creates a brand new model (unexisting spawn) and renders it in the 3D view
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
        self.model.setTag("name", self.spawngroup_name)
        picker.makePickable(self.model)
        # TODO : ADD A WAY TO KEEP ADDED SPAWNS AS A GLOBAL LIST
        #globals.spawn_list.append(self)
        #globals.addspawntolist(self)
        # spawn_coords.append(point)

    def deletemodel(self):
        loader.unloadModel(self.modelname)
        self.model.removeNode()