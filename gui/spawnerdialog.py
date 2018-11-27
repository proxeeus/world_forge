# -*- coding: utf-8 -*-

import wx
import wx.xrc
import re
import globals
from panda3d.core import Point3
pattern = "\(([^\)]+)\)"

class SpawnsFrame ( wx.Frame ):
	
	def __init__(self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Spawns", pos = wx.DefaultPosition, size = wx.Size( 818,497 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
		self.initmenubar()
		treeViewSizer = wx.BoxSizer( wx.VERTICAL )

		# Treeview
		self.m_treeCtrlSpawnGroups = wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 275,445 ), wx.TR_DEFAULT_STYLE )
		# Spawngroup
		self.m_spawnGroupNameStaticText = wx.StaticText(self, wx.ID_ANY, "Spawngroup", wx.Point(300, 9), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupNameTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "", wx.Point(303, 29), wx.Size(227, 22), wx.TR_DEFAULT_STYLE)
		# Spawngroup coords
		self.m_spawnGroupMinXStaticText = wx.StaticText(self, wx.ID_ANY, "minX", wx.Point(300, 64), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupMinXTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(345, 61), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupMaxXStaticText = wx.StaticText(self, wx.ID_ANY, "maX", wx.Point(411, 64), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupMaxXTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(459, 61), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupMinYStaticText = wx.StaticText(self, wx.ID_ANY, "minY", wx.Point(508, 64), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupMMinYTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(552, 61), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupMaxYStaticText = wx.StaticText(self, wx.ID_ANY, "maxY", wx.Point(627, 66), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupMaxYTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(679, 61), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawngroup Dist
		self.m_spawnGroupDistStaticText = wx.StaticText(self, wx.ID_ANY, "Dist", wx.Point(300, 95), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupDistTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(345, 92), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawngroup Min Delay
		self.m_spawnGroupMinDelayStaticText = wx.StaticText(self, wx.ID_ANY, "Min Delay", wx.Point(383, 95), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupMinDelayTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "15000", wx.Point(459, 92), wx.Size(50, 22), wx.TR_DEFAULT_STYLE)
		# Spawngroup Delay
		self.m_spawnGroupDelayStaticText = wx.StaticText(self, wx.ID_ANY, "Delay", wx.Point(508, 95), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupDelayTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "15000", wx.Point(552, 92), wx.Size(50, 22), wx.TR_DEFAULT_STYLE)
		# Spawngroup Despawn
		self.m_spawnGroupDespawnStaticText = wx.StaticText(self, wx.ID_ANY, "Despawn", wx.Point(603, 95), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupDespawnTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(679, 92), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawngroup Despawn Timer
		self.m_spawnGroupDespawnTimerStaticText = wx.StaticText(self, wx.ID_ANY, "Despawn", wx.Point(300, 126), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupDespawnTimerTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(407, 126), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawngroup Spawn Limit
		self.m_spawnGroupSpawnLimitStaticText = wx.StaticText(self, wx.ID_ANY, "Spawn Limit", wx.Point(465, 129), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupSpawnLimitTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(552, 126), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawngroup Change
		self.m_spawnGroupChanceStaticText = wx.StaticText(self, wx.ID_ANY, "Chance", wx.Point(613, 129), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupChanceTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(679, 126), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)

		treeViewSizer.Add( self.m_treeCtrlSpawnGroups, 0, wx.ALL, 5 )

		self.m_treeCtrlSpawnGroups.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnSelectSpawn )
		
		self.SetSizer( treeViewSizer )
		self.Layout()
		
		self.Centre( wx.BOTH )


	### EVENTS

	def initmenubar(self):
		menubar = wx.MenuBar()
		fileMenu = wx.Menu()
		fileItem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
		menubar.Append(fileMenu, '&File')
		self.SetMenuBar(menubar)

		self.Bind(wx.EVT_MENU, self.OnQuit, fileItem)

	def OnQuit(self,e):
		exit(0)

	# Double-click on a node
	def OnSelectSpawn(self, event):
		selectedText = self.m_treeCtrlSpawnGroups.GetItemText(event.GetItem())
		match = re.search(pattern, selectedText)
		if match:
			found = match.group(1)
			coords = found.split(",")
			globals.selectedSpawnXYZ = found
			globals.selectedSpawnPoint3D = Point3(float(coords[1]), float(coords[0]), float(coords[2]))
			model = self.GetModelByXYZ(globals.selectedSpawnPoint3D, globals.spawn_list)
		if model:
			globals.hasClickedSpawn = True;
			print "before dbl click"
			print base.camera.getPos()
			print "after dblclick"
			print base.camera.getPos()



	def GetModelByXYZ(self, point3D, spawn_list):
		print point3D
		for spawn in spawn_list:
			currentP3D = Point3(spawn.model.getX(), spawn.model.getY(), spawn.model.getZ())
			if point3D == currentP3D:
				return spawn.model

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


