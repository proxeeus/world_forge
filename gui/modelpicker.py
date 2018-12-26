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
import globals
from components.spawn import Spawn
from components.gridpointmanager import GridpointManager
from components.gridpoint import Gridpoint
import wx

class ModelPicker(DirectObject.DirectObject):
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
   def getObjectHit(self, mpos): #mpos is the position of the mouse on the screen      self.pickedObj=None #be sure to reset this
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
      picker = Picker(render)
      globals.world.clearSelection(False)
      if self.lastSelectedObject is None:
         self.lastSelectedObject = self.getObjectHit( base.mouseWatcherNode.getMouse())
         print self.lastSelectedObject
         # Try to update the UI
         if self.lastSelectedObject and self.lastSelectedObject.getTag("type") == "spawn":
            print self.lastSelectedObject.getTag("spawn2id")
            selectedspawn = globals.getspawnfromglobalspawnsbyname(self.lastSelectedObject.getTag("spawn2id"))
            if selectedspawn is None:
               selectedspawn = globals.getspawnfromglobalspawnsbyname(globals.database.lastinsertedspawn2id)
            if selectedspawn:
               globals.spawndialog.UpdateGUI(selectedspawn)
               gridmanager = GridpointManager()
               gridmanager.ResetGridList()
               if selectedspawn.spawnentry_pathgrid > 0:
                  gridmanager.picker = self
                  gridmanager.GenerateGrids(selectedspawn.spawnentry_pathgrid, globals.zoneid)
               globals.selectedSpawn = selectedspawn
               if globals.world.inst6:
                  globals.world.inst6.destroy()
               globals.world.inst6 = globals.addInstructions(0.7, "Current selection: " + "[" + str(globals.selectedSpawn.spawnentry_npcid) + "] " + globals.selectedSpawn.spawnentry_npcname + " (" + globals.selectedSpawn.spawngroup_name + ")")
         elif self.lastSelectedObject and self.lastSelectedObject.getTag("type") == "gridpoint":
            print "Grid not yet implemented!!!"
         # If we are in Insert Mode and not in Grid Mode, we'll insert a new spawn point into the world
         if globals.insertMode == True and globals.gridMode == False:
            #picker = Picker(render)
            thePoint = picker.pick()
            print thePoint
            spawn = Spawn()
            spawn.newdbentry = True
            spawn.spawnentry_npcid = int(globals.spawndialog.m_spawnEntryNpcIdTextCtrl.Value)
            if spawn.spawnentry_npcid == 0:
               wx.MessageBox('NPC ID cannot be 0.', 'Error', wx.OK | wx.ICON_ERROR)
               return

            # Coordinates are reversed in the 3D view so we have to adapt.
            spawn.spawnentry_x = thePoint[1].getY()
            spawn.spawnentry_y = thePoint[1].getX()
            spawn.spawnentry_z = thePoint[1].getZ()
            #
            # Spawnentry data
            #
            spawn.spawnentry_npcname = str(globals.database.GetNpcNameById(str(spawn.spawnentry_npcid)))
            spawn.spawnentry_animation = globals.spawndialog.m_spawnEntryAnimationTextCtrl.Value
            spawn.spawnentry_enabled = globals.spawndialog.m_spawnEntryEnabledTextCtrl.Value
            spawn.spawnentry_condvalue = globals.spawndialog.m_spawnEntryConditionValueTextCtrl.Value
            spawn.spawnentry_condition = globals.spawndialog.m_spawnEntryConditionTextCtrl.Value
            spawn.spawnentry_pathgrid = globals.spawndialog.m_spawnEntryPathGridTextCtrl.Value
            spawn.spawnentry_variance = globals.spawndialog.m_spawnEntryVarianceTextCtrl.Value
            spawn.spawnentry_heading = globals.spawndialog.m_spawnEntryHeadingTextCtrl.Value
            spawn.spawnentry_version = globals.spawndialog.m_spawnEntryVersionTextCtrl.Value
            spawn.spawnentry_respawn = globals.spawndialog.m_spawnEntryRespawnTextCtrl.Value
            spawn.spawnentry_zone = globals.spawndialog.m_spawnEntryZoneTextCtrl.Value
            #
            # Spawngroup data
            #
            spawn.spawngroup_name = "World_Forge_spawngroup_" + str(globals.database.GetNextSpawnGroupId())
            spawn.spawnentry_chance = globals.spawndialog.m_spawnGroupChanceTextCtrl.Value
            spawn.spawngroup_despawntimer = globals.spawndialog.m_spawnGroupDespawnTimerTextCtrl.Value
            spawn.spawngroup_mindelay = globals.spawndialog.m_spawnGroupMinDelayTextCtrl.Value
            spawn.spawngroup_miny = globals.spawndialog.m_spawnGroupMinYTextCtrl.Value
            spawn.spawngroup_maxy = globals.spawndialog.m_spawnGroupMaxYTextCtrl.Value
            spawn.spawngroup_minx = globals.spawndialog.m_spawnGroupMinXTextCtrl.Value
            spawn.spawngroup_maxx = globals.spawndialog.m_spawnGroupMaxXTextCtrl.Value
            spawn.spawngroup_dist = globals.spawndialog.m_spawnGroupDistTextCtrl.Value
            spawn.spawngroup_spawnlimit = globals.spawndialog.m_spawnGroupSpawnLimitTextCtrl.Value
            spawn.spawngroup_delay = globals.spawndialog.m_spawnGroupDelayTextCtrl.Value

            spawn.addnewspawntoworld(thePoint, self)
            globals.spawn_list.append(spawn)
            globals.database.InsertNewSpawn(spawn)
            spawn.spawnentry_id = str(globals.database.lastinsertedspawn2id)
            spawn.spawngroup_id = str(globals.database.lastinsertedspawngroupid)
            self.lastSelectedObject = spawn.model
            self.lastSelectedObject.setTag("spawn2id", str(spawn.spawnentry_id))
            self.lastSelectedObject.setTag("type", "spawn")
            globals.spawndialog.AddNewSpawnToTree(spawn)
            globals.selectedSpawn = spawn
            globals.spawndialog.UpdateGUI(globals.selectedSpawn)
            #globals.world.clearSelection()
         # While in Insert + Grid mode, we only insert grid entries to an existing grid. No spawn management
         # whatsoever.
         elif globals.insertMode == True and globals.gridMode == True:
            print "INSERT GRID!!!!"
            sel = globals.griddialog.m_gridComboBox.GetSelection()
            gridid = globals.griddialog.m_gridComboBox.GetString(sel)
            if gridid:
               print gridid
               thePoint = picker.pick()
               gridpoint = Gridpoint()
               # Coordinates are reversed in the 3D view so we have to adapt.
               gridpoint.x = thePoint[1].getY()
               gridpoint.y = thePoint[1].getX()
               gridpoint.z = thePoint[1].getZ()
               gridpoint.zoneid = globals.zoneid
               gridpoint.gridid = gridid
               gridmanager = GridpointManager()
               gridpoint.addnewgridpointtoworld(thePoint, self)
               gridmanager.InsertNewGridEntry(gridpoint)
               globals.grid_list.append(gridpoint)
            else:
               print "NO GRIDID!!!"
      else:
         #picker = Picker(render)
         # TODO: WE NEED TO MAP THE MODEL WHICH HAS BEEN CLICKED ON TO AN INTERNAL LIST OF
         # ALL EXISTING SPAWNS AND RETURN THAT
         # the double click bug stems from the fact that we're testing item selection against
         # self.lastSelectedObject, which is, imo, obsolete.

         namedNode, thePoint, rawNode = picker.pick()
         print thePoint
         print self.lastSelectedObject.getTag("NpcName")
         print "Heading: " ,self.lastSelectedObject.getH()
         if globals.gridMode == False:
            selectedspawn = globals.getspawnfromglobalspawnsbyname(self.lastSelectedObject.getTag("spawn2id"))
            if selectedspawn:
               globals.spawndialog.UpdateGUI(selectedspawn)
               gridmanager = GridpointManager()
               gridmanager.ResetGridList()
               if selectedspawn.spawnentry_pathgrid > 0:
                  gridmanager.picker = self
                  gridmanager.GenerateGrids(selectedspawn.spawnentry_pathgrid, globals.zoneid)
               globals.selectedSpawn = selectedspawn
               if globals.world.inst6:
                  globals.world.inst6.destroy()
               globals.world.inst6 = globals.addInstructions(0.7, "Current selection: " + "[" + str(globals.selectedSpawn.spawnentry_npcid) + "] " + globals.selectedSpawn.spawnentry_npcname + " (" + globals.selectedSpawn.spawngroup_name + ")")
            if globals.editMode == True:
               self.lastSelectedObject.setPos(thePoint)
               if globals.selectedSpawn:
                   globals.selectedSpawn.spawnentry_x = thePoint.getY()
                   globals.selectedSpawn.spawnentry_y = thePoint.getX()
                   globals.selectedSpawn.spawnentry_z = thePoint.getZ()
                   globals.selectedSpawn.setheadingfromworld(self.lastSelectedObject.getH())
                   globals.spawndialog.UpdateGUI(globals.selectedSpawn)
                   if globals.config['autosave_edit-mode'] == 'True':
                      globals.database.UpdateSpawn(globals.selectedSpawn)
                   globals.world.clearSelection()
         else:
            selectedGrid = globals.getgridfromglobalgridsbyname(self.lastSelectedObject.getTag("gridid"), self.lastSelectedObject.getTag("number"))
            if selectedGrid:
                #TODO: implement this
                #globals.griddialog.UpdateGUI(selectedGrid)
                globals.selectedGrid = selectedGrid
                if globals.editMode == True:
                   self.lastSelectedObject.setPos(thePoint)
                   if globals.selectedGrid:
                      globals.selectedGrid.x = thePoint.getY()
                      globals.selectedGrid.y = thePoint.getX()
                      globals.selectedGrid.z = thePoint.getZ()
                      globals.selectedGrid.setheadingfromworld(self.lastSelectedObject.getH())
                      globals.selectedGrid.gridid = self.lastSelectedObject.getTag("gridid")
                      globals.selectedGrid.number = self.lastSelectedObject.getTag("number")
                      print self.lastSelectedObject.getTag("gridid")
                      print self.lastSelectedObject.getTag("number")
                      #TODO: implement this
                      #globals.griddialog.UpdateGUI(globals.selectedGrid)

                      if globals.config['autosave_grid-mode'] == 'True':
                         globals.database.UpdateDbGridPoint(globals.selectedGrid)
                      gridmanager = GridpointManager()
                      gridmanager.ResetGridList()
                      gridmanager.GenerateGrids(globals.selectedGrid.gridid, globals.zoneid)
         self.lastSelectedObject = None