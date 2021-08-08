#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Example script accessing moneydance data in 'headless' mode using jpype

NOTE:  Works with an encryption passphrase from MD2021.2(3088) onwards as this allows you to set the passphrase into
       an environment variable: md_passphrase=  or  md_passphrase_[filename in lowercase format]=

DISCLAIMER: Always BACKUP FIRST
            This is a demo program only....!
            Do not use when Moneydance is open
            I would suggest you stay READONLY - do not update data
            USE AT YOUR OWN RISK!

More information on jpype here: https://jpype.readthedocs.io/en/latest/
note that project jar files are from MD Preview Version

###############################################################################
# MIT License
#
# Copyright (c) 2021 Stuart Beesley
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################

Original concept & credits - Dale Furrow: https://github.com/dkfurrow/md_python_headless_demo

MODIFICATIONS: Stuart Beesley - StuWareSoftSystems 2021 - https://yogi1967.github.io/MoneydancePythonScripts/

Help and credits: hleofxquotes...

INSTRUCTIONS:
- Get Python3 working (outside of Moneydance)
- Read the JPype instructions at the website link provided: https://jpype.readthedocs.io/en/latest/
- Download / pip install the correct JPype for your platform
- extract the moneydance.jar and mdpython.jar files into a directory of your choosing

NOTE:
- This is a basic script to get access to your Moneydance data externally and allows you to open with a user set passphrase
- See Dale Furrow's scripts 1-5 for further examples of automation.
"""

import sys                                                                                                              # noqa

################### `set these variables ##########################################
mdDataFolder = "/Users/xxx/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Documents/XXX.moneydance"
MD_PATH = "../Moneydance_jars/"       # include moneydance.jar and mdpython.jar
################### `set these variables ##########################################

# from datetime import datetime, date
import os

# import jpype
import jpype.imports
from jpype.types import *                                                                                               # noqa

_ENV_PASSPHRASE = "md_passphrase"

def findEnvironmentPassphrases():
    theList = []
    for _k, _v in os.environ.items():
        if _k.startswith(_ENV_PASSPHRASE):
            theList.append([_k,_v])
    return theList


envs = findEnvironmentPassphrases()
if envs:
    print("Current passphrase environment variables set..:")
    for k, v in envs: print("Key:%s Passphrase: %s" %(k,v))
    print()
else:
    print("No passphrases detected in environment\n")

# get oriented, print current working directory (script is based on working directory as project root)
print("Working Directory: {0}".format(os.getcwd()))

###################################################################
# Launch the JVM

listFiles = []
for f in os.listdir(MD_PATH):
    if f.lower().endswith("jar"):
        if f.startswith("moneydance") and f != "moneydance.jar": continue
        listFiles.append(MD_PATH+f)
join_jars = ":".join(listFiles)
print("join_jars\n%s" %(join_jars))

my_user_path = "/Users/xxx"

# Set your JAVA_HOME
# On Mac, output of '/usr/libexec/java_home --verbose' can help
JAVA_HOME="%s/Library/Java/JavaVirtualMachines/adopt-openjdk-15.0.2/Contents/Home" %(my_user_path)

# JavaFX directory
javafx="%s/Documents/Moneydance/My Python Scripts/javafx-sdk-15.0.1/lib" %(my_user_path)
modules="javafx.swing,javafx.media,javafx.web,javafx.fxml"

# set to "" for standard app install name (I add the version and build to the app name when installing)
md_version=" 2021.2 (3090)"

# Where are the MD jar files
md_jars="/Applications/Moneydance${md_version}.app/Contents/Java"
md_icon="/Applications/Moneydance${md_version}.app/Contents/Resources/desktop_icon.icns"

# Set to None for no sandbox (however, with enabled=true is not really a sandbox)
#use_sandbox=None
use_sandbox="-DSandboxEnabled=true"

# NOTE: I set '-Dinstall4j.exeDir=x' to help my Toolbox extension - this is not needed

console_file="%s/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Library/Application Support/Moneydance/errlog.txt" %(my_user_path)

java_args = []
# java_args.append("-Xdock:icon=%s" %(md_icon))
# java_args.append("--module-path %s" %(javafx))
# java_args.append("--add-modules=%s" %(modules))
java_args.append("-Dapple.laf.useScreenMenuBar=true")
java_args.append("-Dcom.apple.macos.use-file-dialog-packages=true")
java_args.append("-Dcom.apple.macos.useScreenMenuBar=true")
java_args.append("-Dcom.apple.mrj.application.apple.menu.about.name=Moneydance")
java_args.append("-Dapple.awt.application.name=Moneydance")
java_args.append("-Dcom.apple.smallTabs=true")
java_args.append("-Dapple.awt.application.appearance=system")
java_args.append("-Dfile.encoding=UTF-8")
java_args.append("-DUserHome=%s" %(my_user_path))
if use_sandbox:
    java_args.append("%s" %(use_sandbox))
java_args.append("-Dinstall4j.exeDir=%s" %(md_jars))
# java_args.append("-Duser.dir=%s/Library/Containers/com.infinitekind.MoneydanceOSX/Data" %(my_user_path))
java_args.append("-Duser.home=%s/Library/Containers/com.infinitekind.MoneydanceOSX/Data" %(my_user_path))
java_args.append("-DApplicationSupportDirectory=%s/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Library/Application Support" %(my_user_path))
java_args.append("-DLibraryDirectory=%s/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Library" %(my_user_path))
java_args.append("-DDownloadsDirectory=%s/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Downloads" %(my_user_path))
java_args.append("-DDesktopDirectory=%s/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Desktop" %(my_user_path))
java_args.append("-DPicturesDirectory=%s/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Pictures" %(my_user_path))
java_args.append("-DDocumentsDirectory=%s/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Documents" %(my_user_path))
java_args.append("-DCachesDirectory=%s/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Library/Caches" %(my_user_path))
java_args.append("-DSharedPublicDirectory=%s/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Public" %(my_user_path))
java_args.append("-DMoviesDirectory=%s/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Movies" %(my_user_path))
java_args.append("-DDownloadsDirectory=%s/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Downloads" %(my_user_path))
java_args.append("-DApplicationDirectory=%s/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Applications" %(my_user_path))
java_args.append("-DMusicDirectory=%s/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Music" %(my_user_path))
java_args.append("-DAutosavedInformationDirectory=%s/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Library/Autosave Information" %(my_user_path))
java_args.append("-Xmx2G")
java_args.append("-Ddummyarg1=arg1")
java_args.append("-Ddummyarg2=arg2")

print("Java arguments:")
for a in java_args: print(a)

print("Starting JVM...")
# noinspection PyUnresolvedReferences
jpype.startJVM(classpath=[join_jars], *java_args)


print("Importing necessary Moneydance Classes...")
from com.moneydance.apps.md.controller import Main

print("Importing useful Moneydance Classes...")
from com.moneydance.apps.md.controller import AccountBookWrapper
from com.infinitekind.moneydance.model import ParentTxn
from com.infinitekind.moneydance.model import CurrencyType
# from com.infinitekind.moneydance.model import AccountBook
# from com.infinitekind.moneydance.model import Account
# from com.infinitekind.moneydance.model import TxnSet
# from com.infinitekind.moneydance.model import AbstractTxn
# from com.infinitekind.moneydance.model import SplitTxn
# from com.infinitekind.moneydance.model import TxnUtil
# from com.infinitekind.moneydance.model import CurrencySnapshot
# from com.infinitekind.moneydance.model import CurrencyTable
# from com.infinitekind.moneydance.model import CurrencyUtil
# from com.infinitekind.moneydance.model import MoneydanceSyncableItem

print("Importing useful Java Classes...")
from java.io import File

print("prove moneydance data file exists, load it into java File object")
print("Moneydance Data File exists? {0}, in {1}".format(os.path.exists(mdDataFolder), mdDataFolder))
if not os.path.exists(mdDataFolder):
    raise Exception("ERROR - Datafile does NOT exist... Aborting...")


mdFileJava = File(mdDataFolder)
last_modded_long = mdFileJava.lastModified()  # type is java class 'JLong'
print("data folder last modified: %s" %(last_modded_long))


###################################################################
# Fire up Moneydance and initialize key stuff...
mdMain = Main()
mdMain.DEBUG = True
mdMain.initializeApp()
# mdMain.startApplication()

###################################################################
# Now get the 'wrapper' etc
print("@@@now get AccountBookWrapper, accountBook, and rootAccount")
wrapper = AccountBookWrapper.wrapperForFolder(mdFileJava)  # type: AccountBookWrapper
mdMain.setCurrentBook(wrapper)

accountBook = wrapper.getBook()
print(accountBook)

###################################################################
# Away we go, accessing the data...

root_account = accountBook.getRootAccount()

print("Verify by printing useful information about these elements...")
print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
print("The name of the rootAccount is {0}".format(root_account.getAccountName()))
print("The id of the rootAccount is {0}".format(root_account.getUUID()))
print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

txnSet = accountBook.getTransactionSet()
transactionCount = int(txnSet.getTransactionCount())
print("There are {0:d} transactions in the AccountBook".format(transactionCount))

accountCount = int(root_account.getSubAccounts().size())
print("There are {0:d} sub-accounts in the rootAccount".format(accountCount))

print("printing details on last 10 parent transactions...")
parent_txns = [x for x in txnSet.iterableTxns() if isinstance(x, ParentTxn)]
ii=0
for txn in parent_txns:
    ii+=1
    if ii > 10: break
    print("transaction date {0:d} account {1} description: {2} for amount {3}"
          .format(int(txn.getDateInt()), txn.getAccount().getAccountName(), txn.getDescription(),
                  txn.getAccount().getCurrencyType().formatFancy(txn.getValue(), '.')))


print("Printing Information on Securities...")
currencies = accountBook.getCurrencies().getAllCurrencies()
# noinspection PyUnresolvedReferences
securities = [x for x in currencies if x.getCurrencyType() == CurrencyType.Type.SECURITY]

ii=0
for security in securities:
    try:
        ii+=1
        if ii > 10: break
        last_snapshot = [x for x in security.getSnapshots()][-1]
        price = 1 / float(last_snapshot.getRate())
        dateInt = last_snapshot.getDateInt()
        ticker = security.getTickerSymbol()
        print("Name: {0} Ticker:{1} last snapshot: {2:d} last price {3:.3f}"
              .format(security.getName(), ticker,dateInt, price))
    except:
        pass


print("Finished peeking at data....")
# theMain.showURL("invokeAndQuitURI")

print("Calling saveCurrentAccount()")
mdMain.saveCurrentAccount()

print("Calling shutdown()")
mdMain.shutdown()

print("Shutting down the JVM...")
# noinspection PyUnresolvedReferences
jpype.shutdownJVM()

print("@@@@  END @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
