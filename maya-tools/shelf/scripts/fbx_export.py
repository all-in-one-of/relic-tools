from PyQt4.QtCore import *
from PyQt4.QtGui import *

import maya.cmds as cmds
import maya.OpenMayaUI as omu
from pymel.core import *
import utilities as amu #asset manager utilities
import os
import sip

WINDOW_WIDTH = 250
WINDOW_HEIGHT = 50

def maya_main_window():
	ptr = omu.MQtUtil.mainWindow()
	return sip.wrapinstance(long(ptr), QObject)		

class FbxExportDialog(QDialog):
	def __init__(self, parent=maya_main_window()):
	#def setup(self, parent):
		QDialog.__init__(self, parent)
		self.saveFile()
		self.setWindowTitle('Select Export Type')
		self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
		self.create_layout()
		self.create_connections()
		#self.create_export_list()
	
	def create_layout(self):
		#Create the selected item list
		# self.selection_list = QListWidget()
		# self.selection_list.setSelectionMode(QAbstractItemView.ExtendedSelection);
		# self.selection_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

		#Create Export Alembic and Cancel buttons
		self.static_button = QPushButton('Static Object')
		self.dynamic_button = QPushButton('Dynamic Object')
		self.cancel_button = QPushButton('Cancel')
		
		#Create button layout
		button_layout = QHBoxLayout()
		button_layout.setSpacing(2)
		button_layout.addStretch()
	
		button_layout.addWidget(self.static_button)
		button_layout.addWidget(self.dynamic_button)
		button_layout.addWidget(self.cancel_button)
		
		#Create main layout
		main_layout = QVBoxLayout()
		main_layout.setSpacing(2)
		main_layout.setMargin(2)
		#main_layout.addWidget(self.selection_list)
		main_layout.addLayout(button_layout)
		
		self.setLayout(main_layout)
	
	def create_connections(self):
		#Connect the buttons
		self.connect(self.static_button, SIGNAL('clicked()'), self.export_static)
		self.connect(self.dynamic_button, SIGNAL('clicked()'), self.export_dynamic)
		self.connect(self.cancel_button, SIGNAL('clicked()'), self.close_dialog)
	
	# def create_export_list(self):
	# 	#Remove all items from the list before repopulating
	# 	self.selection_list.clear()
		
	# 	#Add the list to select from
	# 	loadedRef = self.getLoadedReferences()
		
	# 	for ref in loadedRef:
	# 		item = QListWidgetItem(ref) 
	# 		item.setText(ref)
	# 		self.selection_list.addItem(item)
		
	# 	self.selection_list.sortItems(0)
	
	# def getLoadedReferences(self):
	# 	references = cmds.ls(references=True)
	# 	loaded=[]
	# 	print "Loaded References: "
	# 	for ref in references:
	# 		print "Checking status of " + ref
	# 		try:
	# 			if cmds.referenceQuery(ref, isLoaded=True):
	# 				loaded.append(ref)
	# 		except:
	# 			print "Warning: " + ref + " was not associated with a reference file"
	# 	return loaded
	
	
	########################################################################
	# SLOTS
	########################################################################
	def export_static(self):
		self.saveFile()
		
		# selectedReferences = []
		# selectedItems = self.selection_list.selectedItems()
		# for item in selectedItems:
		# 	selectedReferences.append(item.text())
		
		# if self.showConfirmAlembicDialog(selectedReferences) == 'Yes':
		# 	loadPlugin("AbcExport")
		# 	for ref in selectedReferences:
		# 		abcFilePath = self.build_alembic_filepath(ref)
		# 		print abcFilePath
		# 		command = self.build_alembic_command(ref, abcFilePath)
		# 		print command
		# 		Mel.eval(command)

		exportFilePath = self.build_export_filepath("Static")
		print exportFilePath
		command = self.build_export_command(exportFilePath)
		print command
		Mel.eval(command)

		self.close_dialog()

	def export_dynamic(self):
		self.saveFile()
		
		# selectedReferences = []
		# selectedItems = self.selection_list.selectedItems()
		# for item in selectedItems:
		# 	selectedReferences.append(item.text())
		
		# if self.showConfirmAlembicDialog(selectedReferences) == 'Yes':
		# 	loadPlugin("AbcExport")
		# 	for ref in selectedReferences:
		# 		abcFilePath = self.build_alembic_filepath(ref)
		# 		print abcFilePath
		# 		command = self.build_alembic_command(ref, abcFilePath)
		# 		print command
		# 		Mel.eval(command)

		exportFilePath = self.build_export_filepath("Dynamic")
		print exportFilePath
		command = self.build_export_command(exportFilePath)
		print command
		Mel.eval(command)
		
		self.close_dialog()
	
	def saveFile(self):
		if not cmds.file(q=True, sceneName=True) == '':
			cmds.file(save=True, force=True) #save file
	
	# def showConfirmAlembicDialog(self, references):
	# 	return cmds.confirmDialog( title         = 'Export Alembic'
	# 	                         , message       = 'Export Alembic for:\n' + str(references)
	# 	                         , button        = ['Yes', 'No']
	# 	                         , defaultButton = 'Yes'
	# 	                         , cancelButton  = 'No'
	# 	                         , dismissString = 'No')
	
	def build_export_filepath(self, exportType):
		#Get Repo Directory
		filePath = cmds.file(q=True, sceneName=True)
		destDir = os.path.join(amu.getRepoAssetDir(), 'Environment', exportType, 'Meshes')

		#Get Asset Name
		assetName = os.path.basename(filePath).split('.')[0]
		print assetName
		
		return os.path.join(destDir, assetName+'.fbx')

	def build_export_command(self, exportFilePath):
		# tagged = self.get_tagged_node(ref)

		# if tagged == "":
		# 	return ""

		# depList = self.get_dependancies(ref)

		# roots_string = ""
		# roots_string = " ".join([roots_string, "-root %s"%(tagged.name())])

		# for dep in depList:
		# 	depRef = ls(dep)
		# 	if len(depRef) > 0:
		# 		tagged = self.get_tagged_node(depRef[0]).name()
		# 	else:
		# 		tagged = dep[:-2]

		# 	roots_string = " ".join([roots_string, "-root %s"%(tagged)])

		# start_frame = cmds.playbackOptions(q=1, animationStartTime=True) - 5
		# end_frame = cmds.playbackOptions(q=1, animationEndTime=True) + 5
		command = 'file -force -options "v=0;" -type "FBX export" -pr -ea "%s"'%(exportFilePath)
		#command = 'AbcExport -j "%s -frameRange %s %s -step 0.25 -writeVisibility -nn -uv -file %s"'%(roots_string, str(start_frame), str(end_frame), abcfilepath)
		return command

	# def get_tagged_node(self, ref):
	# 	refNodes = cmds.referenceQuery(unicode(ref), nodes=True)
	# 	rootNode = ls(refNodes[0])
	# 	if rootNode[0].hasAttr("BYU_Alembic_Export_Flag"):
	# 		taggedNode = rootNode[0]
	# 	else:
	# 		taggedNode = self.get_tagged_children(rootNode[0])

	# 	if taggedNode == "":
	# 		self.showNoTagFoundDialog(unicode(ref))
	# 		return ""

	# 	print taggedNode
	# 	return taggedNode

	# def get_tagged_children(self, node):
	# 	for child in node.listRelatives(c=True):
	# 		if child.hasAttr("BYU_Alembic_Export_Flag"):
	# 			return child
	# 		else:
	# 			taggedChild = self.get_tagged_children(child)
	# 			if taggedChild != "":
	# 				return taggedChild
	# 	return ""

	# def get_dependancies(self, ref):
	# 	refNodes = cmds.referenceQuery(unicode(ref), nodes=True)
	# 	rootNode = ls(refNodes[0])
	# 	depList = self.get_dependant_children(rootNode[0])

	# 	return depList

	# def get_dependant_children(self, node):
	# 	depList = []
	# 	for const in node.listRelatives(ad=True, type="parentConstraint"):
	# 		par = const.listRelatives(p=True)
	# 		constNS = par[0].split(':')[0]
	# 		print const
	# 		targetList = cmds.parentConstraint(unicode(const), q=True, tl=True)
	# 		targetNS = targetList[0].split(':')[0]
	# 		if constNS != targetNS and targetNS not in depList:
	# 			depList.append(targetNS + 'RN')

	# 	print depList
	# 	return depList

	# def showNoTagFoundDialog(self, ref):
	# 	return cmds.confirmDialog( title         = 'No Alembic Tag Found'
	# 	                         , message       = 'Unable to locate Alembic Export tag for ' + ref + '.'
	# 	                         , button        = ['OK']
	# 	                         , defaultButton = 'OK'
	# 	                         , cancelButton  = 'OK'
	# 	                         , dismissString = 'OK')
	
	def close_dialog(self):
		self.close()

def go():
	dialog = FbxExportDialog()
	dialog.show()
	
if __name__ == '__main__':
	go()
