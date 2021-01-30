#!/bin/sh

PUSHDIR="../MoneydanceOpen/python_scripts"

echo
echo
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo @@@@ PUSH - RUNNING to $PUSHDIR - module: "$1"
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo
echo

if ! test -f "./build/extension-build.sh"; then
    echo "@@ PLEASE RUN FROM THE PROJECT ROOT directory! @@"
    exit 1
fi

if [ "$1" = "" ] ; then
  echo "@@@ NO PARAMETERS SUPPLIED."
  echo "Run from project root"
  echo "Usage ./build/extension-push.sh module_name"
  echo "Module name must be one of: toolbox, stockglance2020, extract_reminders_csv, extract_investment_transactions_csv, extract_currency_history_csv, extract_account_registers_csv, useful_scripts"
  exit 1
fi

if [ "$1" != "toolbox" ] && [ "$1" != "stockglance2020" ] && [ "$1" != "extract_reminders_csv" ] && [ "$1" != "extract_investment_transactions_csv" ] && [ "$1" != "extract_currency_history_csv" ] && [ "$1" != "extract_account_registers_csv" ] && [ "$1" != "useful_scripts" ] ; then
    echo
    echo "@@ Incorrect Python script name @@"
    echo "must be: toolbox, stockglance2020, extract_reminders_csv, extract_investment_transactions_csv, extract_currency_history_csv, extract_account_registers_csv, useful_scripts"
    exit 1
fi

MODULE=$1

if ! test -d "$PUSHDIR"; then
    echo "@@ $PUSHDIR directory missing? @@"
    exit 1
fi

if ! test -d "$PUSHDIR/$MODULE"; then
    echo "@@ $PUSHDIR/$MODULE directory missing? @@"
    exit 1
fi

if ! test -f "./$MODULE.zip"; then
    echo "@@ ./$MODULE.zip missing? @@"
    exit 2
fi

if  [ "$1" = "useful_scripts" ] ; then

    echo "Skipping checks for non-extension"

else
    if ! test -f "./source/$MODULE/$MODULE.py"; then
        echo "@@ ./source/$MODULE/$MODULE.py missing? @@"
        exit 2
    fi

    if ! test -f "./source/$MODULE/meta_info.dict"; then
        echo "@@ ./source/$MODULE/meta_info.dict missing? @@"
        exit 2
    fi
    if ! test -f "./source/$MODULE/script_info.dict"; then
        echo "@@ ./source/$MODULE/script_info.dict missing? @@"
        exit 2
    fi
fi

cp ./source/"$MODULE"/* "$PUSHDIR/$MODULE"/.
cp "./source/install-readme.txt" "$PUSHDIR/$MODULE"/.

if  [ "$1" = "useful_scripts" ] ; then
    echo "Skipping mxt removal for non-extension"
else
    rm "$PUSHDIR/$MODULE"/*.mxt
fi

if  [ "$1" = "toolbox" ] ; then
    rm "$PUSHDIR/$MODULE"/toolbox_version_requirements.dict
fi

echo "Listing $PUSHDIR/$MODULE"
ls -l "$PUSHDIR/$MODULE"

echo "@@@ module: $MODULE pushed over to $PUSHDIR"