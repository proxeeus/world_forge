# -*- coding: utf-8 -*-

import wx
import wx.xrc
import re
import globals
from components.database import Database
from components.gridpointmanager import GridpointManager
from components.gridpoint import Gridpoint
from panda3d.core import Point3
from config import Configurator
pattern = "\(([^\)]+)\)"

class GridsFrame ( wx.Frame ):
	
	def __init__(self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Grids", pos = wx.DefaultPosition, size = wx.Size( 524, 181 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
		#treeViewSizer = wx.BoxSizer( wx.VERTICAL )

		# Treeview
		self.m_treeCtrlGrids = wx.TreeCtrl( self, wx.ID_ANY, wx.Point(199, 19), wx.Size( 180,100 ), wx.TR_DEFAULT_STYLE )
		# Spawngroup
		self.m_gridStaticText = wx.StaticText(self, wx.ID_ANY, "Grid", wx.Point(4,22), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_gridTypeStaticText = wx.StaticText(self, wx.ID_ANY, "Wander", wx.Point(4, 51), wx.DefaultSize,wx.TR_DEFAULT_STYLE)
		self.m_gridType2StaticText = wx.StaticText(self, wx.ID_ANY, "Pause", wx.Point(4, 80), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_gridComboBox = wx.ComboBox(self, wx.ID_ANY, "", wx.Point(57, 19), wx.Size(136,24), [],wx.CB_DROPDOWN)
		self.m_gridTypeComboBox = wx.ComboBox(self, wx.ID_ANY, "", wx.Point(57, 48), wx.Size(136, 24), ["0","1","2","3","4","5","6"], wx.CB_DROPDOWN)
		self.m_gridType2ComboBox = wx.ComboBox(self, wx.ID_ANY, "", wx.Point(57, 77), wx.Size(136, 24), ["0","1","2"], wx.CB_DROPDOWN)

		#self.m_spawnEntryZoneTextCtrl.SetLabel(globals.config['default_zone'])

		# Buttons
		self.m_LoadGridButton = wx.Button(self, wx.ID_ANY, "Load Grid", wx.Point(385, 19), wx.Size(109, 23), 0, wx.DefaultValidator)
		self.m_DeleteGridButton = wx.Button(self, wx.ID_ANY, "Delete Grid", wx.Point(385, 48), wx.Size(109, 23), 0, wx.DefaultValidator)
		self.m_NewGridButton = wx.Button(self, wx.ID_ANY, "New Grid", wx.Point(385, 77), wx.Size(109, 23), 0, wx.DefaultValidator)

		self.m_LoadGridButton.Bind(wx.EVT_BUTTON, self.OnLoadGrid)
		self.m_NewGridButton.Bind(wx.EVT_BUTTON, self.OnNewGrid)
		#treeViewSizer.Add( self.m_treeCtrlSpawnGroups, 0, wx.ALL, 5 )

		self.m_treeCtrlGrids.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnDoubleClickGrid)
		self.m_treeCtrlGrids.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelectSpawn)
		
		#self.SetSizer( treeViewSizer )
		self.Layout()
		
		self.Centre( wx.BOTH )


	### EVENTS

	def OnNewGrid(self, event):
		print "new grid lol"
		selType = self.m_gridTypeComboBox.GetSelection()
		type = self.m_gridTypeComboBox.GetString(selType)
		selType2 = self.m_gridType2ComboBox.GetSelection()
		type2 = self.m_gridType2ComboBox.GetString(selType2)
		if type and type2:
			gridpoint = Gridpoint()
			gridpoint.zoneid = globals.zoneid
			gridpoint.type = type
			gridpoint.type2 = type2
			globals.database.InsertNewGrid(gridpoint)
			self.m_gridComboBox.Append(str(globals.database.lastinsertedgridid))
		else:
			print "NOPE"

	def OnLoadGrid(self, event):
		self.LoadGrid()

	def LoadGrid(self):
		gridmanager = GridpointManager()
		gridmanager.ResetGridList()
		self.m_treeCtrlGrids.DeleteAllItems()
		root = self.m_treeCtrlGrids.AddRoot('Gridpoints for this grid')
		sel = self.m_gridComboBox.GetSelection()
		gridid = self.m_gridComboBox.GetString(sel)
		cursor = globals.database.GetDbGridPointsData(gridid, globals.zoneid)
		gridsnumrows = cursor.rowcount
		for x in range(0, gridsnumrows):
			row = cursor.fetchone()
			self.m_treeCtrlGrids.AppendItem(root, str(row["number"]) + ": " + str(row["x"]) + ", " + str(row["y"]) + ", " + str(row["z"]))

		gridmanager.GenerateGrids(gridid, globals.zoneid)
		self.m_treeCtrlGrids.ExpandAll()

	# TODO: FINISH THIS
	def OnDelete(self, event):
		print "toto"

	def RecursiveDelete(self, root):
		item, cookie = self.m_treeCtrlGrids.GetFirstChild(root, cookie)

		while item.IsOk():
			text = self.m_treeCtrlGrids.GetItemText(item)
			idpattern = "[" + str(globals.selectedSpawn.spawnentry_id) + "]"
			if idpattern in text:
				self.m_treeCtrlGrids.RemoveChild(item)
			if self.m_treeCtrlGrids.ItemHasChildren(item):
				sibling = self.RecursiveDelete(item)
				if sibling.isOk():
					self.m_treeCtrlGrids.RemoveChild(sibling)
			item = self.m_treeCtrlGrids.GetNextChild(root, cookie)
	#END TODO

	def OnSave(self, event):
		print "toto"

	def OnSelectSpawn(self, event):
		print "toto"
		#idpattern = "\[([^\)]+)\]"
		#selectedText = self.m_treeCtrlSpawnGroups.GetItemText(event.GetItem())
		#match = re.search(idpattern, selectedText)
		#if match:
		#	id = match.group(1)
		#	spawn = globals.getspawnfromglobalspawnsbyname(id)
		#	#TYPE PROBLEM ? ID is int first then string? and it messes up the array search code??
		#	self.UpdateGUI(spawn)
		#	globals.selectedSpawn = spawn
		#	print "cbatte"

	# Double-click on a node
	def OnDoubleClickGrid(self, event):
		print "toto"
		pattern = "\d+.\d+"
		selectedText = self.m_treeCtrlGrids.GetItemText(event.GetItem())
		match = re.search(pattern, selectedText)
		if match:
			found = match.group()
			selectedText = selectedText.split(":")
			coords = selectedText[1].split(",")
			globals.selectedGridXYZ = found
			globals.selectedGridPoint3D = Point3(float(coords[1]), float(coords[0]), float(coords[2]))
			model = self.GetModelByXYZ(globals.selectedGridPoint3D, globals.grid_list)
		if model:
			globals.hasClickedGrid = True;
			print "before dbl click"
			print base.camera.getPos()
			print "after dblclick"
			print base.camera.getPos()


	def UpdateGUI(self,spawn):
		print "toto"


	def GetModelByXYZ(self, point3D, grid_list):
		print point3D
		for grid in grid_list:
			currentP3D = Point3(grid.model.getX(), grid.model.getY(), grid.model.getZ())
			if point3D == currentP3D:
				return grid.model

	def __del__( self ):
		pass

	@property
	def GetGridsComboBox(self):
		return self.m_gridComboBox

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

	def AddNewSpawnToTree(self, spawn):
		print "toto"
		#npcname = globals.database.GetNpcNameById(spawn.spawnentry_npcid)
		#spawngroup = self.m_treeCtrlSpawnGroups.AppendItem(self.m_treeCtrlSpawnGroups.GetRootItem(), spawn.spawngroup_name)
		#self.m_treeCtrlSpawnGroups.AppendItem(spawngroup, "[" + str(spawn.spawnentry_id) + "] " + npcname + "  (" + str(spawn.spawnentry_x) + ", " + str(spawn.spawnentry_y) + ", " + str(spawn.spawnentry_z) + ")")