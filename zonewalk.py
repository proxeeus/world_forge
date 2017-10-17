'''
zonewalk

zonewalk.py main driver
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

import os
import sys, copy, struct
from math import pi, sin, cos, fabs



from direct.gui.OnscreenText import OnscreenText 


import direct.directbase.DirectStart

from panda3d.core import TextNode, PandaNode, NodePath
from panda3d.core import CollisionTraverser,CollisionNode
from panda3d.core import CollisionHandlerQueue,CollisionRay
from panda3d.core import Filename,AmbientLight,DirectionalLight, PointLight
from panda3d.core import Vec3, Vec4, Point3, VBase4, BitMask32
from panda3d.core import Fog, PStatClient

from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import WindowProperties

from gui.picker import Picker
from gui.picker2 import Picker2
from pandac.PandaModules import CollisionSphere

from zone import Zone
from config import Configurator
from gui.filedialog import FileDialog
from net.client import UDPClientStream

last_selected_model = None

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
        self.consoleOut('zonewalk v.%s loading configuration' % VERSION)
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
        self.winprops.setTitle( 'zonewalk')
        self.winprops.setSize(self.xres, self.yres) 
        
        base.win.requestProperties( self.winprops ) 
        base.disableMouse()

        # network test stuff
        self.login_client = None
        if 'testnet' in cfg:
            if cfg['testnet'] == '1':
                self.doLogin()
        
        # Post the instructions
        self.title = addTitle('zonewalk v.' + VERSION)
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
            # Deactivate this for now
            #self.accept("z", self.saveDefaultZone)
            self.accept(cfg['control_cam-left'], self.setKey, ["cam-left",1])
            self.accept(cfg['control_cam-right'], self.setKey, ["cam-right",1])
            self.accept(cfg['control_forward'], self.setKey, ["forward",1])
            # Mouse1 should be for clicking on objects
            #self.accept("mouse1", self.setKey, ["forward",1])
            self.accept("mouse3", self.setKey, ["mouse3",1])
            self.accept(cfg['control_backward'], self.setKey, ["backward",1])
        
            self.accept("k-up", self.hideKeyHelp)
            self.accept(cfg['control_cam-left']+"-up", self.setKey, ["cam-left",0])
            self.accept(cfg['control_cam-right']+"-up", self.setKey, ["cam-right",0])
            self.accept(cfg['control_forward']+"-up", self.setKey, ["forward",0])
            # Mouse1 should be for clicking on objects
            #self.accept("mouse1-up", self.setKey, ["forward",0])
            self.accept("mouse3-up", self.setKey, ["mouse3",0])
            self.accept(cfg['control_backward']+"-up", self.setKey, ["backward",0])
        else:
            messenger.clear()
            
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
        msg = 'ESC: exit zonewalk'
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
   
        if self.login_client != None:
            self.login_client.update()  
        
        
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
        #self.configurator.saveConfig()

    # initial world load after bootup
    def load(self):       
        cfg = self.configurator.config
        
        if self.login_client != None:
            return
            
        zone_name = cfg['default_zone']
        basepath = cfg['basepath']
        self.loadZone(zone_name, basepath)
    

    # config save user interfacce
    def saveDefaultZone(self):
        if self.zone:
            cfg = self.configurator.config
            cfg['default_zone'] = self.zone.name
            #self.configurator.saveConfig()

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
def onModelClick():
    # Code adapted freely from http://www.panda3d.org/forums/viewtopic.php?t=12717
    global picker, selected_model
    namedNode, thePoint, rawNode = picker.pick()
    if namedNode:
        if "_mesh" not in namedNode.getName():  # rough test to avoid printing infos on global zone mesh (ie: "freporte_mesh")
            name = namedNode.getName()
            p = namedNode.getParent()
            pos = p.getPos()
            selected_model = namedNode
            print namedNode.getName()
            print "Collision Point: ", thePoint

            namedNode.ls()
        else:
            print "Clicked location point (y, x, z):", thePoint
            #selected_model.setPos(thePoint.getX(), thePoint.getY(), thePoint.getZ())

            m.setPos(thePoint.getX(), thePoint.getY(), thePoint.getZ())
            print "Moved !"

###################################

# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------

print 'starting zonewalk v' + VERSION

# PStatClient.connect()

world = World()
world.load()


# THIS stuff ought to go into config at some point :)

# this position is near the qeynos side zone in of Blackburrow
world.campos = Point3(-155.6, 41.2, 4.9 + world.eyeHeight)
world.camHeading = 270.0

# point near fire in tunnel anim texture test
# world.campos = Point3( -1643.44, -156.67, 7 )
# world.camHeading = 41.19

base.camera.setPos(world.campos)

### TESTING MODEL CLICK
# loads a model in memory
m = loader.loadModel("models/cube.egg")
# renders it to the scene
m.reparentTo(render)
# set up the collision body
min,macks= m.getTightBounds()
radius = max([macks.getY() - min.getY(), macks.getX() - min.getX()])/2

cs = CollisionSphere(0,0,0, radius)
csNode = m.attachNewNode(CollisionNode("modelCollide"))
csNode.node().addSolid(cs)

#picker = Picker(render)
picker = Picker2()
picker.makePickable(m)

#base.accept("mouse1", onModelClick)
#######

while True:
    world.update();
    
    
    

