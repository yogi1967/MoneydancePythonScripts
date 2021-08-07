#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Example script accessing moneydance data in 'headless' mode using jpython

NOTE: Superceded by open_mdheadless_external_jython_with_environment_passphrase.py when using MD2021.2(3088) onwards....

Usage: ./launch-moneydance-via-jython.sh open_mdheadless_external_jython_with_passphrase2.py [dataset path/name] [encryption passphrase]

DISCLAIMER: This is NOT a method 'supported' by Infinite Kind!
            Always BACKUP FIRST
            Do not use when Moneydance is open
            I would suggest you stay READONLY - do not update data
            USE AT YOUR OWN RISK!
            
More information on jpype here: https://www.jython.org

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

Author: Stuart Beesley - StuWareSoftSystems 2021 - https://yogi1967.github.io/MoneydancePythonScripts/
Credits: Dale Furrow: https://github.com/dkfurrow/md_python_headless_demo
More Help and credits: hleofxquotes...

INSTRUCTIONS:
- Get Jython 2.7.2 downloaded, installed, and working (outside of Moneydance). NOTE - You will need to add jython to PATH
- Read Jython instructions at the website: https://www.jython.org
- Get, install, modify my 'launch-moneydance-via-jython.sh' shell script
- find/extract the moneydance.jar files into a directory of your choosing

NOTE:
- This is a basic script to get access to your Moneydance data externally and allows you to open with a user set passphrase
- See Dale Furrow's scripts 1-5 for further examples of automation. Currently it's tricky to do these steps if you have a user
- passphrase set without extending Main and overriding .getUI(); and extending MoneydanceGUI() and overriding .getSecretKeyCallback(), .showErrorMessage(), .go()
- The IK developer (Sean) has indicated he's willing to set en environment variable to pass the passphrase (April 2021) - let's see....
"""

# ################## `set these default variables or use command line arguments ##########################################
myEncryptionPassphrase = u"bob"  # Just use "" if not set... Moneydance checks the 'key' file and if userpass=0 it will just use it's known 'internal' default...  ;->
mdDataFolder = "/Users/xxx/Library/Containers/com.infinitekind.MoneydanceOSX/Data/Documents/XXX.moneydance"
theScript = None
# ################## `set these variables ################################################################################

import sys
reload(sys)  # Dirty hack to eliminate UTF-8 coding errors
sys.setdefaultencoding('utf8')  # Dirty hack to eliminate UTF-8 coding errors. Without this str() fails on unicode strings...

import os

print("Importing useful Java Classes...")
from java.io import File
from java.lang import System


if len(sys.argv) > 1:
    mdDataFolder = sys.argv[1]

if len(sys.argv) > 2:
    myEncryptionPassphrase = sys.argv[2]

if len(sys.argv) > 3:
    theScript = sys.argv[3]
    print("Python file: '%s'" %(theScript))
    if not os.path.exists(theScript):
        print("Sorry, python script file does not exist...?! Aborting")
        System.exit(0)      # this stops the popup message and infinite loop...

print("\n@@@ Opening file: %s, Encryption: %s @@\n" %(mdDataFolder, myEncryptionPassphrase))

# get oriented, print current working directory (script is based on working directory as project root)
print("Working Directory: {0}".format(os.getcwd()))

###################################################################
print("Importing necessary Moneydance Classes...")
from com.moneydance.apps.md.controller import Main 
from com.moneydance.security import SecretKeyCallback
from com.moneydance.apps.md.controller import AccountBookWrapper
from com.moneydance.apps.md.view.gui import MoneydanceGUI

print("Importing useful Moneydance Classes...")
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

print("prove moneydance data file exists, load it into java File object")
print("Moneydance Data File exists? {0}, in {1}".format(os.path.exists(mdDataFolder), mdDataFolder))
if not os.path.exists(mdDataFolder):
    raise Exception("!!!! ERROR: Datafile: %s does NOT exist! Aborting...." %(mdDataFolder))

mdFileJava = File(mdDataFolder)
last_modded_long = mdFileJava.lastModified()
print("data folder last modified: %s" %(last_modded_long))


###################################################################
# The 'magic' that holds/returns the encryption key....
class MySecret(SecretKeyCallback):
    def __init__(self, theKey):
        self.theKey = theKey
        self.passwordCalls = 0

    def getPassphrase(self, arg1, arg2=None):
        print("@getPassphrase(%s,%s) will return %s" %(arg1,arg2,self.theKey))

        if self.passwordCalls:
            print("@@ Second call to getPassphrase()... Assuming bad password, so aborting.....")
            System.exit(0)      # this stops the popup message and infinite loop...

        self.passwordCalls += 1

        return self.theKey


###################################################################
# Fire up Moneydance and initialize key stuff...

theMain = Main()
theMain.DEBUG = True
theMain.initializeApp()

wrapper = AccountBookWrapper.wrapperForFolder(mdFileJava)  # wrapper is of java type 'AccountBookWrapper'
theMain.setCurrentBook(wrapper)

mdGui = MoneydanceGUI(theMain)

###################################################################

def runPythonScript(mdMain, pythonScript):                                                                    # noqa
    python = mdMain.getPythonInterpreter()
    python.execfile(pythonScript)


if theScript:
    runPythonScript(theMain, theScript)

###################################################################
# Away we go, accessing the data...

accountBook = theMain.getCurrentAccountBook()
print(accountBook)

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
from com.infinitekind.moneydance.model.CurrencyType import CURRTYPE_SECURITY                                            # noqa
currencies = accountBook.getCurrencies().getAllCurrencies()
securities = [x for x in currencies if x.getCurrencyType() == CurrencyType.Type.SECURITY]                               # noqa

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
              .format(security.getName(), ticker, dateInt, price))
    except:
        pass


# theMain.showURL("invokeAndQuitURI")
theMain.saveCurrentAccount()
# theMain.shutdown()


print("@@@@  END @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
