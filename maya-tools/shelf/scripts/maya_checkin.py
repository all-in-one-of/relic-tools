import maya.cmds as cmds
import utilities as amu #asset manager utilities
import os

def saveFile():
        if not cmds.file(q=True, sceneName=True) == '':
                cmds.file(save=True, force=True) #save file

def showFailDialog(): 
        return cmds.confirmDialog( title         = 'Checkin Failed'
                                 , message       = 'Checkin was unsuccessful'
                                 , button        = ['Ok']
                                 , defaultButton = 'Ok'
                                 , cancelButton  = 'Ok'
                                 , dismissString = 'Ok')

def showConfirmAlembicDialog():
        return cmds.confirmDialog( title         = 'Export Alembic'
                                 , message       = 'Export Alembic?'
                                 , button        = ['Yes', 'No']
                                 , defaultButton = 'Yes'
                                 , cancelButton  = 'No'
                                 , dismissString = 'No')

def getAssetName(filepath):
        return os.path.basename(filepath).split('.')[0]

def checkin():
        print 'checkin'
        saveFile() # save the file before doing anything
        print 'save'
        filePath = cmds.file(q=True, sceneName=True)
        print 'filePath: '+filePath
        toCheckin = os.path.join(amu.getUserCheckoutDir(), os.path.basename(os.path.dirname(filePath)))
        print 'toCheckin: '+toCheckin
        if amu.canCheckin(toCheckin):

                comment = 'Comment'
                commentPrompt = cmds.promptDialog(
                                    title='Comment',
                                    message='What changes did you make?',
                                    button=['OK','Cancel'],
                                    defaultButton='OK',
                                    dismissString='Cancel',
                                    sf = True)
                if commentPrompt == 'OK':
                    comment = cmds.promptDialog(query=True, text=True);
                else:
                    return
                amu.setComment(toCheckin, comment)
                dest = amu.getCheckinDest(toCheckin)

                saveFile()
                cmds.file(force=True, new=True) #open new file
                dest = amu.checkin(toCheckin) #checkin
        else:
                showFailDialog()

def go():
        try:
                checkin()
        except Exception as ex:
                msg = "RuntimeException:" + str(ex)
                print msg
                cmds.confirmDialog( title         = 'Uh Oh!'
                                  , message       = 'An exception just occured!\r\nHere is the message: ' + msg
                                  , button        = ['Dismiss']
                                  , defaultButton = 'Dismiss'
                                  , cancelButton  = 'Dismiss'
                                  , dismissString = 'Dismiss')
                

