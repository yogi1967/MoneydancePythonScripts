#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Example script accessing moneydance data in 'headless' mode using jpython

NOTE:  Works with an encryption passphrase from MD2021.2(3088) onwards as this allows you to set the passphrase into
       an environment variable: md_passphrase=  or  md_passphrase_[filename in lowercase format]=

Usage: ./launch-moneydance-via-jython.sh open_mdheadless_external_jython_with_environment_passphrase.py [dataset path/name]

DISCLAIMER: Always BACKUP FIRST
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
"""

# ################## `set these default variables or use command line arguments ##########################################
mdDataFolder = "/Users/stu/Downloads/jpype/moneydanceissue/Development.moneydance"
# ################## `set these variables ################################################################################

import sys
reload(sys)  # Dirty hack to eliminate UTF-8 coding errors
sys.setdefaultencoding('utf8')  # Dirty hack to eliminate UTF-8 coding errors. Without this str() fails on unicode strings...

import os

if len(sys.argv) > 1:
    mdDataFolder = sys.argv[1]

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
    print("")
else:
    print("No passphrases detected in environment\n")

print("\n@@@ Opening file: %s @@\n" %(mdDataFolder))

# get oriented, print current working directory (script is based on working directory as project root)
print("Working Directory: {0}".format(os.getcwd()))

###################################################################
print("Importing necessary Moneydance Classes...")
from com.moneydance.apps.md.controller import Main 
# from com.moneydance.security import SecretKeyCallback
from com.moneydance.apps.md.controller import AccountBookWrapper

print("Importing useful Moneydance Classes...")
from com.infinitekind.moneydance.model import ParentTxn, CurrencyType, Account
# from com.infinitekind.moneydance.model import AccountBook, Account, MoneydanceSyncableItem, TxnSet, TxnUtil, AbstractTxn, SplitTxn, CurrencySnapshot, CurrencyTable, CurrencyUtil

print("Importing useful man Classes...")
from java.io import File
# from java.lang import System

print("Prove moneydance data file exists, load it into java File object")
print("Moneydance Data File exists? {0}, in {1}".format(os.path.exists(mdDataFolder), mdDataFolder))
if not os.path.exists(mdDataFolder):
    raise Exception("!!!! ERROR: Datafile: %s does NOT exist! Aborting...." %(mdDataFolder))

mdFileJava = File(mdDataFolder)
last_modded_long = mdFileJava.lastModified()
print("data folder last modified: %s" %(last_modded_long))

theMain = Main()
theMain.main(["-d", "-v"])
theMain.DEBUG = True
theMain.initializeApp()      # this needs changing post MD2024.3(5219) - from build 5252
# theMain.startApplication()

wrapper = AccountBookWrapper.wrapperForFolder(mdFileJava)  # type: AccountBookWrapper
theMain.setCurrentBook(wrapper)

accountBook = wrapper.getBook()
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

for acct in root_account.getSubAccounts():
    if acct.getAccountType() == Account.AccountType.BANK: print("Found bank account: %s" %(acct))                       # noqa

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


########################################################################################################################
from com.infinitekind.moneydance.model import ParentTxn, SplitTxn
from com.moneydance.apps.md.controller import AccountBookWrapper
from com.infinitekind.util import DateUtil

accountBook = wrapper.getBook()
root_account = accountBook.getRootAccount()
account = root_account.getAccountByName('Transferwise')

desc = "Test Txn - hello"
checknumber = "1234"
memo = "this is a memo"
transdate = 20220203
amount = -222
rate = 1.0
category = account.getDefaultCategory()

new_txn = ParentTxn.makeParentTxn(accountBook, transdate, transdate, DateUtil.getUniqueCurrentTimeMillis(), checknumber,
                                  account, desc, memo, -1, 30)
txn_split = SplitTxn.makeSplitTxn(new_txn, amount, rate, category, memo, -1, 0)
new_txn.addSplit(txn_split)

print("------")
print("TxnSet count before:", accountBook.getTransactionSet().getTransactionCount())
new_txn.syncItem()
print(new_txn.getSyncInfo().toMultilineHumanReadableString())
print("------")
print("Did I find txn in TxnSet?", new_txn in accountBook.getTransactionSet())
print("TxnSet count after:", accountBook.getTransactionSet().getTransactionCount())
print("------")
########################################################################################################################




# theMain.showURL("invokeAndQuitURI")
theMain.saveCurrentAccount()
theMain.shutdown()

print("@@@@  END @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
