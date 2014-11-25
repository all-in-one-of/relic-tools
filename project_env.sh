#!/bin/bash

# project_evn.sh
#	Exports all project environment variables and creates missing directories
#	This script will need to be edited for each project.
#
#   Place this script and other tools inside the ${PROJECT_TOOLS} directory defined below.
#
# @author: Brian Kingery

###############################################################################
# Project specific environment variables
###############################################################################

# Root directory for the project (eg: /groups/owned)
# This directory should be created manually.
# If JOB is not already set, then set it with a hardcoded default.
# Also, set PROJECT_NAME based on JOB.
if [ -z "$JOB" ]
then
    # The name of the project (eg: owned)
    export PROJECT_NAME=relic
    export JOB=/groups2/${PROJECT_NAME}
    # export PROJECT_NAME=relic2015
    # export JOB=~/relic2015

else
    export PROJECT_NAME=`basename $JOB`
fi

# Set PS1 to a sane default if it doesn't already exist
if [ -z "$PS1" ]
then
    PS1="[\u@\h \W]\$ "; # Customize terminal prompt
fi

# Tools/scripts directory. This project_env.sh script should be placed here.
# along with the other tools and scripts.
# Yes, its a chicken egg problem...
export PROJECT_TOOLS=${JOB}/relic-tools

# User directory for checkout files, testing, ect.
export USER_DIR=${JOB}/users/${USER} 

# Root directory for assets
export ASSETS_DIR=${JOB}/assets

# Repo directory with the code for the main game
export REPO_DIR=${JOB}/tombgameugly/GraveRobberUnityProject

# Append to python path so batch scripts can access our modules
export PYTHONPATH=$PYTHONPATH:/usr/autodesk/maya2014-x64/lib/python2.7/site-packages:/usr/lib64/python2.6/site-packages:/usr/lib64/python2.7/site-packages:${PROJECT_TOOLS}:${PROJECT_TOOLS}/asset_manager:${PYTHONPATH}

# Function to build directory structure
buildProjectDirs()
{
    # Create Root directory for assets
    if [ ! -d "$ASSETS_DIR" ]; then
        echo "making assets dir"
        mkdir -p "$ASSETS_DIR"
    fi

    # Create User directory for checkout files, testing, ect.
    if [ ! -d "$USER_DIR" ]; then
        echo "making user dir"
        mkdir -p "$USER_DIR"
        mkdir -p "$USER_DIR"/checkout
        chmod 774 -R "$USER_DIR"
    fi
}

# Uncomment to build the project directories
buildProjectDirs

chmod 774 -R "$USER_DIR"
chmod 774 -R "$ASSETS_DIR"


###############################################################################
# Maya specific environment
###############################################################################

# Add our custom python scripts
export MAYA_TOOLS_DIR=${PROJECT_TOOLS}/maya-tools
export MAYA_SHELF_DIR=${MAYA_TOOLS_DIR}/shelf
export MAYA_SCRIPT_PATH=${MAYA_SCRIPT_PATH}:${PYTHONPATH}:${MAYA_SHELF_DIR}

###############################################################################
# BEGIN AWESOMENESS!!!
###############################################################################

