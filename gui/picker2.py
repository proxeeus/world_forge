# This is a small example program for clicking on 3D objects. A panda, a teapot,
# and a cube will be on screen. When you click on the screen the console will
# tell you the nodePath of what you have clicked on. Its basically a watered down
# version of the tutorial included with Panda 3D 1.0.4. However, all the functionality
# for picking 3D objects is encapsulated into the Picker class which you may feel
# free to use in your own code.

import direct.directbase.DirectStart
#for the events
from direct.showbase import DirectObject
#for collision stuff
from pandac.PandaModules import *
from gui.picker import Picker

#This function, given a line (vector plus origin point) and a desired z value,
#will give us the point on the line where the desired z value is what we want.
#This is how we know where to position an object in 3D space based on a 2D mouse
#position. It also assumes that we are dragging in the XY plane.
#
#This is derived from the mathmatical of a plane, solved for a given point
def PointAtZ(z, point, vec):
  return point + vec * ((z-point.getZ()) / vec.getZ())

# A handy little function for getting the proper position for a given square1
def SquarePos(i):
    return LPoint3((i % 8) - 3.5, int(i // 8) - 3.5, 0)

class Picker2(DirectObject.DirectObject):
   def __init__(self, topNode = None):
      #setup collision stuff
      self.topNode = topNode
      self.picker= CollisionTraverser()
      self.queue=CollisionHandlerQueue()

      self.pickerNode=CollisionNode('mouseRay')
      self.pickerNP=camera.attachNewNode(self.pickerNode)

      self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())

      self.pickerRay=CollisionRay()

      self.pickerNode.addSolid(self.pickerRay)

      self.picker.addCollider(self.pickerNP, self.queue)

      #this holds the object that has been picked
      self.pickedObj=None

      self.lastSelectedObject = None

      self.accept('mouse1', self.selectMe)


   def setTopNode(self, topNode):
        """set the topmost node to traverse when detecting collisions"""
        self.topNode = topNode

   #this function is meant to flag an object as being somthing we can pick
   def makePickable(self,newObj):
      newObj.setTag('pickable','true')

   #this function finds the closest object to the camera that has been hit by our ray
   def getObjectHit(self, mpos): #mpos is the position of the mouse on the screen
      self.pickedObj=None #be sure to reset this
      self.pickerRay.setFromLens(base.camNode, mpos.getX(),mpos.getY())
      self.picker.traverse(render)
      if self.queue.getNumEntries() > 0:
         self.queue.sortEntries()
         self.pickedObj=self.queue.getEntry(0).getIntoNodePath()

         parent=self.pickedObj.getParent()
         self.pickedObj=None

         while parent != render:
            if parent.getTag('pickable')=='true':
               self.pickedObj=parent
               return parent
            else:
               parent=parent.getParent()
      return None

   def getPickedObj(self):
         return self.pickedObj

   def selectMe(self):

      global picker
     # get the mouse position
      # get the mouse position
      mpos = base.mouseWatcherNode.getMouse()
      #Set the position of the ray based on the mouse position
      self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
      #Gets the point described by pickerRay.getOrigin(), which is relative to
      #camera, relative instead to render
      nearPoint = render.getRelativePoint(camera, self.pickerRay.getOrigin())
      #Same thing with the direction of the ray
      nearVec = render.getRelativeVector(camera, self.pickerRay.getDirection())
      print mpos

      if self.lastSelectedObject is None:
         self.lastSelectedObject = self.getObjectHit( base.mouseWatcherNode.getMouse())
         self.getObjectHit( base.mouseWatcherNode.getMouse())
         print self.lastSelectedObject
      else:
         picker = Picker(render)
         # object already selected so we need to do some shit there and unset it
         # bla bla do some shit
         namedNode, thePoint, rawNode = picker.pick()
         print thePoint
         #self.lastSelectedObject.setPos(PointAtZ(.5, nearPoint, nearVec) )
         self.lastSelectedObject.setPos(thePoint)
         self.lastSelectedObject = None