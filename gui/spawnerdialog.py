# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Oct 18 2017)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class SpawnsFrame
###########################################################################

import re
import globals
from panda3d.core import Vec3, Vec4, Point3, VBase4, BitMask32
from math import pi, sin, cos, fabs
pattern = "\(([^\)]+)\)"

class SpawnsFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Spawns", pos = wx.DefaultPosition, size = wx.Size( 500,380 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHints( -1, -1 )
		
		self.m_menubar = wx.MenuBar( 0 )
		self.m_fileMenu = wx.Menu()
		#self.m_menuItemQuit = wx.MenuItem( self.m_fileMenu, wx.ID_ANY, u"Quit", wx.EmptyString, wx.ITEM_NORMAL )
		#self.m_fileMenu.Append( self.m_menuItemQuit )
		
		#self.m_menubar.Append( self.m_fileMenu, u"File" ) 
		
		self.SetMenuBar( self.m_menubar )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_treeCtrlSpawnGroups = wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 15000,10000 ), wx.TR_DEFAULT_STYLE )
		bSizer1.Add( self.m_treeCtrlSpawnGroups, 0, wx.ALL, 5 )

		self.m_treeCtrlSpawnGroups.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnSelectSpawn )
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		self.Centre( wx.BOTH )


	# Double-click on a node
	def OnSelectSpawn(self, event):
		selectedText = self.m_treeCtrlSpawnGroups.GetItemText(event.GetItem())
		match = re.search(pattern, selectedText)
		if match:
			found = match.group(1)
			coords = found.split(",")
			globals.selectedSpawnXYZ = found
			globals.selectedSpawnPoint3D = Point3(float(coords[1]), float(coords[0]), float(coords[2]))
			model = self.GetModelByXYZ(globals.selectedSpawnPoint3D, globals.model_list)
		if model:
			globals.hasClickedSpawn = True;
			print "before dbl click"
			print base.camera.getPos()
			#base.camera.setPos(model.getPos())
			print "after dblclick"
			print base.camera.getPos()



	def GetModelByXYZ(self, point3D, model_list):
		print point3D
		for model in model_list:
			currentP3D = Point3(model.getX(), model.getY(), model.getZ())
			if point3D == currentP3D:
				return model

	def __del__( self ):
		pass

	@property
	def GetSpawnsTreeView(self):
		return self.m_treeCtrlSpawnGroups

	def GetItemByLabel(self, tree, search_text, root_item):
		item, cookie = tree.GetFirstChild(root_item)

		while item.IsOk():
			text = tree.GetItemText(item)
			if text.lower() == search_text.lower():
				return item
			if tree.ItemHasChildren(item):
				match = self.GetItemByLabel(tree, search_text, item)
				if match.IsOk():
					return match
			item, cookie = tree.GetNextChild(root_item, cookie)

		return wx.TreeItemId()


