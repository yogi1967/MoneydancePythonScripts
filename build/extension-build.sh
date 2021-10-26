#!/bin/sh

###############################################################################
# Author:   Stuart Beesley - StuWareSoftSystems 2021
# Purpose:  Build shell script (Mac) to build Python Extensions for Moneydance
#
# NOTE: The Moneydance extension .mxt file is really just a zip / jar file.....
###############################################################################

echo
echo
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo @@@@ BUILD of "$1" RUNNING...
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo
echo

EXTN_LIST=("toolbox" "extract_data" "useful_scripts" "list_future_reminders" "net_account_balances" "extension_tester" "my_networth" "total_selected_transactions" "test")
RESTRICT_SCRIPT_LIST=("toolbox" "net_account_balances" "total_selected_transactions")
NOT_REALLY_EXTENSION_LIST=("useful_scripts")
PUBLISH_ALL_FILES_IN_ZIP_TOO_LIST=("extension_tester" "my_networth")
BUNDLE_OWN_JAVA_LIST=("test")

if [ "$1" = "" ]; then
  echo "@@@ NO PARAMETERS SUPPLIED."
  echo "Run from project root"
  echo "Usage ./build/extension-build.sh module_name"
  echo "Module name must be one of:" "${EXTN_LIST[@]}"
  exit 1
fi

if ! test -f "./build/extension-build.sh"; then
  echo "@@ PLEASE RUN FROM THE PROJECT's ROOT directory! @@"
  exit 1
fi

EXTN_NAME="ERROR"
for EXTN_CHECK in "${EXTN_LIST[@]}"; do
  if [ "${EXTN_CHECK}" = "${1}" ]; then
    EXTN_NAME=$1
  fi
done

if [ "${EXTN_NAME}" = "ERROR" ]; then
  echo
  echo "@@ Incorrect Python script name @@"
  echo "Module name must be one of:" "${EXTN_LIST[@]}"
  exit 1
fi

RESTRICT_SCRIPT="NO"
for RESTRICT_CHECK in "${RESTRICT_SCRIPT_LIST[@]}"; do
  if [ "${RESTRICT_CHECK}" = "${EXTN_NAME}" ]; then
    RESTRICT_SCRIPT="YES"
  fi
done

BUNDLE_JAVA="NO"
for BUNDLE_JAVA_CHECK in "${BUNDLE_OWN_JAVA_LIST[@]}"; do
  if [ "${BUNDLE_JAVA_CHECK}" = "${EXTN_NAME}" ]; then
    BUNDLE_JAVA="YES"
  fi
done

REALLY_EXTENSION="YES"
for NOT_EXTENSION_CHECK in "${NOT_REALLY_EXTENSION_LIST[@]}"; do
  if [ "${NOT_EXTENSION_CHECK}" = "${EXTN_NAME}" ]; then
    REALLY_EXTENSION="NO"
  fi
done

PUBLISH_ALL_FILES="NO"
for PUBLISH_ALL_CHECK in "${PUBLISH_ALL_FILES_IN_ZIP_TOO_LIST[@]}"; do
  if [ "${PUBLISH_ALL_CHECK}" = "${EXTN_NAME}" ]; then
    PUBLISH_ALL_FILES="YES"
  fi
done

echo "Module build for ${EXTN_NAME} running.... Restrict Script Publication=${RESTRICT_SCRIPT}... Bundle Own Java=${BUNDLE_JAVA}... (Really an Extension=${REALLY_EXTENSION})... Publish all files=${PUBLISH_ALL_FILES}"

sMXT="s-${EXTN_NAME}.mxt"
ZIP="./${EXTN_NAME}.zip"
EXTN_DIR="./source/${EXTN_NAME}"
USEFUL_SCRIPTS_DIR="./source/useful_scripts"
MXT="${EXTN_DIR}/${EXTN_NAME}.mxt"

JAVA_JAR="stuwaresoftsystems_commoncode.jar"
#JAVA_PACKAGE_NAME="stuwaresoftsystems/code/CommonCode"
JAVA_PACKAGE_NAME="StuWareSoftSystems_CommonCode"

FM_DIR="com/moneydance/modules/features/${EXTN_NAME}"
ZIP_COMMENT="StuWareSoftSystems: ${EXTN_NAME} Python Extension for Moneydance (by Stuart Beesley). Please see install-readme.txt"
ZIP_COMMENT2="StuWareSoftSystems: A collection of ${EXTN_NAME} for Moneydance."

if [ "${EXTN_NAME}" = "extension_tester" ]; then
  ZIP_COMMENT="Infinite Kind: ${EXTN_NAME} - Sample / demo Python Extension utilising script_info.dict actions for Moneydance - Please see readme.txt (documented by Stuart Beesley)"
fi

# Relies on "ant genkeys" and various jar files from within the Moneydance devkit

if [ "${REALLY_EXTENSION}" = "NO" ]; then

  if ! test -d "${EXTN_DIR}"; then
    echo "ERROR - directory ${EXTN_NAME}/ does not exist!"
    exit 1
  fi

else

  if ! test -f "${EXTN_DIR}/${EXTN_NAME}.py"; then
    echo "ERROR - ${EXTN_NAME}/${EXTN_NAME}.py does not exist!"
    exit 1
  fi

  if ! test -f "${EXTN_DIR}/script_info.dict"; then
    echo "ERROR - ${EXTN_NAME}/script_info.dict does not exist!"
    exit 1
  fi

  if ! test -f "${EXTN_DIR}/meta_info.dict"; then
    echo "ERROR - ${EXTN_NAME}/meta_info.dict does not exist!"
    exit 1
  fi

  if [ "${EXTN_NAME}" = "toolbox" ]; then
    if ! test -f "${EXTN_DIR}/toolbox_version_requirements.dict"; then
      echo "ERROR - ${EXTN_NAME}/toolbox_version_requirements.dict does not exist!"
      exit 1
    fi
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

############# Check and recompile own Java code if needed ##############################################################
if [ "${BUNDLE_JAVA}" = "YES" ]; then

  echo "Bundle Java requested... Checking java, and class files, and compiling if needed...."

  if ! test -f "./java_code/src/${JAVA_PACKAGE_NAME}.java"; then
    echo "ERROR - ./java_code/src/${JAVA_PACKAGE_NAME}.java does not exist!"
    exit 3
  fi

  if [ "./java_code/src/${JAVA_PACKAGE_NAME}.java" -nt "./java_code/compiled/${JAVA_PACKAGE_NAME}.class" ]; then
    echo "Detected that own java file needs compiling into a .class file..."
    javac -verbose -d "./java_code/compiled" "./java_code/src/${JAVA_PACKAGE_NAME}.java"
    if [ $? -ne 0 ]; then
      echo "*** javac compile failed..??"
      exit 3
    fi
  else
    echo "Own java class file does not need recompile.... skipping....."
  fi

  if ! test -f "./java_code/compiled/${JAVA_PACKAGE_NAME}.class"; then
    echo "ERROR - ./java_code/compiled/${JAVA_PACKAGE_NAME}.class does not exist!"
    exit 3
  fi

  # Create a stand-alone jar for stand-alone script usage....
  if [ "./java_code/compiled/${JAVA_PACKAGE_NAME}.class" -nt "./java_code/compiled/${JAVA_JAR}" ]; then
    echo "Detected that own jar file needs reassembling with the latest .class file..."
    jar -v -c -f "./java_code/compiled/${JAVA_JAR}" -C "./java_code/src" "${JAVA_PACKAGE_NAME}.java"
    if [ $? -ne 0 ]; then
      echo "*** jar utility failed creating own jar (with source file): ${JAVA_JAR} ..??"
      exit 3
    fi
    jar -v -u -f "./java_code/compiled/${JAVA_JAR}" -C "./java_code/compiled" "${JAVA_PACKAGE_NAME}.class"
    if [ $? -ne 0 ]; then
      echo "*** jar utility failed creating own jar (with class file): ${JAVA_JAR} ..??"
      exit 3
    fi
  else
    echo "Own java jar file does not need rebuilding.... skipping....."
  fi

  if ! test -f "./java_code/compiled/${JAVA_JAR}"; then
    echo "ERROR - ./java_code/compiled/${JAVA_JAR} does not exist!"
    exit 3
  fi

fi


############## START OF EXTENSION BUILD ################################################################################
rm -f "${MXT}"

if [ "${REALLY_EXTENSION}" = "NO" ]; then

  echo "Skipping extension build for ${EXTN_NAME}"

else

  if [ "${EXTN_NAME}" = "toolbox" ]; then
    echo "Copy extra scripts for Toolbox..."
    cp ${USEFUL_SCRIPTS_DIR}/ofx_*.py "${EXTN_DIR}"/.
    if [ $? -ne 0 ]; then
      echo "*** cp extra scripts ofx*.py failed??"
      exit 5
    fi
  fi

  echo "Checking / creating ${FM_DIR} dir if needed..."
  mkdir -v -p "${FM_DIR}"
  if [ $? -ne 0 ]; then
    echo "*** MKDIR ${FM_DIR} dir failed??"
    exit 6
  fi

  echo "Copy meta_info.dict..."
  cp "${EXTN_DIR}/meta_info.dict" "${FM_DIR}/meta_info.dict"
  if [ $? -ne 0 ]; then
    echo "*** cp meta_info.dict Failed??"
    exit 6
  fi

  echo "Zipping *.py into new mxt..."
  zip -j -z "${MXT}" "${EXTN_DIR}"/*.py <<<"${ZIP_COMMENT}"
  if [ $? -ne 0 ]; then
    echo zip -j -z "${MXT}" "${EXTN_DIR}/*.py"
    echo "*** zip *.py Failed??"
    exit 7
  fi

  echo "Zipping *.pyi stub files into mxt..."
  if test -f "${EXTN_DIR}"/*.pyi; then
    zip -j "${MXT}" "${EXTN_DIR}"/*.pyi
    if [ $? -ne 0 ]; then
      echo "*** zip *.pyi Failed??"
      exit 8
    fi
  else
    echo "No *.pyi stub file(s) to ZIP - skipping....."
  fi

  echo "Zipping PREVIEW MARKER file into mxt..."
  if test -f "${EXTN_DIR}"/_PREVIEW_BUILD_; then
    zip -j "${MXT}" "${EXTN_DIR}"/_PREVIEW_BUILD_
    if [ $? -ne 0 ]; then
      echo "*** zip _PREVIEW_BUILD_ Failed??"
      exit 8
    fi
  else
    echo "No PREVIEW MARKER file to ZIP - skipping....."
  fi

  echo "Zipping *.txt into mxt..."
  if test -f "${EXTN_DIR}"/*.txt; then
    zip -j "${MXT}" "${EXTN_DIR}"/*.txt
    if [ $? -ne 0 ]; then
      echo "*** zip *.txt Failed??"
      exit 8
    fi
  else
    echo "No *.txt file(s) to ZIP - skipping....."
  fi

  if [ "${EXTN_NAME}" != "extension_tester" ]; then
    echo "Zipping install-readme.txt into mxt..."
    zip -j "${MXT}" "./source/install-readme.txt"
    if [ $? -ne 0 ]; then
      echo "*** zip install-readme.txt Failed??"
      exit 9
    fi
  fi

  echo "Zipping script_info.dict into mxt..."
  zip -j "${MXT}" "./source/${EXTN_NAME}/script_info.dict"
  if [ $? -ne 0 ]; then
    echo "*** zip script_info.dict Failed??"
    exit 10
  fi

  echo "Zipping meta_info.dict into mxt..."
  zip -m "${MXT}" "${FM_DIR}/meta_info.dict"
  if [ $? -ne 0 ]; then
    echo "*** zip meta_info.dict Failed??"
    exit 11
  fi

  if [ "${BUNDLE_JAVA}" = "YES" ]; then
    echo "Bundling own java source code, and class(es) into the extension mxt(jar) file..."

    jar -v -u -f "${MXT}" -C "./java_code/src/" "${JAVA_PACKAGE_NAME}.java"
    if [ $? -ne 0 ]; then
      echo "*** jar utility failed bundling own Java source code..??"
      exit 12
    fi

    jar -v -u -f "${MXT}" -C "./java_code/compiled" "${JAVA_PACKAGE_NAME}.class"
    if [ $? -ne 0 ]; then
      echo "*** jar utility failed bundling own Java code/class file..??"
      exit 12
    fi
  fi

  echo "copying extadmin.jar..."
  cp "./moneydance-devkit-5.1 2/lib/extadmin.jar" .
  if [ $? -ne 0 ]; then
    echo "*** cp extadmin.jar Failed??"
    exit 13
  fi

  echo "copying moneydance-dev.jar..."
  cp "./moneydance-devkit-5.1 2/lib/moneydance-dev.jar" .
  if [ $? -ne 0 ]; then
    echo "*** cp moneydance-dev.jar Failed??"
    exit 14
  fi

  echo "copying priv_key..."
  cp "./moneydance-devkit-5.1 2/src/priv_key" .
  if [ $? -ne 0 ]; then
    echo "*** cp priv_key Failed??"
    exit 15
  fi

  echo "copying pub_key..."
  cp "./moneydance-devkit-5.1 2/src/pub_key" .
  if [ $? -ne 0 ]; then
    echo "*** cp pub_key Failed??"
    exit 16
  fi

  if [ "${EXTN_NAME}" = "toolbox" ]; then
    echo "Remove extra scripts compiked into Toolbox..."
    rm "${EXTN_DIR}"/ofx_*.py
    if [ $? -ne 0 ]; then
      echo "*** rm extra scripts ofx*.py failed??"
      exit 5
    fi
  fi

  echo "Removing old signed mxts if they existed..."
  rm -f "${EXTN_DIR}/${sMXT}"
  rm -f "./${sMXT}"

  echo "Executing java mxt signing routines..."
  java -cp extadmin.jar:moneydance-dev.jar com.moneydance.admin.KeyAdmin signextjar priv_key private_key_id "${EXTN_NAME}" "${MXT}" <./build/extension_keyfile.
  if [ $? -ne 0 ]; then
    echo java -cp extadmin.jar:moneydance-dev.jar com.moneydance.admin.KeyAdmin signextjar priv_key private_key_id "${EXTN_NAME}" "${MXT}"
    echo "*** Java self-signing of mxt package Failed??"
    exit 17
  fi

  if ! test -f "${sMXT}"; then
    echo "ERROR - self-signed ${sMXT} does not exist after java signing?"
    exit 18
  else
    echo "Adding comments to signed mxt..."
    zip -z "${sMXT}" <<<"${ZIP_COMMENT}"
    if [ $? -ne 0 ]; then
      echo "*** zip add comments to self-signed ${sMXT} Failed??"
      exit 19
    fi
  fi

  echo "Removing priv_key, pub_key, extadmin.jar, moneydance-dev.jar"
  rm priv_key
  rm pub_key
  rm extadmin.jar
  rm moneydance-dev.jar

  echo "Listing mxt contents..."
  ls -l "${MXT}"

  echo "Listing signed mxt contents..."
  ls -l "${sMXT}"

  echo "Removing non-signed mxt..."
  rm "${MXT}"

  echo "Moving signed mxt to source directory..."
  mv "${sMXT}" "${MXT}"
  if [ $? -ne 0 ]; then
    echo "*** mv of self-signed ${sMXT} to ${MXT} Failed??"
    exit 20
  fi

  if test -f "${MXT}"; then
    echo "Listing signed mxt contents..."
    ls -l "${MXT}"
    unzip -l "${MXT}"
    echo ===================
    echo "FILE ${MXT} has been built..."
  else
    echo "@@@@@@@@@@@@@@@@@"
    echo "PROBLEM CREATING ${MXT} ..."
    exit 21
  fi

  echo "Removing temporary build directories (com/...)... should be empty...."
  rm -r com

fi

echo "@ Building final ZIP file for publication..."

echo "Removing old zip file (if it exists)..."
rm -f "${ZIP}"

ZIP_THIS="./source/install-readme.txt"
if [ "${EXTN_NAME}" = "extension_tester" ]; then
  ZIP_THIS="${EXTN_DIR}/readme.txt"
fi

echo "Creating zip file with ${ZIP_THIS}..."
zip -j -z "${ZIP}" "${ZIP_THIS}" <<<"${ZIP_COMMENT}"
if [ $? -ne 0 ]; then
  echo "*** final zip of package to ${ZIP} Failed??"
  exit 22
fi

if [ "${REALLY_EXTENSION}" = "NO" ]; then

  echo "Adding *.py to zip file..."
  zip -j -c "${ZIP}" "${EXTN_DIR}"/*.py <<<"${ZIP_COMMENT2}"
  if [ $? -ne 0 ]; then
    echo "*** final zip of ${EXTN_NAME} package *.py Failed??"
    exit 23
  fi

  if test -f "${EXTN_DIR}"/*.pyi; then
    echo "Adding *.pyi stub to zip file..."
    zip -j "${ZIP}" "${EXTN_DIR}"/*.pyi
    if [ $? -ne 0 ]; then
      echo "*** final zip of ${EXTN_NAME} package *.pyi Failed??"
      exit 24
    fi
  fi

  echo "Adding *.pdf to zip file..."
  zip -j "${ZIP}" "${EXTN_DIR}"/*.pdf
  if [ $? -ne 0 ]; then
    echo "*** final zip of ${EXTN_NAME} package *.pdf Failed??"
    exit 25
  fi

else

  echo "Adding signed mxt file into zip file..."
  zip -j -c "${ZIP}" "${MXT}" <<<"${ZIP_COMMENT}"
  if [ $? -ne 0 ]; then
    echo "*** final zip of mxt into zip package Failed??"
    exit 26
  fi

  if [ "${RESTRICT_SCRIPT}" != "YES" ]; then
    echo "adding *.py file(s) into zip file..."
    zip -j "${ZIP}" "${EXTN_DIR}"/*.py
    if [ $? -ne 0 ]; then
      echo "*** final zip of *.py script(s) into zip package Failed??"
      exit 27
    fi

    if test -f "${EXTN_DIR}"/*.pyi; then
      echo "Adding *.pyi stub to zip file..."
      zip -j "${ZIP}" "${EXTN_DIR}"/*.pyi
      if [ $? -ne 0 ]; then
        echo "*** final zip of ${EXTN_NAME} package *.pyi Failed??"
        exit 28
      fi
    fi

  else
    echo "@@ Not including *.py file(s) for ${EXTN_NAME} package...."
  fi

  if [ "${PUBLISH_ALL_FILES}" = "YES" ]; then
    echo "adding *.dict file(s) too into zip file..."
    zip -j "${ZIP}" "${EXTN_DIR}"/*.dict
    if [ $? -ne 0 ]; then
      echo "*** final zip of *.dict script(s) into zip package Failed??"
      exit 29
    fi
  else
    echo "@@ Not including *.dict file(s) for ${EXTN_NAME} package...."
  fi

fi

if [ "${EXTN_NAME}" != "extension_tester" ]; then
  if test -f "${EXTN_DIR}"/*.txt; then
    echo "Adding *.txt files into zip file..."
    zip -j "${ZIP}" "${EXTN_DIR}"/*.txt
    if [ $? -ne 0 ]; then
      echo "*** final zip of *.txt file(s) into zip package Failed??"
      exit 30
    fi
  else
    echo "No help *.txt file(s) to ZIP - skipping....."
  fi
fi

if test -f "${ZIP}"; then
  echo "Listing zip file contents..."
  ls -l "${ZIP}"
  unzip -l "${ZIP}"
  echo ===================
  echo "DISTRIBUTION FILE ${ZIP} has been built..."
else
  echo "@@@@@@@@@@@@@@@@@"
  echo "PROBLEM CREATING FINAL DISTRIBUTION ${ZIP} !"
  exit 31
fi
