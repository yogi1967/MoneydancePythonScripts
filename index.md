## Welcome to my site for Moneydance Extensions and Scripts written in Python

_Author: Stuart Beesley - StuWareSoftSystems_

_NOTE: I AM JUST A USER - I HAVE NO AFFILIATION WITH MONEYDANCE! (but I do use all my scripts on my own live dataset...)_

**DISCLAIMER**: ALWAYS BACKUP YOUR DATA BEFORE MAKING ANY CHANGES - The author cannot accept any responsibility from the use of these scripts

Moneydance allows you to run Python scripts and access its functions via their API.
This allows you to perform all sorts of 'wonderful' things based on your own financial data.

Python is actual Jython 2.7 and accesses the Moneydance Java codebase.

My scripts and extensions are identical. The extension version(s) are simply a 'packaged' script version. 
InfiniteKind (the creators of Moneydance) have now signed all my Extensions. NOTE: The signed versions may be a few builds behind my latest versions.
If you require a signed version, then download links are at the bottom of this page...

The Extensions will only run properly on Moneydance version 2021.1 build 3056 onwards... The scripts don't have this requirement.
NOTE: You may need to download the MD [preview version](https://infinitekind.com/preview)
(If you have installed the extension, but nothing happens, then check your MD version)
  
Click a link below to download a ZIP file. The ZIP file contains both the Extension (if available) and Script version for you to choose from....
- Extensions have a file extension of *.mxt
- Scripts have a file extension of *.py

**To run Extensions:**
1) Install the Extension. Load Moneydance, Menu>Extensions>add from file>choose <extension_name>.mxt file
2) Accept the warning that the extension is unsigned / missing (this simply means that Moneydance have not signed / verified my extension). Click Install Extension.
3) Once its installed, restart Moneydance.
4) From now on, just click Menu>Extensions and the name of the Extension

**To run Scripts:**
1) Load Moneydance. Menu>Window>Show Moneybot Console
2) Open Script>choose <scriptname>.py file
3) Click RUN (and not run snippet)
4) That's it.... Repeat these steps each time.

_NOTE: On a Mac, in Moneydance versions older than build 3051, you might see one or two popup System Warning messages saying something like: “jffinnnnnnnnnnnnnnnnnnnn.dylib” cannot be opened because the developer cannot be verified. macOS cannot verify that this app is free from malware. **These are irrelevant and harmless messages** Just click any option (Cancel, Ignore, Trash, Bin), it doesn't matter. The script will run un-affected. It's Mac Gatekeeper complaining about a dynamic cache file being created. The Moneydance developer (IK) is aware of this and is trying to build a fix. It happens with all Python scripts._

### Extension only format (contains only *.mxt file) - Very latest (unsigned) build
- <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/toolbox.zip">**Toolbox**: View Moneydance settings, diagnostics, fix issues, change settings and much more...
NOTE: Toolbox has the ability to update your dataset/settings in Advanced and Hacker mode(s). In the default Basic mode it's READONLY and VERY useful!

### Extension and Scripts formats (*.mxt and *.py format) - Very latest (unsigned) builds
-  <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/extract_data.zip">**extract_data**: Extract data to screen/csv. Options include: Investments, Reminders, Account txns, Investment txns, Currency History; attachments. This is a consolidation of all prior extract scripts in one, including: 
- stockglance2020                       View summary of Securities/Stocks on screen, total by Security, export to csv
- extract_reminders_csv                 View reminders on screen, edit if required, extract all to csv
- extract_currency_history_csv          Extract currency history to csv
- extract_investment_transactions_csv   Extract investment transactions to csv
- extract_account_registers_csv         Extract Account Register(s) to csv along with any attachments

-  <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/list_future_reminders.zip">**list_future_reminders**: Lists your future dated reminders to screen, and allows you to select how far forward to look.

### Signed Versions (hosted by Moneydance at InfiniteKind)
- <a href="https://infinitekind.com/app/md/extensions/toolbox.mxt">Toolbox (signed) (build: 1028 - 8th March 2021)
- <a href="https://infinitekind.com/app/md/extensions/extract_data.mxt">extract_data (signed) (build: 1005 - 8th March 2021)
- <a href="https://infinitekind.com/app/md/extensions/list_future_reminders.mxt">list_future_reminders (signed) (build: 1004 - 8th March 2021)

### Other useful ad-hoc scripts (*.py format only) - Very latest code versions
-  <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/useful_scripts.zip">**Useful_Scripts**: A zip collection of ad-hoc scripts that can be run individually. Including:
  - calculate_moneydance_objs_and_datasetsize.py: Analyse your Moneydance dataset, report on objects, internal file size(s), and list other known datasets...
  - extract_all_attachments.py: extract all your attachments out of Moneydance to a folder of your choice
  - orphan_attachments.py: scans your attachments and detects if any are orphaned (and other related errors)
  - demo_account_currency_rates.py: demo script for beginner coders with some simple Moneydance API calls etc
  - demo_calling_import_functions.py: demo script to show how to call deep API importFile() method and bypass UI popups (for headless running)
  - ofx_create_new_usaa_bank_custom_profile.py: script that creates a new custom USAA bank logon profile so that it can connect within Moneydance


### Source Code sites - you can freely read / review all my code
<a href="https://github.com/yogi1967/MoneydancePythonScripts">**Author's code site**: https://github.com/yogi1967/MoneydancePythonScripts
<BR><BR>
<a href="https://github.com/TheInfiniteKind/moneydance_open/tree/main/python_scripts/">**Moneydance's site for code**: https://github.com/TheInfiniteKind/moneydance_open/tree/main/python_scripts/
