#!/bin/sh

###############################################################################
# Author:   Stuart Beesley - StuWareSoftSystems 2021-2023
###############################################################################

MODULE_LIST=("toolbox" "extract_data" "useful_scripts" "list_future_reminders" "net_account_balances" "extension_tester" "accounts_categories_mega_search_window" "security_performance_graph")

clear

if ! test -f "./build/extension-build.sh"; then
    echo "@@ PLEASE RUN FROM THE PROJECT's ROOT directory! @@"
    exit 1
fi

for THE_MODULE in "${MODULE_LIST[@]}"; do
    ./build/extension-push.sh "${THE_MODULE}"
    if [ $? -ne 0 ]; then
      echo "*** PUSH of ${THE_MODULE} Failed??"
      read -p "Press any key to resume next build..."
    fi
done
