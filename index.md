## Welcome to my site for Moneydance Extensions and Scripts written in Python


_Author: Stuart Beesley - StuWareSoftSystems_

_NOTE: I AM JUST A USER - I HAVE NO AFFILIATION WITH MONEYDANCE! (but I do use all my scripts on my own live dataset...)_

**DISCLAIMER**: ALWAYS BACKUP YOUR DATA BEFORE MAKING ANY CHANGES - The author cannot accept any responsibility from the use of these scripts

Moneydance allows you to run Python scripts and access its functions via their API.
This allows you to perform all sorts of 'wonderful' things based on your own financial data.

Python is actual Jython 2.7 and accesses the Moneydance Java codebase.

My scripts and extensions are identical. The extension version(s) are simply a 'packaged' script version. 
InfiniteKind (the creators of Moneydance) have now signed my Extensions.
NOTE: The signed versions hosted by IK/MD may be a few builds behind my latest versions.
If you require a signed version, then download links are at the bottom of this page (these also appear in the Extensions>Manage Extensions menu))

The Extensions will only run properly on Moneydance version 2021.1 (build 3056 onwards)...
The minimum version to run as standalone scripts is 2019.4 (build 1904)...
_(If you have installed the extension, but nothing happens, then check your MD version/build)_


**NOTE: All extensions listed below (except marked with ^^) are listed within the Moneydance Manage Extensions menu - Check there first for updates**

**ANY NEWER VERSIONS LISTED HERE SHOULD BE CONSIDERED PREVIEW (LATEST) VERSIONS (FULLY WORKING, WITH ENHANCEMENTS, FIXES, AND PREVIEW FEATURES)**

Click a link below to download a ZIP file. The ZIP file contains both the Extension (if available) and Script version for you to choose from....
- Extensions have a file extension of *.mxt
- Scripts have a file extension of *.py

**To install/run Extensions:**

1) Launch Moneydance

2) Double-click the .mxt file (this may not work if you do not have .mxt extensions associated with Moneydance)
  - or drag and drop the .mxt file onto the Moneydance left side bar;
  - or Extensions, Manage Extensions, add from file to install.
  - or Menu>Extensions>add from file>choose \<extension_name\>.mxt file, then click open/install;
  - (Note: The .mxt file must not be renamed. Sometimes downloading/unzipping adds a number to the end of the filename)

3) Accept any warning(s) that the extension is unsigned (this simply means that Moneydance have not signed / verified my extension). Click Install Extension.

4) Once its installed, restart Moneydance.

5) From now on, just click Menu>Extensions and the name of the Extension

**To run Scripts:**

1) Load Moneydance. Menu>Window>Show Moneybot Console

2) Open Script>choose \<scriptname\>.py file

3) Click RUN (and not run snippet)

4) That's it.... Repeat these steps each time.


### Extension ONLY format (contains only *.mxt file) - Very latest PREVIEW (unsigned) build
- <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/toolbox.zip">**Toolbox**: View Moneydance settings, diagnostics, fix issues, change settings and much more...
NOTE: Toolbox has the ability to update your dataset/settings in Update and Advanced mode(s). In the default Basic mode it's READONLY and VERY useful!
NOTE: Also installs two new Extensions Menu options:
  - Move Investment Transactions: Allows you to move the txns you have selected in the visible Investment Register. 
  - Total Selected Transactions:  Will total up the txns you have selected in the visible register.

    <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/source/toolbox/toolbox_readme.txt">(View the Toolbox HELPFILE)


- <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/net_account_balances.zip">**Custom Balances(Net Account Balances)**: Puts a small 'widget' on the Summary Page (Home Page). Displays the total of selected account balances. Now multi-row, display currency, and you can select Accounts/Categories/Securities per row.
NOTE: It's also a demo of how to create a true runtime Python extension and a HomePageView (Summary Page) widget


### Extension (and Scripts formats) (*.mxt and *.py format) - Very latest PREVIEW (unsigned) builds
-  <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/extract_data.zip">**Extract Data**: Extract data to screen/csv. Options include: Investments, Reminders, Account txns, Investment txns, Currency History; attachments. This is a consolidation of various extracts in one, including: 
    - stockglance2020                       View summary of Securities/Stocks on screen, total by Security, export to csv
    - extract_reminders_csv                 View reminders on screen, edit if required, extract all to csv
    - extract_currency_history_csv          Extract currency history to csv
    - extract_investment_transactions_csv   Extract investment transactions to csv
    - extract_account_registers_csv         Extract Account Register(s) to csv along with any attachments

-  <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/accounts_categories_mega_search_window.zip">**^^Accounts & Categories Mega Search Window**: Clones MD Menu> Tools>Accounts/Categories (combined) and adds a Quick Search box/capability.

-  <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/list_future_reminders.zip">**List Future Reminders**: Lists your future dated reminders to screen, and allows you to select how far forward to look.

-  <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/security_performance_graph.zip">**Security Performance Graph**: Graphs selected securities, calculating relative price performance as a percentage. Popup table and other useful info too.

-  <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/extension_tester.zip">**extension_tester**: Demo extension/scripts for coders wanting to build Moneydance Python extensions.

### Signed Versions (hosted by Moneydance at InfiniteKind - These builds appear in the Extensions/Manage Extensions... menu)
- <a href="https://infinitekind.com/app/md/extensions/toolbox.mxt">Toolbox (signed) (build: 1055 - 22nd November 2022) (update logfile; sidebar feature; improved launch code;Toggle active/inactive investment securities; diagnostics: show md+ last digits using Plaid .getMask())
- <a href="https://infinitekind.com/app/md/extensions/extract_data.mxt">Extract Data (signed) (build: 1025 - 22nd November 2022) (Tweaks/fixes; Add date range selector/filter to extract_investment_registers; SG2020 cost_basis conversion fix)
- <a href="https://infinitekind.com/app/md/extensions/list_future_reminders.mxt">List Future Reminders (signed) (build: 1018 - 22nd November 2022) (Added right-click popup to allow deletion of Reminder...; Search field now grabs focus too..)
- <a href="https://infinitekind.com/app/md/extensions/net_account_balances.mxt">Custom Balances (net_account_balances) (signed) (build: 1016 - 22nd November 2022) (fix startup GUI hang; support Indian numbering system; row separators; allow auto hiding of rows)

### Signed Versions (hosted on this site - i.e. NOT InfiniteKind's site - may be newer than appear (or not available) in Moneydance's Extensions menu)
- <a href="https://github.com/yogi1967/MoneydancePythonScripts/tree/master/signed_builds">Directory listing of all current and prior signed builds
- <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/signed_builds/accounts_categories_mega_search_window.mxt">Accounts Categories Mega Search Window (signed) (build: 1005 - 17th November 2022) (enable expand all, search collapsed; CMD-T; tweaks)
- <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/signed_builds/security_performance_graph.mxt">Security Performance Graph (signed) (build: 1002 - 17th November 2022) - (Initial preview release; plus tweaks)

### Other useful ad-hoc scripts (*.py format only) - Very latest code versions
<a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/useful_scripts.zip">**Useful_Scripts**: A zip collection of ad-hoc scripts that can be run individually. Including:
  - calculate_moneydance_objs_and_datasetsize.py: Analyse your Moneydance dataset, report on objects, internal file size(s), and list other known datasets...
  - extract_all_attachments.py: extract all your attachments out of Moneydance to a folder of your choice
  - orphan_attachments.py: scans your attachments and detects if any are orphaned (and other related errors)
  - demo_account_currency_rates.py: demo script for beginner coders with some simple Moneydance API calls etc
  - demo_calling_import_functions.py: demo script to show how to call deep API importFile() method and bypass UI popups (for headless running)
  - ofx_create_new_usaa_bank_custom_profile.py: script that creates a new custom USAA bank logon profile so that it can connect within Moneydance (also built into Toolbox)
  - ofx_populate_multiple_userids.py: script that allows you to modify a working OFX profile and populate with multiple UserIDs (also built into Toolbox)
  - import_categories.py: script that allows you to import from a CSV file to create new Categories


### My Python Extension and coding tips:
-  <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/source/extension_tester/readme.txt">**Extension tips**: A readme.txt file that contains my tips on creating Python extensions and some coding tips....
-  <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/launch-moneydance.sh">**Moneydance Mac Launch Shell Script**: A MacOS shell script that launches Moneydance replicating the standard App launch sequence.... But without Apple sandboxing restrictions... You can also therefore change much of the underlying 'environment' and java libraries...
-  <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/launch-moneydance.bat">**Moneydance basic Windows Launch Shell Script**: A basic Windows batch file that launches Moneydance - update with the relevant bits you need from the more complete Mac sh version...
-  <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/launch-moneydance.scpt">**Moneydance Mac Apple Script Launch Script**: A basic Applescript to launch Moneydance...


### Experimental / advanced:
It's possible to load Moneydance components externally. _This would not be supported by IK and you do so at your own risk._

As of MD2021.2(3088) you can set an environment variable 'md_passphrase=' or 'md_passphrase_\<lowercase\_filename\>' and this will bypass the popup 'Enter your password' prompt.
This means that the headless methods, to access MD data externally will work much more seamlessly. There are examples below on how to do this (with 'environment_passphrase' in filename):_

Method 1: Using Jython (for true Java integration) (with a launch script to set up the JVM properly) - See folder contents:
-  <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/external-access-jython">**external-access-jython**: Folder containing Jython launch script, and Jython examples accessing Moneydance externally....

Method 2: Using Python and JPype (sets up the JVM as part of the script) - See folder contents:
-  <a href="https://github.com/yogi1967/MoneydancePythonScripts/raw/master/external-access-python-jpype">**open-mdheadless-jpype**: Folder containing Python script using JPype to access Moneydance externally....



### Source Code sites - you can freely read / review all my code
<a href="https://github.com/yogi1967/MoneydancePythonScripts">**Author's code site**: https://github.com/yogi1967/MoneydancePythonScripts
<BR><BR>
<a href="https://github.com/TheInfiniteKind/moneydance_open/tree/main/python_scripts/">**Moneydance's site for code**: https://github.com/TheInfiniteKind/moneydance_open/tree/main/python_scripts/

***
_If you like my tools you can donate to support my work via PayPal (completely optional)_<BR>
<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&amp;hosted_button_id=M2NQXMRTWUKBQ" rel="nofollow"><img src="https://www.paypalobjects.com/en_GB/i/btn/btn_donate_LG.gif" alt="Donate" style="max-width: 100%;"></a>
<BR>

_Or perhaps just buy me a "beer" (also via PayPal)_<BR>
<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&amp;hosted_button_id=G2MBHPGLQJXLU" rel="nofollow"><img src="https://pics.paypal.com/00/s/Mzc0NDYyNzQtMGZlYS00NzNjLWI2MGItNjRmZDcyMGViNTY0/file.PNG" alt="Donate" style="max-width: 100%;"></a>


_(site last updated 24th November 2022)_
