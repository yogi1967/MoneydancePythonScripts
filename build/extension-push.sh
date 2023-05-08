#!/bin/sh

###############################################################################
# Author:   Stuart Beesley - StuWareSoftSystems 2021-2023
###############################################################################

MODULE_LIST=("toolbox" "extract_data" "useful_scripts" "list_future_reminders" "net_account_balances" "extension_tester" "accounts_categories_mega_search_window" "security_performance_graph")
NOT_REALLY_EXTENSION_LIST=("useful_scripts")
BUNDLE_OWN_JAVA_LIST=("x")

PUSHDIR="../MoneydanceOpen/python_scripts"
JAVA_PACKAGE_NAME="StuWareSoftSystems_CommonCode"

echo
echo
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo @@@@ PUSH - RUNNING to ${PUSHDIR} - module: "$1"
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo
echo

if ! test -f "./build/extension-build.sh"; then
  echo "@@ PLEASE RUN FROM THE PROJECT ROOT directory! @@"
  exit 1
fi

if [ "$1" = "" ]; then
  echo "@@@ NO PARAMETERS SUPPLIED."
  echo "Run from project root"
  echo "Usage ./build/extension-push.sh module_name"
  echo "Module name must be one of:" "${MODULE_LIST[@]}"
  exit 2
fi

MODULE="ERROR"
for MODULE_CHECK in "${MODULE_LIST[@]}"; do
  if [ "${MODULE_CHECK}" = "${1}" ]; then
    MODULE=$1
  fi
done

if [ "${MODULE}" = "ERROR" ]; then
  echo
  echo "@@ Incorrect Python Module Build name @@"
  echo "Module name must be one of:" "${MODULE_LIST[@]}"
  exit 3
fi

REALLY_EXTENSION="YES"
for NOT_EXTENSION_CHECK in "${NOT_REALLY_EXTENSION_LIST[@]}"; do
  if [ "${NOT_EXTENSION_CHECK}" = "${MODULE}" ]; then
    REALLY_EXTENSION="NO"
  fi
done

BUNDLE_JAVA="NO"
for BUNDLE_JAVA_CHECK in "${BUNDLE_OWN_JAVA_LIST[@]}"; do
  if [ "${BUNDLE_JAVA_CHECK}" = "${MODULE}" ]; then
    BUNDLE_JAVA="YES"
  fi
done

echo "Module PUSH for ${MODULE} running.... (Really an Extension=${REALLY_EXTENSION}, Bundle Own Java=${BUNDLE_JAVA})"

if ! test -d "${PUSHDIR}"; then
  echo "@@ ${PUSHDIR} directory missing? @@"
  exit 4
fi

if ! test -d "${PUSHDIR}/${MODULE}"; then
  echo "@@ ${PUSHDIR}/${MODULE} directory missing? @@"
  exit 5
fi

if ! test -f "./${MODULE}.zip"; then
  echo "@@ ./${MODULE}.zip missing? @@"
  exit 6
fi

if [ "${BUNDLE_JAVA}" = "YES" ]; then

  echo "Bundle Java requested... Checking .java and .class files exists..."
  if ! test -f "./java_code/src/${JAVA_PACKAGE_NAME}.java"; then
    echo "ERROR - ./java_code/src/${JAVA_PACKAGE_NAME}.java does not exist!"
    exit 7
  fi
  if ! test -f "./java_code/compiled/${JAVA_PACKAGE_NAME}.class"; then
    echo "ERROR - ./java_code/compiled/${JAVA_PACKAGE_NAME}.class does not exist!"
    exit 7
  fi

fi

if [ "${REALLY_EXTENSION}" = "NO" ]; then

  echo "Skipping checks for non-extension"

else
  if ! test -f "./source/${MODULE}/${MODULE}.py"; then
    echo "@@ ./source/${MODULE}/${MODULE}.py missing? @@"
    exit 8
  fi

  if ! test -f "./source/${MODULE}/meta_info.dict"; then
    echo "@@ ./source/${MODULE}/meta_info.dict missing? @@"
    exit 9
  fi
  if ! test -f "./source/${MODULE}/script_info.dict"; then
    echo "@@ ./source/${MODULE}/script_info.dict missing? @@"
    exit 10
  fi
fi

echo "Removing all existing files from target directory..."
rm -f "${PUSHDIR}/${MODULE}"/*.*

cp "./source/${MODULE}"/* "${PUSHDIR}/${MODULE}/."
if [ $? -ne 0 ]; then
  echo "*** cp ./source/${MODULE}/* Failed??"
  exit 11
fi

if [ "${MODULE}" = "toolbox" ]; then
  echo "Copy extra scripts for Toolbox..."
  cp "./source/useful_scripts"/ofx_*.py "${PUSHDIR}/${MODULE}/."
  if [ $? -ne 0 ]; then
    echo "*** cp extra scripts ofx*.py failed??"
    exit 5
  fi
fi

if [ "${BUNDLE_JAVA}" = "YES" ]; then
  echo "Copying own .java and .class files to bundle into mxt(jar)..."

  cp "./java_code/src/${JAVA_PACKAGE_NAME}.java" "${PUSHDIR}/${MODULE}/."
  if [ $? -ne 0 ]; then
    echo "*** cp ./java_code/src/${JAVA_PACKAGE_NAME}.java Failed??"
    exit 13
  fi

  cp "./java_code/compiled/${JAVA_PACKAGE_NAME}.class" "${PUSHDIR}/${MODULE}/."
  if [ $? -ne 0 ]; then
    echo "*** cp ./java_code/compiled/${JAVA_PACKAGE_NAME}.class Failed??"
    exit 13
  fi

fi


if [ "${MODULE}" != "extension_tester" ]; then
  cp "./source/install-readme.txt" "${PUSHDIR}/${MODULE}/."
  if [ $? -ne 0 ]; then
    echo "*** cp ./source/install-readme.txt Failed??"
    exit 14
  fi
fi

rm -f "${PUSHDIR}/${MODULE}"/*.docx
rm -f "${PUSHDIR}/${MODULE}"/*.mxt
rm -f "${PUSHDIR}/${MODULE}"/*.pyi
rm -f "${PUSHDIR}/${MODULE}"/*.pyc
rm -f "${PUSHDIR}/${MODULE}/${MODULE}\$py.class"
rm -f "${PUSHDIR}/${MODULE}"/function_thread_map.txt
rm -f "${PUSHDIR}/${MODULE}"/_PREVIEW_BUILD_

if [ "${MODULE}" = "toolbox" ]; then
  rm "${PUSHDIR}/${MODULE}/toolbox_version_requirements.dict"
fi

echo "Listing ${PUSHDIR}/${MODULE}"
ls -l "${PUSHDIR}/${MODULE}"

echo "@@@ module: ${MODULE} pushed over to ${PUSHDIR}"
