#!/bin/sh

clear

if ! test -f "./build/extension-build.sh"; then
    echo "@@ PLEASE RUN FROM THE PROJECT's ROOT directory! @@"
    exit 1
fi

./build/extension-build.sh toolbox
if [ $? -ne 0 ]; then
    echo "*** BUILD Failed??"
    read -p "Press any key to resume next build..."
fi

./build/extension-build.sh extract_data
if [ $? -ne 0 ]; then
    echo "*** BUILD Failed??"
    read -p "Press any key to resume next build..."
fi

./build/extension-build.sh useful_scripts
if [ $? -ne 0 ]; then
    echo "*** BUILD Failed??"
    read -p "Press any key to resume next build..."
fi

./build/extension-build.sh list_future_reminders
if [ $? -ne 0 ]; then
    echo "*** BUILD Failed??"
    read -p "Press any key to resume next build..."
fi
