# -*- coding: utf-8 -*-

import wx
import wx.xrc
import re
import globals
from panda3d.core import Point3
pattern = "\(([^\)]+)\)"

class SpawnsFrame ( wx.Frame ):
	
	def __init__(self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Spawns", pos = wx.DefaultPosition, size = wx.Size( 850,540 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

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
		# Spawngroup Chance
		self.m_spawnGroupChanceStaticText = wx.StaticText(self, wx.ID_ANY, "Chance", wx.Point(613, 129), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupChanceTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(679, 126), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)

		# Spawnentry
		self.m_spawnEntryStaticText = wx.StaticText(self, wx.ID_ANY, "Spawnentry", wx.Point(300, 245), wx.Size(168, 22), wx.TR_DEFAULT_STYLE)
		# Spawnentry Npc ID
		self.m_spawnEntryNpcIdStaticText = wx.StaticText(self, wx.ID_ANY, "NPC Id", wx.Point(320, 268), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryNpcIdTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(379, 265), wx.Size(103, 22), wx.TR_DEFAULT_STYLE)
		# Spawnentry Coords
		self.m_spawnEntryXStaticText = wx.StaticText(self, wx.ID_ANY, "X", wx.Point(493, 267), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryXTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(516, 265), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryYStaticText = wx.StaticText(self, wx.ID_ANY, "Y", wx.Point(558, 268), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryYTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(581, 265), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryZStaticText = wx.StaticText(self, wx.ID_ANY, "Z", wx.Point(622, 267), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryZTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(645, 265), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryHeadingStaticText = wx.StaticText(self, wx.ID_ANY, "Heading", wx.Point(687, 268), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryHeadingTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(753, 265), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawnentry Respawn
		self.m_spawnEntryRespawnStaticText = wx.StaticText(self, wx.ID_ANY, "Respawn", wx.Point(307, 300), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryRespawnTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "600", wx.Point(379, 297), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawnentry Variance
		self.m_spawnEntryVarianceStaticText = wx.StaticText(self, wx.ID_ANY, "Variance", wx.Point(444, 300), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryVarianceTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(536, 297), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawnentry Pathgrid
		self.m_spawnEntryPathGridStaticText = wx.StaticText(self, wx.ID_ANY, "Path grid", wx.Point(578, 302), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryPathGridTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(645, 299), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawnentry Condition
		self.m_spawnEntryConditionStaticText = wx.StaticText(self, wx.ID_ANY, "Condition", wx.Point(306, 335), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryConditionTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(378, 332), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawnentry Condition Value
		self.m_spawnEntryConditionValueStaticText = wx.StaticText(self, wx.ID_ANY, "Condition Value", wx.Point(423, 335), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryConditionValueTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(536, 330), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawnentry Version
		self.m_spawnEntryVersionStaticText = wx.StaticText(self, wx.ID_ANY, "Version", wx.Point(583, 335), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryVersionTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(645, 332), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawnentry Enabled
		self.m_spawnEntryEnabledStaticText = wx.StaticText(self, wx.ID_ANY, "Enabled", wx.Point(313, 367), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryEnabledTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "1", wx.Point(378, 364), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawnentry Animation
		self.m_spawnEntryAnimationStaticText = wx.StaticText(self, wx.ID_ANY, "Animation", wx.Point(456, 367), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryAnimationTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "1", wx.Point(536, 362), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawnentry Zone
		self.m_spawnEntryZoneStaticText = wx.StaticText(self, wx.ID_ANY, "Zone", wx.Point(574, 367), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryZoneTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "", wx.Point(621, 364), wx.Size(168, 22), wx.TR_DEFAULT_STYLE)

		# Buttons
		self.m_AddSpawnButton = wx.Button(self, wx.ID_ANY, "Add",  wx.Point(511, 422), wx.DefaultSize, 0, wx.DefaultValidator)
		self.m_AddDeleteButton = wx.Button(self, wx.ID_ANY, "Delete", wx.Point(594, 422), wx.DefaultSize, 0,  wx.DefaultValidator)
		self.m_AddDeleteButton = wx.Button(self, wx.ID_ANY, "Save", wx.Point(717, 422), wx.DefaultSize, 0,  wx.DefaultValidator)

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


	def UpdateGUI(self,spawn):
		self.m_spawnGroupNameTextCtrl.SetValue(spawn.spawngroup_name)
		self.m_spawnEntryStaticText.SetLabel(spawn.spawnentry_npcname)
		self.m_spawnGroupMinXTextCtrl.SetValue(str(spawn.spawngroup_minx))
		self.m_spawnGroupMaxXTextCtrl.SetValue(str(spawn.spawngroup_maxx))
		self.m_spawnGroupMMinYTextCtrl.SetValue(str(spawn.spawngroup_miny))
		self.m_spawnGroupMaxYTextCtrl.SetValue(str(spawn.spawngroup_maxy))
		self.m_spawnGroupDistTextCtrl.SetValue(str(spawn.spawngroup_dist))
		self.m_spawnGroupMinDelayTextCtrl.SetValue(str(spawn.spawngroup_mindelay))
		self.m_spawnGroupDelayTextCtrl.SetValue(str(spawn.spawngroup_delay))
		self.m_spawnGroupDespawnTextCtrl.SetValue(str(spawn.spawngroup_despawn))
		self.m_spawnGroupDespawnTimerTextCtrl.SetValue(str(spawn.spawngroup_despawntimer))
		self.m_spawnGroupSpawnLimitTextCtrl.SetValue(str(spawn.spawngroup_spawnlimit))
		self.m_spawnGroupChanceTextCtrl.SetValue(str(spawn.spawngroup_chance))
		self.m_spawnEntryNpcIdTextCtrl.SetValue(str(spawn.spawnentry_npcid))
		self.m_spawnEntryXTextCtrl.SetValue(str(spawn.spawnentry_x))
		self.m_spawnEntryYTextCtrl.SetValue(str(spawn.spawnentry_y))
		self.m_spawnEntryZTextCtrl.SetValue(str(spawn.spawnentry_z))
		self.m_spawnEntryHeadingTextCtrl.SetValue(str(spawn.spawnentry_heading))
		self.m_spawnEntryRespawnTextCtrl.SetValue(str(spawn.spawnentry_respawn))
		self.m_spawnEntryVarianceTextCtrl.SetValue(str(spawn.spawnentry_variance))
		self.m_spawnEntryPathGridTextCtrl.SetValue(str(spawn.spawnentry_pathgrid))
		self.m_spawnEntryConditionTextCtrl.SetValue(str(spawn.spawnentry_condition))
		self.m_spawnEntryConditionValueTextCtrl.SetValue(str(spawn.spawnentry_condvalue))
		self.m_spawnEntryVersionTextCtrl.SetValue(str(spawn.spawnentry_version))
		self.m_spawnEntryEnabledTextCtrl.SetValue(str(spawn.spawnentry_enabled))
		self.m_spawnEntryAnimationTextCtrl.SetValue(str(spawn.spawnentry_animation))
		self.m_spawnEntryZoneTextCtrl.SetValue(str(spawn.spawnentry_zone))


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


