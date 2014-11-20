from PyQt4.QtCore import *
from PyQt4.QtGui import *

import maya.cmds as cmd
import maya.OpenMayaUI as omu
import sip
import os, glob, shutil
import utilities as amu

CHECKOUT_WINDOW_WIDTH = 300
CHECKOUT_WINDOW_HEIGHT = 400

def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QObject)

class RollbackDialog(QDialog):
    ORIGINAL_FILE_NAME = cmd.file(query=True, sceneName=True)
    def __init__(self, parent=maya_main_window()):
    #def setup(self, parent):
        self.ORIGINAL_FILE_NAME = cmd.file(query=True, sceneName=True)
        QDialog.__init__(self, parent)
        self.setWindowTitle('Rollback')
        self.setFixedSize(CHECKOUT_WINDOW_WIDTH, CHECKOUT_WINDOW_HEIGHT)
        self.create_layout()
        self.create_connections()
        self.refresh()
  
    def create_layout(self):
        #Create the selected item list
        self.selection_list = QListWidget()
        self.selection_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding) 

        #Create Tag, Select, and Cancel buttons
        self.help_button = QPushButton('Help')
        # self.tag_button = QPushButton('Tag')
        self.checkout_button = QPushButton('Checkout')
        self.cancel_button = QPushButton('Cancel')
	
        #Create Label to hold asset info
        self.version_info_label = QLabel("test")
        self.version_info_label.setWordWrap(True)

        #Create button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(2)
        button_layout.addStretch()
        # button_layout.addWidget(self.tag_button)
        button_layout.addWidget(self.checkout_button)
        button_layout.addWidget(self.cancel_button)

        #Create main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(2)
        main_layout.setMargin(2)
        main_layout.addWidget(self.selection_list)
        main_layout.addWidget(self.version_info_label)
        main_layout.addWidget(self.help_button)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)

    def create_connections(self):
        #Connect the selected item list widget
        self.connect(self.selection_list,
                    SIGNAL('currentItemChanged(QListWidgetItem*, QListWidgetItem*)'),
                    self.set_current_item)
            
        #Connect the buttons
        self.connect(self.help_button, SIGNAL('clicked()'), self.help_dialog)
        #self.connect(self.tag_button, SIGNAL('clicked()'), self.rename_tagged_version)
        self.connect(self.checkout_button, SIGNAL('clicked()'), self.checkout_version)
        self.connect(self.cancel_button, SIGNAL('clicked()'), self.close_dialog)
	
    def update_selection(self, selection):
        #Remove all items from the list before repopulating
        self.selection_list.clear()
        self.version_info_label.clear()

        #Add the list to select from
        for s in selection:
            item = QListWidgetItem(os.path.basename(s)) 
            item.setText(os.path.basename(s))
            self.selection_list.addItem(item)
        self.selection_list.sortItems(0)

    def refresh(self):
        filePath = os.path.join(amu.getUserCheckoutDir(), os.path.basename(os.path.dirname(self.ORIGINAL_FILE_NAME)))
        checkInDest = amu.getCheckinDest(filePath)
        versionFolders = os.path.join(checkInDest, "src")
        selections = glob.glob(os.path.join(versionFolders, '*'))
        self.update_selection(selections)

    def get_checkout_mode(self):
        return ''

    def get_filename(self, parentdir):
        return os.path.basename(os.path.dirname(parentdir))+'_'+os.path.basename(parentdir)

    ########################################################################
    # SLOTS
    ########################################################################
    def close_dialog(self):
        print self.ORIGINAL_FILE_NAME
        # cmd.file(self.ORIGINAL_FILE_NAME, force=True, open=True)
        self.close()

    def set_current_item(self, item):
        self.current_item = item
        self.show_version_info()

    def show_no_file_dialog(self):
        return cmd.confirmDialog(  title           = 'No Such Version'
                                   , message       = 'For some reason this version folder does not contain a file. Please try another version.'
                                   , button        = ['Ok']
                                   , defaultButton = 'Ok'
                                   , cancelButton  = 'Ok'
                                   , dismissString = 'Ok')

    def verify_checkout_dialog(self):
        return cmd.confirmDialog(  title           = 'Verify Checkout'
                                   , message       = 'You are about to checkout an older version of this asset. If you have made changes to your currently checked out file, they will be lost.  Is this OK?'
                                   , button        = ['Yes', 'No']
                                   , defaultButton = 'No'
                                   , cancelButton  = 'No'
                                   , dismissString = 'No')

    def help_dialog(self):
        return cmd.confirmDialog(  title           = 'Help'
                                   , message       = 'CHECKOUT: Checks out the selected version so you can modify it. when you check it in, it will be saved as the newest version.\n If you have made changes to your currently checked out file, you should check those in first'
                                   , button        = ['Ok']
                                   , defaultButton = 'Ok'
                                   , cancelButton  = 'Ok'
                                   , dismissString = 'Ok')

    def checkout_version(self):
        dialogResult = self.verify_checkout_dialog()
        if(dialogResult == 'Yes'):
            #checkout
            version = str(self.current_item.text())[1:]
            filePath = os.path.join(amu.getUserCheckoutDir(), os.path.basename(os.path.dirname(self.ORIGINAL_FILE_NAME)))
            toCheckout = amu.getCheckinDest(filePath)
            
            latestVersion = amu.tempSetVersion(toCheckout, version)
            amu.discard(filePath)
            try:
                destpath = amu.checkout(toCheckout, True)
            except Exception as e:
                if not amu.checkedOutByMe(toCheckout):
                    cmd.confirmDialog(  title          = 'Can Not Checkout'
                                   , message       = str(e)
                                   , button        = ['Ok']
                                   , defaultButton = 'Ok'
                                   , cancelButton  = 'Ok'
                                   , dismissString = 'Ok')
                    return
                else:
                    destpath = amu.getCheckoutDest(toCheckout)

            amu.tempSetVersion(toCheckout, latestVersion)
            # move to correct checkout directory
            correctCheckoutDir = amu.getCheckoutDest(toCheckout)
            if not destpath==correctCheckoutDir:
                if os.path.exists(correctCheckoutDir):
                    shutil.rmtree(correctCheckoutDir)
                os.rename(destpath, correctCheckoutDir)
            toOpen = os.path.join(correctCheckoutDir, self.get_filename(toCheckout)+'.mb')
            self.ORIGINAL_FILE_NAME = toOpen
            if not os.path.exists(toOpen):
                # create new file
                cmd.file(force=True, new=True)
                cmd.file(rename=toOpen)
                cmd.file(save=True, force=True)
            cmd.file(self.ORIGINAL_FILE_NAME, force=True, open=True)
            self.close_dialog()

    def show_version_info(self):
        asset_version = str(self.current_item.text())
        filePath = os.path.join(amu.getUserCheckoutDir(), os.path.basename(os.path.dirname(self.ORIGINAL_FILE_NAME)))
        checkInDest = amu.getCheckinDest(filePath)
        comment = amu.getVersionComment(checkInDest,asset_version)
        self.version_info_label.setText(comment)
            
def go():
    currentFile = cmd.file(query=True, sceneName=True)
    filePath = os.path.join(amu.getUserCheckoutDir(), os.path.basename(os.path.dirname(currentFile)))
    if(amu.isCheckedOutCopyFolder(filePath)):
        cmd.file(save=True, force=True)
        dialog = RollbackDialog()
        dialog.show()
    else:
        cmd.confirmDialog(  title         = 'Invalid Command'
                           , message       = 'This is not a checked out file. There is nothing to rollback.'
                           , button        = ['Ok']
                           , defaultButton = 'Ok'
                           , cancelButton  = 'Ok'
                           , dismissString = 'Ok')
    
if __name__ == '__main__':
    go()
    
