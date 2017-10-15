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
#import zonewalk

class Picker2(DirectObject.DirectObject):
   def __init__(self, topNode = None):
      #setup collision stuff

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

      self.accept('mouse1', self.selectMe)


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
         #thepoint = self.queue.getEntry(0).getSurfacePoint(self.pickerNP)
         parent=self.pickedObj.getParent()
         self.pickedObj=None

         while parent != render:
            if parent.getTag('pickable')=='true':
               self.pickedObj=parent
               return parent#, thepoint
            else:
               parent=parent.getParent()
      return None

   def getPickedObj(self):
         return self.pickedObj

   def selectMe(self):
      print zonewalk.last_selected_model
      if zonewalk.last_selected_model is None:
         print "No last_selected_model, setting..."
         self.getObjectHit( base.mouseWatcherNode.getMouse())
         last_selected_model = self.getObjectHit( base.mouseWatcherNode.getMouse())
         print "last_selected_model set."
      else:
         print "We have a last selected model already."
         # do some shit bla bla
         print "Our shit is done, unsetting last_selected_model"
         last_selected_model = None
      print self.pickedObj

