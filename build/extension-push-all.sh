#!/bin/sh

clear

if ! test -f "./build/extension-build.sh"; then
    echo "@@ PLEASE RUN FROM THE PROJECT's ROOT directory! @@"
    exit 1
fi

./build/extension-push.sh toolbox
if [ $? -ne 0 ]; then
    echo "*** PUSH of toolbox Failed??"
    read -p "Press any key to resume next build..."
fi

./build/extension-push.sh extract_data
if [ $? -ne 0 ]; then
    echo "*** PUSH of extract_data Failed??"
    read -p "Press any key to resume next build..."
fi

./build/extension-push.sh useful_scripts
if [ $? -ne 0 ]; then
    echo "*** PUSH of useful_scripts Failed??"
    read -p "Press any key to resume next build..."
fi

./build/extension-push.sh list_future_reminders
if [ $? -ne 0 ]; then
    echo "*** PUSH of list_future_reminders Failed??"
    read -p "Press any key to resume next build..."
fi
