"""
This module contains functionality to manage the animation project.
@author: Morgan Strong, Brian Kingery
"""

import os, time, shutil, glob, pwd, tempfile, smtplib, re
from ConfigParser import ConfigParser

def getProjectName():
	return os.environ['PROJECT_NAME']
def getProductionDir():
	return os.environ['PRODUCTION_DIR']
def getUsername():
	return os.environ['USER']
def getUserCheckoutDir():
	return os.path.join(os.environ['USER_DIR'], 'checkout')
def getRepoAssetDir():
	return os.path.join(os.environ['REPO_DIR'], 'Assets')

def getHoudiniPython():
	"""precondition: HFS environment variable is set correctly"""
	return "/opt/hfs.current/python/bin/python"
	#return os.path.join(os.environ['HFS'], "python", "bin", "python")

def getMayapy():
	"""precondition: MAYA_LOCATION environment variable is set correctly"""
	return os.path.join(os.environ['MAYA_LOCATION'], "bin", "mayapy")

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Folder Management

def _writeConfigFile(filePath, configParser):
       """
       Will update the config file specified by filePath with the contents of configParser
       @precondition: filePath is a valid path
       @precondition: confgParser is an instance of ConfigParser()
       """
       configFile = open(filePath, 'wb')
       configParser.write(configFile)


def createNodeInfoFile(dirPath, toKeep):
	"""
	Creates the .nodeInfo file in the directory specified by dirPath.
	The Node:Type must be set by concrete nodes
	@precondition: dirPath is a valid directory
	@postcondition: All sections/tags are created and set except "Type".
		"Type" must be set by concrete nodes.
	"""
	username = getUsername()
	timestamp = time.strftime("%a, %d %b %Y %I:%M:%S %p", time.localtime())
	
	nodeInfo = ConfigParser()
	nodeInfo.add_section('Node')
	nodeInfo.set('Node', 'Type', '')
	
	nodeInfo.add_section('Versioning')
	nodeInfo.set('Versioning', 'LatestVersion', '0')
	nodeInfo.set('Versioning', 'VersionsToKeep', str(toKeep))
	nodeInfo.set('Versioning', 'Locked', 'False')
	nodeInfo.set('Versioning', 'LastCheckoutTime', timestamp)
	nodeInfo.set('Versioning', 'LastCheckoutUser', username)
	nodeInfo.set('Versioning', 'LastCheckinTime', timestamp)
	nodeInfo.set('Versioning', 'LastCheckinUser', username)
	nodeInfo.add_section('Comments')
	nodeInfo.set('Comments', 'v000', 'New')

	_writeConfigFile(os.path.join(dirPath, ".nodeInfo"), nodeInfo)
	
def addVersionedFolder(parent, name, toKeep):
	new_dir = os.path.join(parent, name)
	os.makedirs(os.path.join(new_dir, "src", "v000"))
	os.makedirs(os.path.join(new_dir, "stable"))
	os.makedirs(os.path.join(new_dir, 'stable', 'backups'))

	createNodeInfoFile(new_dir, toKeep)
	return new_dir

def addProjectFolder(parent, name):
	newPath = os.path.join(parent, name)
	os.makedirs(newPath)
	return newPath

def createNewAssetFolders(parent, name):
	new_dir = os.path.join(parent, name)
	addProjectFolder(parent, name)
	addVersionedFolder(new_dir, 'model', 5)
	return new_dir

def isVersionedFolder(dirPath):
	if os.path.exists(os.path.join(dirPath, ".nodeInfo")):
		return True
	else:
		return False

def isCheckedOutCopyFolder(dirPath):
	if os.path.exists(os.path.join(dirPath, ".checkoutInfo")):
		return True
	else:
		return False

def isInstalled(dirPath):
	return bool(glob.glob(os.path.join(dirPath, 'stable', '*stable*')))

def getVersionedFolderInfo(dirPath):
	"""
	returns a list containing the following information about the asset in dirPath:
	[0] last person to check it out, if locked
	[1] last person to check it in
	[2] time it was last checked in
	[3] latest comment on checkin
	[4] if it is isInstalled
	[5] filepath to install directory
	"""
	if not isVersionedFolder(dirPath):
		raise Exception("Not a versioned folder")
	
	nodeInfo = []
	cp = ConfigParser()
	cp.read(os.path.join(dirPath, ".nodeInfo"))
	if cp.getboolean("Versioning", "locked"):
		nodeInfo.append(cp.get("Versioning", "lastcheckoutuser"))
	else:
		nodeInfo.append("")
	nodeInfo.append(cp.get("Versioning", "lastcheckinuser"))
	nodeInfo.append(cp.get("Versioning", "lastcheckintime"))
	versionNum = int(cp.get("Versioning", "latestversion"))
	latestVersion = "v"+("%03d" % versionNum) 
	if cp.has_section("Comments"):
		nodeInfo.append(cp.get("Comments", latestVersion))
	else:
		nodeInfo.append('')
	if isInstalled(dirPath):
		nodeInfo.append("Yes")
		nodeInfo.append(glob.glob(os.path.join(dirPath, 'stable', '*stable*'))[0])
	else:
		nodeInfo.append("No")
		nodeInfo.append("")
	return nodeInfo

def getLatestVersion(dirPath):
	if not isVersionedFolder(dirPath):
		raise Exception("Not a versioned folder")
	cp = ConfigParser()
	cp.read(os.path.join(dirPath, ".nodeInfo"))
	return int(cp.get("Versioning", "latestversion"))

def getVersionComment(dirPath, version):
	if not isVersionedFolder(dirPath):
		raise Exception("Not a versioned folder")
	
	nodeInfo = []
	cp = ConfigParser()
	cp.read(os.path.join(dirPath, ".nodeInfo")) 
	return cp.get("Comments",version)

def tempSetVersion(chkInDest, version):
    """
    Temporarily sets the 'latest version' as the specified version without deleting later versions
    Returns the version number that we override
    @precondition 'chkInDest' is a valid versioned folder
    """
    nodeInfo = ConfigParser()
    nodeInfo.read(os.path.join(chkInDest, ".nodeInfo"))
    latestVersion = nodeInfo.get("Versioning", "latestversion")
    nodeInfo.set("Versioning", "latestversion", str(version))
    _writeConfigFile(os.path.join(chkInDest, ".nodeInfo"), nodeInfo)
    return latestVersion

def setVersion(dirPath, version):	
    """
    Sets the 'latest version' as the specified version and deletes later versions
    @precondition: dirPath is a valid path
    @precondition: version is an existing version
    @precondition: the folder has been checked out by the user

    @postcondition: the folder will be checked in and unlocked
    """

    chkoutInfo = ConfigParser()
    chkoutInfo.read(os.path.join(dirPath, ".checkoutInfo"))
    chkInDest = chkoutInfo.get("Checkout", "checkedoutfrom")
    lockedbyme = chkoutInfo.getboolean("Checkout", "lockedbyme")
    
    nodeInfo = ConfigParser()
    nodeInfo.read(os.path.join(chkInDest, ".nodeInfo"))
    newVersionPath = os.path.join(chkInDest, "src", "v"+("%03d" % version))

    if lockedbyme == False:
        print "Cannot overwrite locked folder."
        raise Exception("Can not overwrite locked folder.")
        
    # Set version
    timestamp = time.strftime("%a, %d %b %Y %I:%M:%S %p", time.localtime())
    nodeInfo.set("Versioning", "lastcheckintime", timestamp)
    nodeInfo.set("Versioning", "lastcheckinuser", getUsername())
    nodeInfo.set("Versioning", "latestversion", str(version))
    nodeInfo.set("Versioning", "locked", "False")
    _writeConfigFile(os.path.join(chkInDest, ".nodeInfo"), nodeInfo)
    
    # Clean up
    purgeAfter(os.path.join(chkInDest, "src"), version)
    shutil.rmtree(dirPath)
    #os.remove(os.path.join(newVersionPath, ".checkoutInfo"))

#################################################################################
# Checkout
#################################################################################
def _createCheckoutInfoFile(dirPath, coPath, version, timestamp, lock):
	"""
	Creates a .checkoutInfo file in the directory specified by dirPath
	@precondition: dirPath is a valid path
	@postcondition: dirPath/.checkoutInfo contains complete [Checkout] section
	"""
	chkoutInfo = ConfigParser()
	chkoutInfo.add_section("Checkout")
	chkoutInfo.set("Checkout", "checkedoutfrom", coPath)
	chkoutInfo.set("Checkout", "checkouttime", timestamp)
	chkoutInfo.set("Checkout", "version", version)
	chkoutInfo.set("Checkout", "lockedbyme", str(lock))
	
	_writeConfigFile(os.path.join(dirPath, ".checkoutInfo"), chkoutInfo)

def isCheckedOut(dirPath):
	nodeInfo = os.path.join(dirPath, ".nodeInfo")
	if not os.path.exists(nodeInfo):
		return False
	cp = ConfigParser()
	cp.read(nodeInfo)
	return cp.getboolean("Versioning", "locked")

def checkedOutByMe(dirPath):
	nodeInfo = os.path.join(dirPath, ".nodeInfo")
	if not os.path.exists(nodeInfo):
		return False
	cp = ConfigParser()
	cp.read(nodeInfo)
	return cp.get("Versioning", "lastcheckoutuser") == getUsername()

def getFilesCheckoutTime(filePath):
	checkoutInfo = os.path.join(filePath, ".checkoutInfo")
	#print checkoutInfo
	if not os.path.exists(checkoutInfo):
		raise Exception("No checkout info available")
	cp = ConfigParser()
	cp.read(checkoutInfo)
	return cp.get("Checkout", "checkouttime")

def canCheckout(coPath):
	result = True
	if not os.path.exists(os.path.join(coPath, ".nodeInfo")):
		result = False
	nodeInfo = ConfigParser()
	nodeInfo.read(os.path.join(coPath, ".nodeInfo"))
	if nodeInfo.get("Versioning", "locked") == "True":
		result = False
	return result

def getCheckoutDest(coPath):
	nodeInfo = ConfigParser()
	nodeInfo.read(os.path.join(coPath, ".nodeInfo"))
	version = nodeInfo.get("Versioning", "latestversion")
	return os.path.join(getUserCheckoutDir(), os.path.basename(os.path.dirname(coPath))+"_"+os.path.basename(coPath)+"_"+("%03d" % int(version)))

def lockedBy(logname):
    """
    Returns a tuple containing the logname and the real name

    Raises a generic exception if real name cannot be determined.
    """

    try: # Throws KeyError exception when the name cannot be found
        p = pwd.getpwnam( str(logname) )
    except KeyError as ke: # Re-throws KeyError as generic exception
        raise Exception( str(ke) )

    return p.pw_name, p.pw_gecos # Return lockedBy tuple

def checkout(coPath, lock):
	"""
	Copies the 'latest version' from the src folder into the local directory
	@precondition: coPath is a path to a versioned folder
	@precondition: lock is a boolean value
	
	@postcondition: A copy of the 'latest version' will be placed in the local directory
		with the name of the versioned folder
	@postdondition: If lock == True coPath will be locked until it is released by checkin
	"""
	#if not os.path.exists(os.path.join(coPath, ".nodeInfo")):
	if not isVersionedFolder(coPath):
		raise Exception("Not a versioned folder.")
	
	nodeInfo = ConfigParser()
	nodeInfo.read(os.path.join(coPath, ".nodeInfo"))
	if nodeInfo.get("Versioning", "locked") == "False":
		version = nodeInfo.getint("Versioning", "latestversion")
		toCopy = os.path.join(coPath, "src", "v"+("%03d" % version))
		dest = getCheckoutDest(coPath)
		
		if(os.path.exists(toCopy)):
			try:
				shutil.copytree(toCopy, dest) # Make the copy
			except Exception:
				print "asset_mgr_utils, checkout: Could not copy files."
				raise Exception("Could not copy files.")
			timestamp = time.strftime("%a, %d %b %Y %I:%M:%S %p", time.localtime())
			nodeInfo.set("Versioning", "lastcheckoutuser", getUsername())
			nodeInfo.set("Versioning", "lastcheckouttime", timestamp)
			nodeInfo.set("Versioning", "locked", str(lock))
			
			_writeConfigFile(os.path.join(coPath, ".nodeInfo"), nodeInfo)
			_createCheckoutInfoFile(dest, coPath, version, timestamp, lock)
		else:
			raise Exception("Version doesn't exist "+toCopy)
	else:
		whoLocked = nodeInfo.get("Versioning", "lastcheckoutuser")
		whenLocked = nodeInfo.get("Versioning", "lastcheckouttime")
		logname, realname = lockedBy(whoLocked)
		whoLocked = 'User Name: ' + logname + '\nReal Name: ' + realname + '\n'
		raise Exception("Can not checkout. Folder is locked by:\n\n"+ whoLocked+"\nat "+ whenLocked)
	return dest

def unlock(ulPath):
	
	nodeInfo = ConfigParser()
	nodeInfo.read(os.path.join(ulPath, ".nodeInfo"))
	nodeInfo.set("Versioning", "locked", "False")

	toCopy = getCheckoutDest(ulPath)
	dirname = os.path.basename(toCopy) 
	parentPath = os.path.join(os.path.dirname(toCopy), ".unlocked")
	if not (os.path.exists(parentPath)):
		os.mkdir(parentPath)

	os.system('mv -f '+toCopy+' '+parentPath+'/')
	_writeConfigFile(os.path.join(ulPath, ".nodeInfo"), nodeInfo)
	return 0;

def isLocked(ulPath):
	nodeInfo = ConfigParser()
	nodeInfo.read(os.path.join(ulPath, ".nodeInfo"))
	if nodeInfo.get("Versioning", "locked") == "False":
		return False;
	
	return True;

################################################################################
# Checkin
################################################################################
def canCheckin(toCheckin):
	"""
	@returns: True if destination is not locked by another user
		AND this checkin will not overwrite a newer version
	"""
	chkoutInfo = ConfigParser()
	chkoutInfo.read(os.path.join(toCheckin, ".checkoutInfo"))
	chkInDest = chkoutInfo.get("Checkout", "checkedoutfrom")
	version = chkoutInfo.getint("Checkout", "version")
	lockedbyme = chkoutInfo.getboolean("Checkout", "lockedbyme")
	
	nodeInfo = ConfigParser()
	nodeInfo.read(os.path.join(chkInDest, ".nodeInfo"))
	locked = nodeInfo.getboolean("Versioning", "locked")
	latestVersion = nodeInfo.getint("Versioning", "latestversion")
	
	result = True
	if lockedbyme == False:
		if locked == True:
			result = False
		if version < latestVersion:
			result = False
	
	return result

def setComment(toCheckin, comment):
	chkoutInfo = ConfigParser()
	chkoutInfo.read(os.path.join(toCheckin, ".checkoutInfo"))
	chkInDest = chkoutInfo.get("Checkout", "checkedoutfrom")

	nodeInfo = ConfigParser()
	nodeInfo.read(os.path.join(chkInDest, ".nodeInfo"))
	newVersion = nodeInfo.getint("Versioning", "latestversion") + 1
	timestamp = time.strftime("%a, %d %b %Y %I:%M:%S %p", time.localtime())
	commentLine = getUsername() + ': ' + timestamp + ': ' + '"' + comment + '"' 
	nodeInfo.set("Comments", 'v' + "%03d" % (newVersion,), commentLine)	
	_writeConfigFile(os.path.join(chkInDest, ".nodeInfo"), nodeInfo)

def purge(dirPath, nodeInfo, upto):
	"""
	purges all folders in dirPath with a version less than upto
	"""
	files = glob.glob(os.path.join(dirPath, '*'))
	for f in files:
		version = int(os.path.basename(f).split('v')[1])
		if version < upto:
			shutil.rmtree(f)
			nodeInfo.remove_option("Comments", 'v' + "%03d" % (version,))

def purgeAfter(dirPath, after):
    """
    purges all folders in dirPath with a version higher than after
    """
    files = glob.glob(os.path.join(dirPath, '*'))
    for f in files:
        if int(os.path.basename(f).split('v')[1]) > after:
            shutil.rmtree(f)

def discard(toDiscard):
	"""
	Discards a local checked out folder without creating a new version.
	"""
	print toDiscard
	chkoutInfo = ConfigParser()
	chkoutInfo.read(os.path.join(toDiscard, ".checkoutInfo"))
	chkInDest = chkoutInfo.get("Checkout", "checkedoutfrom")

	nodeInfo = ConfigParser()
	nodeInfo.read(os.path.join(chkInDest, ".nodeInfo"))

	nodeInfo.set("Versioning", "locked", "False")
	_writeConfigFile(os.path.join(chkInDest, ".nodeInfo"), nodeInfo)

	shutil.rmtree(toDiscard)
	if(os.path.exists(toDiscard)):
		os.rmdir(toDiscard)

def getCheckinDest(toCheckin):
	chkoutInfo = ConfigParser()
	chkoutInfo.read(os.path.join(toCheckin, ".checkoutInfo"))
	return chkoutInfo.get("Checkout", "checkedoutfrom")

def checkin(toCheckin):
	"""
	Checks a folder back in as the newest version
	@precondition: toCheckin is a valid path
	@precondition: canCheckin() == True OR all conflicts have been resolved
	"""
	print toCheckin
	chkoutInfo = ConfigParser()
	chkoutInfo.read(os.path.join(toCheckin, ".checkoutInfo"))
	chkInDest = chkoutInfo.get("Checkout", "checkedoutfrom")
	lockedbyme = chkoutInfo.getboolean("Checkout", "lockedbyme")
	
	nodeInfo = ConfigParser()
	nodeInfo.read(os.path.join(chkInDest, ".nodeInfo"))
	locked = nodeInfo.getboolean("Versioning", "locked")
	toKeep = nodeInfo.getint("Versioning", "Versionstokeep")
	newVersion = nodeInfo.getint("Versioning", "latestversion") + 1
	newVersionPath = os.path.join(chkInDest, "src", "v"+("%03d" % newVersion))
	
	if not canCheckin(toCheckin):
		print "Can not overwrite locked folder."
		raise Exception("Can not overwrite locked folder.")
	
	# Checkin
	shutil.copytree(toCheckin, newVersionPath)
	
	timestamp = time.strftime("%a, %d %b %Y %I:%M:%S %p", time.localtime())
	nodeInfo.set("Versioning", "lastcheckintime", timestamp)
	nodeInfo.set("Versioning", "lastcheckinuser", getUsername())
	nodeInfo.set("Versioning", "latestversion", str(newVersion))
	nodeInfo.set("Versioning", "locked", "False")
	_writeConfigFile(os.path.join(chkInDest, ".nodeInfo"), nodeInfo)
	
	#print glob.glob(os.path.join(chkInDest, "src", "*"))
	if toKeep > 0:
		purge(os.path.join(chkInDest, "src"), nodeInfo, newVersion - toKeep)
		_writeConfigFile(os.path.join(chkInDest, ".nodeInfo"), nodeInfo)

	# Clean up
	shutil.rmtree(toCheckin)
	os.remove(os.path.join(newVersionPath, ".checkoutInfo"))

	return chkInDest

################################################################################
# Miscellaneous Versioning
################################################################################
'''
filepath is a valid path to a versioned render folder
finds the latest version folder
if it is empty, it returns it
otherwise creates the next version folder and returns it
'''
def set_version(filepath, prefix=''):
    searchpath = os.path.join(filepath, '*')
    files = glob.glob(searchpath)
    versions = [f for f in files if os.path.isdir(f)]
    versions.sort()
    length = len(versions)
    # print versions
    if length > 0:
        latest = versions[-1]
        index = 0
        v = os.path.basename(latest)
        # make sure it is a versioned folder
        match = False
        while index < length:
            latest = versions[-1-index]
            v = os.path.basename(latest)
            index += 1
            if re.match(prefix+'v[0-9]+', v):
                match = True
                break
        if match:
            # if it's empty use it
            if not os.listdir(latest):
                return latest
        else:
            v = prefix+'v000'
    else:
        v = prefix+'v000'
    
    latest_int = int(v[-3:])+1
    latest = os.path.join(filepath,prefix+'v'+'%03d'%latest_int)

    os.mkdir(latest)
    return latest