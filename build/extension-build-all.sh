#!/bin/sh

clear

if [ "$1" = "" ] ; then
  echo "@@@ NO PARAMETERS SUPPLIED."
  echo "Run from project root. Specify test or final"
  exit 1
fi

if ! test -f "./build/extension-build.sh"; then
    echo "@@ PLEASE RUN FROM THE PROJECT's ROOT directory! @@"
    exit 1
fi

if  [ "$1" != "test" ] && [ "$1" != "final" ] ; then
  echo
  echo "@@ Incorrect build type @@"
  echo "must be: test or final"
  exit 1
fi

./build/extension-build.sh Toolbox $1
if [ $? -ne 0 ]; then
    echo *** BUILD Failed??
    read -p "Press any key to resume next build..."
fi

./build/extension-build.sh StockGlance2020 $1
if [ $? -ne 0 ]; then
    echo *** BUILD Failed??
    read -p "Press any key to resume next build..."
fi

./build/extension-build.sh extract_reminders_csv $1
if [ $? -ne 0 ]; then
    echo *** BUILD Failed??
    read -p "Press any key to resume next build..."
fi

./build/extension-build.sh extract_investment_transactions_csv $1
if [ $? -ne 0 ]; then
    echo *** BUILD Failed??
    read -p "Press any key to resume next build..."
fi

./build/extension-build.sh extract_currency_history_csv $1
if [ $? -ne 0 ]; then
    echo *** BUILD Failed??
    read -p "Press any key to resume next build..."
fi


./build/extension-build.sh extract_account_registers_csv $1
if [ $? -ne 0 ]; then
    echo *** BUILD Failed??
    read -p "Press any key to resume next build..."
fi
