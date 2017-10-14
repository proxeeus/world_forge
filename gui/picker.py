"""
Generic 3d object picker class for Panda3d.
Taken from http://www.panda3d.org/forums/viewtopic.php?t=12717
"""

from pandac.PandaModules import *

class Picker(object):
    """
    Generic object picker class for Panda3d. Given a top Node Path to search,
    it finds the closest collision object under the mouse pointer.

    Picker takes a topNode to test for mouse ray collisions.

    the pick() method returns (NodePathPicked, 3dPosition, rawNode) underneath the mouse position.
    If no collision was detected, it returns None, None, None.

    'NodePathPicked' is the deepest NAMED node path that was collided with, this is
    usually what you want. rawNode is the deep node (such as geom) if you want to
    play with that. 3dPosition is where the mouse ray touched the surface.

    The picker object uses base.camera to collide, so if you have a custom camera,
    well, sorry bout that.

    pseudo code:
    p = Picker(mycollisionTopNode)
    thingPicked, positionPicked, rawNode = p.pick()
    if thingPicked:
        # do something here like
        thingPicked.ls()

    """
    def __init__(self, topNode, cameraObject = None):
        self.traverser = CollisionTraverser()
        self.handler = CollisionHandlerQueue()
        self.topNode = topNode
        self.cam = cameraObject

        pickerNode  = CollisionNode('MouseRay')

        #NEEDS to be set to global camera. boo hoo
        self.pickerNP = base.camera.attachNewNode(pickerNode)

        # this seems to enter the bowels of the node graph, making it
        # difficult to perform logic on
        #pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())

        self.pickRay = CollisionRay()
        pickerNode.addSolid(self.pickRay)
        self.traverser.addCollider(self.pickerNP, self.handler)

    def setTopNode(self, topNode):
        """set the topmost node to traverse when detecting collisions"""
        self.topNode = topNode

    def destroy(self):
        """clean up my stuff."""
        self.ignoreAll()
        # remove colliders, subnodes and such
        self.pickerNP.remove()
        self.traverser.clearColliders()

    def pick(self):
        """
        pick closest object under the mouse if available.
        returns ( NodePathPicked, surfacePoint, rawNode )
        or (None, None None)
        """
        if not self.topNode:
            return None, None, None

        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()

            self.pickRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
            self.traverser.traverse(self.topNode)

            if self.handler.getNumEntries() > 0:
                self.handler.sortEntries()
                picked = self.handler.getEntry(0).getIntoNodePath()
                thepoint = self.handler.getEntry(0).getSurfacePoint(self.topNode)
                return self.getFirstParentWithName(picked), thepoint, picked

        return None, None, None

    def getFirstParentWithName(self, pickedObject):
        """
        return first named object up the node chain from the picked node. This
        helps remove drudgery when you just want to find a simple object to
        work with. Normally, you wouldn't use this method directly.
        """
        name = pickedObject.getName()
        parent = pickedObject
        while not name:
            parent = parent.getParent()
            if not parent:
                raise Exception("Node '%s' needs a parent with a name to accept clicks." % (str(pickedObject)))

            name = parent.getName()
        if parent == self.topNode:
            raise Exception("Collision parent '%s' is top Node, surely you wanted to click something beneath it..." % (str(parent)))

        return parent