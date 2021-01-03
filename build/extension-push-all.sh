#!/bin/sh

clear

if ! test -f "./build/extension-build.sh"; then
    echo "@@ PLEASE RUN FROM THE PROJECT's ROOT directory! @@"
    exit 1
fi

PUSHDIR="../MoneydanceOpen/python_scripts"

echo
echo
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo @@@@ PUSH-ALL RUNNING to $PUSHDIR
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo
echo

if ! test -d "$PUSHDIR"; then
    echo "@@ $PUSHDIR directory missing? @@"
    exit 1
fi

if ! test -d "$PUSHDIR/toolbox"; then
    echo "@@ $PUSHDIR/toolbox directory missing? @@"
    exit 1
fi

if ! test -d "$PUSHDIR/stockglance2020"; then
    echo "@@ $PUSHDIR/stockglance2020 directory missing? @@"
    exit 1
fi

if ! test -d "$PUSHDIR/extract_reminders_csv"; then
    echo "@@ $PUSHDIR/extract_reminders_csv directory missing? @@"
    exit 1
fi

if ! test -d "$PUSHDIR/extract_investment_transactions_csv"; then
    echo "@@ $PUSHDIR/extract_investment_transactions_csv directory missing? @@"
    exit 1
fi

if ! test -d "$PUSHDIR/extract_currency_history_csv"; then
    echo "@@ $PUSHDIR/extract_currency_history_csv directory missing? @@"
    exit 1
fi

if ! test -d "$PUSHDIR/extract_account_registers_csv"; then
    echo "@@ $PUSHDIR/extract_account_registers_csv directory missing? @@"
    exit 1
fi

cp ./toolbox.zip $PUSHDIR/.
cp ./stockglance2020.zip $PUSHDIR/.
cp ./extract_reminders_csv.zip $PUSHDIR/.
cp ./extract_investment_transactions_csv.zip $PUSHDIR/.
cp ./extract_currency_history_csv.zip $PUSHDIR/.
cp ./extract_account_registers_csv.zip $PUSHDIR/.

cp ./source/toolbox/* $PUSHDIR/toolbox/.
cp ./source/install-readme.txt $PUSHDIR/toolbox/.
rm $PUSHDIR/toolbox/*.mxt

cp ./source/stockglance2020/* $PUSHDIR/stockglance2020/.
cp ./source/install-readme.txt $PUSHDIR/stockglance2020/.
rm $PUSHDIR/stockglance2020/*.mxt

cp ./source/extract_reminders_csv/* $PUSHDIR/extract_reminders_csv/.
cp ./source/install-readme.txt $PUSHDIR/extract_reminders_csv/.
rm $PUSHDIR/extract_reminders_csv/*.mxt

cp ./source/extract_investment_transactions_csv/* $PUSHDIR/extract_investment_transactions_csv/.
cp ./source/install-readme.txt $PUSHDIR/extract_investment_transactions_csv/.
rm $PUSHDIR/extract_investment_transactions_csv/*.mxt

cp ./source/extract_currency_history_csv/* $PUSHDIR/extract_currency_history_csv/.
cp ./source/install-readme.txt $PUSHDIR/extract_currency_history_csv/.
rm $PUSHDIR/extract_currency_history_csv/*.mxt

cp ./source/extract_account_registers_csv/* $PUSHDIR/extract_account_registers_csv/.
cp ./source/install-readme.txt $PUSHDIR/extract_account_registers_csv/.
rm $PUSHDIR/extract_account_registers_csv/*.mxt

ls -l $PUSHDIR/*.zip
ls -l $PUSHDIR/toolbox
ls -l $PUSHDIR/stockglance2020
ls -l $PUSHDIR/extract_reminders_csv
ls -l $PUSHDIR/extract_investment_transactions_csv
ls -l $PUSHDIR/extract_currency_history_csv
ls -l $PUSHDIR/extract_account_registers_csv
