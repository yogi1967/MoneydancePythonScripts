#!/bin/sh

echo
echo
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo @@@@ BUILD of "$1" RUNNING
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo
echo

if [ "$1" = "" ] ; then
  echo "@@@ NO PARAMETERS SUPPLIED."
  echo "Run from project root"
  echo "Usage ./build/extension-build.sh module_name"
  echo "Module name must be one of: toolbox, stockglance2020, extract_reminders_csv, extract_investment_transactions_csv, extract_currency_history_csv, extract_account_registers_csv, useful_scripts"
  exit 1
fi

if ! test -f "./build/extension-build.sh"; then
    echo "@@ PLEASE RUN FROM THE PROJECT's ROOT directory! @@"
    exit 1
fi

if [ "$1" != "toolbox" ] && [ "$1" != "stockglance2020" ] && [ "$1" != "extract_reminders_csv" ] && [ "$1" != "extract_investment_transactions_csv" ] && [ "$1" != "extract_currency_history_csv" ] && [ "$1" != "extract_account_registers_csv" ] && [ "$1" != "useful_scripts" ] && [ "$1" != "test" ]; then
    echo
    echo "@@ Incorrect Python script name @@"
    echo "must be: toolbox, stockglance2020, extract_reminders_csv, extract_investment_transactions_csv, extract_currency_history_csv, extract_account_registers_csv, useful_scripts"
    exit 1
else
    FILE=$1
fi

# Relies on "ant genkeys" and various jar files from within the Moneydance devkit

if  [ "$1" = "useful_scripts" ] ; then

  if ! test -d ./source/"$FILE"; then
      echo "ERROR - directory $FILE/ does not exist!"
      exit 1
  fi

else

  if ! test -f ./source/"$FILE/$FILE".py; then
      echo "ERROR - $FILE/$FILE.py does not exist!"
      exit 1
  fi

  if ! test -f ./source/"$FILE"/script_info.dict; then
      echo "ERROR - $FILE/script_info.dict does not exist!"
      exit 1
  fi

  if ! test -f ./source/"$FILE"/meta_info.dict; then
      echo "ERROR - $FILE/meta_info.dict does not exist!"
      exit 1
  fi
fi

if ! test -f "./moneydance-devkit-5.1 2/src/priv_key"; then
    echo "ERROR - Your private key from ant genkeys does not exist!"
    exit 1
fi

if ! test -f "./moneydance-devkit-5.1 2/lib/extadmin.jar"; then
    echo "ERROR - extadmin.jar does not exist!"
    exit 1
fi

if ! test -f "./moneydance-devkit-5.1 2/lib/moneydance-dev.jar"; then
    echo "ERROR - moneydance-dev.jar does not exist!"
    exit 1
fi

if ! test -f "./build/extension_keyfile."; then
    echo "@@@ ERROR - my key file (./build/extension_keyfile) does not exist!"
    exit 2
fi

if ! test -f "./source/install-readme.txt"; then
    echo "@@@ ERROR - ./source/install-readme.txt does not exist!"
    exit 2
fi

if test -f ./source/"$FILE/$FILE".mxt; then
    rm ./source/"$FILE/$FILE".mxt
fi

if  [ "$1" = "useful_scripts" ]; then

    echo "Skipping extension build for $FILE"

else

    if ! test -d "com"; then
        mkdir com
    fi

    if ! test -d "com/moneydance"; then
        mkdir com/moneydance
    fi

    if ! test -d "com/moneydance/modules"; then
        mkdir com/moneydance/modules
    fi

    if ! test -d "com/moneydance/modules/features"; then
        mkdir com/moneydance/modules/features/
    fi

    if ! test -d com/moneydance/modules/features/"$FILE"; then
        mkdir com/moneydance/modules/features/"$FILE"
    fi

    cp ./source/"$FILE"/meta_info.dict com/moneydance/modules/features/"$FILE"/meta_info.dict

    zip -j -z ./source/"$FILE/$FILE".mxt ./source/"$FILE/$FILE".py <<< "StuWareSoftSystems: $FILE Python Extension for Moneydance (by Stuart Beesley). Please see install-readme.txt"

    if test -f ./source/"$FILE"/readme.txt; then
      zip -j ./source/"$FILE/$FILE".mxt ./source/"$FILE"/readme.txt
    else
      echo "No readme.txt file to ZIP - skipping....."
    fi

    zip -j ./source/"$FILE/$FILE".mxt ./source/install-readme.txt

    zip -j ./source/"$FILE/$FILE".mxt ./source/"$FILE"/script_info.dict
    zip -m ./source/"$FILE/$FILE".mxt com/moneydance/modules/features/"$FILE"/meta_info.dict

    cp "./moneydance-devkit-5.1 2/lib/extadmin.jar" .
    cp "./moneydance-devkit-5.1 2/lib/moneydance-dev.jar" .

    cp "./moneydance-devkit-5.1 2/src/priv_key" .
    cp "./moneydance-devkit-5.1 2/src/pub_key" .

    if test -f ./source/"$FILE/s-$FILE".mxt; then
        rm ./source/"$FILE/s-$FILE".mxt
    fi

    if test -f ./s-"$FILE".mxt; then
        rm ./s-"$FILE".mxt
    fi

    #read -p "Press any key to resume ..."

    java -cp extadmin.jar:moneydance-dev.jar com.moneydance.admin.KeyAdmin signextjar priv_key private_key_id "$FILE" ./source/"$FILE/$FILE".mxt < ./build/extension_keyfile.
    if ! test -f s-"$FILE".mxt; then
        echo "ERROR - Signed MXT does not exist?"
        exit 3
    else
        zip -z s-"$FILE".mxt <<< "StuWareSoftSystems: $FILE Python Extension for Moneydance (by Stuart Beesley). Please see install-readme.txt"
    fi

    #read -p "Press any key to resume ..."

    rm priv_key
    rm pub_key
    rm extadmin.jar
    rm moneydance-dev.jar

    ls -l ./source/"$FILE/$FILE".mxt
    ls -l s-"$FILE".mxt

    rm ./source/"$FILE/$FILE".mxt
    mv s-"$FILE".mxt ./source/"$FILE/$FILE".mxt


    if test -f ./source/"$FILE/$FILE".mxt; then
        ls -l ./source/"$FILE/$FILE".mxt
        unzip -l ./source/"$FILE/$FILE".mxt
        echo ===================
        echo FILE ./source/"$FILE/$FILE".mxt has been built...
    else
        echo @@@@@@@@@@@@@@@@@
        echo "PROBLEM CREATING ./source/$FILE/$FILE.mxt ..."
        exit 4
    fi

fi

echo @ Building final ZIP file for publication...
if test -f ./"$FILE".zip; then
    echo "Removing old ./$FILE.zip"
    rm ./"$FILE".zip
fi

zip -j -z ./"$FILE".zip ./source/install-readme.txt <<< "StuWareSoftSystems: $FILE for Moneydance (by Stuart Beesley). Please see install-readme.txt"

if  [ "$1" = "useful_scripts" ]; then

    zip -j -c ./"$FILE".zip ./source/"$FILE/"*.py <<< "StuWareSoftSystems: A collection of $FILE for Moneydance."

else

    zip -j -c ./"$FILE".zip ./source/"$FILE/$FILE".mxt <<< "StuWareSoftSystems: $FILE Extension for Moneydance."

    if  [ "$1" != "toolbox" ] ; then
        zip -j -c ./"$FILE".zip ./source/"$FILE/$FILE".py <<< "StuWareSoftSystems: $FILE Script for Moneydance."
    else
        echo "Not including $FILE.py for toolbox package...."
    fi

fi

if test -f ./source/"$FILE"/readme.txt; then
  zip -j ./"$FILE".zip ./source/"$FILE"/readme.txt
else
  echo "No help file to ZIP - skipping....."
fi


if test -f ./"$FILE".zip; then
    ls -l ./"$FILE".zip
    unzip -l ./"$FILE".zip
    echo ===================
    echo "DISTRIBUTION FILE ./$FILE.zip has been built..."
else
    echo @@@@@@@@@@@@@@@@@
    echo "PROBLEM CREATING FINAL DISTRIBUTION ./$FILE.zip !"
    exit 5
fi





