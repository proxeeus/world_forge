'''
World Forge
based on the Panda zonewalk engine

worldforge.py main driver
gsk December 2012

LICENSE:

Copyright (c) 2012, Gedolian Soft Kram
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided 
that the following conditions are met:

    Redistributions of source code must retain the above copyright notice, this list of conditions 
    and the following disclaimer.
    Redistributions in binary form must reproduce the above copyright notice, this list of conditions 
    and the following disclaimer in the documentation and/or other materials provided with the distribution.
    Neither the name of the <ORGANIZATION> nor the names of its contributors may be used to endorse or 
    promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR 
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, 
OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY 
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''

import sys
from math import pi, sin, cos, fabs

from panda3d.core import TextNode, PandaNode, NodePath
from panda3d.core import CollisionTraverser,CollisionNode
from panda3d.core import CollisionHandlerQueue,CollisionRay
from panda3d.core import AmbientLight,DirectionalLight, PointLight
from panda3d.core import Vec3, Vec4, Point3, VBase4, BitMask32
from panda3d.core import Fog

from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import WindowProperties

from gui.modelpicker import ModelPicker
from pandac.PandaModules import CollisionSphere

from zone import Zone
from config import Configurator
from gui.filedialog import FileDialog

import wx
from gui.spawnerdialog import SpawnsFrame
import globals
import MySQLdb
from components.database import Database
from components.spawn import Spawn

last_selected_model = None
spawndialog = None

VERSION = '0.1.4'

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-1.3, pos), align=TextNode.ALeft, scale = .04)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                        pos=(1.3,-0.95), align=TextNode.ARight, scale = .03)
        
class MouseAccume(object):
    def __init__(self,getCenter,hScaling=1,vScaling=1,aMax=5,dMax=10):
        super(MouseAccume,self).__init__()
        self.getCenter = getCenter
        self.accumMax = aMax
        self.decelMax = dMax
        self.hScale = hScaling
        self.vScale = vScaling
        self.accumCount = 0
        self.decelCount = 0
        self.anchor_x = 0
        self.anchor_y = 0
        self.dx = 0
        self.dy = 0
        self.last_x = 0
        self.last_y = 0

    def update(self):
        mData = base.win.getPointer(0)
        mouse_x = mData.getX()
        mouse_y = mData.getY()
        if self.accumCount == 0:
            self.anchor_x = mouse_x
            self.anchor_y = mouse_y
            self.last_x = mouse_x
            self.last_y = mouse_y
            self.decelCount = 0

        if self.accumCount < self.accumMax:
            #print("Accumulating " + str(self.accumCount) + "max: " + str(self.accumMax))
            self.accumCount += 1
        else:
            if self.decelCount < self.decelMax:
                #print("Smoothing")
                self.dx = (mouse_x - self.anchor_x) * self.hScale
                self.dy = (self.anchor_y - mouse_y) * self.vScale
                #print(" Deltas %f : %f " % (self.dx,self.dy))
                self.anchor_x += self.dx * .3
                self.anchor_y -= self.dy * .3
                
            tdx = self.last_x - mouse_x
            tdy = self.last_y - mouse_y
            if tdx == 0 and tdy == 0:
                self.decelCount += 1
            else:
                self.decelCount = 0

            if self.decelCount > self.decelMax:
                self.dx = 0
                self.dy = 0
                self.accumCount = 0
                center = self.getCenter()
                base.win.movePointer(0, center[0], center[1])

        self.last_x = mouse_x
        self.last_y = mouse_y

    def reset(self):
        self.accumCount = 0
        self.dx = 0
        self.dy = 0


class World(DirectObject):
    cfg = None
    def __init__(self):
        self.last_mousex = 0
        self.last_mousey = 0

        self.zone = None
        self.zone_reload_name = None
        
        self.winprops = WindowProperties( )

        # simple console output
        self.consoleNode = NodePath(PandaNode("console_root"))
        self.consoleNode.reparentTo(aspect2d)

        self.console_num_lines = 24
        self.console_cur_line = -1
        self.console_lines = []
        for i in range(0, self.console_num_lines):
            self.console_lines.append(OnscreenText(text='', style=1, fg=(1,1,1,1),
                        pos=(-1.3, .4-i*.05), align=TextNode.ALeft, scale = .035, parent = self.consoleNode))

        # Configuration
        self.consoleOut('World Forge v.%s loading configuration' % VERSION)
        self.configurator = Configurator(self)
        cfg = self.configurator.config
        resaveRes = False
        if 'xres' in cfg:
            self.xres = int(cfg['xres'])
        else:
            self.xres = 1024
            resaveRes = True

        if 'yres' in cfg:
            self.yres = int(cfg['yres'])
        else:
            self.yres = 768
            resaveRes = True

        if resaveRes:
            self.saveDefaultRes()

        self.xres_half = self.xres / 2
        self.yres_half = self.yres / 2
        self.mouse_accum = MouseAccume( lambda: (self.xres_half,self.yres_half))

        self.eyeHeight = 7.0
        self.rSpeed = 80
        self.flyMode = 1

        # application window setup
        base.win.setClearColor(Vec4(0,0,0,1))
        self.winprops.setTitle( 'World Forge')
        self.winprops.setSize(self.xres, self.yres) 
        
        base.win.requestProperties( self.winprops ) 
        base.disableMouse()
        
        # Post the instructions
        self.title = addTitle('World Forge v.' + VERSION)
        self.inst0 = addInstructions(0.95, "[FLYMODE][1]")
        self.inst1 = addInstructions(-0.95, "Camera control with WSAD/mouselook. Press K for hotkey list, ESC to exit.")
        self.inst2 = addInstructions(0.9,  "Loc:")
        self.inst3 = addInstructions(0.85, "Hdg:")
        self.error_inst = addInstructions(0, '')
        self.kh = []
        
        self.campos = Point3(155.6, 41.2, 4.93)
        base.camera.setPos(self.campos)
        
        # Accept the application control keys: currently just esc to exit navgen       
        self.accept("escape", self.exitGame)
        self.accept("window-event", self.resizeGame)
        
        # Create some lighting
        ambient_level = .6
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor(Vec4(ambient_level, ambient_level, ambient_level, 1.0))
        render.setLight(render.attachNewNode(ambientLight))

        direct_level = 0.8
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(Vec3(0.0, 0.0, -1.0))
        directionalLight.setColor(Vec4(direct_level, direct_level, direct_level, 1))
        directionalLight.setSpecularColor(Vec4(direct_level, direct_level, direct_level, 1))
        render.setLight(render.attachNewNode(directionalLight))
        
        # create a point light that will follow our view point (the camera for now)
        # attenuation is set so that this point light has a torch like effect
        self.plight = PointLight('plight')
        self.plight.setColor(VBase4(0.8, 0.8, 0.8, 1.0))
        self.plight.setAttenuation(Point3(0.0, 0.0, 0.0002))
        
        self.plnp = base.camera.attachNewNode(self.plight)
        self.plnp.setPos(0, 0, 0)
        render.setLight(self.plnp)
        self.cam_light = 1
        
        self.keyMap = {"left":0, "right":0, "forward":0, "backward":0, "cam-left":0, \
            "cam-right":0, "mouse3":0, "flymode":1 }

        # setup FOG
        self.fog_colour = (0.8,0.8,0.8,1.0)
        self.linfog = Fog("A linear-mode Fog node")
        self.linfog.setColor(self.fog_colour)
        self.linfog.setLinearRange(700, 980)         # onset, opaque distances as params
        # linfog.setLinearFallback(45,160,320)
        base.camera.attachNewNode(self.linfog)
        render.setFog(self.linfog)
        self.fog = 1
        
        # camera control
        self.campos = Point3(0, 0, 0)
        self.camHeading = 0.0
        self.camPitch = 0.0
        base.camLens.setFov(65.0)
        base.camLens.setFar(1200) 
        
        self.cam_speed = 0  # index into self.camp_speeds
        self.cam_speeds = [40.0, 80.0, 160.0, 320.0, 640.0]
        
        
        # Collision Detection for "WALKMODE"
        # We will detect the height of the terrain by creating a collision
        # ray and casting it downward toward the terrain.  The ray will start above the camera.
        # A ray may hit the terrain, or it may hit a rock or a tree.  If it
        # hits the terrain, we can detect the height.  If it hits anything
        # else, we rule that the move is illegal.
        
        self.cTrav = CollisionTraverser()
        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0.0, 0.0, 0.0)
        self.camGroundRay.setDirection(0,0,-1)      # straight down
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.camGroundCol.setIntoCollideMask(BitMask32.allOff())
        
        # attach the col node to the camCollider dummy node
        self.camGroundColNp = base.camera.attachNewNode(self.camGroundCol)  
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)
        
        
        # Uncomment this line to see the collision rays
        # self.camGroundColNp.show()
       
        # Uncomment this line to show a visual representation of the 
        # collisions occuring
        # self.cTrav.showCollisions(render)
        
        # Add the spinCameraTask procedure to the task manager.
        # taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        globals.hasClickedSpawn = False;
        taskMgr.add(self.camTask, "camTask")

        self.toggleControls(1)

        # need to step the task manager once to make our fake console work
        taskMgr.step()

    # CONSOLE ---------------------------------------------------------------------
    def consoleScroll(self):
        for i in range(0, self.console_num_lines-1):
            self.console_lines[i].setText(self.console_lines[i+1].getText())
            
    def consoleOut(self, text):
        print text  # output to stdout/log too

        if self.console_cur_line == self.console_num_lines-1:
            self.consoleScroll()
        elif self.console_cur_line < self.console_num_lines-1:
            self.console_cur_line += 1

        self.console_lines[self.console_cur_line].setText(text)

        taskMgr.step()
    
    def consoleOn(self):
        self.consoleNode.show()
        
    def consoleOff(self):
        self.consoleNode.hide()
        
    # User controls -----------------------------------------------------------
    def toggleControls(self, on):

        cfg = self.configurator.config

        if on == 1:
            self.accept("escape", self.exitGame)

            self.accept("1", self.setSpeed, ["speed", 0])
            self.accept("2", self.setSpeed, ["speed", 1])
            self.accept("3", self.setSpeed, ["speed", 2])
            self.accept("4", self.setSpeed, ["speed", 3])
            self.accept("5", self.setSpeed, ["speed", 4])

            self.accept("alt-f", self.fogToggle)

            self.accept(cfg['control_lighting'], self.camLightToggle)
            self.accept(cfg['control_help'], self.displayKeyHelp)
            self.accept(cfg['control_flymode'], self.toggleFlymode)
            self.accept(cfg['control_reload-zone'], self.reloadZone)
            self.accept(cfg['control_cam-left'], self.setKey, ["cam-left",1])
            self.accept(cfg['control_cam-right'], self.setKey, ["cam-right",1])
            self.accept(cfg['control_forward'], self.setKey, ["forward",1])
            self.accept("mouse3", self.setKey, ["mouse3",1])
            self.accept(cfg['control_backward'], self.setKey, ["backward",1])
        
            self.accept("k-up", self.hideKeyHelp)
            self.accept(cfg['control_cam-left']+"-up", self.setKey, ["cam-left",0])
            self.accept(cfg['control_cam-right']+"-up", self.setKey, ["cam-right",0])
            self.accept(cfg['control_forward']+"-up", self.setKey, ["forward",0])
            self.accept("mouse3-up", self.setKey, ["mouse3",0])
            self.accept(cfg['control_backward']+"-up", self.setKey, ["backward",0])
            self.accept(cfg['toggle_edit-mode'], self.toggleEditMode)
            self.accept(cfg['toggle_insert-mode'], self.toggleInsertMode)
            self.accept(cfg['toggle_explore-mode'], self.toggleExploreMode)
            # Accept both single-presses and long presses for rotating models
            self.accept(cfg['rotate-right'] + "-repeat", self.rotateModelRight)
            self.accept(cfg['rotate-left'] + "-repeat", self.rotateModelLeft)
            self.accept(cfg['rotate-right'], self.rotateModelRight)
            self.accept(cfg['rotate-left'], self.rotateModelLeft)
        else:
            messenger.clear()

    def rotateModelRight(self):
        if globals.editMode == True:
            if globals.selectedSpawn:
                cfg = self.configurator.config
                globals.selectedSpawn.model.setH(globals.selectedSpawn.model.getH() + int(cfg['rotation-amount']))
                # Really not sure about that...
                if globals.selectedSpawn.model.getH() > 360:
                    globals.selectedSpawn.model.setH(0)
                print globals.selectedSpawn.model.getH()
                globals.selectedSpawn.setheadingfromworld(globals.selectedSpawn.model.getH())
                globals.spawndialog.m_spawnEntryHeadingTextCtrl.SetValue(str(globals.selectedSpawn.spawnentry_heading))
                if globals.config['autosave_edit-mode'] == 'True':
                    globals.database.UpdateSpawn(globals.selectedSpawn)
                print globals.selectedSpawn.spawnentry_heading

    def rotateModelLeft(self):
        if globals.editMode == True:
            if globals.selectedSpawn:
                cfg = self.configurator.config
                globals.selectedSpawn.model.setH(globals.selectedSpawn.model.getH() - int(cfg['rotation-amount']))
                # Really not sure about that either...
                if globals.selectedSpawn.model.getH() < -360:
                    globals.selectedSpawn.model.setH(0)
                print globals.selectedSpawn.model.getH()
                globals.selectedSpawn.setheadingfromworld(globals.selectedSpawn.model.getH())
                globals.spawndialog.m_spawnEntryHeadingTextCtrl.SetValue(str(globals.selectedSpawn.spawnentry_heading))
                if globals.config['autosave_edit-mode'] == 'True':
                    globals.database.UpdateSpawn(globals.selectedSpawn)
                print globals.selectedSpawn.spawnentry_heading

    def toggleDefaultMode(self):
        globals.editMode = False
        globals.insertMode = False
        globals.exploreMode = True
        print "STARTUP Explore mode ACTIVATED"

    def toggleEditMode(self):
        globals.editMode = True
        globals.insertMode = False
        globals.exploreMode = False
        print "Edit mode ACTIVATED"

    def toggleInsertMode(self):
        globals.editMode = False
        globals.insertMode = True
        globals.exploreMode = False
        print "Insert mode ACTIVATED"

    def toggleExploreMode(self):
        globals.editMode = False
        globals.insertMode = False
        globals.exploreMode = True
        print "Explore mode ACTIVATED"

    def setSpeed(self, key, value):
        self.cam_speed = value
        self.setFlymodeText()
        
    def fogToggle(self):
        if self.fog == 1:
            render.clearFog()
            base.camLens.setFar(100000) 
            self.fog = 0
        else:
            render.setFog(self.linfog)
            base.camLens.setFar(1200) 
            self.fog = 1
            
    def camLightToggle(self):
        if self.cam_light == 0:
            render.setLight(self.plnp)
            self.cam_light = 1
        else:
            render.clearLight(self.plnp)
            self.cam_light = 0
        
    def displayKeyHelp(self):
        self.kh = []
        msg = 'HOTKEYS:'
        pos = 0.75
        self.kh.append(OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-0.5, pos), align=TextNode.ALeft, scale = .04))
        msg = '------------------'
        pos -= 0.05
        self.kh.append(OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-0.5, pos), align=TextNode.ALeft, scale = .04))
        msg = 'W: camera fwd, S: camera bck, A: rotate view left, D: rotate view right'
        pos -= 0.05
        self.kh.append(OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-0.5, pos), align=TextNode.ALeft, scale = .04))
        msg = '1-5: set camera movement speed'
        pos -= 0.05
        self.kh.append(OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-0.5, pos), align=TextNode.ALeft, scale = .04))
        msg = 'F: toggle Flymode/Walkmode'
        pos -= 0.05
        self.kh.append(OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-0.5, pos), align=TextNode.ALeft, scale = .04))
        msg = 'L: load a zone'
        pos -= 0.05
        self.kh.append(OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-0.5, pos), align=TextNode.ALeft, scale = .04))
        msg = 'ALT-F: toggle FOG and FAR plane on/off'
        pos -= 0.05
        self.kh.append(OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-0.5, pos), align=TextNode.ALeft, scale = .04))
        msg = 'T: toggle additional camera "torch" light on/off'
        pos -= 0.05
        self.kh.append(OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-0.5, pos), align=TextNode.ALeft, scale = .04))
        msg = 'Z: set currently loaded zone as new startup default'
        pos -= 0.05
        self.kh.append(OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-0.5, pos), align=TextNode.ALeft, scale = .04))
        msg = 'ESC: exit World Forge'
        pos -= 0.05
        self.kh.append(OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-0.5, pos), align=TextNode.ALeft, scale = .04))
     
    def hideKeyHelp(self):
        for n in self.kh:
            n.removeNode()
                        
    def setFlymodeText(self):
        zname = ''
        if self.zone:
            zname = self.zone.name
            
        if self.flyMode == 0:
            self.inst0.setText("[WALKMODE][%i] %s" % (self.cam_speed+1, zname))
        else:
            self.inst0.setText("[FLYMODE][%i] %s " % (self.cam_speed+1, zname))
        
    def toggleFlymode(self):
        zname = ''
        if self.zone:
            zname = self.zone.name

        if self.flyMode == 0:
            self.flyMode = 1
        else:
            self.flyMode = 0
            
        self.setFlymodeText()

    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        angleDegrees = task.time * 6.0
        angleRadians = angleDegrees * (pi / 180.0)
        base.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
        base.camera.setHpr(angleDegrees, 0, 0)
        return task.cont


    def camTask(self, task):
        if globals.hasClickedSpawn:
           base.camera.setPos(globals.selectedSpawnPoint3D)
           self.campos = globals.selectedSpawnPoint3D
           globals.hasClickedSpawn = False
        else:
            # query the mouse
            mouse_dx = 0
            mouse_dy = 0


            # if we have a mouse and the right button is depressed
            if base.mouseWatcherNode.hasMouse():
                if self.keyMap["mouse3"] != 0:
                    self.mouse_accum.update()
                else:
                    self.mouse_accum.reset()

            mouse_dx = self.mouse_accum.dx
            mouse_dy = self.mouse_accum.dy

            self.rXSpeed = fabs(self.mouse_accum.dx) * (self.cam_speed+1) * max(5 * 1000/self.xres,3)
            self.rYSpeed = fabs(self.mouse_accum.dy) * (self.cam_speed+1) * max(3 * 1000/self.yres,1)
            
            if (self.keyMap["cam-left"]!=0 or mouse_dx < 0):
                if self.rSpeed < 160:
                    self.rSpeed += 80 * globalClock.getDt()

                if mouse_dx != 0:
                    self.camHeading += self.rXSpeed * globalClock.getDt()
                else:
                    self.camHeading += self.rSpeed * globalClock.getDt()

                if self.camHeading > 360.0:
                    self.camHeading = self.camHeading - 360.0
            elif (self.keyMap["cam-right"]!=0 or mouse_dx > 0):
                if self.rSpeed < 160:
                    self.rSpeed += 80 * globalClock.getDt()

                if mouse_dx != 0:
                    self.camHeading -= self.rXSpeed * globalClock.getDt()
                else:
                    self.camHeading -= self.rSpeed * globalClock.getDt()

                if self.camHeading < 0.0:
                    self.camHeading = self.camHeading + 360.0
            else:
                self.rSpeed = 80

            if mouse_dy > 0:
                self.camPitch += self.rYSpeed * globalClock.getDt()
            elif mouse_dy < 0:
                self.camPitch -= self.rYSpeed * globalClock.getDt()
            
            # set camera heading and pitch
            base.camera.setHpr(self.camHeading, self.camPitch, 0)

            # viewer position (camera) movement control
            v = render.getRelativeVector(base.camera, Vec3.forward())
            if not self.flyMode:
                v.setZ(0.0)
        
            move_speed = self.cam_speeds[self.cam_speed]
            if self.keyMap["forward"] == 1:
                self.campos += v * move_speed * globalClock.getDt()
            if self.keyMap["backward"] == 1:
                self.campos -= v * move_speed * globalClock.getDt()            

            # actually move the camera
            lastPos = base.camera.getPos()
            base.camera.setPos(self.campos)
            # self.plnp.setPos(self.campos)      # move the point light with the viewer position

            # WALKMODE: simple collision detection
            # we simply check a ray from slightly below the "eye point" straight down
            # for geometry collisions and if there are any we detect the point of collision
            # and adjust the camera's Z accordingly
            if self.flyMode == 0:   
                # move the camera to where it would be if it made the move 
                # the colliderNode moves with it
                # base.camera.setPos(self.campos)
                # check for collissons
                self.cTrav.traverse(render)
                entries = []
                for i in range(self.camGroundHandler.getNumEntries()):
                    entry = self.camGroundHandler.getEntry(i)
                    entries.append(entry)
                    # print 'collision'
                entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                             x.getSurfacePoint(render).getZ()))
                                     
                if (len(entries) > 0): # and (entries[0].getIntoNode().getName() == "terrain"):
                    # print len(entries)
                    self.campos.setZ(entries[0].getSurfacePoint(render).getZ()+self.eyeHeight)
                else:
                    self.campos = lastPos
                    base.camera.setPos(self.campos)
        
                #if (base.camera.getZ() < self.player.getZ() + 2.0):
                #    base.camera.setZ(self.player.getZ() + 2.0)


            # update loc and hpr display
            pos = base.camera.getPos()
            hpr = base.camera.getHpr()
            self.inst2.setText('Loc: %.2f, %.2f, %.2f' % (pos.getX(), pos.getY(), pos.getZ()))
            self.inst3.setText('Hdg: %.2f, %.2f, %.2f' % (hpr.getX(), hpr.getY(), hpr.getZ()))
        return task.cont

    def exitGame(self):           
        sys.exit(0)

    def resizeGame(self,win):
        props = base.win.getProperties() 
        self.xres = props.getXSize()
        self.yres = props.getYSize()
        self.xres_half = self.xres / 2
        self.yres_half = self.yres / 2
        self.saveDefaultRes()
                
    #Records the state of the arrow keys
    # this is used for camera control
    def setKey(self, key, value):
        self.keyMap[key] = value

    # -------------------------------------------------------------------------
    # this is the mythical MAIN LOOP :)
    def update(self):

        if self.zone_reload_name != None:
            self.doReload(self.zone_reload_name)
            self.zone_reload_name = None

        if self.zone != None:
            self.zone.update()

        taskMgr.step()
        
        
    # ZONE loading ------------------------------------------------------------
    
    # general zone loader driver
    # removes existing zone (if any) and load the new one 
    def loadZone(self, name, path):
        if path[len(path)-1] != '/':
            path += '/'

        if self.zone:
            self.zone.rootNode.removeNode()
            
        self.zone = Zone(self, name, path)
        error = self.zone.load()
        if error == 0:
            self.consoleOff()
            self.setFlymodeText()
            base.setBackgroundColor(self.fog_colour)
        
    def saveDefaultRes(self):
        cfg = self.configurator.config
        cfg['xres'] = str(self.xres)
        cfg['yres'] = str(self.yres)

    # initial world load after bootup
    def load(self):       
        cfg = self.configurator.config
            
        zone_name = cfg['default_zone']
        globals.currentZone = zone_name
        basepath = cfg['basepath']
        self.loadZone(zone_name, basepath)

    # zone reload user interface
    
    # this gets called from our update loop when it detects that zone_reload_name has been set
    # we do this in this convoluted fashion in order to keep the main loop taskMgr updates ticking
    # because otherwise our status console output at various stages during the zone load would not
    # be displayed. Yes, this is hacky.
    def doReload(self, name):
        cfg = self.configurator.config
        basepath = cfg['basepath']
        self.loadZone(name, basepath)

    # form dialog callback
    # this gets called from the form when the user has entered a something
    # (hopefully a correct zone short name)
    def reloadZoneDialogCB(self, name):
        self.frmDialog.end()
        self.zone_reload_name = name
        self.toggleControls(1)

    # this is called when the user presses "l"
    # it disables normal controls and fires up our query form dialog
    def reloadZone(self):
        base.setBackgroundColor((0,0,0))
        self.toggleControls(0)
        self.consoleOn()
        self.frmDialog = FileDialog(
            "Please enter the shortname of the zone you wish to load:", 
            "Examples: qrg, blackburrow, freportn, crushbone etc.",
            self.reloadZoneDialogCB) 
        
        self.frmDialog.activate()   # relies on the main update loop to run

    ###############################
    # EXPERIMENTAL         
    def doLogin(self):
        
        self.login_client = UDPClientStream('127.0.0.1', 5998)

    #####################################
    # Custom methods
    #####################################


    # Handles populating the zone with spawn data from the EQEmu DB
    # also makes each spawner model pickable
    def PopulateSpawns(self, cursor, numrows):
        spawn_coords = list()
        globals.spawn_list = list()
        cfg = self.configurator.config
        for x in range(0, numrows):
            row = cursor.fetchone()
            point = Point3(long(row["Spawn2Y"]), long(row["Spawn2X"]), long(row["Spawn2Z"]))
            if cfg['ignore_duplicate_spawns'] == 'True':
                if point not in spawn_coords:
                    self.PlaceSpawnPointOn3dMap(row)
                    spawn_coords.append(point)
            else:
                self.PlaceSpawnPointOn3dMap(row)

    def PlaceSpawnPointOn3dMap(self, row):
        spawn = Spawn()
        self.InitSpawnData(spawn, row)
        spawn.model = loader.loadModel(spawn.modelname)
        spawn.initmodel()
        spawn.model.reparentTo(render)
        spawn.initheadingfromdb(row["Spawn2Heading"])
        spawn.placeintoworld(row["Spawn2Y"], row["Spawn2X"], row["Spawn2Z"])
        min, macks = spawn.model.getTightBounds()
        radius = max([macks.getY() - min.getY(), macks.getX() - min.getX()]) / 2
        cs = CollisionSphere(row["Spawn2X"], row["Spawn2Y"], row["Spawn2Z"], radius)
        csNode = spawn.model.attachNewNode(CollisionNode("modelCollide"))
        csNode.node().addSolid(cs)
        # TODO: ADD MORE TAGS??
        spawn.model.setTag("name", row["NpcName"])
        spawn.model.setTag("spawngroup_name", row["spawngroup_name"])
        spawn.model.setTag("spawn2id", str(row["Spawn2Id"]))
        spawn.model.setTag("type", "spawn")
        picker.makePickable(spawn.model)
        globals.spawn_list.append(spawn)


    # Initializes a spawn object with database values
    def InitSpawnData(self, spawn, row):
        spawn.spawngroup_id = row["Spawngroup_id"]
        spawn.spawngroup_name = row["spawngroup_name"]
        spawn.spawngroup_minx = row["Spawngroup_minX"]
        spawn.spawngroup_maxx= row["Spawngroup_maxX"]
        spawn.spawngroup_miny = row["Spawngroup_minY"]
        spawn.spawngroup_maxy = row["Spawngroup_maxY"]
        spawn.spawngroup_dist = row["Spawngroup_dist"]
        spawn.spawngroup_mindelay = row["Spawngroup_mindelay"]
        spawn.spawngroup_delay = row["Spawngroup_delay"]
        spawn.spawngroup_despawn = row["Spawngroup_despawntimer"]
        spawn.spawngroup_despawntimer = row["Spawngroup_despawntimer"]
        spawn.spawngroup_spawnlimit = row["Spawngroup_spawnlimit"]


        spawn.spawnentry_id = row["Spawn2Id"]
        spawn.spawnentry_npcid = row["NpcId"]
        spawn.spawnentry_npcname = row["NpcName"]
        spawn.spawnentry_chance = row["Spawnentry_chance"]
        spawn.spawnentry_x = row["Spawn2X"]
        spawn.spawnentry_y = row["Spawn2Y"]
        spawn.spawnentry_z = row["Spawn2Z"]
        spawn.spawnentry_heading = row["Spawn2Heading"]
        spawn.spawnentry_respawn = row["Spawn2Respawn"]
        spawn.spawnentry_variance = row["Spawn2Variance"]
        spawn.spawnentry_pathgrid = row["Spawn2Grid"]
        spawn.spawnentry_condition = row["Spawn2Condition"]
        spawn.spawnentry_condvalue = row["Spawn2CondValue"]
        spawn.spawnentry_version = row["Spawn2Version"]
        spawn.spawnentry_enabled = row["Spawn2Enabled"]
        spawn.spawnentry_animation = row["Spawn2Animation"]
        spawn.spawnentry_zone = row["Spawn2Zone"]

        spawn.spawnentry_originalx = row["Spawn2X"]
        spawn.spawnentry_originaly = row["Spawn2Y"]
        spawn.spawnentry_originalz = row["Spawn2Z"]
        spawn.spawnentry_originalheading = row["Spawn2Heading"]


    # Initializes the camera position upon startup
    def InitCameraPosition(self):
        world.campos = Point3(-155.6, 41.2, 4.9 + world.eyeHeight)
        world.camHeading = 270.0

        base.camera.setPos(world.campos)

    def GetCamera(self):
        return base.camera

    ###################################
    # End
    ###################################

# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------

print 'starting World Forge v' + VERSION

world = World()
world.load()
configurator = Configurator(world)
cfg = configurator.config
globals.config = cfg
globals.zoneid = globals.getzoneidbyname(globals.config['default_zone'])
# Creates a ModelPicker object in charge of setting spawn models as Pickable.
picker = ModelPicker()
globals.grid_list = list()
globals.gridlinks_list = list()

# Loads the various GUI components
app = wx.App()
globals.spawndialog = SpawnsFrame(wx.Frame(None, -1, ' '))
globals.spawndialog.Show()
#

# Connects to the database
globals.database = Database(cfg['host'], cfg['user'], cfg['password'], cfg['port'], cfg['db'])
connection = globals.database.ConnectToDatabase()
# Gets spawn data for the current zone
cursor = globals.database.GetDbSpawnData()

numrows = cursor.rowcount

# Visually loads spawn data in the zone
world.PopulateSpawns(cursor, numrows)

# NEEDS REFACTORING
# Populates the spawns treeview
cursor = globals.database.GetDbSpawnData()
numrows = cursor.rowcount
treeview = globals.spawndialog.GetSpawnsTreeView
root = treeview.AddRoot('Spawns for this zone')

for x in range(0, numrows):
    row = cursor.fetchone()
    result = globals.spawndialog.GetItemByLabel(treeview, row["spawngroup_name"], treeview.GetRootItem())
    if result.IsOk():
        #spawngroup = treeview.AppendItem(result, row["spawngroup_name"])
        spawnpoint = treeview.AppendItem(result, "[" + str(row["Spawn2Id"]) + "] " + row["NpcName"] + "  (" + str(row["Spawn2X"]) + ", " + str(row["Spawn2Y"]) + ", " + str(row["Spawn2Z"]) + ")")
    else:
        spawngroup = treeview.AppendItem(root, row["spawngroup_name"])
        spawnpoint = treeview.AppendItem(spawngroup, "[" + str(row["Spawn2Id"]) + "] " + row["NpcName"] + "  (" + str(row["Spawn2X"]) + ", " + str(row["Spawn2Y"]) + ", " + str(row["Spawn2Z"]) + ")")

# start in Explore mode by default
world.toggleDefaultMode()
#######

while True:
    world.update();
    
    
    

