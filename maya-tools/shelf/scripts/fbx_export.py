from PyQt4.QtCore import *
from PyQt4.QtGui import *

import maya.cmds as cmds
import maya.OpenMayaUI as omu
from pymel.core import *
import utilities as amu #asset manager utilities
import os
import sip

WINDOW_WIDTH = 250
WINDOW_HEIGHT = 120

def maya_main_window():
	ptr = omu.MQtUtil.mainWindow()
	return sip.wrapinstance(long(ptr), QObject)		

class FbxExportDialog(QDialog):
	def __init__(self, parent=maya_main_window()):
		QDialog.__init__(self, parent)
		self.saveFile()
		self.setWindowTitle('Select Export Type')
		self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
		self.create_layout()
		self.create_connections()
	
	def create_layout(self):
		#Create Export Alembic and Cancel buttons
		self.static_button = QPushButton('Static Environment')
		self.dynamic_button = QPushButton('Dynamic Environment')
		self.monster_button = QPushButton('Monster')
		self.player_button = QPushButton('Player')
		self.cancel_button = QPushButton('Cancel')
		
		#Create button layout
		button_layout = QVBoxLayout()
		button_layout.setSpacing(2)
		button_layout.addStretch()
	
		button_layout.addWidget(self.static_button)
		button_layout.addWidget(self.dynamic_button)
		button_layout.addWidget(self.monster_button)
		button_layout.addWidget(self.player_button)
		button_layout.addWidget(self.cancel_button)
		
		#Create main layout
		main_layout = QVBoxLayout()
		main_layout.setSpacing(2)
		main_layout.setMargin(2)
		main_layout.addLayout(button_layout)
		
		self.setLayout(main_layout)
	
	def create_connections(self):
		#Connect the buttons
		self.connect(self.static_button, SIGNAL('clicked()'), self.export_static)
		self.connect(self.dynamic_button, SIGNAL('clicked()'), self.export_dynamic)
		self.connect(self.monster_button, SIGNAL('clicked()'), self.export_monster)
		self.connect(self.player_button, SIGNAL('clicked()'), self.export_player)
		self.connect(self.cancel_button, SIGNAL('clicked()'), self.close_dialog)
	
	
	########################################################################
	# SLOTS
	########################################################################
	def export_static(self):
		self.export_obj("Static", True)

	def export_dynamic(self):
		self.export_obj("Dynamic", True)

	def export_monster(self):
		self.export_obj("Monsters", False)

	def export_player(self):
		self.export_obj("Player", False)

	def export_obj(self, objType, isEnviron):
		self.saveFile()

		loadPlugin("fbxmaya")
		exportFilePath = self.build_export_filepath(objType, isEnviron)
		print exportFilePath
		command = self.build_export_command(exportFilePath)
		print command
		Mel.eval(command)
		
		self.close_dialog()
	
	def saveFile(self):
		if not cmds.file(q=True, sceneName=True) == '':
			cmds.file(save=True, force=True) #save file
	
	def build_export_filepath(self, exportType, isEnviron):
		#Get Repo Directory
		filePath = cmds.file(q=True, sceneName=True)
		if(isEnviron):
			destDir = os.path.join(amu.getRepoAssetDir(), 'Environment', exportType, 'Meshes')
		else:
			destDir = os.path.join(amu.getRepoAssetDir(), exportType, 'Meshes')

		#Get Asset Name
		assetName = os.path.basename(filePath).split('.')[0]
		print assetName
		
		return os.path.join(destDir, assetName+'.fbx')

	def build_export_command(self, exportFilePath):
		command = 'file -force -options "v=0;" -type "FBX export" -pr -ea "%s"'%(exportFilePath)
		return command
	
	def close_dialog(self):
		self.close()

def go():
	dialog = FbxExportDialog()
	dialog.show()
	
if __name__ == '__main__':
	go()
