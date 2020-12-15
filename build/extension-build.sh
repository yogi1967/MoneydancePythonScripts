#!/bin/sh

clear

if [ "$1" = "" ] ; then
  echo "@@@ NO PARAMETERS SUPPLIED."
  echo "Run from project root"
  echo "Usage ./build/extension-build.sh module_name build_type"
  echo "Module name must be one of: Toolbox, StockGlance2020, extract_reminders_csv, extract_investment_transactions_csv, extract_currency_history_csv"
  echo "Build type must be: test or final"
  exit 1
fi

if ! test -f "./build/extension-build.sh"; then
    echo "@@ PLEASE RUN FROM THE PROJECT's ROOT directory! @@"
    exit 1
fi

if [ "$1" != "Toolbox" ] && [ "$1" != "StockGlance2020" ] && [ "$1" != "extract_reminders_csv" ] && [ "$1" != "extract_investment_transactions_csv" ] && [ "$1" != "extract_currency_history_csv" ] ; then
    echo
    echo "@@ Incorrect Python script name @@"
    echo "must be: Toolbox, StockGlance2020, extract_reminders_csv, extract_investment_transactions_csv, extract_currency_history_csv"
    exit 1
else
    FILE=$1
fi

if  [ "$2" != "test" ] && [ "$2" != "final" ] ; then
  echo
  echo "@@ Incorrect build type @@"
  echo "must be: test or final"
  exit 1
fi

# Relies on "ant genkeys" and various jar files from within the Moneydance devkit

if ! test -f "./source/$FILE.py"; then
    echo "ERROR - $FILE.py does not exist!"
    exit 1
fi

if ! test -f "./source/$FILE-script_info.dict"; then
    echo "ERROR - $FILE-script_info.dict does not exist!"
    exit 1
fi

if ! test -f "./source/$FILE-meta_info.dict"; then
    echo "ERROR - $FILE-meta_info.dict does not exist!"
    exit 1
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


if test -f "./source/$FILE.mxt"; then
    rm "./source/$FILE.mxt"
fi

if test -f "./source/script_info.dict"; then
    rm ./source/script_info.dict
fi

if test -f "./source/meta_info.dict"; then
    rm ./source/meta_info.dict
fi

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

if ! test -d "com/moneydance/modules/features/$FILE"; then
    mkdir com/moneydance/modules/features/"$FILE"
fi

cp "./source/$FILE-script_info.dict" ./source/script_info.dict
cp "./source/$FILE-meta_info.dict" com/moneydance/modules/features/"$FILE"/meta_info.dict

zip -j -z ./source/"$FILE".mxt "./source/$FILE".py <<< "StuWareSoftSystems: $FILE Python Extension for Moneydance (by Stuart Beesley). Please see install-readme.txt"

if test -f "./source/$FILE"-README.txt; then
  zip -j ./source/"$FILE".mxt ./source/"$FILE"-README.txt
else
  echo "No help file to ZIP - skipping....."
fi

zip -j ./source/"$FILE.mxt" "./source/install-readme.txt"

zip -m -j ./source/"$FILE.mxt" ./source/script_info.dict
zip -m ./source/"$FILE.mxt" "com/moneydance/modules/features/$FILE/meta_info.dict"

cp "./moneydance-devkit-5.1 2/lib/extadmin.jar" .
cp "./moneydance-devkit-5.1 2/lib/moneydance-dev.jar" .

cp "./moneydance-devkit-5.1 2/src/priv_key" .
cp "./moneydance-devkit-5.1 2/src/pub_key" .

if test -f ./source/"s-$FILE.mxt"; then
    rm ./source/"s-$FILE.mxt"
fi

if test -f ./"s-$FILE.mxt"; then
    rm ./"s-$FILE.mxt"
fi

#read -p "Press any key to resume ..."

java -cp extadmin.jar:moneydance-dev.jar com.moneydance.admin.KeyAdmin signextjar priv_key private_key_id "$FILE" ./source/"$FILE.mxt" < "./build/extension_keyfile."
if ! test -f "s-$FILE.mxt"; then
    echo "ERROR - Signed MXT does not exist?"
    exit 3
else
    zip -z "s-$FILE.mxt" <<< "StuWareSoftSystems: $FILE Python Extension for Moneydance (by Stuart Beesley). Please see install-readme.txt"
fi

#read -p "Press any key to resume ..."

rm priv_key
rm pub_key
rm extadmin.jar
rm moneydance-dev.jar

ls -l ./source/"$FILE".mxt
ls -l "s-$FILE.mxt"

rm ./source/"$FILE".mxt
mv "s-$FILE.mxt" ./source/"$FILE.mxt"


if test -f ./source/"$FILE.mxt"; then
    ls -l ./source/"$FILE".mxt
    unzip -l ./source/"$FILE".mxt
    echo ===================
    echo FILE ./source/"$FILE".mxt has been built using "$2" mode...
else
    echo @@@@@@@@@@@@@@@@@
    echo PROBLEM CREATING ./source/"$FILE".mxt - "$2" mode...
    exit 4
fi

if  [ "$2" != "final" ] ; then
  echo TESTING - your built "$FILE.mxt" will be in the ./source directory
  exit 0
fi

echo @ Building final ZIP file for publication...
if test -f ./"$FILE.zip"; then
    echo "Removing old ./$FILE.zip"
    rm ./"$FILE.zip"
fi

zip -j -z ./"$FILE.zip" "./source/install-readme.txt" <<< "StuWareSoftSystems: $FILE for Moneydance (by Stuart Beesley). Please see install-readme.txt"
zip -j -c ./"$FILE.zip" "./source/$FILE.mxt" <<< "StuWareSoftSystems: $FILE Extension for Moneydance."


if  [ "$1" != "Toolbox" ] ; then
  zip -j -c ./"$FILE.zip" "./source/$FILE.py" <<< "StuWareSoftSystems: $FILE Script for Moneydance."
else
  echo "Not including $FILE.py for Toolbox package...."
fi

if test -f "./source/$FILE"-README.txt; then
  zip -j ./"$FILE".zip ./source/"$FILE"-README.txt
else
  echo "No help file to ZIP - skipping....."
fi


if test -f ./"$FILE.zip"; then
    ls -l ./"$FILE".zip
    unzip -l ./"$FILE".zip
    echo ===================
    echo DISTRIBUTION FILE ./"$FILE".zip has been built...
else
    echo @@@@@@@@@@@@@@@@@
    echo PROBLEM CREATING FINAL DISTRIBUTION ./"$FILE".zip !
    exit 5
fi





