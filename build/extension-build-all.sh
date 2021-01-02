#!/bin/sh

clear

if ! test -f "./build/extension-build.sh"; then
    echo "@@ PLEASE RUN FROM THE PROJECT's ROOT directory! @@"
    exit 1
fi

./build/extension-build.sh toolbox
if [ $? -ne 0 ]; then
    echo *** BUILD Failed??
    read -p "Press any key to resume next build..."
fi

./build/extension-build.sh stockglance2020
if [ $? -ne 0 ]; then
    echo *** BUILD Failed??
    read -p "Press any key to resume next build..."
fi

./build/extension-build.sh extract_reminders_csv
if [ $? -ne 0 ]; then
    echo *** BUILD Failed??
    read -p "Press any key to resume next build..."
fi

./build/extension-build.sh extract_investment_transactions_csv
if [ $? -ne 0 ]; then
    echo *** BUILD Failed??
    read -p "Press any key to resume next build..."
fi

./build/extension-build.sh extract_currency_history_csv
if [ $? -ne 0 ]; then
    echo *** BUILD Failed??
    read -p "Press any key to resume next build..."
fi


./build/extension-build.sh extract_account_registers_csv
if [ $? -ne 0 ]; then
    echo *** BUILD Failed??
    read -p "Press any key to resume next build..."
fi
