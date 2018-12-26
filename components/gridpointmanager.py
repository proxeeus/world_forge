from panda3d.core import CollisionNode
from pandac.PandaModules import CollisionSphere
from panda3d.core import Vec3, Vec4, Point3
from components.gridpoint import Gridpoint
import globals
from pandac.PandaModules import *
from direct.directtools.DirectGeometry import LineNodePath

class GridpointManager():

    picker = None

    def ResetGridList(self):
        for x in globals.grid_list:
            x.deletemodel()
        del globals.grid_list
        globals.grid_list = list()

        self.ResetGridLinks()

    def ResetGridLinks(self):
        for x in globals.gridlinks_list:
            x.removeNode()
        del globals.gridlinks_list
        globals.gridlinks_list = list()

    def LinkGridPoints(self):
        # 1 is to avoid drawing a last line from the last grid point back to the 1st one.
        # having this would mimic grid types being to the type where mobs path back straight to their original spawn point
        # so maybe we could generate this last line dynamically? If grid type == strict patrol start at 1 otherwise 0 ?
        for x in range(1, len(globals.grid_list)):
            lines = LineSegs()
            lines.moveTo(globals.grid_list[x].y, globals.grid_list[x].x, globals.grid_list[x].z)
            lines.drawTo(globals.grid_list[x - 1].y, globals.grid_list[x - 1].x, globals.grid_list[x - 1].z)
            lines.setThickness(4)
            node = lines.create()
            np = NodePath(node)
            np.reparentTo(render)
            globals.gridlinks_list.append(np)

    def GenerateGrids(self,gridid, zoneid):
        gridpoints = globals.database.GetDbGridPointsData(gridid, zoneid)
        pointscount = gridpoints.rowcount

        grid_coords = list()
        for x in range(0, pointscount):
            row = gridpoints.fetchone()
            point = Point3(long(row["y"]), long(row["x"]), long(row["z"]))
            if globals.config['ignore_duplicate_spawns'] == 'True':
                if point not in grid_coords:
                    self.PlaceGridPointOn3dMap(row)
                    grid_coords.append(point)
            else:
                self.PlaceGridPointOn3dMap(row)
        self.LinkGridPoints()
        print "toto"

    def PlaceGridPointOn3dMap(self, row):
        gridPoint = Gridpoint()
        self.InitGridPointsData(gridPoint, row)
        gridPoint.model = loader.loadModel(gridPoint.modelname)
        gridPoint.initmodel()
        gridPoint.model.reparentTo(render)
        gridPoint.initheadingfromdb(row["heading"])
        gridPoint.placeintoworld(row["y"], row["x"], row["z"])
        min, macks = gridPoint.model.getTightBounds()
        radius = max([macks.getY() - min.getY(), macks.getX() - min.getX()]) / 2
        cs = CollisionSphere(row["x"], row["y"], row["z"], radius)
        csNode = gridPoint.model.attachNewNode(CollisionNode("modelCollide"))
        csNode.node().addSolid(cs)
        # TODO: ADD MORE TAGS??
        gridPoint.model.setTag("name", "grid_" + str(row["gridid"]) + "_" + str(row["number"]))
        gridPoint.model.setTag("gridid", str(row["gridid"]))
        gridPoint.model.setTag("number", str(row["number"]))
        gridPoint.model.setTag("type", "gridpoint")
        globals.picker.makePickable(gridPoint.model)
        globals.grid_list.append(gridPoint)

    def InitGridPointsData(self, gridPoint, row):
        gridPoint.gridid = row["gridid"]
        gridPoint.zoneid = row["zoneid"]
        gridPoint.z = row["z"]
        gridPoint.y = row["y"]
        gridPoint.x = row["x"]
        gridPoint.number = row["number"]
        gridPoint.heading = row["heading"]
        gridPoint.pause = row["pause"]

    def InsertNewGridEntry(self, gridPoint):
        globals.database.InsertNewGridEntry(gridPoint)
        self.ResetGridList()
        self.GenerateGrids(gridPoint.gridid, globals.zoneid)
        globals.griddialog.LoadGrid()