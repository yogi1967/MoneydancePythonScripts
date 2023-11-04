#!/bin/sh

# Shell script: launch-moneydance-mac.sh
# Make sure you 'sudo chmod +x launch-moneydance-mac.sh' to make script executable

# THIS IS WRITTEN FOR MacOS Terminal(zsh). Adjust accordingly...!

# Usage:
# Execute using './launch-moneydance-mac.sh' you can add parameters that will be passed to Moneydance
# Parameter: '-d'                 is passed by default by this script and turns on MD DEBUG mode
# Parameter: '-v'                 prints the current version
# Parameter: '-nobackup'          disables auto-backup for this launch session
# Parameter: datasetname          will open the specified dataset - specify the full path wrapped in "quotes"
# Parameter: pythonscriptname.py  adds script to a list of scripts to execute (but this seems to then be ignored)
# Parameter: importfilename       executes file import (mutually exclusive to datasetname option)
# Parameter: '-invoke_and_quit=x' will pass along a string that you can use to invoke an 'fmodule' (extension) and quit (not showing UI)
#                                 executes Main.showURL(invokeAndQuitURI)
#                                 e.g. 'moneydance:fmodule:test:test:customevent:magic'
#                                 (e.g. my own extension with an id of test defines it's own command called 'test:customevent:magic'
#                                 (there are other variations of this parameter and with ? instead of ':' for parameters.....
# Parameter: '-invoke=x'          Same as -invoke_and_quit but does launch the UI first and doesn't quit...!

# MD2021.2(3088): Adds the capability to set the encryption passphrase into an environment variable to bypass the popup question
#                 Either: md_passphrase=  or  md_passphrase_[filename in lowercase format]=

# Known extension(parameters) that can auto invoke from command line:
#   -invoke=moneydance:fmodule:securityquoteload:runstandalone
#   -invoke=moneydance:fmodule:securityquoteload:runstandalone:quit             (same as option above, quits after run)
#   -invoke=moneydance:fmodule:securityquoteload:runstandalone:noquit           (does not quit after QL run)

# -invoke=moneydance:fmodule:extract_data:autoextract:noquit'
# -invoke=moneydance:fmodule:extract_data:autoextract:quit'


CHECK_IF_RUNNING=$(pgrep -i -l -f /moneydance)
if [ "${CHECK_IF_RUNNING}" != "" ]; then
    echo "@@ ERROR - it seems that Moneydance might already be running... So I will abort..."
    echo "pgrep returned: '${CHECK_IF_RUNNING}'"
    exit 99
fi

echo "current tabbing mode is set to..:"
defaults read -g AppleWindowTabbingMode

echo "changing tabbing mode to manual (=never)"
defaults write -g AppleWindowTabbingMode -string manual

my_user_path=~
echo "My user path: ${my_user_path}"

#unset md_passphrase
export md_passphrase=test

"/Applications/Moneydance.app/Contents/MacOS/Moneydance" \
  -d \
#  "/Users/stu/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Documents/Quote Loader Examples.moneydance" \
# -invoke=moneydance:fmodule:securityquoteload:runstandalone:quit
# -invoke=moneydance:fmodule:extract_data:autoextract:quit
exit 0
