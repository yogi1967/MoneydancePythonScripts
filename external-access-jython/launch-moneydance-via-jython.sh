#!/bin/sh

# Co-Author Stuart Beesley - StuWareSoftSystems - April 2021 (last updated: 14th April 2021)

# Shell script: launch-moneydance-via-jython.sh
# Make sure you 'chmod +x launch-moneydance-via-jython.sh' to make script executable

# THIS IS WRITTEN FOR MacOS Terminal(zsh). Adjust accordingly...!

# The purpose of this shell script is to setup Moneydance from the Terminal command line, to allow you to access your data
# outside of Moneydance using jython. The real benefits of using this script are:
#   1. Ability to run without sandbox restrictions (access to all folders, no Gatekeeper messages with Python)
#   2. Ability to launch MD with parameters - e.g. -d for debug mode
#   3. Ability to swap in your own java libraries (assuming you are a developer)

# This has been setup for a Mac, and would need to be changed for Windows/Linux - especially the folder locations...

# Usage:
# Execute using './launch-moneydance-via-jython.sh' you can add parameters that will be passed to Moneydance
# Parameter: '-d'                 is passed by default by this script and turns on MD DEBUG mode
# Parameter: '-v'                 prints the current version
# Parameter: datasetname          will open the specified dataset - specify the full path wrapped in "quotes"
# Parameter: pythonscriptname.py  adds script to a list of scripts to execute (but this seems to then be ignored)
# Parameter: importfilename       executes file import (mutually exclusive to datasetname option)
# Parameter: '-invoke_and_quit=x' will pass along a string that you can to invoke an 'fmodule' (extension) and quit (not showing UI)
#                                 executes Main.showURL(invokeAndQuitURI)
#                                 e.g. 'moneydance:fmodule:test:test:customevent:magic'
#                                 (e.g. my own extension with an id of test defines it's own command called 'test:customevent:magic'
#                                 (there are other variations of this parameter and with ? instead of ':' for parameters.....
# Parameter: '-invoke=x'          Same as -invoke_and_quit but does launch the UI first and doesn't quit...!


# Download/install Java FX (allows Moneybot Console) to run: https://gluonhq.com/download/javafx-15-0-1-sdk-mac/
# Download/install OpenAdoptJDK (Hotspot) v15: https://adoptopenjdk.net/?variant=openjdk15&jvmVariant=hotspot

# Edit the necessary install locations for JDK and JavaFX below

# Edit the necessary settings and your folder locations below

clear
echo
echo
echo
echo
echo
echo
echo "############################################################################################"
echo "############################################################################################"
echo "#########                                                                               ####"
echo "#########  LAUNCHING JYTHON TO ACCESS MONEYDANCE DATA                                   ####"
echo "#########                                                                               ####"
echo "############################################################################################"
echo "############################################################################################"
echo "############################################################################################"
echo

#CHECK_IF_RUNNING=$(ps axlww | grep -v grep | grep -i moneydance)
CHECK_IF_RUNNING=$(pgrep -i -l -f /moneydance)
if [ "${CHECK_IF_RUNNING}" != "" ]; then
    echo "@@ ERROR - it seems that Moneydance might already be running... So I will abort..."
    echo "pgrep returned: '${CHECK_IF_RUNNING}'"
    exit 99
fi

# Prevents Moneydance JFrames appearing in tabs... causes strange problems...
echo "current tabbing mode is set to..:"
defaults read -g AppleWindowTabbingMode

echo "changing tabbing mode to manual (=never)"
defaults write -g AppleWindowTabbingMode -string manual

my_user_path=~
echo "My user path: ${my_user_path}"

# Set your JAVA_HOME
# On Mac, output of '/usr/libexec/java_home --verbose' can help
export JAVA_HOME="${my_user_path}/Library/Java/JavaVirtualMachines/adopt-openjdk-15.0.2/Contents/Home"
export PATH="${JAVA_HOME}/bin:${PATH}"
java=java

jython=jython

export JYTHON_HOME="${my_user_path}/jython2.7.2"
#export JYTHONPATH=?

# JavaFX directory
javafx="${my_user_path}/Documents/Moneydance/My Python Scripts/javafx-sdk-15.0.1/lib"
modules="javafx.swing,javafx.media,javafx.web,javafx.fxml"

# set to "" for standard app install name (I add the version and build to the app name when installing)
#md_version=""
md_version=" 2021 (3065)"

# Where are the MD jar files
md_jars="/Applications/Moneydance${md_version}.app/Contents/Java"
md_icon="/Applications/Moneydance${md_version}.app/Contents/Resources/desktop_icon.icns"


# Set to "" for no sandbox (however, with enabled=true is not really a sandbox)
#use_sandbox=""
use_sandbox="-DSandboxEnabled=true"

# NOTE: I set '-Dinstall4j.exeDir=x' to help my Toolbox extension - this is not needed

# Redirect output to the Moneydance console window...
mkdir -v -p "${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Library/Application Support/Moneydance"
console_file="${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Library/Application Support/Moneydance/errlog.txt"
${java} --version

# shellcheck disable=SC2086
# shellcheck disable=SC2048
${jython} \
  -J-Xdock:icon="${md_icon}" \
  -J-cp "${md_jars}/*" \
  -J--module-path="${javafx}" \
  -J--add-modules=${modules} \
  -J-Dapple.laf.useScreenMenuBar=true \
  -J-Dcom.apple.macos.use-file-dialog-packages=true \
  -J-Dcom.apple.macos.useScreenMenuBar=true \
  -J-Dcom.apple.mrj.application.apple.menu.about.name=Moneydance \
  -J-Dapple.awt.application.name=Moneydance \
  -J-Dcom.apple.smallTabs=true \
  -J-Dapple.awt.application.appearance=system \
  -J-Dfile.encoding=UTF-8 \
  -J-DUserHome=${my_user_path} \
  -J${use_sandbox} \
  -J-Dinstall4j.exeDir="${md_jars}" \
  -J-Duser.dir="${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data" \
  -J-Duser.home="${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data" \
  -J-DApplicationSupportDirectory="${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Library/Application Support" \
  -J-DLibraryDirectory="${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Library" \
  -J-DDownloadsDirectory="${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Downloads" \
  -J-DDesktopDirectory="${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Desktop" \
  -J-DPicturesDirectory="${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Pictures" \
  -J-DDocumentsDirectory="${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Documents" \
  -J-DCachesDirectory="${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Library/Caches" \
  -J-DSharedPublicDirectory="${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Public" \
  -J-DMoviesDirectory="${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Movies" \
  -J-DDownloadsDirectory="${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Downloads" \
  -J-DApplicationDirectory="${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Applications" \
  -J-DMusicDirectory="${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Music" \
  -J-DAutosavedInformationDirectory="${my_user_path}/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Library/Autosave Information" \
  -J-Xmx2G \
  -J-Ddummyarg1=arg1 \
  -J-Ddummyarg2=arg2 \
  $*


#open "$console_file"

echo "changing tabbing mode to fullscreen"
defaults write -g AppleWindowTabbingMode -string fullscreen

exit 0

