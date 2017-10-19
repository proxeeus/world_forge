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

class SpawnsFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Spawns", pos = wx.DefaultPosition, size = wx.Size( 500,380 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		
		self.m_menubar = wx.MenuBar( 0 )
		self.m_fileMenu = wx.Menu()
		self.m_menuItemQuit = wx.MenuItem( self.m_fileMenu, wx.ID_ANY, u"Quit", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_fileMenu.Append( self.m_menuItemQuit )
		
		self.m_menubar.Append( self.m_fileMenu, u"File" ) 
		
		self.SetMenuBar( self.m_menubar )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_treeCtrlSpawnGroups = wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 15000,10000 ), wx.TR_DEFAULT_STYLE )
		bSizer1.Add( self.m_treeCtrlSpawnGroups, 0, wx.ALL, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

