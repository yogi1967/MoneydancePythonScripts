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

./build/extension-push.sh stockglance2020
if [ $? -ne 0 ]; then
    echo "*** PUSH of stockglance2020 Failed??"
    read -p "Press any key to resume next build..."
fi

./build/extension-push.sh extract_reminders_csv
if [ $? -ne 0 ]; then
    echo "*** PUSH of extract_reminders_csv Failed??"
    read -p "Press any key to resume next build..."
fi

./build/extension-push.sh extract_investment_transactions_csv
if [ $? -ne 0 ]; then
    echo "*** PUSH of extract_investment_transactions_csv Failed??"
    read -p "Press any key to resume next build..."
fi

./build/extension-push.sh extract_currency_history_csv
if [ $? -ne 0 ]; then
    echo "*** PUSH of extract_currency_history_csv Failed??"
    read -p "Press any key to resume next build..."
fi

./build/extension-push.sh extract_account_registers_csv
if [ $? -ne 0 ]; then
    echo "*** PUSH of extract_account_registers_csv Failed??"
    read -p "Press any key to resume next build..."
fi

