# -*- coding: utf-8 -*-

import wx
import wx.xrc
import re
import globals
from components.database import Database
from panda3d.core import Point3
from config import Configurator
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
		self.m_spawnGroupMinYTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(552, 61), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
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
		self.m_spawnGroupDelayTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(552, 92), wx.Size(50, 22), wx.TR_DEFAULT_STYLE)
		# Spawngroup Despawn
		self.m_spawnGroupDespawnStaticText = wx.StaticText(self, wx.ID_ANY, "Despawn", wx.Point(603, 95), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupDespawnTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(679, 92), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawngroup Despawn Timer
		self.m_spawnGroupDespawnTimerStaticText = wx.StaticText(self, wx.ID_ANY, "Despawn Timer", wx.Point(300, 126), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupDespawnTimerTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "100", wx.Point(407, 126), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawngroup Spawn Limit
		self.m_spawnGroupSpawnLimitStaticText = wx.StaticText(self, wx.ID_ANY, "Spawn Limit", wx.Point(465, 129), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupSpawnLimitTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(552, 126), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawngroup Chance
		self.m_spawnGroupChanceStaticText = wx.StaticText(self, wx.ID_ANY, "Chance", wx.Point(613, 129), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnGroupChanceTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "100", wx.Point(679, 126), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)

		# Spawnentry
		self.m_spawnEntryStaticText = wx.StaticText(self, wx.ID_ANY, "Spawnentry", wx.Point(300, 245), wx.Size(168, 22), wx.TR_DEFAULT_STYLE)
		# Spawnentry Npc ID
		self.m_spawnEntryNpcIdStaticText = wx.StaticText(self, wx.ID_ANY, "NPC Id", wx.Point(320, 268), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryNpcIdTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(379, 265), wx.Size(75, 22), wx.TR_DEFAULT_STYLE)
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
		self.m_spawnEntryConditionValueTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "1", wx.Point(536, 330), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawnentry Version
		self.m_spawnEntryVersionStaticText = wx.StaticText(self, wx.ID_ANY, "Version", wx.Point(583, 335), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryVersionTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(645, 332), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawnentry Enabled
		self.m_spawnEntryEnabledStaticText = wx.StaticText(self, wx.ID_ANY, "Enabled", wx.Point(313, 367), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryEnabledTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "1", wx.Point(378, 364), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawnentry Animation
		self.m_spawnEntryAnimationStaticText = wx.StaticText(self, wx.ID_ANY, "Animation", wx.Point(456, 367), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryAnimationTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "0", wx.Point(536, 362), wx.Size(32, 22), wx.TR_DEFAULT_STYLE)
		# Spawnentry Zone
		self.m_spawnEntryZoneStaticText = wx.StaticText(self, wx.ID_ANY, "Zone", wx.Point(574, 367), wx.DefaultSize, wx.TR_DEFAULT_STYLE)
		self.m_spawnEntryZoneTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "", wx.Point(621, 364), wx.Size(168, 22), wx.TR_DEFAULT_STYLE)
		# Auto assign zone value
		self.m_spawnEntryZoneTextCtrl.SetLabel(globals.config['default_zone'])

		# Buttons
		self.m_ResetSpawnButton = wx.Button(self, wx.ID_ANY, "Reset", wx.Point(511, 422), wx.DefaultSize, 0, wx.DefaultValidator)
		self.m_AddDeleteButton = wx.Button(self, wx.ID_ANY, "Delete", wx.Point(594, 422), wx.DefaultSize, 0,  wx.DefaultValidator)
		self.m_AddSaveButton = wx.Button(self, wx.ID_ANY, "Save", wx.Point(717, 422), wx.DefaultSize, 0,  wx.DefaultValidator)
		self.m_AddSaveButton.Bind(wx.EVT_BUTTON, self.OnSave)
		self.m_AddDeleteButton.Bind(wx.EVT_BUTTON, self.OnDelete)
		self.m_ResetSpawnButton.Bind(wx.EVT_BUTTON, self.OnReset)
		treeViewSizer.Add( self.m_treeCtrlSpawnGroups, 0, wx.ALL, 5 )

		self.m_treeCtrlSpawnGroups.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnDoubleClickSpawn)
		self.m_treeCtrlSpawnGroups.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelectSpawn)
		
		self.SetSizer( treeViewSizer )
		self.Layout()
		
		self.Centre( wx.BOTH )


	### EVENTS

	def OnReset(self, event):
		# Spawngroup
		self.m_spawnGroupNameTextCtrl.SetValue("World_Forge_spawngroup_" + str(globals.database.GetNextSpawnGroupId()))
		# Spawngroup coords
		self.m_spawnGroupMinXTextCtrl.SetValue("0")
		self.m_spawnGroupMaxXTextCtrl.SetValue("0")
		self.m_spawnGroupMinYTextCtrl.SetValue("0")
		self.m_spawnGroupMaxYTextCtrl.SetValue("0")
		# Spawngroup Dist
		self.m_spawnGroupDistTextCtrl.SetValue("0")
		# Spawngroup Min Delay
		self.m_spawnGroupMinDelayTextCtrl.SetValue("15000")
		# Spawngroup Delay
		self.m_spawnGroupDelayTextCtrl.SetValue("0")
		# Spawngroup Despawn
		self.m_spawnGroupDespawnTextCtrl.SetValue("0")
		# Spawngroup Despawn Timer
		self.m_spawnGroupDespawnTimerTextCtrl.SetValue("100")
		# Spawngroup Spawn Limit
		self.m_spawnGroupSpawnLimitTextCtrl.SetValue("0")
		# Spawngroup Chance
		self.m_spawnGroupChanceTextCtrl.SetValue("100")
		# Spawnentry Npc ID
		self.m_spawnEntryNpcIdTextCtrl.SetValue("0")
		# Spawnentry Coords
		self.m_spawnEntryXTextCtrl.SetValue("0")
		self.m_spawnEntryYTextCtrl.SetValue("0")
		self.m_spawnEntryZTextCtrl.SetValue("0")
		self.m_spawnEntryHeadingTextCtrl.SetValue("0")
		# Spawnentry Respawn
		self.m_spawnEntryRespawnTextCtrl.SetValue("600")
		# Spawnentry Variance
		self.m_spawnEntryVarianceTextCtrl.SetValue("0")
		# Spawnentry Pathgrid
		self.m_spawnEntryPathGridTextCtrl.SetValue("0")
		# Spawnentry Condition
		self.m_spawnEntryConditionTextCtrl.SetValue("0")
		# Spawnentry Condition Value
		self.m_spawnEntryConditionValueTextCtrl.SetValue("1")
		# Spawnentry Version
		self.m_spawnEntryVersionTextCtrl.SetValue("0")
		# Spawnentry Enabled
		self.m_spawnEntryEnabledTextCtrl.SetValue("1")
		# Spawnentry Animation
		self.m_spawnEntryAnimationTextCtrl.SetValue("0")
		# Auto assign zone value
		self.m_spawnEntryZoneTextCtrl.SetLabel(globals.config['default_zone'])
		self.m_spawnEntryStaticText.SetLabel("Spawnentry")

	# TODO: FINISH THIS
	def OnDelete(self, event):
		if globals.selectedSpawn:
			#globals.database.DeleteSpawn(globals.selectedSpawn)
			globals.selectedSpawn.deletemodel()
			cookie = 0
			root = self.m_treeCtrlSpawnGroups.GetFirstChild(self.m_treeCtrlSpawnGroups.GetRootItem(), cookie)
			self.RecursiveDelete(root)
			#self.m_treeCtrlSpawnGroups.

	def RecursiveDelete(self, root):
		item, cookie = self.m_treeCtrlSpawnGroups.GetFirstChild(root, cookie)

		while item.IsOk():
			text = self.m_treeCtrlSpawnGroups.GetItemText(item)
			idpattern = "[" + str(globals.selectedSpawn.spawnentry_id) + "]"
			if idpattern in text:
				self.m_treeCtrlSpawnGroups.RemoveChild(item)
			if self.m_treeCtrlSpawnGroups.ItemHasChildren(item):
				sibling = self.RecursiveDelete(item)
				if sibling.isOk():
					self.m_treeCtrlSpawnGroups.RemoveChild(sibling)
			item = self.m_treeCtrlSpawnGroups.GetNextChild(root, cookie)
	#END TODO

	def OnSave(self, event):
		if globals.selectedSpawn is None:
			wx.MessageBox('No spawn selected!', 'Error', wx.OK | wx.ICON_ERROR)
			return
		if self.m_spawnGroupNameTextCtrl.GetLineLength(0) > 30:
			wx.MessageBox('Spawngroup Name cannot exceed 30 characters!', 'Error', wx.OK | wx.ICON_ERROR)
			return
		# Spawngroup
		globals.selectedSpawn.spawngroup_name = self.m_spawnGroupNameTextCtrl.Value
		# Spawngroup coords
		globals.selectedSpawn.spawngroup_minx = self.m_spawnGroupMinXTextCtrl.Value
		globals.selectedSpawn.spawngroup_maxx = self.m_spawnGroupMaxXTextCtrl.Value
		globals.selectedSpawn.spawngroup_miny = self.m_spawnGroupMinYTextCtrl.Value
		globals.selectedSpawn.spawngroup_maxy = self.m_spawnGroupMaxYTextCtrl.Value
		# Spawngroup Dist
		globals.selectedSpawn.spawngroup_dist = self.m_spawnGroupDistTextCtrl.Value
		# Spawngroup Min Delay
		globals.selectedSpawn.spawngroup_mindelay = self.m_spawnGroupMinDelayTextCtrl.Value
		# Spawngroup Delay
		globals.selectedSpawn.spawngroup_delay = self.m_spawnGroupDelayTextCtrl.Value
		# Spawngroup Despawn
		globals.selectedSpawn.spawngroup_despawn = self.m_spawnGroupDespawnTextCtrl.Value
		# Spawngroup Despawn Timer
		globals.selectedSpawn.spawngroup_despawntimer = self.m_spawnGroupDespawnTimerTextCtrl.Value
		# Spawngroup Spawn Limit
		globals.selectedSpawn.spawngroup_spawnlimit = self.m_spawnGroupSpawnLimitTextCtrl.Value
		# Spawnentry Chance
		globals.selectedSpawn.spawnentry_chance = self.m_spawnGroupChanceTextCtrl.Value
		# Spawnentry Npc ID
		globals.selectedSpawn.spawnentry_npcid = self.m_spawnEntryNpcIdTextCtrl.Value
		# Spawnentry Coords
		globals.selectedSpawn.spawnentry_x = self.m_spawnEntryXTextCtrl.Value
		globals.selectedSpawn.spawnentry_y = self.m_spawnEntryYTextCtrl.Value
		globals.selectedSpawn.spawnentry_z = self.m_spawnEntryZTextCtrl.Value
		globals.selectedSpawn.spawnentry_heading = self.m_spawnEntryHeadingTextCtrl.Value
		# Spawnentry Respawn
		globals.selectedSpawn.spawnentry_respawn = self.m_spawnEntryRespawnTextCtrl.Value
		# Spawnentry Variance
		globals.selectedSpawn.spawnentry_variance = self.m_spawnEntryVarianceTextCtrl.Value
		# Spawnentry Pathgrid
		globals.selectedSpawn.spawnentry_pathgrid = self.m_spawnEntryPathGridTextCtrl.Value
		# Spawnentry Condition
		globals.selectedSpawn.spawnentry_condition = self.m_spawnEntryConditionTextCtrl.Value
		# Spawnentry Condition Value
		globals.selectedSpawn.spawnentry_condvalue = self.m_spawnEntryConditionValueTextCtrl.Value
		# Spawnentry Version
		globals.selectedSpawn.spawnentry_version = self.m_spawnEntryVersionTextCtrl.Value
		# Spawnentry Enabled
		globals.selectedSpawn.spawnentry_enabled = self.m_spawnEntryEnabledTextCtrl.Value
		# Spawnentry Animation
		globals.selectedSpawn.spawnentry_animation = self.m_spawnEntryAnimationTextCtrl.Value
		# Auto assign zone value
		globals.selectedSpawn.spawnentry_zone = self.m_spawnEntryZoneTextCtrl.Value
		#self.m_spawnEntryStaticText.SetLabel("Spawnentry")

		globals.database.UpdateSpawn(globals.selectedSpawn)

	def initmenubar(self):
		menubar = wx.MenuBar()
		fileMenu = wx.Menu()
		fileItem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
		menubar.Append(fileMenu, '&File')
		self.SetMenuBar(menubar)

		self.Bind(wx.EVT_MENU, self.OnQuit, fileItem)

	def OnQuit(self,e):
		exit(0)

	def OnSelectSpawn(self, event):
		idpattern = "\[([^\)]+)\]"
		selectedText = self.m_treeCtrlSpawnGroups.GetItemText(event.GetItem())
		match = re.search(idpattern, selectedText)
		if match:
			id = match.group(1)
			spawn = globals.getspawnfromglobalspawnsbyname(id)
			#TYPE PROBLEM ? ID is int first then string? and it messes up the array search code??
			self.UpdateGUI(spawn)
			globals.selectedSpawn = spawn
			print "cbatte"

	# Double-click on a node
	def OnDoubleClickSpawn(self, event):
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
		self.m_spawnGroupMinYTextCtrl.SetValue(str(spawn.spawngroup_miny))
		self.m_spawnGroupMaxYTextCtrl.SetValue(str(spawn.spawngroup_maxy))
		self.m_spawnGroupDistTextCtrl.SetValue(str(spawn.spawngroup_dist))
		self.m_spawnGroupMinDelayTextCtrl.SetValue(str(spawn.spawngroup_mindelay))
		self.m_spawnGroupDelayTextCtrl.SetValue(str(spawn.spawngroup_delay))
		self.m_spawnGroupDespawnTextCtrl.SetValue(str(spawn.spawngroup_despawn))
		self.m_spawnGroupDespawnTimerTextCtrl.SetValue(str(spawn.spawngroup_despawntimer))
		self.m_spawnGroupSpawnLimitTextCtrl.SetValue(str(spawn.spawngroup_spawnlimit))
		self.m_spawnGroupChanceTextCtrl.SetValue(str(spawn.spawnentry_chance))
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

	def AddNewSpawnToTree(self, spawn):

		npcname = globals.database.GetNpcNameById(spawn.spawnentry_npcid)
		spawngroup = self.m_treeCtrlSpawnGroups.AppendItem(self.m_treeCtrlSpawnGroups.GetRootItem(), spawn.spawngroup_name)
		self.m_treeCtrlSpawnGroups.AppendItem(spawngroup, "[" + str(spawn.spawnentry_id) + "] " + npcname + "  (" + str(spawn.spawnentry_x) + ", " + str(spawn.spawnentry_y) + ", " + str(spawn.spawnentry_z) + ")")

