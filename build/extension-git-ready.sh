#!/bin/sh

clear

echo
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo @@@@ GIT-READY RUNNING - I WILL FETCH AND THEN RESET YOUR LOCAL HEAD @@@
echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo

PUSHDIR="../MoneydanceOpen"
SOURCEDIR="../My Python Scripts"

if ! test -f "./build/extension-build.sh"; then
    echo "@@ PLEASE RUN FROM THE PROJECT's ROOT directory! @@"
    exit 1
fi

if ! test -d "$PUSHDIR"; then
    echo "@@ $PUSHDIR directory missing? @@"
    exit 1
fi

cd "$PUSHDIR" || exit
echo "Now in directory..:"
pwd
git status
# shellcheck disable=SC2162
read -p "Press any key to resume next >> git fetch --all ..."

git fetch --all

# shellcheck disable=SC2162
read -p "Press any key to resume next >> git reset --hard origin/main ..."

git reset --hard origin/main

git status

cd "$SOURCEDIR" || exit
echo "Now in directory..:"
pwd
# shellcheck disable=SC2162
read -p "Press any key to resume next..."


#echo @@@ module: $MODULE pushed over to $PUSHDIR