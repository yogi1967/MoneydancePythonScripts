#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# client_mark_extract_data.py - build: 1001 November 2023 - Stuart Beesley (based on: extract_data build: 1036)
#
# Written specifically for Mark McClintock

########################################################################################################################
#                 You can auto invoke by launching MD with one of the following:
#                           '-d [datasetpath] -invoke=moneydance:fmodule:client_mark_extract_data:autoextract:noquit'
#                           '-d [datasetpath] -invoke=moneydance:fmodule:client_mark_extract_data:autoextract:quit'
#                                             ...NOTE: MD will auto-quit after executing this way...
#
#                 Using the parameter -nobackup will disable backups for that MD session (from build 5047 onwards)
#
#                 You can also enable the 'auto extract every time dataset is closed' option
#                     WARNING: This will execute all extracts everytime dataset is closed.
#                     Thus, you could launch MD with:
#                           '-d [datasetpath] -invoke_and_quit=moneydance:fmodule:client_mark_extract_data:hello'
#                           ('hello' does not exist and does nothing, but MD will then start shutdown and if the
#                            option is set then it will initiate the auto extracts)
#                     NOTE: This runs silently.. MD will appear to hang. View help/console (errlog.txt) for messages....
########################################################################################################################

# MIT License
#
# Copyright (c) 2021-2023 Stuart Beesley - StuWareSoftSystems
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

# Use in Moneydance Menu Window->Show Moneybot Console >> Open Script >> RUN

# Stuart Beesley Created 2023-10-27 - tested on MacOS - MD2021 onwards - StuWareSoftSystems....
# Build: 900 -  Initial beta build - based on extract_data build 1036.
# Build: 901 -  Completed the extracts... first preview product.
# Build: 902 -  Enhanced HomePageView widget
# Build: 903 -  Tweaks as per client's feedback
# Build: 904 -  Added auto execute script(s) features..
# Build: 905 -  Auto relaunch GUI config screen after extracts
# Build: 906 -  Config option for auto relaunch GUI config screen after extracts
# Build: 907 -  Switch to FileDialog
# Build: 908 -  Fixes for Mark's feedback....
# Build: 909 -  Show last run's output when auto relaunching the GUI...
# Build: 1000 - Final, released build....
# Build: 1001 - Tweaks - correct save folder display text


# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################

# SET THESE LINES
myModuleID = u"client_mark_extract_data"
version_build = "1001"
MIN_BUILD_REQD = 1904                                               # Check for builds less than 1904 / version < 2019.4
_I_CAN_RUN_AS_MONEYBOT_SCRIPT = False

global moneydance, moneydance_ui, moneydance_extension_loader, moneydance_extension_parameter

global MD_REF, MD_REF_UI
if "moneydance" in globals(): MD_REF = moneydance           # Make my own copy of reference as MD removes it once main thread ends.. Don't use/hold on to _data variable
if "moneydance_ui" in globals(): MD_REF_UI = moneydance_ui  # Necessary as calls to .getUI() will try to load UI if None - we don't want this....
if "MD_REF" not in globals(): raise Exception("ERROR: 'moneydance' / 'MD_REF' NOT set!?")
if "MD_REF_UI" not in globals(): raise Exception("ERROR: 'moneydance_ui' / 'MD_REF_UI' NOT set!?")

# Nuke unwanted (direct/indirect) reference(s) to AccountBook etc....
if "moneydance_data" in globals():
    moneydance_data = None
    del moneydance_data

if "moneybot" in globals():
    moneybot = None
    del moneybot

from java.lang import Boolean
global debug
if "debug" not in globals():
    # if Moneydance is launched with -d, or this property is set, or extension is being (re)installed with Console open.
    debug = (False or MD_REF.DEBUG or Boolean.getBoolean("moneydance.debug"))

global client_mark_extract_data_frame_
# SET LINES ABOVE ^^^^

# COPY >> START
import __builtin__ as builtins

def checkObjectInNameSpace(objectName):
    """Checks globals() and builtins for the existence of the object name (used for StuWareSoftSystems' bootstrap)"""
    if objectName is None or not isinstance(objectName, basestring) or objectName == u"": return False
    if objectName in globals(): return True
    return objectName in dir(builtins)


if MD_REF is None: raise Exception(u"CRITICAL ERROR - moneydance object/variable is None?")
if checkObjectInNameSpace(u"moneydance_extension_loader"):
    MD_EXTENSION_LOADER = moneydance_extension_loader
else:
    MD_EXTENSION_LOADER = None

if (u"__file__" in globals() and __file__.startswith(u"bootstrapped_")): del __file__       # Prevent bootstrapped loader setting this....

from java.lang import System, Runnable
from javax.swing import JFrame, SwingUtilities, SwingWorker
from java.awt.event import WindowEvent

class QuickAbortThisScriptException(Exception): pass

class MyJFrame(JFrame):

    def __init__(self, frameTitle=None):
        super(JFrame, self).__init__(frameTitle)
        self.disposing = False
        self.myJFrameVersion = 4
        self.isActiveInMoneydance = False
        self.isRunTimeExtension = False
        self.MoneydanceAppListener = None
        self.HomePageViewObj = None

    def dispose(self):
        # This removes all content as Java/Swing (often) retains the JFrame reference in memory...
        if self.disposing: return
        try:
            self.disposing = True
            self.getContentPane().removeAll()
            if self.getJMenuBar() is not None: self.setJMenuBar(None)
            rootPane = self.getRootPane()
            if rootPane is not None:
                rootPane.getInputMap().clear()
                rootPane.getActionMap().clear()
            super(self.__class__, self).dispose()
        except:
            _msg = "%s: ERROR DISPOSING OF FRAME: %s\n" %(myModuleID, self)
            print(_msg); System.err.write(_msg)
        finally:
            self.disposing = False

class GenericWindowClosingRunnable(Runnable):

    def __init__(self, theFrame):
        self.theFrame = theFrame

    def run(self):
        self.theFrame.setVisible(False)
        self.theFrame.dispatchEvent(WindowEvent(self.theFrame, WindowEvent.WINDOW_CLOSING))

class GenericDisposeRunnable(Runnable):
    def __init__(self, theFrame):
        self.theFrame = theFrame

    def run(self):
        self.theFrame.setVisible(False)
        self.theFrame.dispose()

class GenericVisibleRunnable(Runnable):
    def __init__(self, theFrame, lVisible=True, lToFront=False):
        self.theFrame = theFrame
        self.lVisible = lVisible
        self.lToFront = lToFront

    def run(self):
        self.theFrame.setVisible(self.lVisible)
        if self.lVisible and self.lToFront:
            if self.theFrame.getExtendedState() == JFrame.ICONIFIED:
                self.theFrame.setExtendedState(JFrame.NORMAL)
            self.theFrame.toFront()

def getMyJFrame(moduleName):
    try:
        frames = JFrame.getFrames()
        for fr in frames:
            if (fr.getName().lower().startswith(u"%s_main" %moduleName)
                    and (type(fr).__name__ == MyJFrame.__name__ or type(fr).__name__ == u"MyCOAWindow")  # isinstance() won't work across namespaces
                    and fr.isActiveInMoneydance):
                _msg = "%s: Found live frame: %s (MyJFrame() version: %s)\n" %(myModuleID,fr.getName(),fr.myJFrameVersion)
                print(_msg); System.err.write(_msg)
                if fr.isRunTimeExtension:
                    _msg = "%s: ... and this is a run-time self-installed extension too...\n" %(myModuleID)
                    print(_msg); System.err.write(_msg)
                return fr
    except:
        _msg = "%s: Critical error in getMyJFrame(); caught and ignoring...!\n" %(myModuleID)
        print(_msg); System.err.write(_msg)
    return None


frameToResurrect = None
try:
    # So we check own namespace first for same frame variable...
    if (u"%s_frame_"%myModuleID in globals()
            and (isinstance(client_mark_extract_data_frame_, MyJFrame)                 # EDIT THIS
                 or type(client_mark_extract_data_frame_).__name__ == u"MyCOAWindow")  # EDIT THIS
            and client_mark_extract_data_frame_.isActiveInMoneydance):                 # EDIT THIS
        frameToResurrect = client_mark_extract_data_frame_                             # EDIT THIS
    else:
        # Now check all frames in the JVM...
        getFr = getMyJFrame( myModuleID )
        if getFr is not None:
            frameToResurrect = getFr
        del getFr
except:
    msg = "%s: Critical error checking frameToResurrect(1); caught and ignoring...!\n" %(myModuleID)
    print(msg); System.err.write(msg)

# ############################
# Trap startup conditions here.... The 'if's pass through to oblivion (and thus a clean exit)... The final 'else' actually runs the script
if int(MD_REF.getBuild()) < MIN_BUILD_REQD:     # Check for builds less than 1904 (version 2019.4) or build 3056 accordingly
    msg = "SORRY YOUR MONEYDANCE VERSION IS TOO OLD FOR THIS SCRIPT/EXTENSION (min build %s required)" %(MIN_BUILD_REQD)
    print(msg); System.err.write(msg)
    try:    MD_REF_UI.showInfoMessage(msg)
    except: raise Exception(msg)

elif frameToResurrect and frameToResurrect.isRunTimeExtension:
    msg = "%s: Sorry - runtime extension already running. Please uninstall/reinstall properly. Must be on build: %s onwards. Now exiting script!\n" %(myModuleID, MIN_BUILD_REQD)
    print(msg); System.err.write(msg)
    try: MD_REF_UI.showInfoMessage(msg)
    except: raise Exception(msg)

elif not _I_CAN_RUN_AS_MONEYBOT_SCRIPT and u"__file__" in globals():
    msg = "%s: Sorry - this script cannot be run in Moneybot console. Please install mxt and run extension properly. Must be on build: %s onwards. Now exiting script!\n" %(myModuleID, MIN_BUILD_REQD)
    print(msg); System.err.write(msg)
    try: MD_REF_UI.showInfoMessage(msg)
    except: raise Exception(msg)

elif not _I_CAN_RUN_AS_MONEYBOT_SCRIPT and not checkObjectInNameSpace(u"moneydance_extension_loader"):
    msg = "%s: Error - moneydance_extension_loader seems to be missing? Must be on build: %s onwards. Now exiting script!\n" %(myModuleID, MIN_BUILD_REQD)
    print(msg); System.err.write(msg)
    try: MD_REF_UI.showInfoMessage(msg)
    except: raise Exception(msg)

elif frameToResurrect:  # and it's active too...
    try:
        msg = "%s: Detected that %s is already running..... Attempting to resurrect..\n" %(myModuleID, myModuleID)
        print(msg); System.err.write(msg)
        SwingUtilities.invokeLater(GenericVisibleRunnable(frameToResurrect, True, True))
    except:
        msg  = "%s: Failed to resurrect main Frame.. This duplicate Script/extension is now terminating.....\n" %(myModuleID)
        print(msg); System.err.write(msg)
        raise Exception(msg)

else:
    del frameToResurrect
    msg = "%s: Startup conditions passed (and no other instances of this program detected). Now executing....\n" %(myModuleID)
    print(msg); System.err.write(msg)

    # COMMON IMPORTS #######################################################################################################
    # COMMON IMPORTS #######################################################################################################
    # COMMON IMPORTS #######################################################################################################

    global sys
    if "sys" not in globals():
        # NOTE: As of MD2022(4040), python.getSystemState().setdefaultencoding("utf8") is called on the python interpreter at script launch...
        import sys
        reload(sys)                     # Dirty hack to eliminate UTF-8 coding errors
        sys.setdefaultencoding('utf8')  # Without this str() fails on unicode strings...

    import os
    import os.path
    import codecs
    import inspect
    import pickle
    import platform
    import csv
    import datetime
    import traceback
    import subprocess

    from org.python.core.util import FileUtil

    from com.moneydance.util import Platform
    from com.moneydance.awt import JTextPanel, GridC, JDateField
    from com.moneydance.apps.md.view.gui import MDImages

    from com.infinitekind.util import DateUtil, CustomDateFormat, StringUtils

    from com.infinitekind.moneydance.model import *
    from com.infinitekind.moneydance.model import AccountUtil, AcctFilter, CurrencyType, CurrencyUtil
    from com.infinitekind.moneydance.model import Account, Reminder, ParentTxn, SplitTxn, TxnSearch, InvestUtil, TxnUtil

    from com.moneydance.apps.md.controller import AccountBookWrapper, AppEventManager                                   # noqa
    from com.infinitekind.moneydance.model import AccountBook
    from com.infinitekind.tiksync import SyncRecord                                                                     # noqa
    from com.infinitekind.util import StreamTable                                                                       # noqa

    from javax.swing import JButton, JScrollPane, WindowConstants, JLabel, JPanel, JComponent, KeyStroke, JDialog, JComboBox
    from javax.swing import JOptionPane, JTextArea, JMenuBar, JMenu, JMenuItem, AbstractAction, JCheckBoxMenuItem, JFileChooser
    from javax.swing import JTextField, JPasswordField, Box, UIManager, JTable, JCheckBox, JRadioButton, ButtonGroup
    from javax.swing.text import PlainDocument
    from javax.swing.border import EmptyBorder
    from javax.swing.filechooser import FileFilter

    exec("from javax.print import attribute")       # IntelliJ doesnt like the use of 'print' (as it's a keyword). Messy, but hey!
    exec("from java.awt.print import PrinterJob")   # IntelliJ doesnt like the use of 'print' (as it's a keyword). Messy, but hey!
    global attribute, PrinterJob

    from java.awt.datatransfer import StringSelection
    from javax.swing.text import DefaultHighlighter
    from javax.swing.event import AncestorListener

    from java.awt import Color, Dimension, FileDialog, FlowLayout, Toolkit, Font, GridBagLayout, GridLayout
    from java.awt import BorderLayout, Dialog, Insets, Point
    from java.awt.event import KeyEvent, WindowAdapter, InputEvent
    from java.util import Date, Locale

    from java.text import DecimalFormat, SimpleDateFormat, MessageFormat
    from java.util import Calendar, ArrayList
    from java.lang import Thread, IllegalArgumentException, String, Integer, Long
    from java.lang import Double, Math, Character, NoSuchFieldException, NoSuchMethodException, Boolean
    from java.lang.reflect import Modifier
    from java.io import FileNotFoundException, FilenameFilter, File, FileInputStream, FileOutputStream, IOException, StringReader
    from java.io import BufferedReader, InputStreamReader
    from java.nio.charset import Charset

    if int(MD_REF.getBuild()) >= 3067:
        from com.moneydance.apps.md.view.gui.theme import ThemeInfo                                                     # noqa
    else:
        from com.moneydance.apps.md.view.gui.theme import Theme as ThemeInfo                                            # noqa

    if isinstance(None, (JDateField,CurrencyUtil,Reminder,ParentTxn,SplitTxn,TxnSearch, JComboBox, JCheckBox,
                         AccountBook, AccountBookWrapper, Long, Integer, Boolean,
                         JTextArea, JMenuBar, JMenu, JMenuItem, JCheckBoxMenuItem, JFileChooser, JDialog,
                         JButton, FlowLayout, InputEvent, ArrayList, File, IOException, StringReader, BufferedReader,
                         InputStreamReader, Dialog, JTable, BorderLayout, Double, InvestUtil, JRadioButton, ButtonGroup,
                         AccountUtil, AcctFilter, CurrencyType, Account, TxnUtil, JScrollPane, WindowConstants, JFrame,
                         JComponent, KeyStroke, AbstractAction, UIManager, Color, Dimension, Toolkit, KeyEvent, GridLayout,
                         WindowAdapter, CustomDateFormat, SimpleDateFormat, Insets, FileDialog, Thread, SwingWorker)): pass
    if codecs.BOM_UTF8 is not None: pass
    if csv.QUOTE_ALL is not None: pass
    if datetime.MINYEAR is not None: pass
    if Math.max(1,1): pass
    # END COMMON IMPORTS ###################################################################################################

    # COMMON GLOBALS #######################################################################################################
    # none
    # END COMMON GLOBALS ###################################################################################################
    # COPY >> END

    # SET THESE VARIABLES FOR ALL SCRIPTS ##################################################################################
    if "GlobalVars" in globals():   # Prevent wiping if 'buddy' extension - like Toolbox - is running too...
        global GlobalVars
    else:
        class GlobalVars:        # Started using this method for storing global variables from August 2021
            CONTEXT = MD_REF
            defaultPrintService = None
            defaultPrinterAttributes = None
            defaultPrintFontSize = None
            defaultPrintLandscape = None
            defaultDPI = 72     # NOTE: 72dpi is Java2D default for everything; just go with it. No easy way to change
            STATUS_LABEL = None
            DARK_GREEN = Color(0, 192, 0)
            resetPickleParameters = False
            decimalCharSep = "."
            lGlobalErrorDetected = False
            MYPYTHON_DOWNLOAD_URL = "https://yogi1967.github.io/MoneydancePythonScripts/"
            i_am_an_extension_so_run_headless = None
            parametersLoadedFromFile = {}
            thisScriptName = None
            MD_MDPLUS_BUILD = 4040                          # 2022.0
            MD_ALERTCONTROLLER_BUILD = 4077                 # 2022.3
            def __init__(self): pass    # Leave empty

            class Strings:
                def __init__(self): pass    # Leave empty

    GlobalVars.MD_PREFERENCE_KEY_CURRENT_THEME = "gui.current_theme"
    GlobalVars.thisScriptName = "%s.py(Extension)" %(myModuleID)

    GlobalVars.Strings.MD_KEY_BALANCE_ADJUSTMENT = "baladj"
    # END SET THESE VARIABLES FOR ALL SCRIPTS ##############################################################################

    # >>> THIS SCRIPT'S IMPORTS ############################################################################################
    from com.infinitekind.moneydance.model import DateRange
    from com.moneydance.apps.md.controller.time import TimeInterval, TimeIntervalUtil                                   # noqa

    # from extract_account_registers_csv & extract_investment_transactions_csv
    from copy import deepcopy
    import subprocess
    import threading
    from com.moneydance.apps.md.view.gui import DateRangeChooser
    from com.infinitekind.moneydance.model import SecurityType, AbstractTxn                                             # noqa

    from javax.swing import BorderFactory, JSeparator
    
    from com.moneydance.apps.md.controller import AppEventListener, AccountFilter, FullAccountList
    from com.moneydance.apps.md.view.gui import DateRangeChooser
    from com.moneydance.apps.md.view.gui.reporttool import GraphReportUtil
    from com.moneydance.apps.md.view.gui.select import AccountSelectList

    from java.awt.event import ActionEvent, ActionListener
    from com.moneydance.apps.md.view.gui import SecondaryDialog
    from com.moneydance.apps.md.view.gui import MDAction

    # >>> END THIS SCRIPT'S IMPORTS ########################################################################################

    # >>> THIS SCRIPT'S GLOBALS ############################################################################################

    # Reused general variables
    GlobalVars.ENABLE_BESPOKE_CODING = True                # Turn on Mark McClintock's changes to std extracts
    GlobalVars.SCRIPT_RUNNING_LOCK = threading.Lock()

    GlobalVars.dataKeys = None
    GlobalVars.csvfilename = None

    GlobalVars.LAST_END_EXTRACT_MESSAGE = getattr(GlobalVars, "LAST_END_EXTRACT_MESSAGE", None)

    # SAVED VARIABLES
    GlobalVars.saved_dateRangerConfig_EAR = ""
    GlobalVars.saved_dateRangerConfig_EIT = ""
    GlobalVars.saved_autoSelectCurrentAsOfDate_ESB = True
    GlobalVars.saved_securityBalancesDate_ESB = DateRange().getEndDateInt()
    GlobalVars.saved_whichYearOption_EAB = "this_year"

    GlobalVars.saved_exportAmazonScriptPath_SWSS = ""
    GlobalVars.saved_importAmazonScriptPath_SWSS = ""

    GlobalVars.saved_defaultSavePath_SWSS = ""
    GlobalVars.saved_showFolderAfterExtract_SWSS = True
    GlobalVars.saved_extractFileAddDatasetName_SWSS = True
    GlobalVars.saved_extractFileAddNamePrefix_SWSS = ""
    GlobalVars.saved_extractFileAddTimeStampSuffix_SWSS = True

    GlobalVars.saved_selectedAcctListUUIDs_EAR = ""

    GlobalVars.saved_autoExtract_EAR = False
    GlobalVars.saved_autoExtract_EIT = False
    GlobalVars.saved_autoExtract_ESB = False
    GlobalVars.saved_autoExtract_EAB = False

    GlobalVars.saved_relaunchGUIAfterRun_SWSS = False

    # Setup fixed extract parameters here - THESE ARE NO LONGER SAVED - BUT THEY STILL CONTROL THE EXTRACTS!
    GlobalVars.csvDelimiter = ","

    # GlobalVars.excelExtractDateFormat = "%m/%d/%Y"
    GlobalVars.excelExtractDateFormat = "%Y/%m/%d"

    GlobalVars.lStripASCII = False
    GlobalVars.lWriteBOMToExtractFile = True

    GlobalVars.hideInactiveAccounts_EAR = True
    GlobalVars.hideInactiveAccounts_EIT = True
    GlobalVars.hideInactiveAccounts_ESB = False
    GlobalVars.hideInactiveAccounts_EAB = False

    GlobalVars.hideHiddenAccounts_EAR = True
    GlobalVars.hideHiddenAccounts_EIT = True
    GlobalVars.hideHiddenAccounts_ESB = False
    GlobalVars.hideHiddenAccounts_EAB = False

    GlobalVars.lAllAccounts_EAR = True
    GlobalVars.lAllAccounts_EIT = True
    GlobalVars.lAllAccounts_ESB = True
    GlobalVars.lAllAccounts_EAB = True

    GlobalVars.filterForAccounts_EAR = "ALL"
    GlobalVars.filterForAccounts_EIT = "ALL"
    GlobalVars.filterForAccounts_ESB = "ALL"
    GlobalVars.filterForAccounts_EAB = "ALL"

    GlobalVars.hideHiddenSecurities_EAR = True
    GlobalVars.hideHiddenSecurities_EIT = True
    GlobalVars.hideHiddenSecurities_ESB = False
    GlobalVars.hideHiddenSecurities_EAB = False

    GlobalVars.lAllSecurity_EAR = True
    GlobalVars.lAllSecurity_EIT = True
    GlobalVars.lAllSecurity_ESB = True
    GlobalVars.lAllSecurity_EAB = True

    GlobalVars.filterForSecurity_EAR = "ALL"
    GlobalVars.filterForSecurity_EIT = "ALL"
    GlobalVars.filterForSecurity_ESB = "ALL"
    GlobalVars.filterForSecurity_EAB = "ALL"

    GlobalVars.lAllCurrency_EAR = True
    GlobalVars.lAllCurrency_EIT = True
    GlobalVars.lAllCurrency_ESB = True
    GlobalVars.lAllCurrency_EAB = True

    GlobalVars.filterForCurrency_EAR = "ALL"
    GlobalVars.filterForCurrency_EIT = "ALL"
    GlobalVars.filterForCurrency_ESB = "ALL"
    GlobalVars.filterForCurrency_EAB = "ALL"

    # from extract_account_registers_csv
    GlobalVars.lIncludeOpeningBalances_EAR = True
    GlobalVars.lIncludeBalanceAdjustments_EAR = True
    GlobalVars.startDateInt_EAR = DateRange().getStartDateInt()
    GlobalVars.endDateInt_EAR = DateRange().getEndDateInt()
    GlobalVars.lAllTags_EAR = True
    GlobalVars.tagFilter_EAR = "ALL"
    GlobalVars.lAllText_EAR = True
    GlobalVars.textFilter_EAR = "ALL"
    GlobalVars.lAllCategories_EAR = True
    GlobalVars.categoriesFilter_EAR = "ALL"

    # from extract_investment_transactions_csv
    GlobalVars.lIncludeOpeningBalances_EIT = True
    GlobalVars.lIncludeBalanceAdjustments_EIT = True
    GlobalVars.lAdjustForSplits_EIT = True
    GlobalVars.lOmitLOTDataFromExtract_EIT = True
    GlobalVars.lExtractExtraSecurityAcctInfo_EIT = False
    GlobalVars.lFilterDateRange_EIT = True
    GlobalVars.startDateInt_EIT = DateRange().getStartDateInt()
    GlobalVars.endDateInt_EIT = DateRange().getEndDateInt()


    # Do these once here (for objects that might hold Model objects etc) and then release at the end... (not the cleanest method...)
    GlobalVars.baseCurrency = None
    GlobalVars.table = None
    GlobalVars.transactionTable = None
    GlobalVars.selectedAccounts_EAR = None


    # >>> END THIS SCRIPT'S GLOBALS ############################################################################################

    # COPY >> START
    # COMMON CODE ######################################################################################################
    # COMMON CODE ################# VERSION 108 ########################################################################
    # COMMON CODE ######################################################################################################
    GlobalVars.i_am_an_extension_so_run_headless = False
    try:
        GlobalVars.thisScriptName = os.path.basename(__file__)
    except:
        GlobalVars.i_am_an_extension_so_run_headless = True

    scriptExit = """
----------------------------------------------------------------------------------------------------------------------
Thank you for using %s!
The author has other useful Extensions / Moneybot Python scripts available...:

Extension (.mxt) format only:
Toolbox: View Moneydance settings, diagnostics, fix issues, change settings and much more
         + Extension menus: Total selected txns; Move Investment Txns; Zap md+/ofx/qif (default) memo fields;

Custom Balances (net_account_balances): Summary Page (HomePage) widget. Display the total of selected Account Balances

Extension (.mxt) and Script (.py) Versions available:
Extract Data: Extract various data to screen /or csv.. (also auto-extract mode): Includes:
    - StockGlance2020: Securities/stocks, total by security across investment accounts;
    - Reminders; Account register transaction (attachments optional);
    - Investment transactions (attachments optional); Security Balances; Currency price history;
    - Decrypt / extract raw 'Trunk' file; Extract raw data as JSON file; All attachments;

List Future Reminders:                  View future reminders on screen. Allows you to set the days to look forward
Security Performance Graph:             Graphs selected securities, calculating relative price performance as percentage
Accounts Categories Mega Search Window: Combines MD Menu> Tools>Accounts/Categories and adds Quick Search box/capability

A collection of useful ad-hoc scripts (zip file)
useful_scripts:                         Just unzip and select the script you want for the task at hand...

Visit: %s (Author's site)
----------------------------------------------------------------------------------------------------------------------
""" %(GlobalVars.thisScriptName, GlobalVars.MYPYTHON_DOWNLOAD_URL)

    def cleanup_references():
        global MD_REF, MD_REF_UI, MD_EXTENSION_LOADER
        # myPrint("DB","About to delete reference to MD_REF, MD_REF_UI and MD_EXTENSION_LOADER....!")
        # del MD_REF, MD_REF_UI, MD_EXTENSION_LOADER

        resetGlobalVariables()

        myPrint("DB", "... destroying own reference to frame('client_mark_extract_data_frame_')...")
        global client_mark_extract_data_frame_
        client_mark_extract_data_frame_ = None
        del client_mark_extract_data_frame_

    def load_text_from_stream_file(theStream):
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")

        cs = Charset.forName("UTF-8")

        istream = theStream

        if not istream:
            myPrint("B","... Error - the input stream is None")
            return "<NONE>"

        fileContents = ""
        istr = bufr = None
        try:
            istr = InputStreamReader(istream, cs)
            bufr = BufferedReader(istr)
            while True:
                line = bufr.readLine()
                if line is not None:
                    line += "\n"                   # not very efficient - should convert this to "\n".join() to contents
                    fileContents+=line
                    continue
                break
            fileContents+="\n<END>"
        except:
            myPrint("B", "ERROR reading from input stream... ")
            dump_sys_error_to_md_console_and_errorlog()

        try: bufr.close()
        except: pass

        try: istr.close()
        except: pass

        try: istream.close()
        except: pass

        myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return fileContents

    # P=Display on Python Console, J=Display on MD (Java) Console Error Log, B=Both, D=If Debug Only print, DB=print both
    def myPrint(where, *args):
        if where[0] == "D" and not debug: return

        try:
            printString = ""
            for what in args:
                printString += "%s " %what
            printString = printString.rstrip(" ")

            if where == "P" or where == "B" or where[0] == "D":
                if not GlobalVars.i_am_an_extension_so_run_headless:
                    try:
                        print(printString)
                    except:
                        print("Error writing to screen...")
                        dump_sys_error_to_md_console_and_errorlog()

            if where == "J" or where == "B" or where == "DB":
                dt = datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
                try:
                    System.err.write(GlobalVars.thisScriptName + ":" + dt + ": ")
                    System.err.write(printString)
                    System.err.write("\n")
                except:
                    System.err.write(GlobalVars.thisScriptName + ":" + dt + ": " + "Error writing to console")
                    dump_sys_error_to_md_console_and_errorlog()

        except IllegalArgumentException:
            myPrint("B","ERROR - Probably on a multi-byte character..... Will ignore as code should just continue (PLEASE REPORT TO DEVELOPER).....")
            dump_sys_error_to_md_console_and_errorlog()

        return


    if debug: myPrint("B", "** DEBUG IS ON **")

    def dump_sys_error_to_md_console_and_errorlog(lReturnText=False):

        tb = traceback.format_exc()
        trace = traceback.format_stack()
        theText =  ".\n" \
                   "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" \
                   "@@@@@ Unexpected error caught!\n".upper()
        theText += tb
        for trace_line in trace: theText += trace_line
        theText += "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
        myPrint("B", theText)
        if lReturnText: return theText
        return

    def safeStr(_theText): return ("%s" %(_theText))

    def pad(theText, theLength, padChar=u" "):
        if not isinstance(theText, (unicode, str)): theText = safeStr(theText)
        theText = theText[:theLength].ljust(theLength, padChar)
        return theText

    def rpad(theText, theLength, padChar=u" "):
        if not isinstance(theText, (unicode, str)): theText = safeStr(theText)
        theText = theText[:theLength].rjust(theLength, padChar)
        return theText

    def cpad(theText, theLength, padChar=u" "):
        if not isinstance(theText, (unicode, str)): theText = safeStr(theText)
        if len(theText) >= theLength: return theText[:theLength]
        padLength = int((theLength - len(theText)) / 2)
        theText = theText[:theLength]
        theText = ((padChar * padLength)+theText+(padChar * padLength))[:theLength]
        return theText

    myPrint("B", GlobalVars.thisScriptName, ": Python Script Initialising.......", "Build:", version_build)

    def getMonoFont():
        try:
            theFont = MD_REF.getUI().getFonts().code
            # if debug: myPrint("B","Success setting Font set to Moneydance code: %s" %theFont)
        except:
            theFont = Font("monospaced", Font.PLAIN, 15)
            if debug: myPrint("B","Failed to Font set to Moneydance code - So using: %s" %theFont)

        return theFont

    def isOSXVersionAtLeast(compareVersion):
        # type: (basestring) -> bool
        """Pass a string in the format 'x.x.x'. Will check that this MacOSX version is at least that version. The 3rd micro number is optional"""

        try:
            if not Platform.isOSX(): return False

            def convertVersion(convertString):
                _os_major = _os_minor = _os_micro = 0
                _versionNumbers = []

                for versionPart in StringUtils.splitIntoList(convertString, '.'):
                    strippedPart = StringUtils.stripNonNumbers(versionPart, '.')
                    if (StringUtils.isInteger(strippedPart)):
                        _versionNumbers.append(Integer.valueOf(Integer.parseInt(strippedPart)))
                    else:
                        _versionNumbers.append(0)

                if len(_versionNumbers) >= 1: _os_major = max(0, _versionNumbers[0])
                if len(_versionNumbers) >= 2: _os_minor = max(0, _versionNumbers[1])
                if len(_versionNumbers) >= 3: _os_micro = max(0, _versionNumbers[2])

                return _os_major, _os_minor, _os_micro


            os_major, os_minor, os_micro = convertVersion(System.getProperty("os.version", "0.0.0"))
            myPrint("DB", "MacOS Version number(s): %s.%s.%s" %(os_major, os_minor, os_micro))

            if not isinstance(compareVersion, basestring) or len(compareVersion) < 1:
                myPrint("B", "ERROR: Invalid compareVersion of '%s' passed - returning False" %(compareVersion))
                return False

            chk_os_major, chk_os_minor, chk_os_micro = convertVersion(compareVersion)
            myPrint("DB", "Comparing against Version(s): %s.%s.%s" %(chk_os_major, chk_os_minor, chk_os_micro))


            if os_major < chk_os_major: return False
            if os_major > chk_os_major: return True

            if os_minor < chk_os_minor: return False
            if os_minor > chk_os_minor: return True

            if os_micro < chk_os_micro: return False
            return True

        except:
            myPrint("B", "ERROR: isOSXVersionAtLeast() failed - returning False")
            dump_sys_error_to_md_console_and_errorlog()
            return False

    def isOSXVersionCheetahOrLater():       return isOSXVersionAtLeast("10.0")
    def isOSXVersionPumaOrLater():          return isOSXVersionAtLeast("10.1")
    def isOSXVersionJaguarOrLater():        return isOSXVersionAtLeast("10.2")
    def isOSXVersionPantherOrLater():       return isOSXVersionAtLeast("10.3")
    def isOSXVersionTigerOrLater():         return isOSXVersionAtLeast("10.4")
    def isOSXVersionLeopardOrLater():       return isOSXVersionAtLeast("10.5")
    def isOSXVersionSnowLeopardOrLater():   return isOSXVersionAtLeast("10.6")
    def isOSXVersionLionOrLater():          return isOSXVersionAtLeast("10.7")
    def isOSXVersionMountainLionOrLater():  return isOSXVersionAtLeast("10.8")
    def isOSXVersionMavericksOrLater():     return isOSXVersionAtLeast("10.9")
    def isOSXVersionYosemiteOrLater():      return isOSXVersionAtLeast("10.10")
    def isOSXVersionElCapitanOrLater():     return isOSXVersionAtLeast("10.11")
    def isOSXVersionSierraOrLater():        return isOSXVersionAtLeast("10.12")
    def isOSXVersionHighSierraOrLater():    return isOSXVersionAtLeast("10.13")
    def isOSXVersionMojaveOrLater():        return isOSXVersionAtLeast("10.14")
    def isOSXVersionCatalinaOrLater():      return isOSXVersionAtLeast("10.15")
    def isOSXVersionBigSurOrLater():        return isOSXVersionAtLeast("10.16")  # BigSur is officially 11.0, but started at 10.16
    def isOSXVersionMontereyOrLater():      return isOSXVersionAtLeast("12.0")
    def isOSXVersionVenturaOrLater():       return isOSXVersionAtLeast("13.0")

    def get_home_dir():
        homeDir = None

        # noinspection PyBroadException
        try:
            if Platform.isOSX():
                homeDir = System.getProperty(u"UserHome")  # On a Mac in a Java VM, the homedir is hidden
            else:
                # homeDir = System.getProperty("user.home")
                homeDir = os.path.expanduser(u"~")  # Should work on Unix and Windows
                if homeDir is None or homeDir == u"":
                    homeDir = System.getProperty(u"user.home")
                if homeDir is None or homeDir == u"":
                    homeDir = os.environ.get(u"HOMEPATH")
        except:
            pass

        if homeDir is None or homeDir == u"":
            homeDir = MD_REF.getCurrentAccountBook().getRootFolder().getParent()  # Better than nothing!

        if homeDir is None or homeDir == u"":
            homeDir = u""

        myPrint("DB", "Home Directory detected...:", homeDir)
        return homeDir

    def getDecimalPoint():
        decimalFormat = DecimalFormat.getInstance()
        # noinspection PyUnresolvedReferences
        decimalSymbols = decimalFormat.getDecimalFormatSymbols()

        try:
            _decimalCharSep = decimalSymbols.getDecimalSeparator()
            myPrint(u"D",u"Decimal Point Character: %s" %(_decimalCharSep))
            return _decimalCharSep
        except:
            myPrint(u"B",u"Error in getDecimalPoint() routine....?")
            dump_sys_error_to_md_console_and_errorlog()
        return u"error"

    GlobalVars.ALLOWED_CSV_FILE_DELIMITER_STRINGS = [";", "|", ","]
    GlobalVars.decimalCharSep = getDecimalPoint()


    def isMacDarkModeDetected():
        darkResponse = "LIGHT"
        if Platform.isOSX():
            try:
                darkResponse = subprocess.check_output("defaults read -g AppleInterfaceStyle", shell=True)
                darkResponse = darkResponse.strip().lower()
            except: pass
        return ("dark" in darkResponse)

    def isMDThemeDark():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            try:
                if currentTheme.isSystemDark(): return True     # NOTE: Only VAQua has isSystemDark()
            except: pass
            if "dark" in currentTheme.getThemeID().lower(): return True
            if isMDThemeFlatDark(): return True
            if isMDThemeDarcula(): return True
        except: pass
        return False

    def isMDThemeDarcula():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if isMDThemeFlatDark(): return False                    # Flat Dark pretends to be Darcula!
            if "darcula" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeCustomizable():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if currentTheme.isCustomizable(): return True
        except: pass
        return False

    def isMDThemeHighContrast():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "high_contrast" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeDefault():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "default" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeClassic():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "classic" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeSolarizedLight():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "solarized_light" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeSolarizedDark():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "solarized_dark" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeFlatDark():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "flat dark" in currentTheme.toString().lower(): return True
        except: pass
        return False

    def isMDThemeVAQua():
        if Platform.isOSX():
            try:
                # currentTheme = MD_REF.getUI().getCurrentTheme()       # Not reset when changed in-session as it's a final variable!
                # if ".vaqua" in safeStr(currentTheme.getClass()).lower(): return True
                currentTheme = ThemeInfo.themeForID(MD_REF.getUI(), MD_REF.getPreferences().getSetting(GlobalVars.MD_PREFERENCE_KEY_CURRENT_THEME, ThemeInfo.DEFAULT_THEME_ID))
                if ".vaqua" in currentTheme.getClass().getName().lower(): return True                                   # noqa
            except:
                myPrint("B", "@@ Error in isMDThemeVAQua() - Alert author! Error:", sys.exc_info()[1])
        return False

    def isIntelX86_32bit():
        """Detect Intel x86 32bit system"""
        return String(System.getProperty("os.arch", "null").strip()).toLowerCase(Locale.ROOT) == "x86"

    def getMDIcon(startingIcon=None, lAlwaysGetIcon=False):
        if lAlwaysGetIcon or isIntelX86_32bit():
            return MD_REF.getUI().getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")
        return startingIcon

    # JOptionPane.DEFAULT_OPTION, JOptionPane.YES_NO_OPTION, JOptionPane.YES_NO_CANCEL_OPTION, JOptionPane.OK_CANCEL_OPTION
    # JOptionPane.ERROR_MESSAGE, JOptionPane.INFORMATION_MESSAGE, JOptionPane.WARNING_MESSAGE, JOptionPane.QUESTION_MESSAGE, JOptionPane.PLAIN_MESSAGE

    # Copies MD_REF.getUI().showInfoMessage (but a newer version now exists in MD internal code)
    def myPopupInformationBox(theParent=None, theMessage="What no message?!", theTitle="Info", theMessageType=JOptionPane.INFORMATION_MESSAGE):

        if theParent is None and (theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE):
            icon = getMDIcon(lAlwaysGetIcon=True)
        else:
            icon = getMDIcon(None)
        JOptionPane.showMessageDialog(theParent, JTextPanel(theMessage), theTitle, theMessageType, icon)

    def wrapLines(message, numChars=40):
        charCount = 0
        result=""
        for ch in message:
            if ch == '\n' or ch == '\r':
                charCount = 0
            elif charCount > numChars and not Character.isWhitespace(ch):
                result+="\n"
                charCount = 0
            else:
                charCount+=1
            result+=ch
        return result

    def myPopupAskBackup(theParent=None, theMessage="What no message?!", lReturnTheTruth=False):

        _options=["STOP", "PROCEED WITHOUT BACKUP", "DO BACKUP NOW"]
        response = JOptionPane.showOptionDialog(theParent,
                                                theMessage,
                                                "PERFORM BACKUP BEFORE UPDATE?",
                                                0,
                                                JOptionPane.WARNING_MESSAGE,
                                                getMDIcon(),
                                                _options,
                                                _options[0])

        if response == 2:
            myPrint("B", "User requested to create a backup before update/fix - calling Moneydance's 'Export Backup' routine...")
            MD_REF.getUI().setStatus("%s is creating a backup...." %(GlobalVars.thisScriptName),-1.0)
            MD_REF.getUI().saveToBackup(None)
            MD_REF.getUI().setStatus("%s create (export) backup process completed...." %(GlobalVars.thisScriptName),0)
            return True

        elif response == 1:
            myPrint("B", "User DECLINED to create a backup before update/fix...!")
            if not lReturnTheTruth:
                return True

        return False

    # Copied MD_REF.getUI().askQuestion
    def myPopupAskQuestion(theParent=None,
                           theTitle="Question",
                           theQuestion="What?",
                           theOptionType=JOptionPane.YES_NO_OPTION,
                           theMessageType=JOptionPane.QUESTION_MESSAGE):

        if theParent is None and (theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE):
            icon = getMDIcon(lAlwaysGetIcon=True)
        else:
            icon = getMDIcon(None)

        # question = wrapLines(theQuestion)
        question = theQuestion
        result = JOptionPane.showConfirmDialog(theParent,
                                               question,
                                               theTitle,
                                               theOptionType,
                                               theMessageType,
                                               icon)
        return result == 0

    # Copies Moneydance .askForQuestion
    def myPopupAskForInput(theParent,
                           theTitle,
                           theFieldLabel,
                           theFieldDescription="",
                           defaultValue=None,
                           isPassword=False,
                           theMessageType=JOptionPane.INFORMATION_MESSAGE):

        if theParent is None and (theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE):
            icon = getMDIcon(lAlwaysGetIcon=True)
        else:
            icon = getMDIcon(None)

        p = JPanel(GridBagLayout())
        defaultText = None
        if defaultValue: defaultText = defaultValue
        if isPassword:
            field = JPasswordField(defaultText)
        else:
            field = JTextField(defaultText)
        field.addAncestorListener(RequestFocusListener())

        _x = 0
        if theFieldLabel:
            p.add(JLabel(theFieldLabel), GridC.getc(_x, 0).east())
            _x+=1

        p.add(field, GridC.getc(_x, 0).field())
        p.add(Box.createHorizontalStrut(244), GridC.getc(_x, 0))
        if theFieldDescription:
            p.add(JTextPanel(theFieldDescription), GridC.getc(_x, 1).field().colspan(_x + 1))
        if (JOptionPane.showConfirmDialog(theParent,
                                          p,
                                          theTitle,
                                          JOptionPane.OK_CANCEL_OPTION,
                                          theMessageType,
                                          icon) == 0):
            return field.getText()
        return None

    # APPLICATION_MODAL, DOCUMENT_MODAL, MODELESS, TOOLKIT_MODAL
    class MyPopUpDialogBox():

        def __init__(self,
                     theParent=None,
                     theStatus="",
                     theMessage="",
                     maxSize=Dimension(0,0),
                     theTitle="Info",
                     lModal=True,
                     lCancelButton=False,
                     OKButtonText="OK",
                     lAlertLevel=0):

            self.theParent = theParent
            self.theStatus = theStatus
            self.theMessage = theMessage
            self.maxSize = maxSize
            self.theTitle = theTitle
            self.lModal = lModal
            self.lCancelButton = lCancelButton
            self.OKButtonText = OKButtonText
            self.lAlertLevel = lAlertLevel
            self.fakeJFrame = None
            self._popup_d = None
            self.lResult = [None]
            self.statusLabel = None
            self.messageJText = None
            if not self.theMessage.endswith("\n"): self.theMessage+="\n"
            if self.OKButtonText == "": self.OKButtonText="OK"
            if isMDThemeDark() or isMacDarkModeDetected(): self.lAlertLevel = 0

        def updateMessages(self, newTitle=None, newStatus=None, newMessage=None, lPack=True):
            # We wait when on the EDT as most scripts execute on the EDT.. So this is probably an in execution update message
            # ... if we invokeLater() then the message will (probably) only appear after the EDT script finishes....
            genericSwingEDTRunner(False, True, self._updateMessages, newTitle, newStatus, newMessage, lPack)

        def _updateMessages(self, newTitle=None, newStatus=None, newMessage=None, lPack=True):
            if not newTitle and not newStatus and not newMessage: return
            if newTitle:
                self.theTitle = newTitle
                self._popup_d.setTitle(self.theTitle)
            if newStatus:
                self.theStatus = newStatus
                self.statusLabel.setText(self.theStatus)
            if newMessage:
                self.theMessage = newMessage
                self.messageJText.setText(self.theMessage)
            if lPack: self._popup_d.pack()

        class WindowListener(WindowAdapter):

            def __init__(self, theDialog, theFakeFrame, lResult):
                self.theDialog = theDialog
                self.theFakeFrame = theFakeFrame
                self.lResult = lResult

            def windowClosing(self, WindowEvent):                                                                       # noqa
                myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", WindowEvent)
                myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                myPrint("DB", "JDialog Frame shutting down....")

                self.lResult[0] = False

                # Note - listeners are already on the EDT
                if self.theFakeFrame is not None:
                    self.theDialog.dispose()
                    self.theFakeFrame.dispose()
                else:
                    self.theDialog.dispose()

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class OKButtonAction(AbstractAction):

            def __init__(self, theDialog, theFakeFrame, lResult):
                self.theDialog = theDialog
                self.theFakeFrame = theFakeFrame
                self.lResult = lResult

            def actionPerformed(self, event):
                myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event)
                myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                self.lResult[0] = True

                # Note - listeners are already on the EDT
                if self.theFakeFrame is not None:
                    self.theDialog.dispose()
                    self.theFakeFrame.dispose()
                else:
                    self.theDialog.dispose()

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class CancelButtonAction(AbstractAction):

            def __init__(self, theDialog, theFakeFrame, lResult):
                self.theDialog = theDialog
                self.theFakeFrame = theFakeFrame
                self.lResult = lResult

            def actionPerformed(self, event):
                myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event)
                myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                self.lResult[0] = False

                # Note - listeners are already on the EDT
                if self.theFakeFrame is not None:
                    self.theDialog.dispose()
                    self.theFakeFrame.dispose()
                else:
                    self.theDialog.dispose()

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        def kill(self):
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

            if not SwingUtilities.isEventDispatchThread():
                SwingUtilities.invokeLater(GenericVisibleRunnable(self._popup_d, False))
                if self.fakeJFrame is not None:
                    SwingUtilities.invokeLater(GenericDisposeRunnable(self._popup_d))
                    SwingUtilities.invokeLater(GenericDisposeRunnable(self.fakeJFrame))
                else:
                    SwingUtilities.invokeLater(GenericDisposeRunnable(self._popup_d))
            else:
                self._popup_d.setVisible(False)
                if self.fakeJFrame is not None:
                    self._popup_d.dispose()
                    self.fakeJFrame.dispose()
                else:
                    self._popup_d.dispose()

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        def result(self): return self.lResult[0]

        def go(self):
            myPrint("DB", "In MyPopUpDialogBox.", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

            class MyPopUpDialogBoxRunnable(Runnable):
                def __init__(self, callingClass):
                    self.callingClass = callingClass

                def run(self):                                                                                          # noqa
                    myPrint("DB", "In MyPopUpDialogBoxRunnable.", inspect.currentframe().f_code.co_name, "()")
                    myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                    # Create a fake JFrame so we can set the Icons...
                    if self.callingClass.theParent is None:
                        self.callingClass.fakeJFrame = MyJFrame()
                        self.callingClass.fakeJFrame.setName(u"%s_fake_dialog" %(myModuleID))
                        self.callingClass.fakeJFrame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)
                        self.callingClass.fakeJFrame.setUndecorated(True)
                        self.callingClass.fakeJFrame.setVisible(False)
                        if not Platform.isOSX():
                            self.callingClass.fakeJFrame.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))

                    class MyJDialog(JDialog):
                        def __init__(self, maxSize, *args):
                            self.maxSize = maxSize                                                                      # type: Dimension
                            super(self.__class__, self).__init__(*args)

                        # On Windows, the height was exceeding the screen height when default size of Dimension (0,0), so set the max....
                        def getPreferredSize(self):
                            calcPrefSize = super(self.__class__, self).getPreferredSize()
                            newPrefSize = Dimension(min(calcPrefSize.width, self.maxSize.width), min(calcPrefSize.height, self.maxSize.height))
                            return newPrefSize

                    screenSize = Toolkit.getDefaultToolkit().getScreenSize()

                    if isinstance(self.callingClass.maxSize, Dimension)\
                            and self.callingClass.maxSize.height and self.callingClass.maxSize.width:
                        maxDialogWidth = min(screenSize.width-20, self.callingClass.maxSize.width)
                        maxDialogHeight = min(screenSize.height-40, self.callingClass.maxSize.height)
                        maxDimension = Dimension(maxDialogWidth,maxDialogHeight)
                    else:
                        maxDialogWidth = min(screenSize.width-20, max(GetFirstMainFrame.DEFAULT_MAX_WIDTH, int(round(GetFirstMainFrame.getSize().width *.9,0))))
                        maxDialogHeight = min(screenSize.height-40, max(GetFirstMainFrame.DEFAULT_MAX_WIDTH, int(round(GetFirstMainFrame.getSize().height *.9,0))))
                        maxDimension = Dimension(maxDialogWidth,maxDialogHeight)

                    # noinspection PyUnresolvedReferences
                    self.callingClass._popup_d = MyJDialog(maxDimension,
                                                           self.callingClass.theParent, self.callingClass.theTitle,
                                                           Dialog.ModalityType.APPLICATION_MODAL if (self.callingClass.lModal) else Dialog.ModalityType.MODELESS)

                    self.callingClass._popup_d.getContentPane().setLayout(BorderLayout())
                    self.callingClass._popup_d.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)

                    shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()

                    # Add standard CMD-W keystrokes etc to close window
                    self.callingClass._popup_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
                    self.callingClass._popup_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
                    self.callingClass._popup_d.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")
                    self.callingClass._popup_d.getRootPane().getActionMap().put("close-window", self.callingClass.CancelButtonAction(self.callingClass._popup_d, self.callingClass.fakeJFrame,self.callingClass.lResult))
                    self.callingClass._popup_d.addWindowListener(self.callingClass.WindowListener(self.callingClass._popup_d, self.callingClass.fakeJFrame,self.callingClass.lResult))

                    if (not Platform.isMac()):
                        # MD_REF.getUI().getImages()
                        self.callingClass._popup_d.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))

                    self.callingClass.messageJText = JTextArea(self.callingClass.theMessage)
                    self.callingClass.messageJText.setFont(getMonoFont())
                    self.callingClass.messageJText.setEditable(False)
                    self.callingClass.messageJText.setLineWrap(False)
                    self.callingClass.messageJText.setWrapStyleWord(False)

                    _popupPanel = JPanel(BorderLayout())
                    _popupPanel.setBorder(EmptyBorder(8, 8, 8, 8))

                    if self.callingClass.theStatus:
                        _statusPnl = JPanel(BorderLayout())
                        self.callingClass.statusLabel = JLabel(self.callingClass.theStatus)
                        self.callingClass.statusLabel.setForeground(getColorBlue())
                        self.callingClass.statusLabel.setBorder(EmptyBorder(8, 0, 8, 0))
                        _popupPanel.add(self.callingClass.statusLabel, BorderLayout.NORTH)

                    myScrollPane = JScrollPane(self.callingClass.messageJText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
                    myScrollPane.setWheelScrollingEnabled(True)
                    _popupPanel.add(myScrollPane, BorderLayout.CENTER)

                    buttonPanel = JPanel()
                    if self.callingClass.lModal or self.callingClass.lCancelButton:
                        buttonPanel.setLayout(FlowLayout(FlowLayout.CENTER))

                        if self.callingClass.lCancelButton:
                            cancel_button = JButton("CANCEL")
                            cancel_button.setPreferredSize(Dimension(100,40))
                            cancel_button.setBackground(Color.LIGHT_GRAY)
                            cancel_button.setBorderPainted(False)
                            cancel_button.setOpaque(True)
                            cancel_button.setBorder(EmptyBorder(8, 8, 8, 8))

                            cancel_button.addActionListener(self.callingClass.CancelButtonAction(self.callingClass._popup_d, self.callingClass.fakeJFrame,self.callingClass.lResult) )
                            buttonPanel.add(cancel_button)

                        if self.callingClass.lModal:
                            ok_button = JButton(self.callingClass.OKButtonText)
                            if len(self.callingClass.OKButtonText) <= 2:
                                ok_button.setPreferredSize(Dimension(100,40))
                            else:
                                ok_button.setPreferredSize(Dimension(200,40))

                            ok_button.setBackground(Color.LIGHT_GRAY)
                            ok_button.setBorderPainted(False)
                            ok_button.setOpaque(True)
                            ok_button.setBorder(EmptyBorder(8, 8, 8, 8))
                            ok_button.addActionListener( self.callingClass.OKButtonAction(self.callingClass._popup_d, self.callingClass.fakeJFrame, self.callingClass.lResult) )
                            buttonPanel.add(ok_button)

                        _popupPanel.add(buttonPanel, BorderLayout.SOUTH)

                    if self.callingClass.lAlertLevel >= 2:
                        # internalScrollPane.setBackground(Color.RED)
                        self.callingClass.messageJText.setBackground(Color.RED)
                        self.callingClass.messageJText.setForeground(Color.BLACK)
                        self.callingClass.messageJText.setOpaque(True)
                        _popupPanel.setBackground(Color.RED)
                        _popupPanel.setForeground(Color.BLACK)
                        _popupPanel.setOpaque(True)
                        buttonPanel.setBackground(Color.RED)
                        buttonPanel.setOpaque(True)

                    elif self.callingClass.lAlertLevel >= 1:
                        # internalScrollPane.setBackground(Color.YELLOW)
                        self.callingClass.messageJText.setBackground(Color.YELLOW)
                        self.callingClass.messageJText.setForeground(Color.BLACK)
                        self.callingClass.messageJText.setOpaque(True)
                        _popupPanel.setBackground(Color.YELLOW)
                        _popupPanel.setForeground(Color.BLACK)
                        _popupPanel.setOpaque(True)
                        buttonPanel.setBackground(Color.YELLOW)
                        buttonPanel.setOpaque(True)

                    self.callingClass._popup_d.add(_popupPanel, BorderLayout.CENTER)
                    self.callingClass._popup_d.pack()
                    self.callingClass._popup_d.setLocationRelativeTo(self.callingClass.theParent)
                    self.callingClass._popup_d.setVisible(True)

            if not SwingUtilities.isEventDispatchThread():
                if not self.lModal:
                    myPrint("DB",".. Not running on the EDT, but also NOT Modal, so will .invokeLater::MyPopUpDialogBoxRunnable()...")
                    SwingUtilities.invokeLater(MyPopUpDialogBoxRunnable(self))
                else:
                    myPrint("DB",".. Not running on the EDT so calling .invokeAndWait::MyPopUpDialogBoxRunnable()...")
                    SwingUtilities.invokeAndWait(MyPopUpDialogBoxRunnable(self))
            else:
                myPrint("DB",".. Already on the EDT, just executing::MyPopUpDialogBoxRunnable() now...")
                MyPopUpDialogBoxRunnable(self).run()

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

            return self.lResult[0]

    def play_the_money_sound():

        # Seems to cause a crash on Virtual Machine with no Audio - so just in case....
        try:
            if MD_REF.getPreferences().getSetting("beep_on_transaction_change", "y") == "y":
                MD_REF.getUI().getSounds().playSound("cash_register.wav")
        except:
            pass

        return

    def get_filename_addition():

        cal = Calendar.getInstance()
        hhmm = str(10000 + cal.get(11) * 100 + cal.get(12))[1:]
        nameAddition = "-" + str(DateUtil.getStrippedDateInt()) + "-"+hhmm

        return nameAddition

    def check_file_writable(fnm):
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )
        myPrint("DB","Checking path: ", fnm)

        if os.path.exists(fnm):
            myPrint("DB", "path exists..")
            # path exists
            if os.path.isfile(fnm):  # is it a file or a dir?
                myPrint("DB","path is a file..")
                # also works when file is a link and the target is writable
                return os.access(fnm, os.W_OK)
            else:
                myPrint("DB", "path is not a file..")
                return False  # path is a dir, so cannot write as a file
        # target does not exist, check perms on parent dir
        myPrint("DB","path does not exist...")
        pdir = os.path.dirname(fnm)
        if not pdir: pdir = '.'
        # target is creatable if parent dir is writable
        return os.access(pdir, os.W_OK)

    class ExtFilenameFilter(FilenameFilter):
        """File extension filter for FileDialog"""
        def __init__(self, ext): self.ext = "." + ext.upper()                                                           # noqa

        def accept(self, thedir, filename):                                                                             # noqa
            # type: (File, str) -> bool
            if filename is not None and filename.upper().endswith(self.ext): return True
            return False

    class ExtFileFilterJFC(FileFilter):
        """File extension filter for JFileChooser"""
        def __init__(self, ext): self.ext = "." + ext.upper()

        def getDescription(self): return "*"+self.ext                                                                   # noqa

        def accept(self, _theFile):                                                                                     # noqa
            # type: (File) -> bool
            if _theFile is None: return False
            if _theFile.isDirectory(): return True
            return _theFile.getName().upper().endswith(self.ext)

    def MDDiag():
        myPrint("D", "Moneydance Build:", MD_REF.getVersion(), "Build:", MD_REF.getBuild())


    MDDiag()

    myPrint("DB","System file encoding is:", sys.getfilesystemencoding() )   # Not used, but interesting. Perhaps useful when switching between Windows/Macs and writing files...

    def checkVersions():
        lError = False
        plat_j = platform.system()
        plat_p = platform.python_implementation()
        python_maj = sys.version_info.major
        python_min = sys.version_info.minor

        myPrint("DB","Platform:", plat_p, plat_j, python_maj, ".", python_min)
        myPrint("DB", sys.version)

        if plat_p != "Jython":
            lError = True
            myPrint("DB", "Error: Script requires Jython")
        if plat_j != "Java":
            lError = True
            myPrint("DB", "Error: Script requires Java  base")
        if (python_maj != 2 or python_min != 7):
            lError = True
            myPrint("DB", "\n\nError: Script was  designed on version 2.7. By all means bypass this test and see what happens.....")

        if lError:
            myPrint("J", "Platform version issue - will terminate script!")
            myPrint("P", "\n@@@ TERMINATING PROGRAM @@@\n")
            raise(Exception("Platform version issue - will terminate script!"))

        return not lError


    checkVersions()

    def setDefaultFonts():
        """Grabs the MD defaultText font, reduces default size down to below 18, sets UIManager defaults (if runtime extension, will probably error, so I catch and skip)"""
        if MD_REF_UI is None: return

        # If a runtime extension, then this may fail, depending on timing... Just ignore and return...
        try:
            myFont = MD_REF.getUI().getFonts().defaultText
        except:
            myPrint("B","ERROR trying to call .getUI().getFonts().defaultText - skipping setDefaultFonts()")
            return

        if myFont is None:
            myPrint("B","WARNING: In setDefaultFonts(): calling .getUI().getFonts().defaultText has returned None (but moneydance_ui was set) - skipping setDefaultFonts()")
            return

        if myFont.getSize()>18:
            try:
                myFont = myFont.deriveFont(16.0)
                myPrint("B", "I have reduced the font size down to point-size 16 - Default Fonts are now set to: %s" %(myFont))
            except:
                myPrint("B","ERROR - failed to override font point size down to 16.... will ignore and continue. Font set to: %s" %(myFont))
        else:
            myPrint("DB", "Attempting to set default font to %s" %myFont)

        try:
            UIManager.getLookAndFeelDefaults().put("defaultFont", myFont )

            # https://thebadprogrammer.com/swing-uimanager-keys/
            UIManager.put("CheckBoxMenuItem.acceleratorFont", myFont)
            UIManager.put("Button.font", myFont)
            UIManager.put("ToggleButton.font", myFont)
            UIManager.put("RadioButton.font", myFont)
            UIManager.put("CheckBox.font", myFont)
            UIManager.put("ColorChooser.font", myFont)
            UIManager.put("ComboBox.font", myFont)
            UIManager.put("Label.font", myFont)
            UIManager.put("List.font", myFont)
            UIManager.put("MenuBar.font", myFont)
            UIManager.put("Menu.acceleratorFont", myFont)
            UIManager.put("RadioButtonMenuItem.acceleratorFont", myFont)
            UIManager.put("MenuItem.acceleratorFont", myFont)
            UIManager.put("MenuItem.font", myFont)
            UIManager.put("RadioButtonMenuItem.font", myFont)
            UIManager.put("CheckBoxMenuItem.font", myFont)
            UIManager.put("OptionPane.buttonFont", myFont)
            UIManager.put("OptionPane.messageFont", myFont)
            UIManager.put("Menu.font", myFont)
            UIManager.put("PopupMenu.font", myFont)
            UIManager.put("OptionPane.font", myFont)
            UIManager.put("Panel.font", myFont)
            UIManager.put("ProgressBar.font", myFont)
            UIManager.put("ScrollPane.font", myFont)
            UIManager.put("Viewport.font", myFont)
            UIManager.put("TabbedPane.font", myFont)
            UIManager.put("Slider.font", myFont)
            UIManager.put("Table.font", myFont)
            UIManager.put("TableHeader.font", myFont)
            UIManager.put("TextField.font", myFont)
            UIManager.put("Spinner.font", myFont)
            UIManager.put("PasswordField.font", myFont)
            UIManager.put("TextArea.font", myFont)
            UIManager.put("TextPane.font", myFont)
            UIManager.put("EditorPane.font", myFont)
            UIManager.put("TabbedPane.smallFont", myFont)
            UIManager.put("TitledBorder.font", myFont)
            UIManager.put("ToolBar.font", myFont)
            UIManager.put("ToolTip.font", myFont)
            UIManager.put("Tree.font", myFont)
            UIManager.put("FormattedTextField.font", myFont)
            UIManager.put("IconButton.font", myFont)
            UIManager.put("InternalFrame.optionDialogTitleFont", myFont)
            UIManager.put("InternalFrame.paletteTitleFont", myFont)
            UIManager.put("InternalFrame.titleFont", myFont)
        except:
            myPrint("B","Failed to set Swing default fonts to use Moneydance defaults... sorry")

        myPrint("DB",".setDefaultFonts() successfully executed...")
        return

    setDefaultFonts()

    def who_am_i():
        try: username = System.getProperty("user.name")
        except: username = "???"
        return username

    def getHomeDir():
        # Yup - this can be all over the place...
        myPrint("D", 'System.getProperty("user.dir")', System.getProperty("user.dir"))
        myPrint("D", 'System.getProperty("UserHome")', System.getProperty("UserHome"))
        myPrint("D", 'System.getProperty("user.home")', System.getProperty("user.home"))
        myPrint("D", 'os.path.expanduser("~")', os.path.expanduser("~"))
        myPrint("D", 'os.environ.get("HOMEPATH")', os.environ.get("HOMEPATH"))
        return

    myPrint("D", "I am user:", who_am_i())
    if debug: getHomeDir()

    # noinspection PyArgumentList
    class JTextFieldLimitYN(PlainDocument):

        limit = 10  # Default
        toUpper = False
        what = ""

        def __init__(self, limit, toUpper, what):

            super(PlainDocument, self).__init__()
            self.limit = limit
            self.toUpper = toUpper
            self.what = what

        def insertString(self, myOffset, myString, myAttr):

            if (myString is None): return
            if self.toUpper: myString = myString.upper()
            if (self.what == "YN" and (myString in "YN")) \
                    or (self.what == "DELIM" and (myString in ";|,")) \
                    or (self.what == "1234" and (myString in "1234")) \
                    or (self.what == "CURR"):
                if ((self.getLength() + len(myString)) <= self.limit):
                    super(JTextFieldLimitYN, self).insertString(myOffset, myString, myAttr)                             # noqa

    def fix_delimiter( theDelimiter ):

        try:
            if sys.version_info.major >= 3: return theDelimiter
            if sys.version_info.major <  2: return str(theDelimiter)

            if sys.version_info.minor >  7: return theDelimiter
            if sys.version_info.minor <  7: return str(theDelimiter)

            if sys.version_info.micro >= 2: return theDelimiter
        except:
            pass

        return str( theDelimiter )

    def get_StuWareSoftSystems_parameters_from_file(myFile="StuWareSoftSystems.dict"):
        global debug    # This global for debug must be here as we set it from loaded parameters

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        if GlobalVars.resetPickleParameters:
            myPrint("B", "User has specified to reset parameters... keeping defaults and skipping pickle()")
            GlobalVars.parametersLoadedFromFile = {}
            return

        migratedFilename = os.path.join(MD_REF.getCurrentAccountBook().getRootFolder().getAbsolutePath(), myFile)

        myPrint("DB", "Now checking for parameter file:", migratedFilename)

        if os.path.exists(migratedFilename):
            myPrint("DB", "loading parameters from (non-encrypted) Pickle file:", migratedFilename)
            myPrint("DB", "Parameter file", migratedFilename, "exists..")
            # Open the file
            try:
                # Really we should open() the file in binary mode and read/write as binary, then we wouldn't get platform differences!
                istr = FileInputStream(migratedFilename)
                load_file = FileUtil.wrap(istr)
                if not Platform.isWindows():
                    load_string = load_file.read().replace('\r', '')    # This allows for files migrated from windows (strip the extra CR)
                else:
                    load_string = load_file.read()

                GlobalVars.parametersLoadedFromFile = pickle.loads(load_string)
                load_file.close()
            except FileNotFoundException:
                myPrint("B", "Error: failed to find parameter file...")
                GlobalVars.parametersLoadedFromFile = None
            except EOFError:
                myPrint("B", "Error: reached EOF on parameter file....")
                GlobalVars.parametersLoadedFromFile = None
            except:
                myPrint("B", "Error opening Pickle File Unexpected error:", sys.exc_info()[0], "Error:", sys.exc_info()[1], "Line:", sys.exc_info()[2].tb_lineno)
                myPrint("B", ">> Will ignore saved parameters, and create a new file...")
                GlobalVars.parametersLoadedFromFile = None

            if GlobalVars.parametersLoadedFromFile is None:
                GlobalVars.parametersLoadedFromFile = {}
                myPrint("DB","Parameters did NOT load, will use defaults..")
            else:
                myPrint("DB","Parameters successfully loaded from file...")
        else:
            myPrint("DB", "Parameter Pickle file does NOT exist - will use default and create new file..")
            GlobalVars.parametersLoadedFromFile = {}

        if not GlobalVars.parametersLoadedFromFile: return

        myPrint("DB","GlobalVars.parametersLoadedFromFile read from file contains...:")
        for key in sorted(GlobalVars.parametersLoadedFromFile.keys()):
            myPrint("DB","...variable:", key, GlobalVars.parametersLoadedFromFile[key])

        if GlobalVars.parametersLoadedFromFile.get("debug") is not None: debug = GlobalVars.parametersLoadedFromFile.get("debug")

        myPrint("DB","Parameter file loaded if present and GlobalVars.parametersLoadedFromFile{} dictionary set.....")

        # Now load into memory!
        load_StuWareSoftSystems_parameters_into_memory()

        return

    def save_StuWareSoftSystems_parameters_to_file(myFile="StuWareSoftSystems.dict"):
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}

        # Don't forget, any parameters loaded earlier will be preserved; just add changed variables....
        GlobalVars.parametersLoadedFromFile["__Author"] = "Stuart Beesley - (c) StuWareSoftSystems"
        GlobalVars.parametersLoadedFromFile["debug"] = debug

        dump_StuWareSoftSystems_parameters_from_memory()

        # Pickle was originally encrypted, no need, migrating to unencrypted
        migratedFilename = os.path.join(MD_REF.getCurrentAccountBook().getRootFolder().getAbsolutePath(),myFile)

        myPrint("DB","Will try to save parameter file:", migratedFilename)

        ostr = FileOutputStream(migratedFilename)

        myPrint("DB", "about to Pickle.dump and save parameters to unencrypted file:", migratedFilename)

        try:
            save_file = FileUtil.wrap(ostr)
            pickle.dump(GlobalVars.parametersLoadedFromFile, save_file, protocol=0)
            save_file.close()

            myPrint("DB","GlobalVars.parametersLoadedFromFile now contains...:")
            for key in sorted(GlobalVars.parametersLoadedFromFile.keys()):
                myPrint("DB","...variable:", key, GlobalVars.parametersLoadedFromFile[key])

        except:
            myPrint("B", "Error - failed to create/write parameter file.. Ignoring and continuing.....")
            dump_sys_error_to_md_console_and_errorlog()

            return

        myPrint("DB","Parameter file written and parameters saved to disk.....")

        return

    def get_time_stamp_as_nice_text(timeStamp, _format=None, lUseHHMMSS=True):

        if _format is None: _format = MD_REF.getPreferences().getShortDateFormat()

        humanReadableDate = ""
        try:
            c = Calendar.getInstance()
            c.setTime(Date(timeStamp))
            longHHMMSSText = " HH:mm:ss(.SSS) Z z zzzz" if (lUseHHMMSS) else ""
            dateFormatter = SimpleDateFormat("%s%s" %(_format, longHHMMSSText))
            humanReadableDate = dateFormatter.format(c.getTime())
        except: pass
        return humanReadableDate

    def currentDateTimeMarker():
        c = Calendar.getInstance()
        dateformat = SimpleDateFormat("_yyyyMMdd_HHmmss")
        _datetime = dateformat.format(c.getTime())
        return _datetime

    def destroyOldFrames(moduleName):
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
        myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))
        frames = JFrame.getFrames()
        for fr in frames:
            if fr.getName().lower().startswith(moduleName+"_"):
                myPrint("DB","Found old frame %s and active status is: %s" %(fr.getName(),fr.isActiveInMoneydance))
                try:
                    fr.isActiveInMoneydance = False
                    if not SwingUtilities.isEventDispatchThread():
                        SwingUtilities.invokeLater(GenericVisibleRunnable(fr, False, False))
                        SwingUtilities.invokeLater(GenericDisposeRunnable(fr))  # This should call windowClosed() which should remove MD listeners.....
                    else:
                        fr.setVisible(False)
                        fr.dispose()            # This should call windowClosed() which should remove MD listeners.....
                    myPrint("DB","disposed of old frame: %s" %(fr.getName()))
                except:
                    myPrint("B","Failed to dispose old frame: %s" %(fr.getName()))
                    dump_sys_error_to_md_console_and_errorlog()

    def classPrinter(className, theObject):
        try:
            text = "Class: %s %s@{:x}".format(System.identityHashCode(theObject)) %(className, theObject.__class__)
        except:
            text = "Error in classPrinter(): %s: %s" %(className, theObject)
        return text

    def getColorBlue():
        # if not isMDThemeDark() and not isMacDarkModeDetected(): return(MD_REF.getUI().getColors().reportBlueFG)
        # return (MD_REF.getUI().getColors().defaultTextForeground)
        return MD_REF.getUI().getColors().reportBlueFG

    def getColorRed(): return (MD_REF.getUI().getColors().errorMessageForeground)

    def getColorDarkGreen(): return (MD_REF.getUI().getColors().budgetHealthyColor)

    def setDisplayStatus(_theStatus, _theColor=None):
        """Sets the Display / Status label on the main diagnostic display: G=Green, B=Blue, R=Red, DG=Dark Green"""

        if GlobalVars.STATUS_LABEL is None or not isinstance(GlobalVars.STATUS_LABEL, JLabel): return

        class SetDisplayStatusRunnable(Runnable):
            def __init__(self, _status, _color):
                self.status = _status; self.color = _color

            def run(self):
                GlobalVars.STATUS_LABEL.setText((_theStatus))
                if self.color is None or self.color == "": self.color = "X"
                self.color = self.color.upper()
                if self.color == "R":    GlobalVars.STATUS_LABEL.setForeground(getColorRed())
                elif self.color == "B":  GlobalVars.STATUS_LABEL.setForeground(getColorBlue())
                elif self.color == "DG": GlobalVars.STATUS_LABEL.setForeground(getColorDarkGreen())
                else:                    GlobalVars.STATUS_LABEL.setForeground(MD_REF.getUI().getColors().defaultTextForeground)

        if not SwingUtilities.isEventDispatchThread():
            SwingUtilities.invokeLater(SetDisplayStatusRunnable(_theStatus, _theColor))
        else:
            SetDisplayStatusRunnable(_theStatus, _theColor).run()

    def setJFileChooserParameters(_jf, lReportOnly=False, lDefaults=False, lPackagesT=None, lApplicationsT=None, lOptionsButton=None, lNewFolderButton=None):
        """sets up Client Properties for JFileChooser() to behave as required >> Mac only"""

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if not Platform.isOSX(): return
        if not isinstance(_jf, JFileChooser): return

        _PKG = "JFileChooser.packageIsTraversable"
        _APP = "JFileChooser.appBundleIsTraversable"
        _OPTIONS = "JFileChooser.optionsPanelEnabled"
        _NEWFOLDER = "JFileChooser.canCreateDirectories"

        # JFileChooser defaults: https://violetlib.org/vaqua/filechooser.html
        # "JFileChooser.packageIsTraversable"   default False   >> set "true" to allow Packages to be traversed
        # "JFileChooser.appBundleIsTraversable" default False   >> set "true" to allow App Bundles to be traversed
        # "JFileChooser.optionsPanelEnabled"    default False   >> set "true" to allow Options button
        # "JFileChooser.canCreateDirectories"   default False   >> set "true" to allow New Folder button

        if debug or lReportOnly:
            myPrint("B", "Parameters set: ReportOnly: %s, Defaults:%s, PackagesT: %s, ApplicationsT:%s, OptionButton:%s, NewFolderButton: %s" %(lReportOnly, lDefaults, lPackagesT, lApplicationsT, lOptionsButton, lNewFolderButton))
            txt = ("Before setting" if not lReportOnly else "Reporting only")
            for setting in [_PKG, _APP, _OPTIONS, _NEWFOLDER]: myPrint("DB", "%s: '%s': '%s'" %(pad(txt,14), pad(setting,50), _jf.getClientProperty(setting)))
            if lReportOnly: return

        if lDefaults:
            _jf.putClientProperty(_PKG, None)
            _jf.putClientProperty(_APP, None)
            _jf.putClientProperty(_OPTIONS, None)
            _jf.putClientProperty(_NEWFOLDER, None)
        else:
            if lPackagesT       is not None: _jf.putClientProperty(_PKG, lPackagesT)
            if lApplicationsT   is not None: _jf.putClientProperty(_APP, lApplicationsT)
            if lOptionsButton   is not None: _jf.putClientProperty(_OPTIONS, lOptionsButton)
            if lNewFolderButton is not None: _jf.putClientProperty(_NEWFOLDER, lNewFolderButton)

        for setting in [_PKG, _APP, _OPTIONS, _NEWFOLDER]: myPrint("DB", "%s: '%s': '%s'" %(pad("After setting",14), pad(setting,50), _jf.getClientProperty(setting)))

        return

    def setFileDialogParameters(lReportOnly=False, lDefaults=False, lSelectDirectories=None, lPackagesT=None):
        """sets up System Properties for FileDialog() to behave as required >> Mac only"""

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if not Platform.isOSX(): return

        _TRUE = "true"
        _FALSE = "false"

        _DIRS_FD = "apple.awt.fileDialogForDirectories"        # When True you can select a Folder (rather than a file)
        _PKGS_FD = "apple.awt.use-file-dialog-packages"        # When True allows you to select a 'bundle' as a file; False means navigate inside the bundle
        # "com.apple.macos.use-file-dialog-packages"           # DEPRECATED since Monterrey - discovered this about MD2022.5(4090) - refer: java.desktop/sun/lwawt/macosx/CFileDialog.java

        # FileDialog defaults
        # "apple.awt.fileDialogForDirectories"       default "false" >> set "true"  to allow Directories to be selected
        # "apple.awt.use-file-dialog-packages"       default "true"  >> set "false" to allow access to Mac 'packages'

        if debug or lReportOnly:
            myPrint("B", "Parameters set: ReportOnly: %s, Defaults:%s, SelectDirectories:%s, PackagesT:%s" % (lReportOnly, lDefaults, lSelectDirectories, lPackagesT))
            txt = ("Before setting" if not lReportOnly else "Reporting only")
            for setting in [_DIRS_FD, _PKGS_FD]: myPrint("DB", "%s: '%s': '%s'" %(pad(txt,14), pad(setting,50), System.getProperty(setting)))
            if lReportOnly: return

        if lDefaults:
            System.setProperty(_DIRS_FD,_FALSE)
            System.setProperty(_PKGS_FD,_TRUE)
        else:
            if lSelectDirectories is not None: System.setProperty(_DIRS_FD, (_TRUE if lSelectDirectories   else _FALSE))
            if lPackagesT         is not None: System.setProperty(_PKGS_FD, (_TRUE if lPackagesT           else _FALSE))

        for setting in [_DIRS_FD, _PKGS_FD]: myPrint("DB", "After setting:  '%s': '%s'" %(pad(setting,50), System.getProperty(setting)))

        return

    def getFileFromFileChooser(fileChooser_parent,                  # The Parent Frame, or None
                               fileChooser_starting_dir,            # The Starting Dir
                               fileChooser_filename,                # Default filename (or None)
                               fileChooser_title,                   # The Title (with FileDialog, only works on SAVE)
                               fileChooser_multiMode,               # Normally False (True has not been coded!)
                               fileChooser_open,                    # True for Open/Load, False for Save
                               fileChooser_selectFiles,             # True for files, False for Directories
                               fileChooser_OK_text,                 # Normally None, unless set - use text
                               fileChooser_fileFilterText=None,     # E.g. "txt" or "qif"
                               lForceJFC=False,
                               lForceFD=False,
                               lAllowTraversePackages=None,
                               lAllowTraverseApplications=None,     # JFileChooser only..
                               lAllowNewFolderButton=True,          # JFileChooser only..
                               lAllowOptionsButton=None):           # JFileChooser only..
        """Launches FileDialog on Mac, or JFileChooser on other platforms... NOTE: Do not use Filter on Macs!"""

        _THIS_METHOD_NAME = "Dynamic File Chooser"

        if fileChooser_multiMode:
            myPrint("B","@@ SORRY Multi File Selection Mode has not been coded! Exiting...")
            return None

        if fileChooser_starting_dir is None or fileChooser_starting_dir == "" or not os.path.exists(fileChooser_starting_dir):
            fileChooser_starting_dir = MD_REF.getPreferences().getSetting("gen.data_dir", None)

        if fileChooser_starting_dir is None or not os.path.exists(fileChooser_starting_dir):
            fileChooser_starting_dir = None
            myPrint("B","ERROR: Starting Path does not exist - will start with no starting path set..")

        else:
            myPrint("DB", "Preparing the Dynamic File Chooser with path: %s" %(fileChooser_starting_dir))
            if Platform.isOSX() and "/Library/Containers/" in fileChooser_starting_dir:
                myPrint("DB", "WARNING: Folder will be restricted by MacOSx...")
                if not lForceJFC:
                    txt = ("FileDialog: MacOSx restricts Java Access to 'special' locations like 'Library\n"
                          "Folder: %s\n"
                          "Please navigate to this location manually in the next popup. This grants permission"
                          %(fileChooser_starting_dir))
                else:
                    txt = ("JFileChooser: MacOSx restricts Java Access to 'special' locations like 'Library\n"
                          "Folder: %s\n"
                          "Your files will probably be hidden.. If so, switch to FileDialog()...(contact author)"
                          %(fileChooser_starting_dir))
                MyPopUpDialogBox(fileChooser_parent,
                                 "NOTE: Mac Security Restriction",
                                 txt,
                                 theTitle=_THIS_METHOD_NAME,
                                 lAlertLevel=1).go()

        if (Platform.isOSX() and not lForceJFC) or lForceFD:

            setFileDialogParameters(lPackagesT=lAllowTraversePackages, lSelectDirectories=(not fileChooser_selectFiles))

            myPrint("DB", "Preparing FileDialog() with path: %s" %(fileChooser_starting_dir))
            if fileChooser_filename is not None: myPrint("DB", "... and filename:                 %s" %(fileChooser_filename))

            fileDialog = FileDialog(fileChooser_parent, fileChooser_title)

            fileDialog.setTitle(fileChooser_title)

            if fileChooser_starting_dir is not None:    fileDialog.setDirectory(fileChooser_starting_dir)
            if fileChooser_filename is not None:        fileDialog.setFile(fileChooser_filename)

            fileDialog.setMultipleMode(fileChooser_multiMode)

            if fileChooser_open:
                fileDialog.setMode(FileDialog.LOAD)
            else:
                fileDialog.setMode(FileDialog.SAVE)

            if fileChooser_fileFilterText is not None and (not Platform.isOSX() or isOSXVersionMontereyOrLater()):
                myPrint("DB",".. Adding file filter for: %s" %(fileChooser_fileFilterText))
                fileDialog.setFilenameFilter(ExtFilenameFilter(fileChooser_fileFilterText))

            fileDialog.setVisible(True)

            setFileDialogParameters(lDefaults=True)

            myPrint("DB", "FileDialog returned File:      %s" %(fileDialog.getFile()))
            myPrint("DB", "FileDialog returned Directory: %s" %(fileDialog.getDirectory()))

            if fileDialog.getFile() is None or fileDialog.getFile() == "": return None

            _theFile = os.path.join(fileDialog.getDirectory(), fileDialog.getFile())

        else:

            myPrint("DB", "Preparing JFileChooser() with path: %s" %(fileChooser_starting_dir))
            if fileChooser_filename is not None: myPrint("DB", "... and filename:                   %s" %(fileChooser_filename))

            if fileChooser_starting_dir is not None:
                jfc = JFileChooser(fileChooser_starting_dir)
            else:
                jfc = JFileChooser()

            if fileChooser_filename is not None: jfc.setSelectedFile(File(fileChooser_filename))
            setJFileChooserParameters(jfc,
                                      lPackagesT=lAllowTraversePackages,
                                      lApplicationsT=lAllowTraverseApplications,
                                      lNewFolderButton=lAllowNewFolderButton,
                                      lOptionsButton=lAllowOptionsButton)

            jfc.setDialogTitle(fileChooser_title)
            jfc.setMultiSelectionEnabled(fileChooser_multiMode)

            if fileChooser_selectFiles:
                jfc.setFileSelectionMode(JFileChooser.FILES_ONLY)         # FILES_ONLY, DIRECTORIES_ONLY, FILES_AND_DIRECTORIES
            else:
                jfc.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)   # FILES_ONLY, DIRECTORIES_ONLY, FILES_AND_DIRECTORIES

            if fileChooser_fileFilterText is not None and (not Platform.isOSX() or isOSXVersionMontereyOrLater()):
                myPrint("DB",".. Adding file filter for: %s" %(fileChooser_fileFilterText))
                jfc.setFileFilter(ExtFileFilterJFC(fileChooser_fileFilterText))

            if fileChooser_OK_text is not None:
                returnValue = jfc.showDialog(fileChooser_parent, fileChooser_OK_text)
            else:
                if fileChooser_open:
                    returnValue = jfc.showOpenDialog(fileChooser_parent)
                else:
                    returnValue = jfc.showSaveDialog(fileChooser_parent)

            if returnValue == JFileChooser.CANCEL_OPTION \
                    or (jfc.getSelectedFile() is None or jfc.getSelectedFile().getName()==""):
                myPrint("DB","JFileChooser was cancelled by user, or no file was selected...")
                return None

            _theFile = jfc.getSelectedFile().getAbsolutePath()
            myPrint("DB","JFileChooser returned File/path..: %s" %(_theFile))

        myPrint("DB","...File/path exists..: %s" %(os.path.exists(_theFile)))
        return _theFile

    class RequestFocusListener(AncestorListener):
        """Add this Listener to a JTextField by using .addAncestorListener(RequestFocusListener()) before calling JOptionPane.showOptionDialog()"""

        def __init__(self, removeListener=True):
            self.removeListener = removeListener

        def ancestorAdded(self, e):
            component = e.getComponent()
            component.requestFocusInWindow()
            component.selectAll()
            if (self.removeListener): component.removeAncestorListener(self)

        def ancestorMoved(self, e): pass
        def ancestorRemoved(self, e): pass

    class SearchAction(AbstractAction):

        def __init__(self, theFrame, searchJText):
            self.theFrame = theFrame
            self.searchJText = searchJText
            self.lastSearch = ""
            self.lastPosn = -1
            self.previousEndPosn = -1
            self.lastDirection = 0

        def actionPerformed(self, event):
            myPrint("D","in SearchAction(), Event: ", event)

            p = JPanel(FlowLayout())
            lbl = JLabel("Enter the search text:")
            tf = JTextField(self.lastSearch,20)
            p.add(lbl)
            p.add(tf)

            tf.addAncestorListener(RequestFocusListener())

            _search_options = [ "Next", "Previous", "Cancel" ]

            defaultDirection = _search_options[self.lastDirection]

            response = JOptionPane.showOptionDialog(self.theFrame,
                                                    p,
                                                    "Search for text",
                                                    JOptionPane.OK_CANCEL_OPTION,
                                                    JOptionPane.QUESTION_MESSAGE,
                                                    getMDIcon(None),
                                                    _search_options,
                                                    defaultDirection)

            lSwitch = False
            if (response == 0 or response == 1):
                if response != self.lastDirection: lSwitch = True
                self.lastDirection = response
                searchWhat = tf.getText()
            else:
                searchWhat = None

            del p, lbl, tf, _search_options

            if not searchWhat or searchWhat == "": return

            theText = self.searchJText.getText().lower()
            highlighter = self.searchJText.getHighlighter()
            highlighter.removeAllHighlights()

            startPos = 0

            if response == 0:
                direction = "[forwards]"
                if searchWhat == self.lastSearch:
                    startPos = self.lastPosn
                    if lSwitch: startPos=startPos+len(searchWhat)+1
                self.lastSearch = searchWhat

                # if startPos+len(searchWhat) >= len(theText):
                #     startPos = 0
                #
                pos = theText.find(searchWhat.lower(),startPos)     # noqa
                myPrint("DB", "Search %s Pos: %s, searchWhat: '%s', startPos: %s, endPos: %s" %(direction, pos, searchWhat,startPos, -1))

            else:
                direction = "[backwards]"
                endPos = len(theText)-1

                if searchWhat == self.lastSearch:
                    if self.previousEndPosn < 0: self.previousEndPosn = len(theText)-1
                    endPos = max(0,self.previousEndPosn)
                    if lSwitch: endPos = max(0,self.lastPosn-1)

                self.lastSearch = searchWhat

                pos = theText.rfind(searchWhat.lower(),startPos,endPos)     # noqa
                myPrint("DB", "Search %s Pos: %s, searchWhat: '%s', startPos: %s, endPos: %s" %(direction, pos, searchWhat,startPos,endPos))

            if pos >= 0:
                self.searchJText.setCaretPosition(pos)
                try:
                    highlighter.addHighlight(pos,min(pos+len(searchWhat),len(theText)),DefaultHighlighter.DefaultPainter)
                except: pass
                if response == 0:
                    self.lastPosn = pos+len(searchWhat)
                    self.previousEndPosn = len(theText)-1
                else:
                    self.lastPosn = pos-len(searchWhat)
                    self.previousEndPosn = pos-1
            else:
                self.lastPosn = 0
                self.previousEndPosn = len(theText)-1
                myPopupInformationBox(self.theFrame,"Searching %s text not found" %direction)

            return

    def saveOutputFile(_theFrame, _theTitle, _fileName, _theText):

        theTitle = "Select location to save the current displayed output... (CANCEL=ABORT)"
        copyToFile = getFileFromFileChooser(_theFrame,          # Parent frame or None
                                            get_home_dir(),     # Starting path
                                            _fileName,          # Default Filename
                                            theTitle,           # Title
                                            False,              # Multi-file selection mode
                                            False,              # True for Open/Load, False for Save
                                            True,               # True = Files, else Dirs
                                            None,               # Load/Save button text, None for defaults
                                            "txt",              # File filter (non Mac only). Example: "txt" or "qif"
                                            lAllowTraversePackages=False,
                                            lForceJFC=False,
                                            lForceFD=True,
                                            lAllowNewFolderButton=True,
                                            lAllowOptionsButton=True)

        if copyToFile is None or copyToFile == "":
            return
        elif not safeStr(copyToFile).endswith(".txt"):
            myPopupInformationBox(_theFrame, "Sorry - please use a .txt file extension when saving output txt")
            return
        elif ".moneydance" in os.path.dirname(copyToFile):
            myPopupInformationBox(_theFrame, "Sorry, please choose a location outside of the Moneydance location")
            return

        if not check_file_writable(copyToFile):
            myPopupInformationBox(_theFrame, "Sorry, that file/location does not appear allowed by the operating system!?")

        toFile = copyToFile
        try:
            with open(toFile, 'w') as f: f.write(_theText)
            myPrint("B", "%s: text output copied to: %s" %(_theTitle, toFile))

            if os.path.exists(toFile):
                play_the_money_sound()
                txt = "%s: Output text saved as requested to: %s" %(_theTitle, toFile)
                setDisplayStatus(txt, "B")
                myPopupInformationBox(_theFrame, txt)
            else:
                txt = "ERROR - failed to write output text to file: %s" %(toFile)
                myPrint("B", txt)
                myPopupInformationBox(_theFrame, txt)
        except:
            txt = "ERROR - failed to write output text to file: %s" %(toFile)
            dump_sys_error_to_md_console_and_errorlog()
            myPopupInformationBox(_theFrame, txt)

        return

    if MD_REF_UI is not None:       # Only action if the UI is loaded - e.g. scripts (not run time extensions)
        try: GlobalVars.defaultPrintFontSize = eval("MD_REF.getUI().getFonts().print.getSize()")   # Do this here as MD_REF disappears after script ends...
        except: GlobalVars.defaultPrintFontSize = 12
    else:
        GlobalVars.defaultPrintFontSize = 12

    ####################################################################################################################
    # PRINTING UTILITIES...: Points to MM, to Inches, to Resolution: Conversion routines etc
    _IN2MM = 25.4; _IN2CM = 2.54; _IN2PT = 72
    def pt2dpi(_pt,_resolution):    return _pt * _resolution / _IN2PT
    def mm2pt(_mm):                 return _mm * _IN2PT / _IN2MM
    def mm2mpt(_mm):                return _mm * 1000 * _IN2PT / _IN2MM
    def pt2mm(_pt):                 return round(_pt * _IN2MM / _IN2PT, 1)
    def mm2in(_mm):                 return _mm / _IN2MM
    def in2mm(_in):                 return _in * _IN2MM
    def in2mpt(_in):                return _in * _IN2PT * 1000
    def in2pt(_in):                 return _in * _IN2PT
    def mpt2in(_mpt):               return _mpt / _IN2PT / 1000
    def mm2px(_mm, _resolution):    return mm2in(_mm) * _resolution
    def mpt2px(_mpt, _resolution):  return mpt2in(_mpt) * _resolution

    def printDeducePrintableWidth(_thePageFormat, _pAttrs):

        _BUFFER_PCT = 0.95

        myPrint("DB", "PageFormat after user dialog: Portrait=%s Landscape=%s W: %sMM(%spts) H: %sMM(%spts) Paper: %s Paper W: %sMM(%spts) H: %sMM(%spts)"
                %(_thePageFormat.getOrientation()==_thePageFormat.PORTRAIT, _thePageFormat.getOrientation()==_thePageFormat.LANDSCAPE,
                  pt2mm(_thePageFormat.getWidth()),_thePageFormat.getWidth(), pt2mm(_thePageFormat.getHeight()),_thePageFormat.getHeight(),
                  _thePageFormat.getPaper(),
                  pt2mm(_thePageFormat.getPaper().getWidth()), _thePageFormat.getPaper().getWidth(), pt2mm(_thePageFormat.getPaper().getHeight()), _thePageFormat.getPaper().getHeight()))

        if _pAttrs.get(attribute.standard.MediaSizeName):
            myPrint("DB", "Requested Media: %s" %(_pAttrs.get(attribute.standard.MediaSizeName)))

        if not _pAttrs.get(attribute.standard.MediaPrintableArea):
            raise Exception("ERROR: MediaPrintableArea not present in pAttrs!?")

        mediaPA = _pAttrs.get(attribute.standard.MediaPrintableArea)
        myPrint("DB", "MediaPrintableArea settings from Printer Attributes..: w%sMM h%sMM MediaPrintableArea: %s, getPrintableArea: %s "
                % (mediaPA.getWidth(attribute.standard.MediaPrintableArea.MM),
                   mediaPA.getHeight(attribute.standard.MediaPrintableArea.MM),
                   mediaPA, mediaPA.getPrintableArea(attribute.standard.MediaPrintableArea.MM)))

        if (_thePageFormat.getOrientation()==_thePageFormat.PORTRAIT):
            deducedWidthMM = mediaPA.getWidth(attribute.standard.MediaPrintableArea.MM)
        elif (_thePageFormat.getOrientation()==_thePageFormat.LANDSCAPE):
            deducedWidthMM = mediaPA.getHeight(attribute.standard.MediaPrintableArea.MM)
        else:
            raise Exception("ERROR: thePageFormat.getOrientation() was not PORTRAIT or LANDSCAPE!?")

        myPrint("DB","Paper Orientation: %s" %("LANDSCAPE" if _thePageFormat.getOrientation()==_thePageFormat.LANDSCAPE else "PORTRAIT"))

        _maxPaperWidthPTS = mm2px(deducedWidthMM, GlobalVars.defaultDPI)
        _maxPaperWidthPTS_buff = _maxPaperWidthPTS * _BUFFER_PCT

        myPrint("DB", "MediaPrintableArea: deduced printable width: %sMM(%sPTS) (using factor of *%s = %sPTS)" %(round(deducedWidthMM,1), round(_maxPaperWidthPTS,1), _BUFFER_PCT, _maxPaperWidthPTS_buff))
        return deducedWidthMM, _maxPaperWidthPTS, _maxPaperWidthPTS_buff

    def loadDefaultPrinterAttributes(_pAttrs=None):

        if _pAttrs is None:
            _pAttrs = attribute.HashPrintRequestAttributeSet()
        else:
            _pAttrs.clear()

        # Refer: https://docs.oracle.com/javase/7/docs/api/javax/print/attribute/standard/package-summary.html
        _pAttrs.add(attribute.standard.DialogTypeSelection.NATIVE)
        if GlobalVars.defaultPrintLandscape:
            _pAttrs.add(attribute.standard.OrientationRequested.LANDSCAPE)
        else:
            _pAttrs.add(attribute.standard.OrientationRequested.PORTRAIT)
        _pAttrs.add(attribute.standard.Chromaticity.MONOCHROME)
        _pAttrs.add(attribute.standard.JobSheets.NONE)
        _pAttrs.add(attribute.standard.Copies(1))
        _pAttrs.add(attribute.standard.PrintQuality.NORMAL)

        return _pAttrs

    def printOutputFile(_callingClass=None, _theTitle=None, _theJText=None, _theString=None):

        # Possible future modification, leverage MDPrinter, and it's classes / methods to save/load preferences and create printers
        try:
            if _theJText is None and _theString is None: return
            if _theJText is not None and len(_theJText.getText()) < 1: return
            if _theString is not None and len(_theString) < 1: return

            # Make a new one for printing
            if _theJText is not None:
                printJTextArea = JTextArea(_theJText.getText())
            else:
                printJTextArea = JTextArea(_theString)

            printJTextArea.setEditable(False)
            printJTextArea.setLineWrap(True)    # As we are reducing the font size so that the width fits the page width, this forces any remainder to wrap
            # if _callingClass is not None: printJTextArea.setLineWrap(_callingClass.lWrapText)  # Mirror the word wrap set by user
            printJTextArea.setWrapStyleWord(False)
            printJTextArea.setOpaque(False); printJTextArea.setBackground(Color(0,0,0,0)); printJTextArea.setForeground(Color.BLACK)
            printJTextArea.setBorder(EmptyBorder(0, 0, 0, 0))

            # IntelliJ doesnt like the use of 'print' (as it's a keyword)
            try:
                if checkObjectInNameSpace("MD_REF"):
                    usePrintFontSize = eval("MD_REF.getUI().getFonts().print.getSize()")
                elif checkObjectInNameSpace("moneydance"):
                    usePrintFontSize = eval("moneydance.getUI().getFonts().print.getSize()")
                else:
                    usePrintFontSize = GlobalVars.defaultPrintFontSize  # Just in case cleanup_references() has tidied up once script ended
            except:
                usePrintFontSize = 12   # Font print did not exist before build 3036

            theFontToUse = getMonoFont()       # Need Monospaced font, but with the font set in MD preferences for print
            theFontToUse = theFontToUse.deriveFont(float(usePrintFontSize))
            printJTextArea.setFont(theFontToUse)

            def computeFontSize(_theComponent, _maxPaperWidth, _dpi):

                # Auto shrink font so that text fits on one line when printing
                # Note: Java seems to operate it's maths at 72DPI (so must factor that into the maths)
                try:
                    _DEFAULT_MIN_WIDTH = mm2px(100, _dpi)   # 100MM
                    _minFontSize = 5                        # Below 5 too small
                    theString = _theComponent.getText()
                    _startingComponentFont = _theComponent.getFont()

                    if not theString or len(theString) < 1: return -1

                    fm = _theComponent.getFontMetrics(_startingComponentFont)
                    _maxFontSize = curFontSize = _startingComponentFont.getSize()   # Max out at the MD default for print font size saved in preferences
                    myPrint("DB","Print - starting font:", _startingComponentFont)
                    myPrint("DB","... calculating.... The starting/max font size is:", curFontSize)

                    maxLineWidthInFile = _DEFAULT_MIN_WIDTH
                    longestLine = ""
                    for line in theString.split("\n"):              # Look for the widest line adjusted for font style
                        _w = pt2dpi(fm.stringWidth(line), _dpi)
                        # myPrint("DB", "Found line (len: %s):" %(len(line)), line)
                        # myPrint("DB", "...calculated length metrics: %s/%sPTS (%sMM)" %(fm.stringWidth(line), _w, pt2mm(_w)))
                        if _w > maxLineWidthInFile:
                            longestLine = line
                            maxLineWidthInFile = _w
                    myPrint("DB","longest line width %s chars; maxLineWidthInFile now: %sPTS (%sMM)" %(len(longestLine),maxLineWidthInFile, pt2mm(maxLineWidthInFile)))

                    # Now shrink the font size to fit.....
                    while (pt2dpi(fm.stringWidth(longestLine) + 5,_dpi) > _maxPaperWidth):
                        myPrint("DB","At font size: %s; (pt2dpi(fm.stringWidth(longestLine) + 5,_dpi):" %(curFontSize), (pt2dpi(fm.stringWidth(longestLine) + 5,_dpi)), pt2mm(pt2dpi(fm.stringWidth(longestLine) + 5,_dpi)), "MM", " >> max width:", _maxPaperWidth)
                        curFontSize -= 1
                        fm = _theComponent.getFontMetrics(Font(_startingComponentFont.getName(), _startingComponentFont.getStyle(), curFontSize))
                        myPrint("DB","... next will be: at font size: %s; (pt2dpi(fm.stringWidth(longestLine) + 5,_dpi):" %(curFontSize), (pt2dpi(fm.stringWidth(longestLine) + 5,_dpi)), pt2mm(pt2dpi(fm.stringWidth(longestLine) + 5,_dpi)), "MM")

                        myPrint("DB","... calculating.... length of line still too long... reducing font size to:", curFontSize)
                        if curFontSize < _minFontSize:
                            myPrint("DB","... calculating... Next font size is too small... exiting the reduction loop...")
                            break

                    if not Platform.isMac():
                        curFontSize -= 1   # For some reason, sometimes on Linux/Windows still too big....
                        myPrint("DB","..knocking 1 off font size for good luck...! Now: %s" %(curFontSize))

                    # Code to increase width....
                    # while (pt2dpi(fm.stringWidth(theString) + 5,_dpi) < _maxPaperWidth):
                    #     curSize += 1
                    #     fm = _theComponent.getFontMetrics(Font(_startingComponentFont.getName(), _startingComponentFont.getStyle(), curSize))

                    curFontSize = max(_minFontSize, curFontSize); curFontSize = min(_maxFontSize, curFontSize)
                    myPrint("DB","... calculating.... Adjusted final font size to:", curFontSize)

                except:
                    myPrint("B", "ERROR: computeFontSize() crashed?"); dump_sys_error_to_md_console_and_errorlog()
                    return -1
                return curFontSize

            myPrint("DB", "Creating new PrinterJob...")
            printer_job = PrinterJob.getPrinterJob()

            if GlobalVars.defaultPrintService is not None:
                printer_job.setPrintService(GlobalVars.defaultPrintService)
                myPrint("DB","Assigned remembered PrintService...: %s" %(printer_job.getPrintService()))

            if GlobalVars.defaultPrinterAttributes is not None:
                pAttrs = attribute.HashPrintRequestAttributeSet(GlobalVars.defaultPrinterAttributes)
            else:
                pAttrs = loadDefaultPrinterAttributes(None)

            pAttrs.remove(attribute.standard.JobName)
            pAttrs.add(attribute.standard.JobName("%s: %s" %(myModuleID.capitalize(), _theTitle), None))

            if GlobalVars.defaultDPI != 72:
                pAttrs.remove(attribute.standard.PrinterResolution)
                pAttrs.add(attribute.standard.PrinterResolution(GlobalVars.defaultDPI, GlobalVars.defaultDPI, attribute.standard.PrinterResolution.DPI))

            for atr in pAttrs.toArray(): myPrint("DB", "Printer attributes before user dialog: %s:%s" %(atr.getName(), atr))

            if not printer_job.printDialog(pAttrs):
                myPrint("DB","User aborted the Print Dialog setup screen, so exiting...")
                return

            selectedPrintService = printer_job.getPrintService()
            myPrint("DB", "User selected print service:", selectedPrintService)

            thePageFormat = printer_job.getPageFormat(pAttrs)

            # .setPrintable() seems to modify pAttrs & adds MediaPrintableArea. Do this before printDeducePrintableWidth()
            header = MessageFormat(_theTitle)
            footer = MessageFormat("- page {0} -")
            printer_job.setPrintable(printJTextArea.getPrintable(header, footer), thePageFormat)    # Yes - we do this twice

            for atr in pAttrs.toArray(): myPrint("DB", "Printer attributes **AFTER** user dialog (and setPrintable): %s:%s" %(atr.getName(), atr))

            deducedWidthMM, maxPaperWidthPTS, maxPaperWidthPTS_buff = printDeducePrintableWidth(thePageFormat, pAttrs)

            if _callingClass is None or not _callingClass.lWrapText:

                newFontSize = computeFontSize(printJTextArea, int(maxPaperWidthPTS), GlobalVars.defaultDPI)

                if newFontSize > 0:
                    theFontToUse = theFontToUse.deriveFont(float(newFontSize))
                    printJTextArea.setFont(theFontToUse)

            # avoiding Intellij errors
            # eval("printJTextArea.print(header, footer, False, selectedPrintService, pAttrs, True)")  # If you do this, then native features like print to PDF will get ignored - so print via PrinterJob

            # Yup - calling .setPrintable() twice - before and after .computeFontSize()
            printer_job.setPrintable(printJTextArea.getPrintable(header, footer), thePageFormat)
            eval("printer_job.print(pAttrs)")

            del printJTextArea

            myPrint("DB", "Saving current print service:", printer_job.getPrintService())
            GlobalVars.defaultPrinterAttributes = attribute.HashPrintRequestAttributeSet(pAttrs)
            GlobalVars.defaultPrintService = printer_job.getPrintService()

        except:
            myPrint("B", "ERROR in printing routines.....:"); dump_sys_error_to_md_console_and_errorlog()
        return

    def pageSetup():

        myPrint("DB","Printer Page setup routines..:")

        myPrint("DB", 'NOTE: A4        210mm x 297mm	8.3" x 11.7"	Points: w595 x h842')
        myPrint("DB", 'NOTE: Letter    216mm x 279mm	8.5" x 11.0"	Points: w612 x h791')

        pj = PrinterJob.getPrinterJob()

        # Note: PrintService is not used/remembered/set by .pageDialog

        if GlobalVars.defaultPrinterAttributes is not None:
            pAttrs = attribute.HashPrintRequestAttributeSet(GlobalVars.defaultPrinterAttributes)
        else:
            pAttrs = loadDefaultPrinterAttributes(None)

        for atr in pAttrs.toArray(): myPrint("DB", "Printer attributes before Page Setup: %s:%s" %(atr.getName(), atr))

        if not pj.pageDialog(pAttrs):
            myPrint("DB", "User cancelled Page Setup - exiting...")
            return

        for atr in pAttrs.toArray(): myPrint("DB", "Printer attributes **AFTER** Page Setup: %s:%s" %(atr.getName(), atr))

        if debug: printDeducePrintableWidth(pj.getPageFormat(pAttrs), pAttrs)

        myPrint("DB", "Printer selected: %s" %(pj.getPrintService()))

        GlobalVars.defaultPrinterAttributes = attribute.HashPrintRequestAttributeSet(pAttrs)
        myPrint("DB", "Printer Attributes saved....")

        return

    class SetupMDColors:

        OPAQUE = None
        FOREGROUND = None
        FOREGROUND_REVERSED = None
        BACKGROUND = None
        BACKGROUND_REVERSED = None

        def __init__(self): raise Exception("ERROR - Should not create instance of this class!")

        @staticmethod
        def updateUI():
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")

            SetupMDColors.OPAQUE = False

            SetupMDColors.FOREGROUND = GlobalVars.CONTEXT.getUI().getColors().defaultTextForeground
            SetupMDColors.FOREGROUND_REVERSED = SetupMDColors.FOREGROUND

            SetupMDColors.BACKGROUND = GlobalVars.CONTEXT.getUI().getColors().defaultBackground
            SetupMDColors.BACKGROUND_REVERSED = SetupMDColors.BACKGROUND

            if ((not isMDThemeVAQua() and not isMDThemeDark() and isMacDarkModeDetected())
                    or (not isMacDarkModeDetected() and isMDThemeDarcula())):
                SetupMDColors.FOREGROUND_REVERSED = GlobalVars.CONTEXT.getUI().colors.defaultBackground
                SetupMDColors.BACKGROUND_REVERSED = GlobalVars.CONTEXT.getUI().colors.defaultTextForeground

    global ManuallyCloseAndReloadDataset            # Declare it for QuickJFrame/IDE, but not present in common code. Other code will ignore it

    class GetFirstMainFrame:

        DEFAULT_MAX_WIDTH = 1024
        DEFAULT_MAX_HEIGHT = 768

        def __init__(self): raise Exception("ERROR: DO NOT CREATE INSTANCE OF GetFirstMainFrame!")

        @staticmethod
        def getSize(defaultWidth=None, defaultHeight=None):
            if defaultWidth is None: defaultWidth = GetFirstMainFrame.DEFAULT_MAX_WIDTH
            if defaultHeight is None: defaultHeight = GetFirstMainFrame.DEFAULT_MAX_HEIGHT
            try:
                firstMainFrame = MD_REF.getUI().firstMainFrame
                return firstMainFrame.getSize()
            except: pass
            return Dimension(defaultWidth, defaultHeight)

        @staticmethod
        def getSelectedAccount():
            try:
                firstMainFrame = MD_REF.getUI().firstMainFrame
                return firstMainFrame.getSelectedAccount()
            except: pass
            return None

    class QuickJFrame():

        def __init__(self,
                     title,
                     output,
                     lAlertLevel=0,
                     copyToClipboard=False,
                     lJumpToEnd=False,
                     lWrapText=True,
                     lQuitMDAfterClose=False,
                     lRestartMDAfterClose=False,
                     screenLocation=None,
                     lAutoSize=False):
            self.title = title
            self.output = output
            self.lAlertLevel = lAlertLevel
            self.returnFrame = None
            self.copyToClipboard = copyToClipboard
            self.lJumpToEnd = lJumpToEnd
            self.lWrapText = lWrapText
            self.lQuitMDAfterClose = lQuitMDAfterClose
            self.lRestartMDAfterClose = lRestartMDAfterClose
            self.screenLocation = screenLocation
            self.lAutoSize = lAutoSize
            # if Platform.isOSX() and int(float(MD_REF.getBuild())) >= 3039: self.lAlertLevel = 0    # Colors don't work on Mac since VAQua
            if isMDThemeDark() or isMacDarkModeDetected(): self.lAlertLevel = 0

        class QJFWindowListener(WindowAdapter):

            def __init__(self, theFrame, lQuitMDAfterClose=False, lRestartMDAfterClose=False):
                self.theFrame = theFrame
                self.lQuitMDAfterClose = lQuitMDAfterClose
                self.lRestartMDAfterClose = lRestartMDAfterClose
                self.saveMD_REF = MD_REF

            def windowClosing(self, WindowEvent):                                                                       # noqa
                myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", WindowEvent)
                myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                myPrint("DB", "QuickJFrame() Frame shutting down.... Calling .dispose()")
                self.theFrame.dispose()

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

            def windowClosed(self, WindowEvent):                                                                       # noqa
                myPrint("DB","In ", inspect.currentframe().f_code.co_name, "()")
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                if self.lQuitMDAfterClose or self.lRestartMDAfterClose:
                    if "ManuallyCloseAndReloadDataset" not in globals():
                        myPrint("DB", "'ManuallyCloseAndReloadDataset' not in globals(), so just exiting MD the easy way...")
                        myPrint("B", "@@ EXITING MONEYDANCE @@")
                        MD_REF.getUI().exit()
                    else:
                        if self.lQuitMDAfterClose:
                            myPrint("B", "Quit MD after Close triggered... Now quitting MD")
                            ManuallyCloseAndReloadDataset.moneydanceExitOrRestart(lRestart=False)
                        elif self.lRestartMDAfterClose:
                            myPrint("B", "Restart MD after Close triggered... Now restarting MD")
                            ManuallyCloseAndReloadDataset.moneydanceExitOrRestart(lRestart=True)
                else:
                    myPrint("DB", "FYI No Quit MD after Close triggered... So doing nothing...")

        class CloseAction(AbstractAction):

            def __init__(self, theFrame):
                self.theFrame = theFrame

            def actionPerformed(self, event):
                myPrint("D","in CloseAction(), Event: ", event)
                myPrint("DB", "QuickJFrame() Frame shutting down....")

                try:
                    if not SwingUtilities.isEventDispatchThread():
                        SwingUtilities.invokeLater(GenericDisposeRunnable(self.theFrame))
                    else:
                        self.theFrame.dispose()
                except:
                    myPrint("B","Error. QuickJFrame dispose failed....?")
                    dump_sys_error_to_md_console_and_errorlog()


        class ToggleWrap(AbstractAction):

            def __init__(self, theCallingClass, theJText):
                self.theCallingClass = theCallingClass
                self.theJText = theJText

            def actionPerformed(self, event):
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                self.theCallingClass.lWrapText = not self.theCallingClass.lWrapText
                self.theJText.setLineWrap(self.theCallingClass.lWrapText)

        class QuickJFrameNavigate(AbstractAction):

            def __init__(self, theJText, lTop=False, lBottom=False):
                self.theJText = theJText
                self.lTop = lTop
                self.lBottom = lBottom

            def actionPerformed(self, event):
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                if self.lBottom: self.theJText.setCaretPosition(self.theJText.getDocument().getLength())
                if self.lTop:    self.theJText.setCaretPosition(0)

        class QuickJFramePrint(AbstractAction):

            def __init__(self, theCallingClass, theJText, theTitle=""):
                self.theCallingClass = theCallingClass
                self.theJText = theJText
                self.theTitle = theTitle

            def actionPerformed(self, event):
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )
                printOutputFile(_callingClass=self.theCallingClass, _theTitle=self.theTitle, _theJText=self.theJText)

        class QuickJFramePageSetup(AbstractAction):

            def __init__(self): pass

            def actionPerformed(self, event):
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )
                pageSetup()

        class QuickJFrameSaveTextToFile(AbstractAction):

            def __init__(self, theText, callingFrame):
                self.theText = theText
                self.callingFrame = callingFrame

            def actionPerformed(self, event):
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )
                saveOutputFile(self.callingFrame, "QUICKJFRAME", "%s_output.txt" %(myModuleID), self.theText)

        def show_the_frame(self):

            class MyQuickJFrameRunnable(Runnable):

                def __init__(self, callingClass):
                    self.callingClass = callingClass

                def run(self):                                                                                          # noqa
                    screenSize = Toolkit.getDefaultToolkit().getScreenSize()
                    frame_width = min(screenSize.width-20, max(GetFirstMainFrame.DEFAULT_MAX_WIDTH, int(round(GetFirstMainFrame.getSize().width *.9,0))))
                    frame_height = min(screenSize.height-20, max(GetFirstMainFrame.DEFAULT_MAX_HEIGHT, int(round(GetFirstMainFrame.getSize().height *.9,0))))

                    # JFrame.setDefaultLookAndFeelDecorated(True)   # Note: Darcula Theme doesn't like this and seems to be OK without this statement...
                    if self.callingClass.lQuitMDAfterClose:
                        extraText =  ">> MD WILL QUIT AFTER VIEWING THIS <<"
                    elif self.callingClass.lRestartMDAfterClose:
                        extraText =  ">> MD WILL RESTART AFTER VIEWING THIS <<"
                    else:
                        extraText = ""

                    jInternalFrame = MyJFrame(self.callingClass.title + " (%s+F to find/search for text)%s" %(MD_REF.getUI().ACCELERATOR_MASK_STR, extraText))
                    jInternalFrame.setName(u"%s_quickjframe" %myModuleID)

                    if not Platform.isOSX(): jInternalFrame.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))

                    jInternalFrame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)
                    jInternalFrame.setResizable(True)

                    shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W,  shortcut), "close-window")
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F,  shortcut), "search-window")
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_P, shortcut),  "print-me")
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")

                    theJText = JTextArea(self.callingClass.output)
                    theJText.setEditable(False)
                    theJText.setLineWrap(self.callingClass.lWrapText)
                    theJText.setWrapStyleWord(False)
                    theJText.setFont(getMonoFont())

                    jInternalFrame.getRootPane().getActionMap().put("close-window", self.callingClass.CloseAction(jInternalFrame))
                    jInternalFrame.getRootPane().getActionMap().put("search-window", SearchAction(jInternalFrame,theJText))
                    jInternalFrame.getRootPane().getActionMap().put("print-me", self.callingClass.QuickJFramePrint(self.callingClass, theJText, self.callingClass.title))
                    jInternalFrame.addWindowListener(self.callingClass.QJFWindowListener(jInternalFrame, self.callingClass.lQuitMDAfterClose, self.callingClass.lRestartMDAfterClose))

                    internalScrollPane = JScrollPane(theJText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)

                    if self.callingClass.lAlertLevel>=2:
                        # internalScrollPane.setBackground(Color.RED)
                        theJText.setBackground(Color.RED)
                        theJText.setForeground(Color.BLACK)
                        theJText.setOpaque(True)
                    elif self.callingClass.lAlertLevel>=1:
                        # internalScrollPane.setBackground(Color.YELLOW)
                        theJText.setBackground(Color.YELLOW)
                        theJText.setForeground(Color.BLACK)
                        theJText.setOpaque(True)

                    if not self.callingClass.lAutoSize:
                        jInternalFrame.setPreferredSize(Dimension(frame_width, frame_height))

                    SetupMDColors.updateUI()

                    printButton = JButton("Print")
                    printButton.setToolTipText("Prints the output displayed in this window to your printer")
                    printButton.setOpaque(SetupMDColors.OPAQUE)
                    printButton.setBackground(SetupMDColors.BACKGROUND); printButton.setForeground(SetupMDColors.FOREGROUND)
                    printButton.addActionListener(self.callingClass.QuickJFramePrint(self.callingClass, theJText, self.callingClass.title))

                    if GlobalVars.defaultPrinterAttributes is None:
                        printPageSetup = JButton("Page Setup")
                        printPageSetup.setToolTipText("Printer Page Setup")
                        printPageSetup.setOpaque(SetupMDColors.OPAQUE)
                        printPageSetup.setBackground(SetupMDColors.BACKGROUND); printPageSetup.setForeground(SetupMDColors.FOREGROUND)
                        printPageSetup.addActionListener(self.callingClass.QuickJFramePageSetup())

                    saveButton = JButton("Save to file")
                    saveButton.setToolTipText("Saves the output displayed in this window to a file")
                    saveButton.setOpaque(SetupMDColors.OPAQUE)
                    saveButton.setBackground(SetupMDColors.BACKGROUND); saveButton.setForeground(SetupMDColors.FOREGROUND)
                    saveButton.addActionListener(self.callingClass.QuickJFrameSaveTextToFile(self.callingClass.output, jInternalFrame))

                    wrapOption = JCheckBox("Wrap Contents (Screen & Print)", self.callingClass.lWrapText)
                    wrapOption.addActionListener(self.callingClass.ToggleWrap(self.callingClass, theJText))
                    wrapOption.setForeground(SetupMDColors.FOREGROUND_REVERSED); wrapOption.setBackground(SetupMDColors.BACKGROUND_REVERSED)

                    topButton = JButton("Top")
                    topButton.setOpaque(SetupMDColors.OPAQUE)
                    topButton.setBackground(SetupMDColors.BACKGROUND); topButton.setForeground(SetupMDColors.FOREGROUND)
                    topButton.addActionListener(self.callingClass.QuickJFrameNavigate(theJText, lTop=True))

                    botButton = JButton("Bottom")
                    botButton.setOpaque(SetupMDColors.OPAQUE)
                    botButton.setBackground(SetupMDColors.BACKGROUND); botButton.setForeground(SetupMDColors.FOREGROUND)
                    botButton.addActionListener(self.callingClass.QuickJFrameNavigate(theJText, lBottom=True))

                    closeButton = JButton("Close")
                    closeButton.setOpaque(SetupMDColors.OPAQUE)
                    closeButton.setBackground(SetupMDColors.BACKGROUND); closeButton.setForeground(SetupMDColors.FOREGROUND)
                    closeButton.addActionListener(self.callingClass.CloseAction(jInternalFrame))

                    if Platform.isOSX():
                        save_useScreenMenuBar= System.getProperty("apple.laf.useScreenMenuBar")
                        if save_useScreenMenuBar is None or save_useScreenMenuBar == "":
                            save_useScreenMenuBar= System.getProperty("com.apple.macos.useScreenMenuBar")
                        System.setProperty("apple.laf.useScreenMenuBar", "false")
                        System.setProperty("com.apple.macos.useScreenMenuBar", "false")
                    else:
                        save_useScreenMenuBar = "true"

                    mb = JMenuBar()
                    mb.setBorder(EmptyBorder(0, 0, 0, 0))
                    mb.add(Box.createRigidArea(Dimension(10, 0)))
                    mb.add(topButton)
                    mb.add(Box.createRigidArea(Dimension(10, 0)))
                    mb.add(botButton)
                    mb.add(Box.createHorizontalGlue())
                    mb.add(wrapOption)

                    if GlobalVars.defaultPrinterAttributes is None:
                        mb.add(Box.createRigidArea(Dimension(10, 0)))
                        mb.add(printPageSetup)                                                                          # noqa

                    mb.add(Box.createHorizontalGlue())
                    mb.add(printButton)
                    mb.add(Box.createRigidArea(Dimension(10, 0)))
                    mb.add(saveButton)
                    mb.add(Box.createRigidArea(Dimension(10, 0)))
                    mb.add(closeButton)
                    mb.add(Box.createRigidArea(Dimension(30, 0)))

                    jInternalFrame.setJMenuBar(mb)

                    jInternalFrame.add(internalScrollPane)

                    jInternalFrame.pack()
                    if self.callingClass.screenLocation and isinstance(self.callingClass.screenLocation, Point):
                        jInternalFrame.setLocation(self.callingClass.screenLocation)
                    else:
                        jInternalFrame.setLocationRelativeTo(None)

                    jInternalFrame.setVisible(True)

                    if Platform.isOSX():
                        System.setProperty("apple.laf.useScreenMenuBar", save_useScreenMenuBar)
                        System.setProperty("com.apple.macos.useScreenMenuBar", save_useScreenMenuBar)

                    if "errlog.txt" in self.callingClass.title or self.callingClass.lJumpToEnd:
                        theJText.setCaretPosition(theJText.getDocument().getLength())

                    try:
                        if self.callingClass.copyToClipboard:
                            Toolkit.getDefaultToolkit().getSystemClipboard().setContents(StringSelection(self.callingClass.output), None)
                    except:
                        myPrint("J","Error copying contents to Clipboard")
                        dump_sys_error_to_md_console_and_errorlog()

                    self.callingClass.returnFrame = jInternalFrame

            if not SwingUtilities.isEventDispatchThread():
                myPrint("DB",".. Not running within the EDT so calling via MyQuickJFrameRunnable()...")
                SwingUtilities.invokeAndWait(MyQuickJFrameRunnable(self))
            else:
                myPrint("DB",".. Already within the EDT so calling naked...")
                MyQuickJFrameRunnable(self).run()

            return (self.returnFrame)

    class AboutThisScript(AbstractAction, Runnable):

        def __init__(self, theFrame):
            self.theFrame = theFrame
            self.aboutDialog = None

        def actionPerformed(self, event):
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event:", event)
            self.aboutDialog.dispose()  # Listener is already on the Swing EDT...

        def go(self):
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")

            if not SwingUtilities.isEventDispatchThread():
                myPrint("DB",".. Not running within the EDT so calling via MyAboutRunnable()...")
                SwingUtilities.invokeAndWait(self)
            else:
                myPrint("DB",".. Already within the EDT so calling naked...")
                self.run()

        def run(self):                                                                                                  # noqa
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

            # noinspection PyUnresolvedReferences
            self.aboutDialog = JDialog(self.theFrame, "About", Dialog.ModalityType.MODELESS)

            shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
            self.aboutDialog.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
            self.aboutDialog.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
            self.aboutDialog.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")

            self.aboutDialog.getRootPane().getActionMap().put("close-window", self)
            self.aboutDialog.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)

            if (not Platform.isMac()):
                # MD_REF.getUI().getImages()
                self.aboutDialog.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))

            aboutPanel = JPanel()
            aboutPanel.setLayout(FlowLayout(FlowLayout.LEFT))
            aboutPanel.setPreferredSize(Dimension(1120, 550))

            _label1 = JLabel(pad("Author: Stuart Beesley", 800))
            _label1.setForeground(getColorBlue())
            aboutPanel.add(_label1)

            _label2 = JLabel(pad("StuWareSoftSystems (2020-2023)", 800))
            _label2.setForeground(getColorBlue())
            aboutPanel.add(_label2)

            _label3 = JLabel(pad("Script/Extension: %s (build: %s)" %(GlobalVars.thisScriptName, version_build), 800))
            _label3.setForeground(getColorBlue())
            aboutPanel.add(_label3)

            displayString = scriptExit
            displayJText = JTextArea(displayString)
            displayJText.setFont(getMonoFont())
            displayJText.setEditable(False)
            displayJText.setLineWrap(False)
            displayJText.setWrapStyleWord(False)
            displayJText.setMargin(Insets(8, 8, 8, 8))

            aboutPanel.add(displayJText)

            self.aboutDialog.add(aboutPanel)

            self.aboutDialog.pack()
            self.aboutDialog.setLocationRelativeTo(None)
            self.aboutDialog.setVisible(True)

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

    def isGoodRate(theRate):

        if Double.isNaN(theRate) or Double.isInfinite(theRate) or theRate == 0:
            return False
        return True

    def safeInvertRate(theRate):

        if not isGoodRate(theRate):
            return theRate
        return (1.0 / theRate)

    def convertBytesGBs(_size): return round((_size/(1000.0*1000.0*1000)),1)

    def convertBytesMBs(_size): return round((_size/(1000.0*1000.0)),1)

    def convertBytesKBs(_size): return round((_size/(1000.0)),1)

    def convertMDShortDateFormat_strftimeFormat(lIncludeTime=False, lForceYYMMDDHMS=False):
        """Returns a Python strftime format string in accordance with MD Preferences for Date Format"""
        # https://strftime.org

        _MDFormat = MD_REF.getPreferences().getShortDateFormat()

        rtnFormat = "%Y-%m-%d"

        if lForceYYMMDDHMS:
            lIncludeTime = True
        else:
            if _MDFormat == "MM/dd/yyyy":
                rtnFormat = "%m/%d/%Y"
            elif _MDFormat == "MM.dd.yyyy":
                rtnFormat = "%m.%d.%Y"
            elif _MDFormat == "yyyy/MM/dd":
                rtnFormat = "%Y/%m/%d"
            elif _MDFormat == "yyyy.MM.dd":
                rtnFormat = "%Y.%m.%d"
            elif _MDFormat == "dd/MM/yyyy":
                rtnFormat = "%d/%m/%Y"
            elif _MDFormat == "dd.MM.yyyy":
                rtnFormat = "%d.%m.%Y"

        if lIncludeTime: rtnFormat += " %H:%M:%S"
        return rtnFormat

    def getHumanReadableDateTimeFromTimeStamp(_theTimeStamp, lIncludeTime=False, lForceYYMMDDHMS=False):
        return datetime.datetime.fromtimestamp(_theTimeStamp).strftime(convertMDShortDateFormat_strftimeFormat(lIncludeTime=lIncludeTime, lForceYYMMDDHMS=lForceYYMMDDHMS))

    def getHumanReadableModifiedDateTimeFromFile(_theFile, lIncludeTime=True, lForceYYMMDDHMS=True):
        return getHumanReadableDateTimeFromTimeStamp(os.path.getmtime(_theFile), lIncludeTime=lIncludeTime, lForceYYMMDDHMS=lForceYYMMDDHMS)

    def convertStrippedIntDateFormattedText(strippedDateInt, _format=None):

        # if _format is None: _format = "yyyy/MM/dd"
        if _format is None: _format = MD_REF.getPreferences().getShortDateFormat()

        if strippedDateInt is None or strippedDateInt == 0:
            return "<not set>"

        try:
            c = Calendar.getInstance()
            dateFromInt = DateUtil.convertIntDateToLong(strippedDateInt)
            c.setTime(dateFromInt)
            dateFormatter = SimpleDateFormat(_format)
            convertedDate = dateFormatter.format(c.getTime())
        except:
            return "<error>"

        return convertedDate

    def selectHomeScreen():

        try:
            currentViewAccount = MD_REF.getUI().firstMainFrame.getSelectedAccount()
            if currentViewAccount != MD_REF.getRootAccount():
                myPrint("DB","Switched to Home Page Summary Page (from: %s)" %(currentViewAccount))
                MD_REF.getUI().firstMainFrame.selectAccount(MD_REF.getRootAccount())
        except:
            myPrint("B","@@ Error switching to Summary Page (Home Page)")

    def fireMDPreferencesUpdated():
        """This triggers MD to firePreferencesUpdated().... Hopefully refreshing Home Screen Views too"""
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()" )

        class FPSRunnable(Runnable):
            def __init__(self): pass

            def run(self):
                myPrint("DB",".. Inside FPSRunnable() - calling firePreferencesUpdated()...")
                myPrint("B","Triggering an update to the Summary/Home Page View")
                MD_REF.getPreferences().firePreferencesUpdated()

        if not SwingUtilities.isEventDispatchThread():
            myPrint("DB",".. Not running within the EDT so calling via FPSRunnable()...")
            SwingUtilities.invokeLater(FPSRunnable())
        else:
            myPrint("DB",".. Already running within the EDT so calling FPSRunnable() naked...")
            FPSRunnable().run()
        return

    def decodeCommand(passedEvent):
        param = ""
        uri = passedEvent
        command = uri
        theIdx = uri.find('?')
        if(theIdx>=0):
            command = uri[:theIdx]
            param = uri[theIdx+1:]
        else:
            theIdx = uri.find(':')
            if(theIdx>=0):
                command = uri[:theIdx]
                param = uri[theIdx+1:]
        return command, param

    def getFieldByReflection(theObj, fieldName, isInt=False):
        try: theClass = theObj.getClass()
        except TypeError: theClass = theObj     # This catches where the object is already the Class
        reflectField = None
        while theClass is not None:
            try:
                reflectField = theClass.getDeclaredField(fieldName)
                break
            except NoSuchFieldException:
                theClass = theClass.getSuperclass()
        if reflectField is None: raise Exception("ERROR: could not find field: %s in class hierarchy" %(fieldName))
        if Modifier.isPrivate(reflectField.getModifiers()): reflectField.setAccessible(True)
        elif Modifier.isProtected(reflectField.getModifiers()): reflectField.setAccessible(True)
        isStatic = Modifier.isStatic(reflectField.getModifiers())
        if isInt: return reflectField.getInt(theObj if not isStatic else None)
        return reflectField.get(theObj if not isStatic else None)

    def invokeMethodByReflection(theObj, methodName, params, *args):
        try: theClass = theObj.getClass()
        except TypeError: theClass = theObj     # This catches where the object is already the Class
        reflectMethod = None
        while theClass is not None:
            try:
                if params is None:
                    reflectMethod = theClass.getDeclaredMethod(methodName)
                    break
                else:
                    reflectMethod = theClass.getDeclaredMethod(methodName, params)
                    break
            except NoSuchMethodException:
                theClass = theClass.getSuperclass()
        if reflectMethod is None: raise Exception("ERROR: could not find method: %s in class hierarchy" %(methodName))
        reflectMethod.setAccessible(True)
        return reflectMethod.invoke(theObj, *args)

    def setFieldByReflection(theObj, fieldName, newValue):
        try: theClass = theObj.getClass()
        except TypeError: theClass = theObj     # This catches where the object is already the Class
        reflectField = None
        while theClass is not None:
            try:
                reflectField = theClass.getDeclaredField(fieldName)
                break
            except NoSuchFieldException:
                theClass = theClass.getSuperclass()
        if reflectField is None: raise Exception("ERROR: could not find field: %s in class hierarchy" %(fieldName))
        if Modifier.isPrivate(reflectField.getModifiers()): reflectField.setAccessible(True)
        elif Modifier.isProtected(reflectField.getModifiers()): reflectField.setAccessible(True)
        isStatic = Modifier.isStatic(reflectField.getModifiers())
        return reflectField.set(theObj if not isStatic else None, newValue)

    def find_feature_module(theModule):
        # type: (str) -> bool
        """Searches Moneydance for a specific extension loaded"""
        fms = MD_REF.getLoadedModules()
        for fm in fms:
            if fm.getIDStr().lower() == theModule:
                myPrint("DB", "Found extension: %s" %(theModule))
                return fm
        return None

    GlobalVars.MD_KOTLIN_COMPILED_BUILD = 5000                                                                          # 2023.0
    def isKotlinCompiledBuild(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_KOTLIN_COMPILED_BUILD)                                           # 2023.0(5000)

    def isMDPlusEnabledBuild(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_MDPLUS_BUILD)                         # 2022.0

    def isAlertControllerEnabledBuild(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_ALERTCONTROLLER_BUILD)       # 2022.3

    def genericSwingEDTRunner(ifOffEDTThenRunNowAndWait, ifOnEDTThenRunNowAndWait, codeblock, *args):
        """Will detect and then run the codeblock on the EDT"""

        isOnEDT = SwingUtilities.isEventDispatchThread()
        # myPrint("DB", "** In .genericSwingEDTRunner(), ifOffEDTThenRunNowAndWait: '%s', ifOnEDTThenRunNowAndWait: '%s', codeblock: '%s', args: '%s'" %(ifOffEDTThenRunNowAndWait, ifOnEDTThenRunNowAndWait, codeblock, args))
        myPrint("DB", "** In .genericSwingEDTRunner(), ifOffEDTThenRunNowAndWait: '%s', ifOnEDTThenRunNowAndWait: '%s', codeblock: <codeblock>, args: <args>" %(ifOffEDTThenRunNowAndWait, ifOnEDTThenRunNowAndWait))
        myPrint("DB", "** In .genericSwingEDTRunner(), isOnEDT:", isOnEDT)

        class GenericSwingEDTRunner(Runnable):

            def __init__(self, _codeblock, arguments):
                self.codeBlock = _codeblock
                self.params = arguments

            def run(self):
                myPrint("DB", "** In .genericSwingEDTRunner():: GenericSwingEDTRunner().run()... about to execute codeblock.... isOnEDT:", SwingUtilities.isEventDispatchThread())
                self.codeBlock(*self.params)
                myPrint("DB", "** In .genericSwingEDTRunner():: GenericSwingEDTRunner().run()... finished executing codeblock....")

        _gser = GenericSwingEDTRunner(codeblock, args)

        if ((isOnEDT and not ifOnEDTThenRunNowAndWait) or (not isOnEDT and not ifOffEDTThenRunNowAndWait)):
            myPrint("DB", "... calling codeblock via .invokeLater()...")
            SwingUtilities.invokeLater(_gser)
        elif not isOnEDT:
            myPrint("DB", "... calling codeblock via .invokeAndWait()...")
            SwingUtilities.invokeAndWait(_gser)
        else:
            myPrint("DB", "... calling codeblock.run() naked...")
            _gser.run()

        myPrint("DB", "... finished calling the codeblock via method reported above...")

    def genericThreadRunner(daemon, codeblock, *args):
        """Will run the codeblock on a new Thread"""

        # myPrint("DB", "** In .genericThreadRunner(), codeblock: '%s', args: '%s'" %(codeblock, args))
        myPrint("DB", "** In .genericThreadRunner(), codeblock: <codeblock>, args: <args>")

        class GenericThreadRunner(Runnable):

            def __init__(self, _codeblock, arguments):
                self.codeBlock = _codeblock
                self.params = arguments

            def run(self):
                myPrint("DB", "** In .genericThreadRunner():: GenericThreadRunner().run()... about to execute codeblock....")
                self.codeBlock(*self.params)
                myPrint("DB", "** In .genericThreadRunner():: GenericThreadRunner().run()... finished executing codeblock....")

        _gtr = GenericThreadRunner(codeblock, args)

        _t = Thread(_gtr, "NAB_GenericThreadRunner".lower())
        _t.setDaemon(daemon)
        _t.start()

        myPrint("DB", "... finished calling the codeblock...")

    GlobalVars.EXTN_PREF_KEY = "stuwaresoftsystems" + "." + myModuleID
    GlobalVars.EXTN_PREF_KEY_ENABLE_OBSERVER = "enable_observer"
    GlobalVars.EXTN_PREF_KEY_DISABLE_FORESIGHT = "disable_moneyforesight"

    class StreamTableFixed(StreamTable):
        """Replicates StreamTable. Provide a source to merge. Method .getBoolean() is 'fixed' to be backwards compatible with builds prior to Kotlin (Y/N vs 0/1)"""
        def __init__(self, _streamTableToCopy):
            # type: (StreamTable) -> None
            if not isinstance(_streamTableToCopy, StreamTable): raise Exception("LOGIC ERROR: Must pass a StreamTable! (Passed: %s)" %(type(_streamTableToCopy)))
            self.merge(_streamTableToCopy)

        def getBoolean(self, key, defaultVal):
            # type: (basestring, bool) -> bool
            if isKotlinCompiledBuild():     # MD2023.0 First Kotlin release - changed the code from detecting only Y/N to Y/N/T/F/0/1
                return super(self.__class__, self).getBoolean(key, defaultVal)
            _value = self.get(key, None)
            if _value in ["1", "Y", "y", "T", "t", "true", True]: return True
            if _value in ["0", "N", "n", "F", "f", "false", False]: return False
            return defaultVal

    def getExtensionDatasetSettings():
        # type: () -> SyncRecord
        _extnSettings =  GlobalVars.CONTEXT.getCurrentAccountBook().getLocalStorage().getSubset(GlobalVars.EXTN_PREF_KEY)
        if debug: myPrint("B", "Retrieved Extension Dataset Settings from LocalStorage: %s" %(_extnSettings))
        return _extnSettings

    def saveExtensionDatasetSettings(newExtnSettings):
        # type: (SyncRecord) -> None
        if not isinstance(newExtnSettings, SyncRecord):
            raise Exception("ERROR: 'newExtnSettings' is not a SyncRecord (given: '%s')" %(type(newExtnSettings)))
        _localStorage = GlobalVars.CONTEXT.getCurrentAccountBook().getLocalStorage()
        _localStorage.put(GlobalVars.EXTN_PREF_KEY, newExtnSettings)
        if debug: myPrint("B", "Stored Extension Dataset Settings into LocalStorage: %s" %(newExtnSettings))

    def getExtensionGlobalPreferences(enhancedBooleanCheck=True):
        # type: (bool) -> StreamTable
        _extnPrefs =  GlobalVars.CONTEXT.getPreferences().getTableSetting(GlobalVars.EXTN_PREF_KEY, StreamTable())
        if not isKotlinCompiledBuild():
            if enhancedBooleanCheck:
                _extnPrefs = StreamTableFixed(_extnPrefs)
                myPrint("DB", "... copied retrieved Extension Global Preferences into enhanced StreamTable for backwards .getBoolean() capability...")
        if debug: myPrint("B", "Retrieved Extension Global Preference: %s" %(_extnPrefs))
        return _extnPrefs

    def saveExtensionGlobalPreferences(newExtnPrefs):
        # type: (StreamTable) -> None
        if not isinstance(newExtnPrefs, StreamTable):
            raise Exception("ERROR: 'newExtnPrefs' is not a StreamTable (given: '%s')" %(type(newExtnPrefs)))
        GlobalVars.CONTEXT.getPreferences().setSetting(GlobalVars.EXTN_PREF_KEY, newExtnPrefs)
        if debug: myPrint("B", "Stored Extension Global Preferences: %s" %(newExtnPrefs))

    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################
    # COPY >> END

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def isValidScriptPath(_scriptPath):
        return isinstance(_scriptPath, basestring) and os.path.exists(_scriptPath) and os.path.isfile(_scriptPath) and _scriptPath.endswith(".py")

    def isValidExtractFolder(_extractFolder):
        return isinstance(_extractFolder, basestring) and os.path.exists(_extractFolder) and os.path.isdir(_extractFolder)

    def load_StuWareSoftSystems_parameters_into_memory():

        # >>> THESE ARE THIS SCRIPT's PARAMETERS TO LOAD

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )
        myPrint("DB", "Loading variables into memory...")

        if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}

        for _paramKey in ["saved_exportAmazonScriptPath_SWSS", "saved_importAmazonScriptPath_SWSS"]:
            _paramValue = GlobalVars.parametersLoadedFromFile.get(_paramKey)
            if isValidScriptPath(_paramValue):
                setattr(GlobalVars, _paramKey, _paramValue)
            else:
                myPrint("B", "Warning: loaded parameter '%s' does not appear to be a valid file / python script (will ignore): '%s'" %(_paramKey, _paramValue))

        for _paramKey in ["saved_selectedAcctListUUIDs_EAR",
                          "saved_dateRangerConfig_EAR",
                          "saved_dateRangerConfig_EIT",
                          "saved_securityBalancesDate_ESB",
                          "saved_autoSelectCurrentAsOfDate_ESB",
                          "saved_autoExtract_EAR",
                          "saved_autoExtract_EIT",
                          "saved_autoExtract_ESB",
                          "saved_autoExtract_EAB",
                          "saved_whichYearOption_EAB",
                          "saved_showFolderAfterExtract_SWSS",
                          "saved_extractFileAddTimeStampSuffix_SWSS",
                          "saved_extractFileAddDatasetName_SWSS",
                          "saved_relaunchGUIAfterRun_SWSS",
                          "saved_extractFileAddNamePrefix_SWSS"
                          ]:
            _paramValue = GlobalVars.parametersLoadedFromFile.get(_paramKey)
            if _paramValue is not None: setattr(GlobalVars, _paramKey, _paramValue)

        for _paramKey in ["saved_defaultSavePath_SWSS"]:
            _paramValue = GlobalVars.parametersLoadedFromFile.get(_paramKey)
            if isValidExtractFolder(_paramValue):
                setattr(GlobalVars, _paramKey, _paramValue)
            else:
                myPrint("B","Warning: loaded parameter '%s' does not appear to be a valid directory (will ignore): '%s'" %(_paramKey, _paramValue))

        myPrint("DB","parametersLoadedFromFile{} set into memory (as variables).....")

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def dump_StuWareSoftSystems_parameters_from_memory():
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
        # (i.e. other StuWareSoftSystems programs might be sharing the same file)

        if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}

        # save parameters
        for _paramKey in [
                          "saved_exportAmazonScriptPath_SWSS",
                          "saved_importAmazonScriptPath_SWSS",
                          "saved_selectedAcctListUUIDs_EAR",
                          "saved_dateRangerConfig_EAR",
                          "saved_dateRangerConfig_EIT",
                          "saved_securityBalancesDate_ESB",
                          "saved_autoSelectCurrentAsOfDate_ESB",
                          "saved_autoExtract_EAR",
                          "saved_autoExtract_EIT",
                          "saved_autoExtract_ESB",
                          "saved_autoExtract_EAB",
                          "saved_whichYearOption_EAB",
                          "saved_showFolderAfterExtract_SWSS",
                          "saved_extractFileAddTimeStampSuffix_SWSS",
                          "saved_extractFileAddDatasetName_SWSS",
                          "saved_extractFileAddNamePrefix_SWSS",
                          "saved_relaunchGUIAfterRun_SWSS",
                          "saved_defaultSavePath_SWSS"
                          ]:
            GlobalVars.parametersLoadedFromFile[_paramKey] = getattr(GlobalVars, _paramKey)

        myPrint("DB","variables dumped from memory back into parametersLoadedFromFile{}.....")

    # clear up any old left-overs....
    destroyOldFrames(myModuleID)

    get_StuWareSoftSystems_parameters_from_file(myFile="%s_extension.dict" %(myModuleID))

    myPrint("DB", "DEBUG IS ON..")

    if SwingUtilities.isEventDispatchThread():
        myPrint("DB", "FYI - This script/extension is currently running within the Swing Event Dispatch Thread (EDT)")
    else:
        myPrint("DB", "FYI - This script/extension is NOT currently running within the Swing Event Dispatch Thread (EDT)")

    def cleanup_actions(theFrame=None):
        myPrint("DB", "In", inspect.currentframe().f_code.co_name, "()")
        myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

        if theFrame is not None and not theFrame.isActiveInMoneydance:
            destroyOldFrames(myModuleID)

        try:
            if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                MD_REF.getUI().setStatus(">> StuWareSoftSystems - thanks for using >> %s......." %(GlobalVars.thisScriptName),0)
        except: pass  # If this fails, then MD is probably shutting down.......

        if not GlobalVars.i_am_an_extension_so_run_headless: print(scriptExit)

        cleanup_references()

    # .moneydance_invoke_called() is used via the _invoke.py script as defined in script_info.dict. Not used for runtime extensions
    def moneydance_invoke_called(theCommand):
        # ... modify as required to handle .showURL() events sent to this extension/script...
        myPrint("B", "INVOKE - Received extension command: '%s'" %(theCommand))

    GlobalVars.defaultPrintLandscape = True
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################

    def resetGlobalVariables():
        myPrint("DB", "@@ RESETTING KEY GLOBAL REFERENCES.....")
        # Do these once here (for objects that might hold Model objects etc) and then release at the end... (not the cleanest method...)
        GlobalVars.baseCurrency = None
        GlobalVars.table = None
        GlobalVars.transactionTable = None
        GlobalVars.selectedAccounts_EAR = None


    resetGlobalVariables()


    if isKotlinCompiledBuild():
        from okio import BufferedSource, Buffer, Okio                                                                   # noqa
        if debug: myPrint("B", "** Kotlin compiled build detected, new libraries enabled.....")

    def convertBufferedSourceToInputStream(bufferedSource):
        if isKotlinCompiledBuild() and isinstance(bufferedSource, BufferedSource):
            return bufferedSource.inputStream()
        return bufferedSource

    def getUnadjustedStartBalance(theAccount):
        if isKotlinCompiledBuild(): return theAccount.getUnadjustedStartBalance()
        return theAccount.getStartBalance()

    def getBalanceAdjustment(theAccount):
        if isKotlinCompiledBuild(): return theAccount.getBalanceAdjustment()
        return theAccount.getLongParameter(GlobalVars.Strings.MD_KEY_BALANCE_ADJUSTMENT, 0)

    def getStatusCharRevised(txn):                  # Requested by Ron Lewin - changes Reconciling from 'x' to 'r'
        status = unicode(txn.getStatusChar())
        if status == u"x": return "r"
        return status

    def isPreviewBuild():
        if MD_EXTENSION_LOADER is not None:
            try:
                stream = MD_EXTENSION_LOADER.getResourceAsStream("/_PREVIEW_BUILD_")
                if stream is not None:
                    myPrint("B", "@@ PREVIEW BUILD (%s) DETECTED @@" %(version_build))
                    stream.close()
                    return True
            except: pass
        return False

    # noinspection PyUnresolvedReferences
    def isIncomeExpenseAcct(_acct):
        return (_acct.getAccountType() == Account.AccountType.EXPENSE or _acct.getAccountType() == Account.AccountType.INCOME)

    def validateCSVFileDelimiter(requestedDelimiter=None):
        decimalStrings = [".", ","]
        delimStrings = GlobalVars.ALLOWED_CSV_FILE_DELIMITER_STRINGS
        currentDecimal = MD_REF.getPreferences().getDecimalChar()
        if currentDecimal not in decimalStrings:
            myPrint("B", "@@ WARNING: MD Decimal ('%s') appears invalid... Overriding to '.' @@" %(currentDecimal))
            currentDecimal = "."
        if requestedDelimiter is None or not isinstance(requestedDelimiter, basestring) or len(requestedDelimiter) != 1:
            if currentDecimal != ",":
                requestedDelimiter = ","
            myPrint("DB", "Attempting to set default Delimiter >> will attempt: '%s'" %(requestedDelimiter))
        else:
            myPrint("DB", "Validating requested Delimiter: '%s'" %(requestedDelimiter))
        if currentDecimal in decimalStrings and requestedDelimiter in delimStrings and currentDecimal != requestedDelimiter:
            myPrint("DB", "Requested Delimiter: '%s' validated (current Decimal: '%s')" %(requestedDelimiter, currentDecimal))
            return requestedDelimiter
        if currentDecimal == ".":
            newDelimiter = ","
        else:
            newDelimiter = ";"
        myPrint("B", "Invalid Delimiter: '%s' requested (Decimal: '%s') >> OVERRIDING Delimiter to: '%s'"
                %(requestedDelimiter, currentDecimal, newDelimiter))
        return newDelimiter

    def separateYearMonthDayFromDateInt(_dateInt):
        year = _dateInt / 10000
        month = _dateInt / 100 % 100
        day = _dateInt % 100
        return year, month, day

    class MyJTextField(JTextField):
        def __init__(self, *args, **kwargs):
            self.maxWidth = -1
            self.fm = None
            self.minColWidth = kwargs.pop("minColWidth", None)
            super(self.__class__, self).__init__(*args, **kwargs)
            self.setFocusable(True)

        def updateUI(self):
            super(self.__class__, self).updateUI()

        def getMinimumSize(self):
            dim = super(self.__class__, self).getMinimumSize()
            if self.minColWidth is None: return dim
            if (self.fm is None):
                f = self.getFont()
                if (f is not None):
                    self.fm = self.getFontMetrics(f)
            strWidth = 35 if self.fm is None else self.fm.stringWidth("W" * self.minColWidth)
            dim.width = Math.max(dim.width, strWidth)
            return dim

        def getPreferredSize(self):
            dim = super(self.__class__, self).getPreferredSize()
            self.maxWidth = Math.max(self.maxWidth, dim.width)
            dim.width = self.maxWidth
            return dim


    class MyMoneydanceEventListener(AppEventListener):

        def __init__(self, theFrame):
            self.alreadyClosed = False
            self.theFrame = theFrame
            self.myModuleID = myModuleID

        def getMyself(self):
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")
            fm = MD_REF.getModuleForID(self.myModuleID)
            if fm is None: return None, None
            try:
                pyObject = getFieldByReflection(fm, "extensionObject")
            except:
                myPrint("DB","Error retrieving my own Python extension object..?")
                dump_sys_error_to_md_console_and_errorlog()
                return None, None

            return fm, pyObject

        # noinspection PyMethodMayBeStatic
        def handleEvent(self, appEvent):
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB", "I am .handleEvent() within %s" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))
            myPrint("DB","Extension .handleEvent() received command: %s" %(appEvent))

            if self.alreadyClosed:
                myPrint("DB","....I'm actually still here (MD EVENT %s CALLED).. - Ignoring and returning back to MD...." %(appEvent))
                return

            # MD doesn't call .unload() or .cleanup(), so if uninstalled I need to close myself
            fm, pyObject = self.getMyself()
            myPrint("DB", "Checking myself: %s : %s" %(fm, pyObject))
            if (((fm is None and "__file__" not in globals()) or (self.theFrame.isRunTimeExtension and pyObject is None))
                    and appEvent != AppEventManager.APP_EXITING):
                myPrint("B", "@@ ALERT - I've detected that I'm no longer installed as an extension - I will deactivate.. (switching event code to :close)")
                appEvent = "%s:customevent:close" %self.myModuleID

            # I am only closing Toolbox when a new Dataset is opened.. I was calling it on MD Close/Exit, but it seemed to cause an Exception...
            if (appEvent == AppEventManager.FILE_CLOSING
                    or appEvent == AppEventManager.FILE_CLOSED
                    or appEvent == AppEventManager.FILE_OPENING
                    or appEvent == AppEventManager.APP_EXITING):
                myPrint("DB","@@ Ignoring MD handleEvent: %s" %(appEvent))

            elif (appEvent == AppEventManager.FILE_OPENED or appEvent == "%s:customevent:close" %self.myModuleID):
                if debug:
                    myPrint("DB","MD event %s triggered.... Will call GenericWindowClosingRunnable (via the Swing EDT) to push a WINDOW_CLOSING Event to %s to close itself (while I exit back to MD quickly) ...." %(appEvent, self.myModuleID))
                else:
                    myPrint("B","Moneydance triggered event %s triggered - So I am closing %s now...." %(appEvent, self.myModuleID))
                self.alreadyClosed = True
                try:
                    # t = Thread(GenericWindowClosingRunnable(self.theFrame))
                    # t.start()
                    SwingUtilities.invokeLater(GenericWindowClosingRunnable(self.theFrame))
                    myPrint("DB","Back from calling GenericWindowClosingRunnable to push a WINDOW_CLOSING Event (via the Swing EDT) to %s.... ;-> ** I'm getting out quick! **" %(self.myModuleID))
                except:
                    dump_sys_error_to_md_console_and_errorlog()
                    myPrint("B","@@ ERROR calling GenericWindowClosingRunnable to push a WINDOW_CLOSING Event (via the Swing EDT) to %s.... :-< ** I'm getting out quick! **" %(self.myModuleID))
                if not debug: myPrint("DB","Returning back to Moneydance after calling for %s to close...." %self.myModuleID)

    class WhichYearChooser(JPanel):
        # 0=this year and last year, 1=just this year, 2=just last year
        KEY = "which_year_option"
        LABEL = "Which year:"
        LABEL_BOTH = "Both years:"
        LABEL_THIS = "This year:"
        LABEL_LAST = "Last year"
        BOTH_YEARS_KEY = "both_years"
        THIS_YEAR_KEY = "this_year"
        LAST_YEAR_KEY = "last_year"

        def __init__(self, *args):
            # type: (any) -> None
            super(self.__class__, self).__init__(*args)

            self.buttonGroup = ButtonGroup()
            self.bothYearsButton = JRadioButton(self.LABEL_BOTH, False)
            self.thisYearButton = JRadioButton(self.LABEL_THIS, True)
            self.lastYearButton = JRadioButton(self.LABEL_LAST, False)
            for btn in self.getAllButtons():
                self.buttonGroup.add(btn)
                self.add(btn)

        def getAllButtons(self): return [self.bothYearsButton, self.thisYearButton, self.lastYearButton]
        def getChoiceLabel(self): return JLabel(self.__class__.LABEL)

        def getSelectedItem(self):
            if self.bothYearsButton.isSelected(): return self.BOTH_YEARS_KEY
            if self.thisYearButton.isSelected(): return self.THIS_YEAR_KEY
            if self.lastYearButton.isSelected(): return self.LAST_YEAR_KEY

        def isBothYears(self): return self.bothYearsButton.isSelected()
        def isThisYear(self): return self.thisYearButton.isSelected()
        def isLastYear(self): return self.lastYearButton.isSelected()

        def setBothYears(self, val): self.bothYearsButton.setSelected(val)
        def setThisYear(self, val): self.thisYearButton.setSelected(val)
        def setLastYear(self, val): self.lastYearButton.setSelected(val)

        def getBothYearsBtn(self): return self.bothYearsButton
        def getThisYearBtn(self): return self.thisYearButton
        def getLastYearBtn(self): return self.lastYearButton

        def setEnabled(self, enabled):
            for btn in self.getAllButtons(): btn.setEnabled(enabled)

        def storeToParameters(self, parameters, saveKey=None):
            # type: (SyncRecord, str) -> None
            if saveKey is None: saveKey = self.KEY
            parameters.put(saveKey, self.getSelectedItem())

        def loadFromParameters(self, parameters, loadKey=None):
            # type: (SyncRecord, str) -> None
            if loadKey is None: loadKey = self.KEY
            for btn in self.getAllButtons(): btn.setSelected(False)
            loadOption = parameters.getStr(loadKey, self.THIS_YEAR_KEY)
            if loadOption == self.BOTH_YEARS_KEY: self.bothYearsButton.setSelected(True)
            elif loadOption == self.THIS_YEAR_KEY: self.thisYearButton.setSelected(True)
            elif loadOption == self.LAST_YEAR_KEY: self.lastYearButton.setSelected(True)
            else: self.thisYearButton.setSelected(True)

    # We only recreate if not pre-existing so we can detect first usage
    global ParametersSecondaryDialog
    if "ParametersSecondaryDialog" not in globals():
        class ParametersSecondaryDialog(SecondaryDialog, ActionListener):
            FIRST_TIME_GUI_LOADED = True
            ABORT_ACTION = "abort"
            RUN_ALL_EXTRACTS_ACTION = "run_all_extracts"
            SET_EXTRACT_FOLDER_ACTION = "set_extract_folder"
            SHOW_EXTRACT_FOLDER_ACTION = "show_extract_folder"
            RUN_ACCT_TXN_EXTRACT_ACTION = "run_acct_txn_extracts"
            RUN_INVEST_TXN_EXTRACT_ACTION = "run_invest_txn_extracts"
            RUN_SEC_BALS_EXTRACT_ACTION = "run_sec_bals_extracts"
            RUN_ACCT_BALS_EXTRACT_ACTION = "run_acct_bals_extracts"
            RUN_AMZ_EXPORT_SCRIPT_ACTION = "run_amz_export_script"
            RUN_AMZ_IMPORT_SCRIPT_ACTION = "run_amz_import_script"
            SELECT_EXPORT_SCRIPT_ACTION = "select_amz_export_script"
            SELECT_IMPORT_SCRIPT_ACTION = "select_amz_import_script"
            SHOW_EXPORT_SCRIPT_ACTION = "show_amz_export_script"
            SHOW_IMPORT_SCRIPT_ACTION = "show_amz_import_script"
            SAVE_PARAMETERS_ACTION = "save_parameters_list"
            ENABLE_AUTO_EXTRACT_WHEN_DATASET_CLOSES_ACTION = "enable_auto_extract_when_dataset_closes"
            SHOW_EXTRACT_FOLDER_AFTER_EXTRACTS_ACTION = "show_extract_folder_after_extracts"
            ENABLE_AUTO_EAR_ACTION = "enable_auto_ear"
            ENABLE_AUTO_EIT_ACTION = "enable_auto_eit"
            ENABLE_AUTO_ESB_ACTION = "enable_auto_esb"
            ENABLE_AUTO_EAB_ACTION = "enable_auto_eab"
            ADD_DATASET_NAME_PREFIX_ACTION = "add_dataset_name_prefix"
            ADD_TIMESTAMP_SUFFIX_ACTION = "add_timestamp_suffix"
            AUTO_SELECT_CURRENT_DATE_ACTION = "auto_select_current_date"
            RELAUNCH_GUI_AFTER_RUN_ACTION = "relaunch_gui_after_run"
            DEBUG_ACTION = "debug"

            EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING = "auto_extract_when_file_closing"

            # Remember: When you close the window, then .goAway() is called (which ultimately calls .dispose())
            #           This will self-save the window's size/location, remove PrefsListener, and call .goneAway()
            #           Override .goneAway() to perform tasks when dialog is closing.

            def __init__(self, mdGUI, isAutoRun):
                super(self.__class__, self).__init__(mdGUI, client_mark_extract_data_frame_, "Extract Data: Parameters", True)

                self._isAutoRun = isAutoRun

                self._aborted = True
                self._clickedExtractAll = False
                self._clickedExtractEAR = False
                self._clickedExtractEIT = False
                self._clickedExtractESB = False
                self._clickedExtractEAB = False
                self._clickedExportAMZ = False
                self._clickedImportAMZ = False

                self.myModuleID = myModuleID
                self.mdGUI = mdGUI
                self.book = mdGUI.getMain().getCurrentAccountBook()

                self.extnSettings = getExtensionDatasetSettings()

                self.setRememberSizeLocationKeys("gui.%s_size" %(self.myModuleID), "gui.%s_location" %(self.myModuleID), Dimension(960, 865))

                try: self.setEscapeKeyCancels(True)
                except: pass

                # Create these controls here, so we can load / get saved parameters without loading the GUI...
                self.statusText_JTA = None

                self.dateRangerEAR_DRC = DateRangeChooser(mdGUI)
                self.dateRangerEIT_DRC = DateRangeChooser(mdGUI)
                self.securityBalancesDate_JDF = JDateField(mdGUI)

                self.enableAutoExtract_JCB = JCheckBox(MDAction.makeNonKeyedAction(mdGUI, "Enable auto extract EVERY TIME this dataset closes", self.ENABLE_AUTO_EXTRACT_WHEN_DATASET_CLOSES_ACTION, self))
                self.showFolderAfterExtract_JCB = JCheckBox(MDAction.makeNonKeyedAction(mdGUI, "Show extract folder after extract(s)", self.SHOW_EXTRACT_FOLDER_AFTER_EXTRACTS_ACTION, self))

                self.relaunchGUIAfterRun_JCB = JCheckBox(MDAction.makeNonKeyedAction(mdGUI, "Relaunch GUI after run(s)", self.RELAUNCH_GUI_AFTER_RUN_ACTION, self))

                self.extractFileAddDatasetName_JCB = JCheckBox(MDAction.makeNonKeyedAction(mdGUI, "Dataset name prefix", self.ADD_DATASET_NAME_PREFIX_ACTION, self))
                self.extractFileAddNamePrefix_JTF = MyJTextField("", 12, minColWidth=7)
                self.extractFileAddTimeStampSuffix_JCB = JCheckBox(MDAction.makeNonKeyedAction(mdGUI, "Timestamp Suffix", self.ADD_TIMESTAMP_SUFFIX_ACTION, self))

                self.autoExtractEAR_JCB = JCheckBox(MDAction.makeNonKeyedAction(mdGUI, "Acct txns", self.ENABLE_AUTO_EAR_ACTION, self))
                self.autoExtractEIT_JCB = JCheckBox(MDAction.makeNonKeyedAction(mdGUI, "Invst txns", self.ENABLE_AUTO_EIT_ACTION, self))
                self.autoExtractESB_JCB = JCheckBox(MDAction.makeNonKeyedAction(mdGUI, "Sec bals", self.ENABLE_AUTO_ESB_ACTION, self))
                self.autoExtractEAB_JCB = JCheckBox(MDAction.makeNonKeyedAction(mdGUI, "Acct bals", self.ENABLE_AUTO_EAB_ACTION, self))

                self.accountList_ASL = None
                self.setupAccountSelector()

                self.whichYearOptionEAB_CHO = WhichYearChooser()
                self.autoSelectCurrentAsOfDateESB_JCB = JCheckBox(MDAction.makeNonKeyedAction(mdGUI, "Auto select current date", self.AUTO_SELECT_CURRENT_DATE_ACTION, self))

                self.loadParameters(self.isAutoRun() or self.__class__.FIRST_TIME_GUI_LOADED)
                if not self.isAutoRun():
                    if self.__class__.FIRST_TIME_GUI_LOADED:
                        myPrint("B", "Detected first time usage of GUI (non-auto mode) - loaded default dates...")
                    else:
                        myPrint("B", "Detected that it's not the first time usage of GUI (non-auto mode) - loaded saved dates...")
                    self.__class__.FIRST_TIME_GUI_LOADED = False

            def isAutoRun(self): return self._isAutoRun
            def isAborted(self): return self._aborted
            def setAborted(self, aborted): self._aborted = aborted

            def setupPanel(self):

                main_JPNL = JPanel(BorderLayout())
                main_JPNL.setBorder(EmptyBorder(0, 0, 8, 0))
                main_JPNL.setBackground(self.mdGUI.getColors().defaultBackground)

                p = JPanel(GridBagLayout())
                p.setBorder(EmptyBorder(8, 10, 8, 10))

                main_JPNL.add(p, BorderLayout.CENTER)

                onRow = 0

                runAllExtracts_JBTN = JButton(MDAction.makeNonKeyedAction(self.mdGUI, "Run All Extracts", self.RUN_ALL_EXTRACTS_ACTION, self))
                p.add(runAllExtracts_JBTN, GridC.getc(0, onRow).fillx())

                setExtractFolder_JBTN = JButton(MDAction.makeNonKeyedAction(self.mdGUI, "Set Extract Folder", self.SET_EXTRACT_FOLDER_ACTION, self))
                showExtractFolder_JBTN = JButton(MDAction.makeNonKeyedAction(self.mdGUI, "Show Extract Folder", self.SHOW_EXTRACT_FOLDER_ACTION, self))

                y = 0
                button_JPNL = JPanel(GridBagLayout())
                button_JPNL.add(setExtractFolder_JBTN, GridC.getc(y, 0)); y+=1
                button_JPNL.add(showExtractFolder_JBTN,   GridC.getc(y, 0)); y+=1
                p.add(button_JPNL, GridC.getc(1, onRow).colspan(3).west())
                onRow += 1

                runAcctTxnExtract_JBTN = JButton(MDAction.makeNonKeyedAction(self.mdGUI, "Run Account Transactions Extract", self.RUN_ACCT_TXN_EXTRACT_ACTION, self))
                p.add(runAcctTxnExtract_JBTN, GridC.getc(0, onRow).fillx())

                y = 0
                dateRangerEAR_JPNL = JPanel(GridBagLayout())
                dateRangerEAR_JPNL.add(self.dateRangerEAR_DRC.getChoiceLabel(), GridC.getc(y, 0).label()); y+=1
                dateRangerEAR_JPNL.add(self.dateRangerEAR_DRC.getChoice(),      GridC.getc(y, 0).field()); y+=1
                dateRangerEAR_JPNL.add(self.dateRangerEAR_DRC.getStartLabel(),  GridC.getc(y, 0).label()); y+=1
                dateRangerEAR_JPNL.add(self.dateRangerEAR_DRC.getStartField(),  GridC.getc(y, 0).field()); y+=1
                dateRangerEAR_JPNL.add(self.dateRangerEAR_DRC.getEndLabel(),    GridC.getc(y, 0).label()); y+=1
                dateRangerEAR_JPNL.add(self.dateRangerEAR_DRC.getEndField(),    GridC.getc(y, 0).field()); y+=1
                p.add(dateRangerEAR_JPNL, GridC.getc(1, onRow).colspan(3).leftInset(5).east())
                onRow += 1

                runInvestTxnExtract_JBTN = JButton(MDAction.makeNonKeyedAction(self.mdGUI, "Run Investment Transactions Extract", self.RUN_INVEST_TXN_EXTRACT_ACTION, self))
                p.add(runInvestTxnExtract_JBTN, GridC.getc(0, onRow).fillx())

                y = 0
                dateRangerEIT_JPNL = JPanel(GridBagLayout())
                dateRangerEIT_JPNL.add(self.dateRangerEIT_DRC.getChoiceLabel(), GridC.getc(y, 0).label()); y+=1
                dateRangerEIT_JPNL.add(self.dateRangerEIT_DRC.getChoice(),      GridC.getc(y, 0).field()); y+=1
                dateRangerEIT_JPNL.add(self.dateRangerEIT_DRC.getStartLabel(),  GridC.getc(y, 0).label()); y+=1
                dateRangerEIT_JPNL.add(self.dateRangerEIT_DRC.getStartField(),  GridC.getc(y, 0).field()); y+=1
                dateRangerEIT_JPNL.add(self.dateRangerEIT_DRC.getEndLabel(),    GridC.getc(y, 0).label()); y+=1
                dateRangerEIT_JPNL.add(self.dateRangerEIT_DRC.getEndField(),    GridC.getc(y, 0).field()); y+=1
                p.add(dateRangerEIT_JPNL, GridC.getc(1, onRow).colspan(3).leftInset(5).east())
                onRow += 1

                runSecBalsExtract_JBTN = JButton(MDAction.makeNonKeyedAction(self.mdGUI, "Run Security Balances Extract", self.RUN_SEC_BALS_EXTRACT_ACTION, self))
                p.add(runSecBalsExtract_JBTN, GridC.getc(0, onRow).fillx())

                y = 0
                secBalsDate_JPNL = JPanel(GridBagLayout())
                secBalsDate_JPNL.add(self.autoSelectCurrentAsOfDateESB_JCB,     GridC.getc(y, 0).label().west());                   y+=1
                secBalsDate_JPNL.add(JLabel("as of:"),                          GridC.getc(y, 0).label().west().leftInset(10));     y+=1
                secBalsDate_JPNL.add(self.securityBalancesDate_JDF,             GridC.getc(y, 0).field());                          y+=1
                p.add(secBalsDate_JPNL, GridC.getc(1, onRow).colspan(3).east())
                onRow += 1

                runAcctBalsExtract_JBTN = JButton(MDAction.makeNonKeyedAction(self.mdGUI, "Run Account Balances Extract", self.RUN_ACCT_BALS_EXTRACT_ACTION, self))
                p.add(runAcctBalsExtract_JBTN, GridC.getc(0, onRow).fillx())

                y = 0
                whichYear_JPNL = JPanel(GridBagLayout())
                whichYear_JPNL.add(self.whichYearOptionEAB_CHO.getChoiceLabel(), GridC.getc(y, 0).label());   y+=1
                whichYear_JPNL.add(self.whichYearOptionEAB_CHO, GridC.getc(y, 0).west());                     y+=1
                p.add(whichYear_JPNL, GridC.getc(1, onRow).colspan(3).west().leftInset(5))
                onRow += 1

                p.add(JSeparator(), GridC.getc(0, onRow).colspan(4).fillx().topInset(5))
                onRow += 1

                runAMZExportScript_JBTN = JButton(MDAction.makeNonKeyedAction(self.mdGUI, "Export AMZ Payments", self.RUN_AMZ_EXPORT_SCRIPT_ACTION, self))
                selectAMZExportScript_JBTN = JButton(MDAction.makeNonKeyedAction(self.mdGUI, "Select Script", self.SELECT_EXPORT_SCRIPT_ACTION, self))
                showAMZExportScript_JBTN = JButton(MDAction.makeNonKeyedAction(self.mdGUI, "Show Scriptpath", self.SHOW_EXPORT_SCRIPT_ACTION, self))

                p.add(runAMZExportScript_JBTN, GridC.getc(0, onRow).fillx().topInset(5))

                y = 0
                button_JPNL = JPanel(GridBagLayout())
                button_JPNL.add(selectAMZExportScript_JBTN, GridC.getc(y, 0)); y+=1
                button_JPNL.add(showAMZExportScript_JBTN,   GridC.getc(y, 0)); y+=1
                p.add(button_JPNL, GridC.getc(1, onRow).colspan(3).west().topInset(5))
                onRow += 1

                runAMZImportScript_JBTN = JButton(MDAction.makeNonKeyedAction(self.mdGUI, "Import AMZ Payments", self.RUN_AMZ_IMPORT_SCRIPT_ACTION, self))
                selectAMZImportScript_JBTN = JButton(MDAction.makeNonKeyedAction(self.mdGUI, "Select Script", self.SELECT_IMPORT_SCRIPT_ACTION, self))
                showAMZImportScript_JBTN = JButton(MDAction.makeNonKeyedAction(self.mdGUI, "Show Scriptpath", self.SHOW_IMPORT_SCRIPT_ACTION, self))

                p.add(runAMZImportScript_JBTN, GridC.getc(0, onRow).fillx())

                y = 0
                button_JPNL = JPanel(GridBagLayout())
                button_JPNL.add(selectAMZImportScript_JBTN, GridC.getc(y, 0)); y+=1
                button_JPNL.add(showAMZImportScript_JBTN,   GridC.getc(y, 0)); y+=1
                p.add(button_JPNL, GridC.getc(1, onRow).colspan(3).west())
                onRow += 1

                p.add(JLabel("Account selection list (only for Account Transactions extract):"), GridC.getc(0, onRow).topInset(10).west())
                onRow += 1

                if isinstance(self.accountList_ASL, AccountSelectList): pass
                self.accountList_ASL.layoutComponentUI()
                p.add(self.accountList_ASL.getView(), GridC.getc(0, onRow).field().wxy(1.0, 1.0).colspan(4).fillboth())
                onRow += 1

                y = 0
                autoExtracts_JPNL = JPanel(GridBagLayout())
                autoExtracts_JPNL.add(JLabel("Enable One-Click Auto Extract for:"), GridC.getc(y, 0).label()); y+=1
                autoExtracts_JPNL.add(self.autoExtractEAR_JCB,                      GridC.getc(y, 0).field()); y+=1
                autoExtracts_JPNL.add(self.autoExtractEIT_JCB,                      GridC.getc(y, 0).field()); y+=1
                autoExtracts_JPNL.add(self.autoExtractESB_JCB,                      GridC.getc(y, 0).field()); y+=1
                autoExtracts_JPNL.add(self.autoExtractEAB_JCB,                      GridC.getc(y, 0).field()); y+=1
                p.add(autoExtracts_JPNL, GridC.getc(0, onRow).colspan(4).west())
                onRow += 1

                y = 0
                extractNamePrefixSuffix_JPNL = JPanel(GridBagLayout())
                extractNamePrefixSuffix_JPNL.add(JLabel("Configure extract name format:"), GridC.getc(y, 0).label()); y+=1
                extractNamePrefixSuffix_JPNL.add(self.extractFileAddDatasetName_JCB,       GridC.getc(y, 0).leftInset(5)); y+=1
                extractNamePrefixSuffix_JPNL.add(self.extractFileAddNamePrefix_JTF,        GridC.getc(y, 0).field().leftInset(5).filly()); y+=1
                extractNamePrefixSuffix_JPNL.add(JLabel("Name prefix:"),                   GridC.getc(y, 0).label()); y+=1
                extractNamePrefixSuffix_JPNL.add(self.extractFileAddTimeStampSuffix_JCB,   GridC.getc(y, 0).leftInset(5)); y+=1
                p.add(extractNamePrefixSuffix_JPNL, GridC.getc(0, onRow).colspan(4).west())
                onRow += 1

                p.add(self.showFolderAfterExtract_JCB, GridC.getc(0, onRow).west())
                p.add(self.enableAutoExtract_JCB, GridC.getc(1, onRow).west())
                onRow += 1

                p.add(self.relaunchGUIAfterRun_JCB, GridC.getc(0, onRow).west())

                debug_JCB = JCheckBox(MDAction.makeNonKeyedAction(self.mdGUI, "Debug", self.DEBUG_ACTION, self))
                debug_JCB.setSelected(debug)
                p.add(debug_JCB, GridC.getc(1, onRow).west())

                saveParameters_JBTN = JButton(MDAction.makeNonKeyedAction(self.mdGUI, "Save Parameters", self.SAVE_PARAMETERS_ACTION, self))
                abort_JBTN = JButton(MDAction.makeNonKeyedAction(self.mdGUI, "Abort", self.ABORT_ACTION, self))

                y = 0
                saveAbort_JPNL = JPanel(GridBagLayout())
                saveAbort_JPNL.add(saveParameters_JBTN, GridC.getc(y, 0)); y+=1
                saveAbort_JPNL.add(abort_JBTN,          GridC.getc(y, 0)); y+=1
                p.add(saveAbort_JPNL, GridC.getc(2, onRow).colspan(2).east())
                onRow += 1

                p.add(JSeparator(), GridC.getc(0, onRow).colspan(4).fillx().topInset(5))
                onRow += 1

                p.add(JLabel("Status:"), GridC.getc(0, onRow).topInset(10).west())
                onRow += 1

                self.statusText_JTA = JTextArea("")
                self.statusText_JTA.setFont(getMonoFont())
                self.statusText_JTA.setEditable(False)
                self.statusText_JTA.setLineWrap(False)
                self.statusText_JTA.setWrapStyleWord(False)
                self.statusText_JTA.setMargin(Insets(8, 8, 8, 8))
                self.statusText_JTA.setBackground(self.mdGUI.getColors().defaultBackground)
                self.statusText_JTA.setForeground(self.mdGUI.getColors().defaultTextForeground)
                self.statusText_JTA.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10))
                # self.statusText_JTA.setForeground(getColorRed())
                p.add(JScrollPane(self.statusText_JTA), GridC.getc(0, onRow).colspan(4).fillboth().wxy(1.0, 0.5))
                p.add(Box.createVerticalStrut(40), GridC.getc(0, onRow).filly())
                onRow += 1

                if debug: self.setStatus("DEBUG ON")

                self.setContentPane(main_JPNL)
                self.pack()

            def goneAway(self):
                # type: () -> None
                myPrint("DB", "Inside .goneAway() - Dialog must be closing....")
                super(self.__class__, self).goneAway()                                                                      # noqa

            def setupAccountSelector(self):
                accountFilter = self.buildAccountFilter(None)
                self.accountList_ASL = AccountSelectList(self.mdGUI)
                self.accountList_ASL.setAccountFilter(accountFilter)
                # self.accountList_ASL.setSpecialDisplayToolTip(this.mdGUI.getStr("zero_bal_asof_tip"));

            def buildAccountFilter(self, existing):
                accountFilter = AccountFilter("all_accounts")
                accountFilter.addAllowedType(Account.AccountType.BANK)                                                      # noqa
                accountFilter.addAllowedType(Account.AccountType.CREDIT_CARD)                                               # noqa

                # accountFilter.addAllowedType(Account.AccountType.LOAN)
                # accountFilter.addAllowedType(Account.AccountType.LIABILITY)
                # accountFilter.addAllowedType(Account.AccountType.ASSET)

                # accountFilter.addAllowedType(Account.AccountType.INVESTMENT)
                # accountFilter.addAllowedType(Account.AccountType.SECURITY)
                # if (showAllAccounts):
                #     accountFilter.addAllowedType(Account.AccountType.EXPENSE)
                #     accountFilter.addAllowedType(Account.AccountType.INCOME)

                fullAccountList = FullAccountList(self.book, accountFilter, True)
                accountFilter.setFullList(fullAccountList)
                if (existing is not None):
                    previouslyAllowedTypes = existing.getAllowedTypes()
                    for account in accountFilter.buildIncludedAccountList(self.book):
                        if (not previouslyAllowedTypes.contains(account.getAccountType()) or existing.filter(account)):
                            continue
                        accountFilter.exclude(account)
                return accountFilter

            def setStatus(self, statusTxt): self.statusText_JTA.append(statusTxt + "\n")

            def readFromString(self, paramString):
                # type: (str) -> SyncRecord
                _settings = SyncRecord()
                if isKotlinCompiledBuild():
                    _settings.readSet(Buffer().writeUtf8(paramString))
                else:
                    _settings.readSet(StringReader(paramString))
                return _settings

            def getSelectedAccounts(self):
                # type: () -> [Account]

                # Note: .getSelectedAccountIds() returns -code (Account Type) where all selected, not the actual IDs
                # selectedAccounts = []
                # if self.accountList_ASL is not None:
                #     acctUUIDs = self.accountList_ASL.getSelectedAccountIds()
                #     # myPrint("B", "@@@", getFieldByReflection(self.accountList_ASL, "_controller").".getSelectedAccountIds());
                #     for acctUUID in acctUUIDs:
                #         acct = self.book.getAccountByUUID(acctUUID)
                #         if acct is not None: selectedAccounts.append(acct)
                # return selectedAccounts

                return AccountUtil.allMatchesForSearch(self.book, self.accountList_ASL.getAccountFilter().getAcctSearch())

            def getDateRangeChooserEAR(self): return self.dateRangerEAR_DRC
            def getDateRangeChooserEIT(self): return self.dateRangerEIT_DRC
            def getSecurityBalancesDateESB(self): return self.securityBalancesDate_JDF.getDateInt()
            def clickedExtractAll(self): return self._clickedExtractAll
            def clickedExtractEAR(self): return self._clickedExtractEAR
            def clickedExtractEIT(self): return self._clickedExtractEIT
            def clickedExtractESB(self): return self._clickedExtractESB
            def clickedExtractEAB(self): return self._clickedExtractEAB
            def clickedExportAMZ(self): return self._clickedExportAMZ
            def clickedImportAMZ(self): return self._clickedImportAMZ

            def returnParametersOrDefaults(self, _paramStr, _isAutoRun):
                # type: (str, bool) -> SyncRecord
                if _isAutoRun: return SyncRecord()
                return self.readFromString(_paramStr)

            def resetDefaultDateParameters(self, _isAutoRun):

                # Load EAB Which year setting
                try:
                    self.whichYearOptionEAB_CHO.loadFromParameters(self.returnParametersOrDefaults(GlobalVars.saved_whichYearOption_EAB, _isAutoRun))
                except: pass

                # Load Date Ranges
                try:
                    self.dateRangerEAR_DRC.loadFromParameters(self.returnParametersOrDefaults(GlobalVars.saved_dateRangerConfig_EAR, _isAutoRun))
                    self.dateRangerEIT_DRC.loadFromParameters(self.returnParametersOrDefaults(GlobalVars.saved_dateRangerConfig_EIT, _isAutoRun))
                    self.autoSelectCurrentAsOfDateESB_JCB.setSelected(_isAutoRun or GlobalVars.saved_autoSelectCurrentAsOfDate_ESB)
                    if self.autoSelectCurrentAsOfDateESB_JCB.isSelected():
                        self.securityBalancesDate_JDF.setDateInt(DateUtil.getStrippedDateInt())
                    else:
                        self.securityBalancesDate_JDF.setDateInt(GlobalVars.saved_securityBalancesDate_ESB)
                except: pass

            def loadParameters(self, _isAutoRun):

                # load or reset date parameters (for auto runs etc)
                self.resetDefaultDateParameters(_isAutoRun)

                # Load Auto Extract setting
                try: self.enableAutoExtract_JCB.setSelected(self.extnSettings.getBoolean(self.EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING, False))
                except: pass

                # Load Show Extract Folder after extract(s) setting
                try: self.showFolderAfterExtract_JCB.setSelected(GlobalVars.saved_showFolderAfterExtract_SWSS)
                except: pass

                try: self.relaunchGUIAfterRun_JCB.setSelected(GlobalVars.saved_relaunchGUIAfterRun_SWSS)
                except: pass

                # Load Extract file name prefix(s) and suffix
                try:
                    self.extractFileAddDatasetName_JCB.setSelected(GlobalVars.saved_extractFileAddDatasetName_SWSS)
                    self.extractFileAddNamePrefix_JTF.setText(GlobalVars.saved_extractFileAddNamePrefix_SWSS)
                    self.extractFileAddTimeStampSuffix_JCB.setSelected(GlobalVars.saved_extractFileAddTimeStampSuffix_SWSS)
                except: pass

                # Load Selected Accounts
                try: GraphReportUtil.selectIndices(self.book, GlobalVars.saved_selectedAcctListUUIDs_EAR, self.accountList_ASL)
                except: pass

                # save Auto Extract flags
                try:
                    self.autoExtractEAR_JCB.setSelected(GlobalVars.saved_autoExtract_EAR)
                    self.autoExtractEIT_JCB.setSelected(GlobalVars.saved_autoExtract_EIT)
                    self.autoExtractESB_JCB.setSelected(GlobalVars.saved_autoExtract_ESB)
                    self.autoExtractEAB_JCB.setSelected(GlobalVars.saved_autoExtract_EAB)
                except: pass

            def saveParameters(self):

                # Save EAB Which Year chooser setting
                settings = SyncRecord()
                self.whichYearOptionEAB_CHO.storeToParameters(settings)
                GlobalVars.saved_whichYearOption_EAB = settings.writeToString()
                if debug: self.setStatus("Saved saved_whichYearOption_EAB: '%s'" %(GlobalVars.saved_whichYearOption_EAB))

                # Save Auto Extract setting
                self.extnSettings.put(self.EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING, self.enableAutoExtract_JCB.isSelected())
                myPrint("DB", "'%s' parameter set to: %s" %(self.EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING, self.extnSettings.getBoolean(self.EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING, False)))

                saveExtensionDatasetSettings(self.extnSettings)
                txt = "Saved '%s' parameter: %s for this dataset back to local storage..." %(self.EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING, self.extnSettings.getBoolean(self.EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING, False))
                if debug:
                    myPrint("B", txt)
                    self.setStatus("Saved '%s' parameter: %s for this dataset back to local storage..." %(self.EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING, self.extnSettings.getBoolean(self.EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING, False)))

                # Save Show Extract Folder after extract(s) setting
                GlobalVars.saved_showFolderAfterExtract_SWSS = self.showFolderAfterExtract_JCB.isSelected()
                if debug: self.setStatus("Saved saved_showFolderAfterExtract_SWSS: '%s'" %(GlobalVars.saved_showFolderAfterExtract_SWSS))

                GlobalVars.saved_relaunchGUIAfterRun_SWSS = self.relaunchGUIAfterRun_JCB.isSelected()
                if debug: self.setStatus("Saved saved_relaunchGUIAfterRun_SWSS: '%s'" %(GlobalVars.saved_relaunchGUIAfterRun_SWSS))

                # Load Extract file name prefix(s) and suffix
                GlobalVars.saved_extractFileAddDatasetName_SWSS = self.extractFileAddDatasetName_JCB.isSelected()
                GlobalVars.saved_extractFileAddNamePrefix_SWSS = self.extractFileAddNamePrefix_JTF.getText()
                GlobalVars.saved_extractFileAddTimeStampSuffix_SWSS = self.extractFileAddTimeStampSuffix_JCB.isSelected()
                if debug: self.setStatus("Saved add Dataset prefix: %s, add prefix: '%s', add timestamp suffix: %s"
                                         %(GlobalVars.saved_extractFileAddDatasetName_SWSS, GlobalVars.saved_extractFileAddNamePrefix_SWSS, GlobalVars.saved_extractFileAddTimeStampSuffix_SWSS))

                # Save Date Ranges
                settings = SyncRecord()
                self.dateRangerEAR_DRC.storeToParameters(settings)
                GlobalVars.saved_dateRangerConfig_EAR = settings.writeToString()
                if debug: self.setStatus("Saved saved_dateRangerConfig_EAR: '%s'" %(GlobalVars.saved_dateRangerConfig_EAR))

                settings = SyncRecord()
                self.dateRangerEIT_DRC.storeToParameters(settings)
                GlobalVars.saved_dateRangerConfig_EIT = settings.writeToString()
                if debug: self.setStatus("Saved saved_dateRangerConfig_EIT: '%s'" %(GlobalVars.saved_dateRangerConfig_EIT))

                GlobalVars.saved_autoSelectCurrentAsOfDate_ESB = self.autoSelectCurrentAsOfDateESB_JCB.isSelected()
                if debug: self.setStatus("Saved saved_autoSelectCurrentAsOfDate_ESB: '%s'" %(GlobalVars.saved_autoSelectCurrentAsOfDate_ESB))

                GlobalVars.saved_securityBalancesDate_ESB = self.securityBalancesDate_JDF.getDateInt()
                if debug: self.setStatus("Saved saved_securityBalancesDate_ESB: '%s'" %(GlobalVars.saved_securityBalancesDate_ESB))

                # Save Selected Accounts
                acctUUIDs = self.accountList_ASL.getSelectedAccountIds()
                acctListStr = ",".join(acctUUIDs)
                GlobalVars.saved_selectedAcctListUUIDs_EAR = acctListStr
                if debug: self.setStatus("Saved Account UUIDs: '%s'" %(acctListStr))

                # save Auto Extract flags
                GlobalVars.saved_autoExtract_EAR = self.autoExtractEAR_JCB.isSelected()
                GlobalVars.saved_autoExtract_EIT = self.autoExtractEIT_JCB.isSelected()
                GlobalVars.saved_autoExtract_ESB = self.autoExtractESB_JCB.isSelected()
                GlobalVars.saved_autoExtract_EAB = self.autoExtractEAB_JCB.isSelected()
                if debug: self.setStatus("Saved all auto extract flags: EAR: %s, EIT: %s, ESB: %s, EAB: %s"
                                          %(GlobalVars.saved_autoExtract_EAR, GlobalVars.saved_autoExtract_EIT, GlobalVars.saved_autoExtract_ESB, GlobalVars.saved_autoExtract_EAB))

                save_StuWareSoftSystems_parameters_to_file(myFile="%s_extension.dict" %(myModuleID))
                if debug: self.setStatus("Saved parameters back to disk...")

            def isExtractFolderValidOKToProceed(self):
                _folder = GlobalVars.saved_defaultSavePath_SWSS
                if not isValidExtractFolder(_folder):
                    myPopupInformationBox(self, theTitle="ERROR", theMessage="Extract folder invalid", theMessageType=JOptionPane.ERROR_MESSAGE)
                    self.setStatus("ERROR: Extract folder invalid: '%s'" %(_folder))
                    return False
                return True

            def isScriptFolderValidOKToProceed(self, _cmd):
                lExport = (_cmd == self.SHOW_EXPORT_SCRIPT_ACTION)
                scriptPath = GlobalVars.saved_exportAmazonScriptPath_SWSS if lExport else GlobalVars.saved_importAmazonScriptPath_SWSS
                prefix = "Export script" if lExport else "Import script"
                if not isValidScriptPath(scriptPath):
                    myPopupInformationBox(self, theTitle="ERROR", theMessage="%s path invalid" %(prefix), theMessageType=JOptionPane.ERROR_MESSAGE)
                    self.setStatus("ERROR: %s path invalid: '%s'" %(prefix, scriptPath))
                    return False
                return True

            def actionPerformed(self, event):
                global debug
                if isinstance(event, ActionEvent): pass
                _cmd = event.getActionCommand()
                source = event.getSource()
                self.setStatus("")

                myPrint("DB", "@@@@ actionPerformed() @@@", _cmd, event, source)

                if _cmd == self.ABORT_ACTION:
                    self.setAborted(True)
                    self.goAway()

                elif _cmd == self.RUN_AMZ_EXPORT_SCRIPT_ACTION:
                    if self.isScriptFolderValidOKToProceed(self.SHOW_EXPORT_SCRIPT_ACTION):
                        self.setAborted(False)
                        self._clickedExportAMZ = True
                        self.goAway()

                elif _cmd == self.RUN_AMZ_IMPORT_SCRIPT_ACTION:
                    if self.isScriptFolderValidOKToProceed(self.SHOW_IMPORT_SCRIPT_ACTION):
                        self.setAborted(False)
                        self._clickedImportAMZ = True
                        self.goAway()

                elif _cmd == self.ENABLE_AUTO_EAR_ACTION: pass
                elif _cmd == self.ENABLE_AUTO_EIT_ACTION: pass
                elif _cmd == self.ENABLE_AUTO_ESB_ACTION: pass
                elif _cmd == self.ENABLE_AUTO_EAB_ACTION: pass

                elif _cmd == self.RUN_ALL_EXTRACTS_ACTION:
                    if self.isExtractFolderValidOKToProceed():
                        self.setAborted(False)
                        self._clickedExtractAll = True
                        self.saveParameters()
                        self.goAway()

                elif _cmd == self.RUN_ACCT_TXN_EXTRACT_ACTION:
                    if self.isExtractFolderValidOKToProceed():
                        self.setAborted(False)
                        self._clickedExtractEAR = True
                        self.saveParameters()
                        self.goAway()

                elif _cmd == self.RUN_INVEST_TXN_EXTRACT_ACTION:
                    if self.isExtractFolderValidOKToProceed():
                        self.setAborted(False)
                        self._clickedExtractEIT = True
                        self.saveParameters()
                        self.goAway()

                elif _cmd == self.RUN_SEC_BALS_EXTRACT_ACTION:
                    if self.isExtractFolderValidOKToProceed():
                        self.setAborted(False)
                        self._clickedExtractESB = True
                        self.saveParameters()
                        self.goAway()

                elif _cmd == self.RUN_ACCT_BALS_EXTRACT_ACTION:
                    if self.isExtractFolderValidOKToProceed():
                        self.setAborted(False)
                        self._clickedExtractEAB = True
                        self.saveParameters()
                        self.goAway()

                elif _cmd == self.DEBUG_ACTION:
                    if isinstance(source, JCheckBox): pass
                    debug = source.isSelected()
                    self.setStatus("DEBUG: %s" %(debug))

                elif _cmd == self.SAVE_PARAMETERS_ACTION:
                    self.saveParameters()

                elif _cmd == self.SET_EXTRACT_FOLDER_ACTION:
                    defaultPath = GlobalVars.saved_defaultSavePath_SWSS
                    defaultFolder = get_home_dir()
                    if isValidExtractFolder(defaultPath):
                        defaultFolder = os.path.dirname(defaultPath)
                    extractFolder = getFileFromFileChooser(client_mark_extract_data_frame_,     # Parent frame or None
                                                           defaultFolder,                       # Starting path
                                                           None,                                # Default Filename
                                                           "Select Extract Folder",             # Title
                                                           False,                               # Multi-file selection mode
                                                           True,                                # True for Open/Load, False for Save
                                                           False,                               # True = Files, else Dirs
                                                           None,                                # Load/Save button text, None for defaults
                                                           lForceFD=True
                                                           )
                    if isValidExtractFolder(extractFolder):
                        GlobalVars.saved_defaultSavePath_SWSS = extractFolder
                        self.showExtractFolder()
                    else:
                        self.setStatus("Extract folder not changed")

                elif _cmd == self.SHOW_EXTRACT_FOLDER_ACTION:
                    self.showExtractFolder()

                elif _cmd == self.SHOW_EXPORT_SCRIPT_ACTION or _cmd == self.SHOW_IMPORT_SCRIPT_ACTION:
                    self.showScriptPath(_cmd)

                elif _cmd == self.SELECT_EXPORT_SCRIPT_ACTION or _cmd == self.SELECT_IMPORT_SCRIPT_ACTION:
                    lExport = (_cmd == self.SELECT_EXPORT_SCRIPT_ACTION)
                    defaultPath = GlobalVars.saved_exportAmazonScriptPath_SWSS if lExport else GlobalVars.saved_importAmazonScriptPath_SWSS
                    defaultFolder = get_home_dir()
                    defaultFilename = ""
                    if os.path.exists(defaultPath):
                        defaultFolder = os.path.dirname(defaultPath)
                        defaultFilename = os.path.basename(defaultPath)
                    scriptFile = getFileFromFileChooser(client_mark_extract_data_frame_,    # Parent frame or None
                                                        defaultFolder,                      # Starting path
                                                        defaultFilename,                    # Default Filename
                                                        "Select Python Script",             # Title
                                                        False,                              # Multi-file selection mode
                                                        True,                               # True for Open/Load, False for Save
                                                        True,                               # True = Files, else Dirs
                                                        None,                               # Load/Save button text, None for defaults
                                                        fileChooser_fileFilterText="py",    # File filter (non Mac only). Example: "txt" or "qif"
                                                        lForceFD=True
                                                        )
                    if isValidScriptPath(scriptFile):
                        if lExport:
                            GlobalVars.saved_exportAmazonScriptPath_SWSS = scriptFile
                        else:
                            GlobalVars.saved_importAmazonScriptPath_SWSS = scriptFile
                        self.showScriptPath(self.SHOW_EXPORT_SCRIPT_ACTION if lExport else self.SHOW_IMPORT_SCRIPT_ACTION)
                    else:
                        self.setStatus("Script path not changed")


            def showScriptPath(self, _cmd):
                lExport = (_cmd == self.SHOW_EXPORT_SCRIPT_ACTION)
                scriptPath = GlobalVars.saved_exportAmazonScriptPath_SWSS if lExport else GlobalVars.saved_importAmazonScriptPath_SWSS
                prefix = "Export script:" if lExport else "Import script:"
                if scriptPath is None or scriptPath == "":
                    txt = "<NOT SET>"
                elif not isValidScriptPath(scriptPath):
                    txt = "<INVALID>"
                else:
                    txt = "<%s>" %(scriptPath)
                self.setStatus("%s\n%s" %(prefix, txt))

            def showExtractFolder(self):
                extractFolder = GlobalVars.saved_defaultSavePath_SWSS
                prefix = "Extract folder:"
                if extractFolder is None or extractFolder == "": txt = "<NOT SET>"
                elif not isValidExtractFolder(extractFolder): txt = "<INVALID>"
                else: txt = "<%s>" %(extractFolder)
                self.setStatus("%s\n%s" %(prefix, txt))

    def listCommonExtractParameters():
        myPrint("B","---------------------------------------------------------------------------------------")
        myPrint("B","Common Data Extract Parameters: All extracts:")
        myPrint("B", "  Strip non-ASCII characters...........: %s" %(GlobalVars.lStripASCII))
        myPrint("B", "  Add BOM to front of file.............: %s" %(GlobalVars.lWriteBOMToExtractFile))
        myPrint("B", "  CSV extract delimiter................: %s" %(GlobalVars.csvDelimiter))
        myPrint("B", "  Excel extract date format............: %s" %(GlobalVars.excelExtractDateFormat))
        myPrint("B","---------------------------------------------------------------------------------------")

    def listParametersEAR():
        myPrint("B","---------------------------------------------------------------------------------------")
        myPrint("B","Parameters: Extract Account Registers:")
        # myPrint("B", "  Hide Hidden Securities...............:", GlobalVars.hideHiddenSecurities_EAR);
        # myPrint("B", "  Hide Inactive Accounts...............:", GlobalVars.hideInactiveAccounts_EAR)
        # myPrint("B", "  Hide Hidden Accounts.................:", GlobalVars.hideHiddenAccounts_EAR)
        # myPrint("B", "  Currency filter......................: %s '%s'" %(GlobalVars.lAllCurrency_EAR, GlobalVars.filterForCurrency_EAR))
        # myPrint("B", "  Security filter......................: %s '%s'" %(GlobalVars.lAllSecurity_EAR, GlobalVars.filterForSecurity_EAR))
        # myPrint("B", "  Account filter.......................: %s '%s'" %(GlobalVars.lAllAccounts_EAR, GlobalVars.filterForAccounts_EAR))
        myPrint("B", "  Selected accounts filter (UUIDs).....: %s" %(GlobalVars.saved_selectedAcctListUUIDs_EAR))
        myPrint("B", "  Selected accounts filter.............: %s" %(GlobalVars.selectedAccounts_EAR))

        if not GlobalVars.AUTO_EXTRACT_MODE:
            myPrint("B", "  Date ranger config...................: '%s'" %(GlobalVars.saved_dateRangerConfig_EAR))

        myPrint("B", "  Filtering Transactions by date range.: (Start: %s End: %s)"
                %(convertStrippedIntDateFormattedText(GlobalVars.startDateInt_EAR), convertStrippedIntDateFormattedText(GlobalVars.endDateInt_EAR)))

        myPrint("B", "  Include Unadjusted Opening Balances..:", GlobalVars.lIncludeOpeningBalances_EAR)
        myPrint("B", "  Including Balance Adjustments........:", GlobalVars.lIncludeBalanceAdjustments_EAR)
        myPrint("B", "  Tag filter...........................: %s '%s'" %(GlobalVars.lAllTags_EAR, GlobalVars.tagFilter_EAR))
        myPrint("B", "  Text filter..........................: %s '%s'" %(GlobalVars.lAllText_EAR, GlobalVars.textFilter_EAR))
        myPrint("B", "  Categories filter....................: %s '%s'" %(GlobalVars.lAllCategories_EAR, GlobalVars.categoriesFilter_EAR))

        myPrint("B", "  Auto Extract.........................:", GlobalVars.saved_autoExtract_EAR)
        myPrint("B","---------------------------------------------------------------------------------------")

    def listParametersEIT():
        myPrint("B","---------------------------------------------------------------------------------------")
        myPrint("B","Parameters: Extract Investment Transactions:")
        myPrint("B", "  Hide Hidden Securities...............:", GlobalVars.hideHiddenSecurities_EIT)
        myPrint("B", "  Hide Inactive Accounts...............:", GlobalVars.hideInactiveAccounts_EIT)
        myPrint("B", "  Hide Hidden Accounts.................:", GlobalVars.hideHiddenAccounts_EIT)
        myPrint("B", "  Currency filter......................: %s '%s'" %(GlobalVars.lAllCurrency_EIT, GlobalVars.filterForCurrency_EIT))
        myPrint("B", "  Security filter......................: %s '%s'" %(GlobalVars.lAllSecurity_EIT, GlobalVars.filterForSecurity_EIT))
        myPrint("B", "  Account filter.......................: %s '%s'" %(GlobalVars.lAllAccounts_EIT, GlobalVars.filterForAccounts_EIT))

        if not GlobalVars.AUTO_EXTRACT_MODE:
            myPrint("B", "  Date ranger config...................: '%s'" %(GlobalVars.saved_dateRangerConfig_EIT))

        if GlobalVars.lFilterDateRange_EIT and GlobalVars.startDateInt_EIT != 0 and GlobalVars.endDateInt_EIT != 0:
            myPrint("B", "  Filtering Transactions by date range.: (Start: %s End: %s)"
                    %(convertStrippedIntDateFormattedText(GlobalVars.startDateInt_EIT), convertStrippedIntDateFormattedText(GlobalVars.endDateInt_EIT)))
        else:
            myPrint("B", "  Selecting all dates (no date filter).:", True)

        myPrint("B", "  Include Unadjusted Opening Balances..:", GlobalVars.lIncludeOpeningBalances_EIT)
        myPrint("B", "  Including Balance Adjustments........:", GlobalVars.lIncludeBalanceAdjustments_EIT)
        myPrint("B", "  Adjust for Stock Splits..............:", GlobalVars.lAdjustForSplits_EIT)
        myPrint("B", "  OMIT Buy/Sell LOT matching data......:", GlobalVars.lOmitLOTDataFromExtract_EIT)
        myPrint("B", "  Extract extra security account info..:", GlobalVars.lExtractExtraSecurityAcctInfo_EIT )
        myPrint("B", "  Auto Extract.........................:", GlobalVars.saved_autoExtract_EIT)
        myPrint("B","---------------------------------------------------------------------------------------")

    def listParametersESB():
        myPrint("B","---------------------------------------------------------------------------------------")
        myPrint("B","Parameters: Extract Security Balances:")
        myPrint("B", "  Hide Hidden Securities...............:", GlobalVars.hideHiddenSecurities_ESB)
        myPrint("B", "  Hide Inactive Accounts...............:", GlobalVars.hideInactiveAccounts_ESB)
        myPrint("B", "  Hide Hidden Accounts.................:", GlobalVars.hideHiddenAccounts_ESB)
        myPrint("B", "  Currency filter......................: %s '%s'" %(GlobalVars.lAllCurrency_ESB, GlobalVars.filterForCurrency_ESB))
        myPrint("B", "  Security filter......................: %s '%s'" %(GlobalVars.lAllSecurity_ESB, GlobalVars.filterForSecurity_ESB))
        myPrint("B", "  Account filter.......................: %s '%s'" %(GlobalVars.lAllAccounts_ESB, GlobalVars.filterForAccounts_ESB))

        if not GlobalVars.AUTO_EXTRACT_MODE:
            myPrint("B", "  AUTO set asof balance date to today..: %s" %(GlobalVars.saved_autoSelectCurrentAsOfDate_ESB))

        if GlobalVars.saved_autoSelectCurrentAsOfDate_ESB:
            myPrint("B", "  As of balance date...................: AUTO: (%s)" %(convertStrippedIntDateFormattedText(DateUtil.getStrippedDateInt())))
        else:
            myPrint("B", "  As of balance date...................: %s" %(convertStrippedIntDateFormattedText(GlobalVars.saved_securityBalancesDate_ESB)))
        myPrint("B", "  Auto Extract.........................:", GlobalVars.saved_autoExtract_ESB)
        myPrint("B","---------------------------------------------------------------------------------------")

    def listParametersEAB():
        myPrint("B","---------------------------------------------------------------------------------------")
        myPrint("B","Parameters: Extract Account Balances:")
        myPrint("B", "  Which year flag......................:", GlobalVars.saved_whichYearOption_EAB)
        myPrint("B", "  Hide Hidden Securities...............:", GlobalVars.hideHiddenSecurities_EAB)
        myPrint("B", "  Hide Inactive Accounts...............:", GlobalVars.hideInactiveAccounts_EAB)
        myPrint("B", "  Hide Hidden Accounts.................:", GlobalVars.hideHiddenAccounts_EAB)
        myPrint("B", "  Currency filter......................: %s '%s'" %(GlobalVars.lAllCurrency_EAB, GlobalVars.filterForCurrency_EAB))
        myPrint("B", "  Security filter......................: %s '%s'" %(GlobalVars.lAllSecurity_EAB, GlobalVars.filterForSecurity_EAB))
        myPrint("B", "  Account filter.......................: %s '%s'" %(GlobalVars.lAllAccounts_EAB, GlobalVars.filterForAccounts_EAB))
        myPrint("B", "  Auto Extract.........................:", GlobalVars.saved_autoExtract_EAB)
        myPrint("B","---------------------------------------------------------------------------------------")

    def getExtractFullPath(extractType, lDoNotAddTimeStamp=False, extn=".csv"):

        extractType = extractType.lower().strip()
        if extractType == "ear":
            defaultFileName = "extract_account_registers"
        elif extractType == "eit":
            defaultFileName = "extract_investment_transactions"
        elif extractType == "esb":
            defaultFileName = "extract_security_balances"
        elif extractType == "eab":
            defaultFileName = "extract_account_balances"
        else: raise Exception("ERROR: extractType invalid (passed: '%s')!?" %(extractType))

        bookNamePrefix = "" if not GlobalVars.saved_extractFileAddDatasetName_SWSS else GlobalVars.CONTEXT.getCurrentAccountBook().getName() + "_"
        namePrefix = "" if GlobalVars.saved_extractFileAddNamePrefix_SWSS == "" else GlobalVars.saved_extractFileAddNamePrefix_SWSS + "_"

        timeStampSuffix = ""
        if not lDoNotAddTimeStamp and GlobalVars.saved_extractFileAddTimeStampSuffix_SWSS:
            timeStampSuffix += currentDateTimeMarker()

        extractFullPath = os.path.join(GlobalVars.saved_defaultSavePath_SWSS, bookNamePrefix + namePrefix + defaultFileName + timeStampSuffix + extn)
        myPrint("DB", "Derived full extract path: '%s'" %(extractFullPath))
        return extractFullPath

    def scriptRunnerFromDisk(_runThisScript, _method):

        if MD_EXTENSION_LOADER is None:
            txt = "%s: Sorry - You must be running this as an extension to run this script...." %(_method)
            setDisplayStatus(txt, "R"); myPrint("B", txt)
            myPopupInformationBox(client_mark_extract_data_frame_, txt,theMessageType=JOptionPane.ERROR_MESSAGE)
            return False

        if GlobalVars.SCRIPT_RUNNING_LOCK.locked():
            txt = "%s: Sorry - a script is already running with an active Lock" %(_method)
            setDisplayStatus(txt, "R"); myPrint("B", txt)
            myPopupInformationBox(client_mark_extract_data_frame_, txt,theMessageType=JOptionPane.ERROR_MESSAGE)
            return False

        with GlobalVars.SCRIPT_RUNNING_LOCK:
            myPrint("B","**********************************************************")
            myPrint("B","**********************************************************")
            myPrint("B","**********************************************************")
            py = MD_REF.getPythonInterpreter()
            py.set("%s_script_runner" %(myModuleID), _runThisScript)
            py.getSystemState().setClassLoader(MD_EXTENSION_LOADER)
            py.set("moneydance_extension_loader", MD_EXTENSION_LOADER)

            class ScriptRunnable(Runnable):

                def __init__(self, _context, _python, _scriptToRun):
                    self.context = _context
                    self.python = _python
                    self.scriptToRun = _scriptToRun

                def run(self):  # NOTE: This will not start in the EDT (the same as Moneybot Console)
                    myPrint("B","..About to execfile(%s)" %(self.scriptToRun))
                    self.python.execfile(self.scriptToRun)
                    myPrint("DB", "....I am back from script, within the special Thread().....")
                    self.context.resetPythonInterpreter(self.python)

            Thread(ScriptRunnable(MD_REF, py, _runThisScript), "%s_scriptRunnerFromDisk" %(myModuleID)).start()

            myPrint("DB", ".... post calling Thread().....")
            myPrint("B","**********************************************************")
            myPrint("B","**********************************************************")
            myPrint("B","**********************************************************")

        return True


    ####################################################################################################################

    if checkObjectInNameSpace("moneydance_extension_parameter") and GlobalVars.i_am_an_extension_so_run_headless:
        MD_EXTENSION_PARAMETER = moneydance_extension_parameter
        cmd, cmdParam = decodeCommand(MD_EXTENSION_PARAMETER)
    else:
        MD_EXTENSION_PARAMETER = ""
        cmd = cmdParam = ""

    cmd = cmd.lower()
    cmdParam = cmdParam.lower()

    GlobalVars.validCommands = ["autoextract", "autoexport", "autoimport", "showconsole"]

    if "showconsole" in cmd:
        myPrint("B", "@@ Auto relaunch of GUI screen requested...")
        cmd = cmdParam = MD_EXTENSION_PARAMETER = ""

    GlobalVars.AUTO_EXEC_SCRIPT_MODE = ("autoexport" in cmd or "autoimport" in cmd)
    GlobalVars.AUTO_INVOKE_CALLED = (cmd in GlobalVars.validCommands)
    GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE = (MD_EXTENSION_PARAMETER == AppEventManager.FILE_CLOSING)
    GlobalVars.AUTO_EXTRACT_MODE = (cmd == "menu2_auto" or GlobalVars.AUTO_INVOKE_CALLED or GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE)

    GlobalVars.AUTO_INVOKE_THEN_QUIT = False
    if GlobalVars.AUTO_INVOKE_CALLED:
        GlobalVars.AUTO_INVOKE_THEN_QUIT = (cmdParam == "quit")

    myPrint("B", "Book: '%s', Auto Extract Mode: %s, Auto Invoke: %s (MD Quit after extract: %s), Handle_Event triggered: %s (Menu/Parameter/Event detected: '%s'), Auto Execute AMZ Script: %s (cmd: '%s')"
            %(MD_REF.getCurrentAccountBook(), GlobalVars.AUTO_EXTRACT_MODE, GlobalVars.AUTO_INVOKE_CALLED, GlobalVars.AUTO_INVOKE_THEN_QUIT, GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE, MD_EXTENSION_PARAMETER, GlobalVars.AUTO_EXEC_SCRIPT_MODE, cmd))

    ####################################################################################################################
    if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
        MD_REF.getUI().setStatus(">> StuWareSoftSystems - %s launching......." %(GlobalVars.thisScriptName),0)
    ####################################################################################################################


    class MainAppRunnable(Runnable):
        def __init__(self): pass

        def run(self):
            global client_mark_extract_data_frame_      # global as defined / changed here

            myPrint("DB", "In MainAppRunnable()", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

            if not SwingUtilities.isEventDispatchThread():
                if GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                    myPrint("B", "Allowing auto extract(s) to run on non-EDT thread - as triggered from file closing event....")
                else:
                    raise Exception("LOGIC ERROR: Should only be run on the EDT!?")

            if MD_REF.getCurrentAccountBook() is None:
                msgTxt = "Moneydance appears to be empty - no data to scan - aborting..."
                myPrint("B", msgTxt)
                if not GlobalVars.AUTO_EXTRACT_MODE:
                    myPopupInformationBox(None, msgTxt, "EMPTY DATASET", theMessageType=JOptionPane.ERROR_MESSAGE)
                raise Exception(msgTxt)

            if GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                client_mark_extract_data_frame_ = None
            else:
                # Create application JFrame() so that all popups have correct Moneydance Icons etc
                # JFrame.setDefaultLookAndFeelDecorated(True)   # Note: Darcula Theme doesn't like this and seems to be OK without this statement...
                client_mark_extract_data_frame_ = MyJFrame()
                client_mark_extract_data_frame_.setName(u"%s_main" %(myModuleID))
                if (not Platform.isMac()):
                    MD_REF.getUI().getImages()
                    client_mark_extract_data_frame_.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))
                client_mark_extract_data_frame_.setVisible(False)
                client_mark_extract_data_frame_.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
                myPrint("DB","Main JFrame %s for application created.." %(client_mark_extract_data_frame_.getName()))

            try:

                GlobalVars.csvfilename = None
                GlobalVars.decimalCharSep = MD_REF.getPreferences().getDecimalChar()
                GlobalVars.csvDelimiter = validateCSVFileDelimiter(GlobalVars.csvDelimiter)   # Get initial default delimiter (NOTE: Parameters already preloaded at this point)
                myPrint("DB", "MD's Decimal point: '%s', CSV Delimiter set to: '%s'" %(GlobalVars.decimalCharSep, GlobalVars.csvDelimiter))

                GlobalVars.EXTRACT_DATA = False

                GlobalVars.AUTO_MESSAGES = []

                #######################
                # Validate auto extract

                if GlobalVars.AUTO_EXEC_SCRIPT_MODE:
                    pass
                else:
                    if GlobalVars.AUTO_EXTRACT_MODE:
                        iCountAutos = 0
                        for checkAutoExtract in [GlobalVars.saved_autoExtract_EAR, GlobalVars.saved_autoExtract_EIT, GlobalVars.saved_autoExtract_ESB, GlobalVars.saved_autoExtract_EAB]:
                            if checkAutoExtract: iCountAutos += 1

                        if iCountAutos < 1:
                            GlobalVars.AUTO_EXTRACT_MODE = False
                            msgTxt = "@@ AUTO EXTRACT MODE DISABLED - No auto extracts found/enabled @@"
                            myPrint("B", msgTxt)
                            if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                MyPopUpDialogBox(client_mark_extract_data_frame_, theStatus=msgTxt,
                                                 theMessage="Configure Auto Extract Mode using the setup screen (and selecting 'auto extract')",
                                                 theTitle="EXTRACT_DATA: AUTO_MODE",
                                                 lModal=False).go()

                        elif not isValidExtractFolder(GlobalVars.saved_defaultSavePath_SWSS):
                            GlobalVars.AUTO_EXTRACT_MODE = False
                            msgTxt = "@@ AUTO EXTRACT MODE DISABLED: Pre-saved extract folder appears invalid @@"
                            myPrint("B", "%s: '%s'" %(msgTxt, GlobalVars.saved_defaultSavePath_SWSS))
                            if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                MyPopUpDialogBox(client_mark_extract_data_frame_, theStatus=msgTxt,
                                                 theMessage="Configure Auto Extract Mode using the setup screen (and select the folder to save extracts)\n"
                                                                    "Invalid extract folder:\n"
                                                                    "'%s'" %(GlobalVars.saved_defaultSavePath_SWSS),
                                                 theTitle="EXTRACT_DATA: AUTO_MODE",
                                                 lModal=False).go()

                        else:

                            for exType in ["EAR", "EIT", "ESB", "EAB"]:

                                checkPath = getExtractFullPath(exType, lDoNotAddTimeStamp=True)
                                if check_file_writable(checkPath):
                                    myPrint("B", "AUTO EXTRACT: CONFIRMED >> Default path: '%s' writable... (exists/overwrite: %s)" %(checkPath, os.path.exists(checkPath)))
                                else:
                                    GlobalVars.AUTO_EXTRACT_MODE = False
                                    msgTxt = "@@ AUTO EXTRACT MODE DISABLED: Default extract path invalid (review console) @@"
                                    myPrint("B", "%s: '%s'" %(msgTxt, checkPath))
                                    if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                        MyPopUpDialogBox(client_mark_extract_data_frame_, theStatus=msgTxt,
                                                         theMessage="Configure Auto Extract Mode using setup screen (and selecting the directory to save extracts)\n"
                                                                    "Invalid default path:\n"
                                                                    "'%s'" %(checkPath),
                                                         theTitle="EXTRACT_DATA: AUTO_MODE",
                                                         lModal=False).go()
                                    break

                        if not GlobalVars.AUTO_EXTRACT_MODE:
                            myPrint("B", "@@ AUTO EXTRACT DISABLED - Aborting execution.....! @@")
                            raise QuickAbortThisScriptException

                #######################

                # Create instance to load and obtain parameters - No gui at this point....
                paramDialog = ParametersSecondaryDialog(MD_REF.getUI(), GlobalVars.AUTO_EXTRACT_MODE)

                if GlobalVars.AUTO_EXEC_SCRIPT_MODE:
                    if not isValidScriptPath(GlobalVars.saved_exportAmazonScriptPath_SWSS) or not isValidScriptPath(GlobalVars.saved_importAmazonScriptPath_SWSS):
                        txt = "Invalid script path(s).. Please use the GUI screen and save valid script paths"
                        myPrint("B", txt)
                        myPopupInformationBox(client_mark_extract_data_frame_, txt, theMessageType=JOptionPane.ERROR_MESSAGE)
                        raise QuickAbortThisScriptException
                    else:
                        if "export" in cmd:
                            myPrint("B", "@@ AUTO EXECUTING Export script:")
                            genericSwingEDTRunner(False, False, scriptRunnerFromDisk, GlobalVars.saved_exportAmazonScriptPath_SWSS, "Export Amazon Txns:")
                            raise QuickAbortThisScriptException
                        elif "import" in cmd:
                            myPrint("B", "@@ AUTO EXECUTING Import script:")
                            genericSwingEDTRunner(False, False, scriptRunnerFromDisk, GlobalVars.saved_importAmazonScriptPath_SWSS, "Import Amazon Txns:")
                            raise QuickAbortThisScriptException
                        raise Exception("ERROR: cmd: '%s', script not coded!?" %(cmd))

                elif GlobalVars.AUTO_EXTRACT_MODE:
                    lExtractAccountTxns = GlobalVars.saved_autoExtract_EAR
                    lExtractInvestmentTxns = GlobalVars.saved_autoExtract_EIT
                    lExtractSecurityBalances = GlobalVars.saved_autoExtract_ESB
                    lExtractAccountBalances = GlobalVars.saved_autoExtract_EAB

                    GlobalVars.EXTRACT_DATA = True

                    myPrint("B", "AUTO EXTRACT MODE: Will auto extract the following...:\n"
                                 "     Account Transactions....: %s\n"
                                 "     Investment Transactions.: %s\n"
                                 "     Security Balances.......: %s\n"
                                 "     Account Balances.......: %s\n"
                            %(GlobalVars.saved_autoExtract_EAR, GlobalVars.saved_autoExtract_EIT, GlobalVars.saved_autoExtract_ESB, GlobalVars.saved_autoExtract_EAB))

                else:
                    if GlobalVars.LAST_END_EXTRACT_MESSAGE:
                        myPrint("B", "Result of last manual extract(s):\n", GlobalVars.LAST_END_EXTRACT_MESSAGE)
                        MyPopUpDialogBox(client_mark_extract_data_frame_,
                                         theStatus="LAST EXTRACT PROCESS COMPLETED >> review status below:)",
                                         theMessage=GlobalVars.LAST_END_EXTRACT_MESSAGE,
                                         theTitle="EXTRACT_DATA: MANUAL MODE",
                                         lModal=True).go()
                        GlobalVars.LAST_END_EXTRACT_MESSAGE = None

                    paramDialog.setupPanel()
                    paramDialog.setVisible(True)

                    if paramDialog.isAborted():
                        myPrint("B", "User chose to quit...")
                        raise QuickAbortThisScriptException

                    if paramDialog.clickedExportAMZ():
                        genericSwingEDTRunner(False, False, scriptRunnerFromDisk, GlobalVars.saved_exportAmazonScriptPath_SWSS, "Export Amazon Txns:")
                        raise QuickAbortThisScriptException
                    elif paramDialog.clickedImportAMZ():
                        genericSwingEDTRunner(False, False, scriptRunnerFromDisk, GlobalVars.saved_importAmazonScriptPath_SWSS, "Import Amazon Txns:")
                        raise QuickAbortThisScriptException
                    else:
                        lExtractAccountTxns = paramDialog.clickedExtractAll() or paramDialog.clickedExtractEAR()
                        lExtractInvestmentTxns = paramDialog.clickedExtractAll() or paramDialog.clickedExtractEIT()
                        lExtractSecurityBalances = paramDialog.clickedExtractAll() or paramDialog.clickedExtractESB()
                        lExtractAccountBalances = paramDialog.clickedExtractAll() or paramDialog.clickedExtractEAB()

                        for _check in [lExtractAccountTxns, lExtractInvestmentTxns, lExtractSecurityBalances, lExtractAccountBalances]:
                            GlobalVars.EXTRACT_DATA = True
                        del _check

                ####

                # Get parameters from GUI screen; override the background (fixed) parameters... (they are already saved to disk)
                GlobalVars.saved_securityBalancesDate_ESB = paramDialog.getSecurityBalancesDateESB()

                GlobalVars.selectedAccounts_EAR = paramDialog.getSelectedAccounts()

                drc = paramDialog.getDateRangeChooserEAR()
                GlobalVars.startDateInt_EAR = drc.getDateRange().getStartDateInt()
                GlobalVars.endDateInt_EAR = drc.getDateRange().getEndDateInt()
                if drc.getAllDatesSelected():
                    GlobalVars.endDateInt_EAR = DateRange().getEndDateInt()  # Fix for DRC ALL_DATES Only returning +1 year! (upto builds 5046)
                    myPrint("DB", "@@ All Dates detected; overriding endDateInt_EAR to: %s" %(GlobalVars.endDateInt_EAR))
                del drc

                GlobalVars.lFilterDateRange_EIT = True                                                                             
                drc = paramDialog.getDateRangeChooserEIT()
                GlobalVars.startDateInt_EIT = drc.getDateRange().getStartDateInt()
                GlobalVars.endDateInt_EIT = drc.getDateRange().getEndDateInt()
                if drc.getAllDatesSelected():
                    GlobalVars.endDateInt_EIT = DateRange().getEndDateInt()  # Fix for DRC ALL_DATES Only returning +1 year! (upto builds 5046)
                    myPrint("DB", "@@ All Dates detected; overriding endDateInt_EIT to: %s" %(GlobalVars.endDateInt_EIT))
                del drc

                # Avoid memory leaks....
                paramDialog.book = None
                paramDialog.goAway()
                del paramDialog

                myPrint("DB", "DEBUG IS ON..")
                if lExtractAccountTxns: listParametersEAR()
                if lExtractInvestmentTxns: listParametersEIT()
                if lExtractSecurityBalances: listParametersESB()
                if lExtractAccountBalances: listParametersEAB()
                listCommonExtractParameters()

                # ############################
                # START OF MAIN CODE EXECUTION
                # ############################

                if not GlobalVars.EXTRACT_DATA: raise Exception("LOGIC ERROR - not in Extract Data mode!?")

                GlobalVars.countFilesCreated = 0
                GlobalVars.countErrorsDuringExtract = 0

                class DoExtractsSwingWorker(SwingWorker):

                    pleaseWaitDiag = None       # Single Instance class - so not too worried about multiple access etc

                    @staticmethod
                    def getPleaseWait():
                        # type: () -> MyPopUpDialogBox
                        return DoExtractsSwingWorker.pleaseWaitDiag

                    @staticmethod
                    def setPleaseWait(pleaseWaitDiag):
                        # type: (MyPopUpDialogBox) -> None
                        DoExtractsSwingWorker.pleaseWaitDiag = pleaseWaitDiag

                    @staticmethod
                    def killPleaseWait():
                        # type: () -> None
                        pwd = DoExtractsSwingWorker.getPleaseWait()
                        if pwd is not None:
                            pwd.kill()
                            DoExtractsSwingWorker.setPleaseWait(None)

                    def __init__(self, pleaseWaitDiag):
                        # type: (MyPopUpDialogBox) -> None
                        self.setPleaseWait(pleaseWaitDiag)

                    def process(self, chunks):              # This executes on the EDT
                        if isinstance(chunks, list): pass
                        pwd = self.getPleaseWait()
                        if pwd is not None:
                            if not self.isDone() and not self.isCancelled():
                                for pMsg in chunks:
                                    _msgTxt = pad("PLEASE WAIT - PROCESSING: %s" %(pMsg), 100, padChar=".")
                                    pwd.updateMessages(newTitle=_msgTxt, newStatus=_msgTxt)

                    def doInBackground(self):
                        myPrint("DB", "In DoExtractsSwingWorker()", inspect.currentframe().f_code.co_name, "()")
                        myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                        GlobalVars.baseCurrency = MD_REF.getCurrentAccountBook().getCurrencies().getBaseType()

                        try:
                            cThread = Thread.currentThread()
                            if "_extn_ED" not in cThread.getName(): cThread.setName(u"%s_extn_ED" %(cThread.getName()))
                            del cThread

                            if lExtractAccountTxns:
                                # ##############################################
                                # EXTRACT_ACCOUNT_REGISTERS_CSV EXECUTION
                                # ##############################################

                                _THIS_EXTRACT_NAME = pad("EXTRACT: Account Registers:", 34)
                                GlobalVars.lGlobalErrorDetected = False

                                if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                    self.super__publish([_THIS_EXTRACT_NAME.strip()])                                   # noqa

                                GlobalVars.csvfilename = getExtractFullPath("EAR")

                                def do_extract_account_registers():

                                    # class MyAcctFilterEAR(AcctFilter):
                                    #
                                    #     def __init__(self,
                                    #                  _hideInactiveAccounts=True,
                                    #                  _hideHiddenAccounts=True,
                                    #                  _lAllAccounts=True,
                                    #                  _filterForAccounts="ALL",
                                    #                  _lAllCurrency=True,
                                    #                  _filterForCurrency="ALL"):
                                    #
                                    #         self._hideHiddenAccounts = _hideHiddenAccounts
                                    #         self._hideInactiveAccounts = _hideInactiveAccounts
                                    #         self._lAllAccounts = _lAllAccounts
                                    #         self._filterForAccounts = _filterForAccounts
                                    #         self._lAllCurrency = _lAllCurrency
                                    #         self._filterForCurrency = _filterForCurrency
                                    #
                                    #     def matches(self, acct):
                                    #
                                    #         # noinspection PyUnresolvedReferences
                                    #         if not (acct.getAccountType() == Account.AccountType.BANK
                                    #                 or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                                    #                 or acct.getAccountType() == Account.AccountType.LOAN
                                    #                 or acct.getAccountType() == Account.AccountType.LIABILITY
                                    #                 or acct.getAccountType() == Account.AccountType.ASSET):
                                    #             return False
                                    #
                                    #         if self._hideInactiveAccounts:
                                    #
                                    #             # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
                                    #             if (acct.getAccountOrParentIsInactive()): return False
                                    #             if (acct.getHideOnHomePage() and acct.getBalance() == 0): return False
                                    #
                                    #         if self._lAllAccounts or (self._filterForAccounts.upper().strip() in acct.getFullAccountName().upper().strip()):
                                    #             pass
                                    #         else:
                                    #             return False
                                    #
                                    #         curr = acct.getCurrencyType()
                                    #         currID = curr.getIDString()
                                    #         currName = curr.getName()
                                    #
                                    #         # All accounts and security records can have currencies
                                    #         if self._lAllCurrency:
                                    #             pass
                                    #         elif (self._filterForCurrency.upper().strip() in currID.upper().strip()):
                                    #             pass
                                    #         elif (self._filterForCurrency.upper().strip() in currName.upper().strip()):
                                    #             pass
                                    #         else:
                                    #             return False
                                    #
                                    #         # Phew! We made it....
                                    #         return True
                                    #     # enddef

                                    # Overridden for Mark's bespoke extension.
                                    # validAccountList = AccountUtil.allMatchesForSearch(MD_REF.getCurrentAccountBook(),
                                    #                                                    MyAcctFilterEAR(_hideInactiveAccounts=GlobalVars.hideInactiveAccounts_EAR,
                                    #                                                                    _hideHiddenAccounts=GlobalVars.hideHiddenAccounts_EAR,
                                    #                                                                    _lAllAccounts=GlobalVars.lAllAccounts_EAR,
                                    #                                                                    _filterForAccounts=GlobalVars.filterForAccounts_EAR,
                                    #                                                                    _lAllCurrency=GlobalVars.lAllCurrency_EAR,
                                    #                                                                    _filterForCurrency=GlobalVars.filterForCurrency_EAR))

                                    validAccountList = GlobalVars.selectedAccounts_EAR

                                    if debug:
                                        myPrint("DB", _THIS_EXTRACT_NAME + "%s Accounts selected in filters" %len(validAccountList))
                                        for element in validAccountList: myPrint("D", _THIS_EXTRACT_NAME + "...selected acct: %s" %element)

                                    # _msg = MyPopUpDialogBox(client_mark_extract_data_frame_, theStatus="PLEASE WAIT....", theTitle="Building Database", lModal=False)
                                    # _msg.go()

                                    _COLUMN = 0
                                    _HEADING = 1
                                    GlobalVars.dataKeys = {
                                        "_ACCOUNTTYPE":             [0,  "AccountType"],
                                        "_ACCOUNT":                 [1,  "Account"],
                                        "_DATE":                    [2,  "Date"],
                                        "_TAXDATE":                 [3,  "TaxDate"],
                                        "_CURR":                    [4,  "Currency"],
                                        "_CHEQUE":                  [5,  "Cheque"],
                                        "_DESC":                    [6,  "Description"],
                                        "_MEMO":                    [7,  "Memo"],
                                        "_CLEARED":                 [8,  "Cleared"],
                                        "_TOTALAMOUNT":             [9,  "TotalAmount"],
                                        "_FOREIGNTOTALAMOUNT":      [10, "ForeignTotalAmount"],
                                        "_PARENTTAGS":              [11, "ParentTags"],
                                        "_PARENTHASATTACHMENTS":    [12, "ParentHasAttachments"],
                                        "_SPLITIDX":                [13, "SplitIndex"],
                                        "_SPLITMEMO":               [14, "SplitMemo"],
                                        "_SPLITCAT":                [15, "SplitCategory"],
                                        "_SPLITAMOUNT":             [16, "SplitAmount"],
                                        "_FOREIGNSPLITAMOUNT":      [17, "ForeignSplitAmount"],
                                        "_SPLITTAGS":               [18, "SplitTags"],
                                        "_ISTRANSFERTOACCT":        [19, "isTransferToAnotherAccount"],
                                        "_ISTRANSFERSELECTED":      [20, "isTransferWithinThisExtract"],
                                        "_SPLITHASATTACHMENTS":     [21, "SplitHasAttachments"],
                                        "_ATTACHMENTLINK":          [22, "AttachmentLink"],
                                        "_ATTACHMENTLINKREL":       [23, "AttachmentLinkRelative"],
                                        "_KEY":                     [24, "Key"],
                                        "_END":                     [25, "_END"]
                                    }

                                    GlobalVars.dumpKeys_EAR = []
                                    if GlobalVars.ENABLE_BESPOKE_CODING:                                                # PATCH: client_mark_extract_data
                                        GlobalVars.dumpKeys_EAR.append(GlobalVars.dataKeys["_TAXDATE"][_COLUMN])
                                        GlobalVars.dumpKeys_EAR.append(GlobalVars.dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN])
                                        GlobalVars.dumpKeys_EAR.append(GlobalVars.dataKeys["_PARENTTAGS"][_COLUMN])
                                        GlobalVars.dumpKeys_EAR.append(GlobalVars.dataKeys["_SPLITTAGS"][_COLUMN])
                                        GlobalVars.dumpKeys_EAR.append(GlobalVars.dataKeys["_PARENTHASATTACHMENTS"][_COLUMN])
                                        GlobalVars.dumpKeys_EAR.append(GlobalVars.dataKeys["_SPLITHASATTACHMENTS"][_COLUMN])
                                        GlobalVars.dumpKeys_EAR.append(GlobalVars.dataKeys["_FOREIGNSPLITAMOUNT"][_COLUMN])
                                        GlobalVars.dumpKeys_EAR.append(GlobalVars.dataKeys["_ATTACHMENTLINK"][_COLUMN])
                                        GlobalVars.dumpKeys_EAR.append(GlobalVars.dataKeys["_ATTACHMENTLINKREL"][_COLUMN])

                                    GlobalVars.transactionTable = []

                                    myPrint("DB", _THIS_EXTRACT_NAME, GlobalVars.dataKeys)

                                    book = MD_REF.getCurrentAccountBook()

                                    # noinspection PyArgumentList
                                    class MyTxnSearchCostBasisEAR(TxnSearch):

                                        def __init__(self, _validAccounts):
                                            self._validAccounts = _validAccounts

                                        # noinspection PyMethodMayBeStatic
                                        def matchesAll(self):
                                            return False

                                        def matches(self, _txn):

                                            _txnAcct = _txn.getAccount()

                                            if _txnAcct in self._validAccounts:
                                                return True
                                            else:
                                                return False

                                    txns = book.getTransactionSet().getTransactions(MyTxnSearchCostBasisEAR(validAccountList))

                                    iBal = 0
                                    accountBalances = {}

                                    _local_storage = MD_REF.getCurrentAccountBook().getLocalStorage()

                                    iCount = 0

                                    def tag_search( searchForTags, theTagListToSearch ):

                                        searchTagList = searchForTags.upper().strip().split(",")

                                        for tag in theTagListToSearch:
                                            for searchTag in searchTagList:
                                                if searchTag in tag.upper().strip():
                                                    return True

                                        return False

                                    def getTotalLocalValue( theTxn ):

                                        lValue = 0

                                        for _iSplit in range(0, (theTxn.getOtherTxnCount())):
                                            lValue += GlobalVars.baseCurrency.getDoubleValue(parent_Txn.getOtherTxn(_iSplit).getValue()) * -1

                                        return lValue

                                    copyValidAccountList = ArrayList()
                                    if GlobalVars.lIncludeOpeningBalances_EAR:
                                        for acctBal in validAccountList:
                                            if getUnadjustedStartBalance(acctBal) != 0:
                                                if GlobalVars.startDateInt_EAR <= acctBal.getCreationDateInt() <= GlobalVars.endDateInt_EAR:
                                                    copyValidAccountList.add(acctBal)

                                    if GlobalVars.lIncludeBalanceAdjustments_EAR:
                                        for acctBal in validAccountList:
                                            if getBalanceAdjustment(acctBal) != 0:
                                                if acctBal not in copyValidAccountList:
                                                    copyValidAccountList.add(acctBal)

                                    for txn in txns:

                                        if not (GlobalVars.startDateInt_EAR <= txn.getDateInt() <= GlobalVars.endDateInt_EAR):
                                            continue

                                        lParent = isinstance(txn, ParentTxn)

                                        parent_Txn = txn.getParentTxn()
                                        txnAcct = txn.getAccount()
                                        acctCurr = txnAcct.getCurrencyType()  # Currency of the txn

                                        # Only include opening balances if not filtering records.... (this is caught during parameter selection earlier)
                                        if (GlobalVars.lIncludeOpeningBalances_EAR or GlobalVars.lIncludeBalanceAdjustments_EAR):
                                            if txnAcct in copyValidAccountList:
                                                copyValidAccountList.remove(txnAcct)

                                            if accountBalances.get(txnAcct):
                                                pass
                                            else:
                                                accountBalances[txnAcct] = True
                                                if (GlobalVars.lIncludeOpeningBalances_EAR):
                                                    if GlobalVars.startDateInt_EAR <= txnAcct.getCreationDateInt() <= GlobalVars.endDateInt_EAR:
                                                        openBal = acctCurr.getDoubleValue(getUnadjustedStartBalance(txnAcct))
                                                        if openBal != 0:
                                                            iBal += 1
                                                            _row = ([None] * GlobalVars.dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                            _row[GlobalVars.dataKeys["_KEY"][_COLUMN]] = txnAcct.getUUID()
                                                            _row[GlobalVars.dataKeys["_ACCOUNTTYPE"][_COLUMN]] = safeStr(txnAcct.getAccountType())
                                                            _row[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                                                            _row[GlobalVars.dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                                            _row[GlobalVars.dataKeys["_DESC"][_COLUMN]] = "MANUAL (UNADJUSTED) OPENING BALANCE"
                                                            _row[GlobalVars.dataKeys["_CHEQUE"][_COLUMN]] = "MANUAL"
                                                            _row[GlobalVars.dataKeys["_DATE"][_COLUMN]] = txnAcct.getCreationDateInt()
                                                            _row[GlobalVars.dataKeys["_SPLITIDX"][_COLUMN]] = 0
                                                            if acctCurr == GlobalVars.baseCurrency:
                                                                _row[GlobalVars.dataKeys["_TOTALAMOUNT"][_COLUMN]] = openBal
                                                                _row[GlobalVars.dataKeys["_SPLITAMOUNT"][_COLUMN]] = openBal
                                                            else:
                                                                _row[GlobalVars.dataKeys["_TOTALAMOUNT"][_COLUMN]] = round(openBal / acctCurr.getRate(GlobalVars.baseCurrency),2)
                                                                _row[GlobalVars.dataKeys["_SPLITAMOUNT"][_COLUMN]] = round(openBal / acctCurr.getRate(GlobalVars.baseCurrency),2)
                                                                _row[GlobalVars.dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = openBal
                                                                _row[GlobalVars.dataKeys["_FOREIGNSPLITAMOUNT"][_COLUMN]] = openBal

                                                            myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                            GlobalVars.transactionTable.append(_row)
                                                            del openBal

                                                if (GlobalVars.lIncludeBalanceAdjustments_EAR):
                                                    adjBal = acctCurr.getDoubleValue(getBalanceAdjustment(txnAcct))
                                                    if adjBal != 0:
                                                        iBal += 1
                                                        _row = ([None] * GlobalVars.dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                        _row[GlobalVars.dataKeys["_KEY"][_COLUMN]] = txnAcct.getUUID()
                                                        _row[GlobalVars.dataKeys["_ACCOUNTTYPE"][_COLUMN]] = safeStr(txnAcct.getAccountType())
                                                        _row[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                                                        _row[GlobalVars.dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                                        _row[GlobalVars.dataKeys["_DESC"][_COLUMN]] = "MANUAL BALANCE ADJUSTMENT (MD2023 onwards)"
                                                        _row[GlobalVars.dataKeys["_CHEQUE"][_COLUMN]] = "MANUAL"
                                                        _row[GlobalVars.dataKeys["_DATE"][_COLUMN]] = DateUtil.getStrippedDateInt()
                                                        _row[GlobalVars.dataKeys["_SPLITIDX"][_COLUMN]] = 0
                                                        if acctCurr == GlobalVars.baseCurrency:
                                                            _row[GlobalVars.dataKeys["_TOTALAMOUNT"][_COLUMN]] = adjBal
                                                            _row[GlobalVars.dataKeys["_SPLITAMOUNT"][_COLUMN]] = adjBal
                                                        else:
                                                            _row[GlobalVars.dataKeys["_TOTALAMOUNT"][_COLUMN]] = round(adjBal / acctCurr.getRate(GlobalVars.baseCurrency),2)
                                                            _row[GlobalVars.dataKeys["_SPLITAMOUNT"][_COLUMN]] = round(adjBal / acctCurr.getRate(GlobalVars.baseCurrency),2)
                                                            _row[GlobalVars.dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = adjBal
                                                            _row[GlobalVars.dataKeys["_FOREIGNSPLITAMOUNT"][_COLUMN]] = adjBal


                                                        myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                        GlobalVars.transactionTable.append(_row)
                                                        del adjBal

                                        keyIndex = 0
                                        _row = ([None] * GlobalVars.dataKeys["_END"][0])  # Create a blank row to be populated below...

                                        txnKey = txn.getUUID()
                                        _row[GlobalVars.dataKeys["_KEY"][_COLUMN]] = txnKey + "-" + str(keyIndex).zfill(3)

                                        _row[GlobalVars.dataKeys["_ACCOUNTTYPE"][_COLUMN]] = safeStr(txnAcct.getAccountType())
                                        _row[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                                        _row[GlobalVars.dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                        _row[GlobalVars.dataKeys["_DATE"][_COLUMN]] = txn.getDateInt()
                                        if parent_Txn.getTaxDateInt() != txn.getDateInt():
                                            _row[GlobalVars.dataKeys["_TAXDATE"][_COLUMN]] = txn.getTaxDateInt()

                                        _row[GlobalVars.dataKeys["_CHEQUE"][_COLUMN]] = txn.getCheckNumber()

                                        _row[GlobalVars.dataKeys["_DESC"][_COLUMN]] = parent_Txn.getDescription()
                                        if lParent:
                                            _row[GlobalVars.dataKeys["_MEMO"][_COLUMN]] = txn.getMemo()
                                        else:
                                            _row[GlobalVars.dataKeys["_MEMO"][_COLUMN]] = txn.getDescription()
                                        _row[GlobalVars.dataKeys["_CLEARED"][_COLUMN]] = getStatusCharRevised(txn)


                                        if acctCurr == GlobalVars.baseCurrency:
                                            _row[GlobalVars.dataKeys["_TOTALAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())
                                        else:
                                            if lParent:
                                                _row[GlobalVars.dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())
                                                localValue = getTotalLocalValue( txn )
                                                _row[GlobalVars.dataKeys["_TOTALAMOUNT"][_COLUMN]] = localValue
                                            else:
                                                _row[GlobalVars.dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())
                                                _row[GlobalVars.dataKeys["_TOTALAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getAmount())

                                        _row[GlobalVars.dataKeys["_PARENTHASATTACHMENTS"][_COLUMN]] = parent_Txn.hasAttachments()
                                        if str(parent_Txn.getKeywords()) != "[]": _row[GlobalVars.dataKeys["_PARENTTAGS"][_COLUMN]] = safeStr(parent_Txn.getKeywords())

                                        lNeedToPrintTotalAmount = True

                                        for _ii in range(0, int(parent_Txn.getOtherTxnCount())):        # If a split, then it will always make it here...

                                            if not lParent and _ii > 0: break

                                            splitRowCopy = deepcopy(_row)

                                            if lParent:

                                                if (not GlobalVars.lAllTags_EAR
                                                        and not tag_search(GlobalVars.tagFilter_EAR, txn.getKeywords())
                                                        and not tag_search(GlobalVars.tagFilter_EAR, parent_Txn.getOtherTxn(_ii).getKeywords())):
                                                    continue

                                                if (not GlobalVars.lAllText_EAR
                                                        and GlobalVars.textFilter_EAR not in (parent_Txn.getDescription().upper().strip()
                                                                                   +txn.getMemo().upper().strip()
                                                                                   +parent_Txn.getOtherTxn(_ii).getDescription().upper()).strip()):
                                                    continue

                                                # The category logic below was added by IK user @Mark
                                                if (not GlobalVars.lAllCategories_EAR):        # Note: we only select Accounts, thus Parents are always Accounts (not categories)
                                                    splitTxnAccount = parent_Txn.getOtherTxn(_ii).getAccount()
                                                    parentAccount = parent_Txn.getAccount()
                                                    if ( (isIncomeExpenseAcct(parentAccount) and GlobalVars.categoriesFilter_EAR in (parentAccount.getFullAccountName().upper().strip()))
                                                            or (isIncomeExpenseAcct(splitTxnAccount) and GlobalVars.categoriesFilter_EAR in (splitTxnAccount.getFullAccountName().upper().strip())) ):
                                                        pass
                                                    else:
                                                        continue

                                                splitMemo = parent_Txn.getOtherTxn(_ii).getDescription()
                                                splitTags = safeStr(parent_Txn.getOtherTxn(_ii).getKeywords())
                                                splitCat = parent_Txn.getOtherTxn(_ii).getAccount().getFullAccountName()
                                                splitHasAttachments = parent_Txn.getOtherTxn(_ii).hasAttachments()

                                                splitFAmount = None
                                                if parent_Txn.getOtherTxn(_ii).getAmount() != parent_Txn.getOtherTxn(_ii).getValue():
                                                    splitFAmount = acctCurr.getDoubleValue(parent_Txn.getOtherTxn(_ii).getValue()) * -1
                                                    splitAmount = acctCurr.getDoubleValue(parent_Txn.getOtherTxn(_ii).getAmount()) * -1
                                                else:
                                                    splitAmount = acctCurr.getDoubleValue(parent_Txn.getOtherTxn(_ii).getValue()) * -1

                                                transferAcct = parent_Txn.getOtherTxn(_ii).getAccount()
                                                transferType = transferAcct.getAccountType()

                                                # noinspection PyUnresolvedReferences
                                                if transferAcct != txnAcct and not (
                                                        transferType == Account.AccountType.ROOT
                                                        or transferType == Account.AccountType.INCOME
                                                        or transferType == Account.AccountType.EXPENSE):
                                                    isTransfer = True
                                                else:
                                                    isTransfer = False

                                                isTransferWithinExtract = (isTransfer and transferAcct in validAccountList)

                                                if splitTags == "[]": splitTags = ""

                                            else:
                                                # ######################################################################################
                                                # We are on a split - which is a standalone transfer in/out
                                                if (not GlobalVars.lAllTags_EAR
                                                        and not tag_search(GlobalVars.tagFilter_EAR, txn.getKeywords())
                                                        and not tag_search(GlobalVars.tagFilter_EAR, parent_Txn.getKeywords())):
                                                    break

                                                if (not GlobalVars.lAllText_EAR
                                                        and GlobalVars.textFilter_EAR not in (txn.getDescription().upper().strip()
                                                                                   +parent_Txn.getDescription().upper().strip()
                                                                                   +parent_Txn.getMemo().upper().strip())):
                                                    break

                                                # The category logic below was added by IK user @Mark (and amended by me.....)
                                                if (not GlobalVars.lAllCategories_EAR):
                                                    parentAcct = parent_Txn.getAccount()
                                                    splitTxnAcct = txn.getAccount()
                                                    if ( (isIncomeExpenseAcct(parentAcct) and GlobalVars.categoriesFilter_EAR in parentAcct.getFullAccountName().upper().strip())
                                                            or (isIncomeExpenseAcct(splitTxnAcct) and GlobalVars.categoriesFilter_EAR in splitTxnAcct.getFullAccountName().upper().strip()) ):
                                                        pass
                                                    else:
                                                        break

                                                splitMemo = txn.getDescription()
                                                splitTags = safeStr(txn.getKeywords())
                                                splitCat = parent_Txn.getAccount().getFullAccountName()
                                                splitHasAttachments = txn.hasAttachments()


                                                splitFAmount = None
                                                if txn.getAmount() != txn.getValue():
                                                    splitFAmount = acctCurr.getDoubleValue(txn.getValue())
                                                    splitAmount = acctCurr.getDoubleValue(txn.getAmount())
                                                else:
                                                    splitAmount = acctCurr.getDoubleValue(txn.getValue())

                                                transferAcct = parent_Txn.getAccount()
                                                transferType = transferAcct.getAccountType()

                                                # noinspection PyUnresolvedReferences
                                                if transferAcct != txnAcct and not (
                                                        transferType == Account.AccountType.ROOT
                                                        or transferType == Account.AccountType.INCOME
                                                        or transferType == Account.AccountType.EXPENSE):
                                                    isTransfer = True
                                                else:
                                                    isTransfer = False

                                                isTransferWithinExtract = (isTransfer and transferAcct in validAccountList)

                                                if splitTags == "[]": splitTags = ""

                                            if lNeedToPrintTotalAmount:
                                                lNeedToPrintTotalAmount = False
                                            else:
                                                splitRowCopy[GlobalVars.dataKeys["_TOTALAMOUNT"][_COLUMN]] = None  # Don't repeat this on subsequent rows
                                                splitRowCopy[GlobalVars.dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = None  # Don't repeat this on subsequent rows

                                            splitRowCopy[GlobalVars.dataKeys["_KEY"][_COLUMN]] = txnKey + "-" + str(keyIndex).zfill(3)
                                            splitRowCopy[GlobalVars.dataKeys["_SPLITIDX"][_COLUMN]] = _ii
                                            splitRowCopy[GlobalVars.dataKeys["_SPLITMEMO"][_COLUMN]] = splitMemo
                                            splitRowCopy[GlobalVars.dataKeys["_SPLITAMOUNT"][_COLUMN]] = splitAmount
                                            splitRowCopy[GlobalVars.dataKeys["_FOREIGNSPLITAMOUNT"][_COLUMN]] = splitFAmount
                                            splitRowCopy[GlobalVars.dataKeys["_SPLITTAGS"][_COLUMN]] = splitTags
                                            splitRowCopy[GlobalVars.dataKeys["_SPLITCAT"][_COLUMN]] = splitCat

                                            if GlobalVars.ENABLE_BESPOKE_CODING:                                        # PATCH: client_mark_extract_data
                                                if isTransfer:
                                                    splitRowCopy[GlobalVars.dataKeys["_SPLITCAT"][_COLUMN]] = "[%s]" %(splitCat)

                                            splitRowCopy[GlobalVars.dataKeys["_SPLITHASATTACHMENTS"][_COLUMN]] = splitHasAttachments
                                            splitRowCopy[GlobalVars.dataKeys["_ISTRANSFERTOACCT"][_COLUMN]] = isTransfer
                                            splitRowCopy[GlobalVars.dataKeys["_ISTRANSFERSELECTED"][_COLUMN]] = isTransferWithinExtract

                                            holdTheKeys = ArrayList()
                                            holdTheLocations = ArrayList()

                                            if _ii == 0 and txn.hasAttachments():
                                                # noinspection PyUnresolvedReferences
                                                holdTheKeys = holdTheKeys + txn.getAttachmentKeys()
                                                for _attachKey in txn.getAttachmentKeys():
                                                    # noinspection PyUnresolvedReferences
                                                    holdTheLocations.append(txn.getAttachmentTag(_attachKey))

                                            if lParent and parent_Txn.getOtherTxn(_ii).hasAttachments():
                                                holdTheKeys = holdTheKeys + parent_Txn.getOtherTxn(_ii).getAttachmentKeys()
                                                for _attachKey in parent_Txn.getOtherTxn(_ii).getAttachmentKeys():
                                                    # noinspection PyUnresolvedReferences
                                                    holdTheLocations.append(parent_Txn.getOtherTxn(_ii).getAttachmentTag(_attachKey))

                                            if holdTheKeys:
                                                splitRowCopy[GlobalVars.dataKeys["_ATTACHMENTLINK"][_COLUMN]] = safeStr(holdTheKeys)
                                            myPrint("D", _THIS_EXTRACT_NAME, splitRowCopy)
                                            GlobalVars.transactionTable.append(splitRowCopy)
                                            # abort
                                            keyIndex += 1
                                            iCount += 1
                                            continue

                                    if (GlobalVars.lIncludeOpeningBalances_EAR or GlobalVars.lIncludeBalanceAdjustments_EAR) and len(copyValidAccountList) > 0:
                                        myPrint("DB", _THIS_EXTRACT_NAME + "Now iterating remaining %s Accounts with no txns for balances...." %(len(copyValidAccountList)))

                                        # Yes I should just move this section from above so the code is not inefficient....
                                        for acctBal in copyValidAccountList:

                                            acctCurr = acctBal.getCurrencyType()  # Currency of the acct

                                            if (GlobalVars.lIncludeOpeningBalances_EAR):
                                                openBal = acctCurr.getDoubleValue(getUnadjustedStartBalance(acctBal))
                                                if openBal != 0:
                                                    iBal += 1
                                                    _row = ([None] * GlobalVars.dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                    _row[GlobalVars.dataKeys["_KEY"][_COLUMN]] = acctBal.getUUID()
                                                    _row[GlobalVars.dataKeys["_ACCOUNTTYPE"][_COLUMN]] = safeStr(acctBal.getAccountType())
                                                    _row[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]] = acctBal.getFullAccountName()
                                                    _row[GlobalVars.dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                                    _row[GlobalVars.dataKeys["_DESC"][_COLUMN]] = "MANUAL (UNADJUSTED) OPENING BALANCE"
                                                    _row[GlobalVars.dataKeys["_CHEQUE"][_COLUMN]] = "MANUAL"
                                                    _row[GlobalVars.dataKeys["_DATE"][_COLUMN]] = acctBal.getCreationDateInt()
                                                    _row[GlobalVars.dataKeys["_SPLITIDX"][_COLUMN]] = 0
                                                    if acctCurr == GlobalVars.baseCurrency:
                                                        _row[GlobalVars.dataKeys["_TOTALAMOUNT"][_COLUMN]] = openBal
                                                        _row[GlobalVars.dataKeys["_SPLITAMOUNT"][_COLUMN]] = openBal
                                                    else:
                                                        _row[GlobalVars.dataKeys["_TOTALAMOUNT"][_COLUMN]] = round(openBal / acctCurr.getRate(GlobalVars.baseCurrency),2)
                                                        _row[GlobalVars.dataKeys["_SPLITAMOUNT"][_COLUMN]] = round(openBal / acctCurr.getRate(GlobalVars.baseCurrency),2)
                                                        _row[GlobalVars.dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = openBal
                                                        _row[GlobalVars.dataKeys["_FOREIGNSPLITAMOUNT"][_COLUMN]] = openBal

                                                    myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                    GlobalVars.transactionTable.append(_row)
                                                    del openBal

                                            if (GlobalVars.lIncludeBalanceAdjustments_EAR):
                                                adjBal = acctCurr.getDoubleValue(getBalanceAdjustment(acctBal))
                                                if adjBal != 0:
                                                    iBal += 1
                                                    _row = ([None] * GlobalVars.dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                    _row[GlobalVars.dataKeys["_KEY"][_COLUMN]] = acctBal.getUUID()
                                                    _row[GlobalVars.dataKeys["_ACCOUNTTYPE"][_COLUMN]] = safeStr(acctBal.getAccountType())
                                                    _row[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]] = acctBal.getFullAccountName()
                                                    _row[GlobalVars.dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                                    _row[GlobalVars.dataKeys["_DESC"][_COLUMN]] = "MANUAL BALANCE ADJUSTMENT (MD2023 onwards)"
                                                    _row[GlobalVars.dataKeys["_CHEQUE"][_COLUMN]] = "MANUAL"
                                                    _row[GlobalVars.dataKeys["_DATE"][_COLUMN]] = DateUtil.getStrippedDateInt()
                                                    _row[GlobalVars.dataKeys["_SPLITIDX"][_COLUMN]] = 0
                                                    if acctCurr == GlobalVars.baseCurrency:
                                                        _row[GlobalVars.dataKeys["_TOTALAMOUNT"][_COLUMN]] = adjBal
                                                        _row[GlobalVars.dataKeys["_SPLITAMOUNT"][_COLUMN]] = adjBal
                                                    else:
                                                        _row[GlobalVars.dataKeys["_TOTALAMOUNT"][_COLUMN]] = round(adjBal / acctCurr.getRate(GlobalVars.baseCurrency),2)
                                                        _row[GlobalVars.dataKeys["_SPLITAMOUNT"][_COLUMN]] = round(adjBal / acctCurr.getRate(GlobalVars.baseCurrency),2)
                                                        _row[GlobalVars.dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = adjBal
                                                        _row[GlobalVars.dataKeys["_FOREIGNSPLITAMOUNT"][_COLUMN]] = adjBal

                                                    myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                    GlobalVars.transactionTable.append(_row)
                                                    del adjBal

                                    myPrint("B", _THIS_EXTRACT_NAME + "Account Register Transaction Records (Parents, Splits) selected:", len(GlobalVars.transactionTable) )

                                    if iBal: myPrint("B", _THIS_EXTRACT_NAME + "...and %s Manual Opening Balance / Adjustment (MD2023 onwards) entries created too..." %iBal)
                                    ###########################################################################################################

                                    # sort the file:
                                    GlobalVars.transactionTable = sorted(GlobalVars.transactionTable, key=lambda x: (x[GlobalVars.dataKeys["_ACCOUNTTYPE"][_COLUMN]],
                                                                                                                 x[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]],
                                                                                                                 x[GlobalVars.dataKeys["_DATE"][_COLUMN]],
                                                                                                                 x[GlobalVars.dataKeys["_KEY"][_COLUMN]],
                                                                                                                 x[GlobalVars.dataKeys["_SPLITIDX"][_COLUMN]]) )
                                    ###########################################################################################################

                                    def ExtractDataToFile():
                                        myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                        headings = []
                                        sortDataFields = sorted(GlobalVars.dataKeys.items(), key=lambda x: x[1][_COLUMN])
                                        for i in sortDataFields:
                                            if GlobalVars.ENABLE_BESPOKE_CODING:                                        # PATCH: client_mark_extract_data
                                                if i[1][_COLUMN] in GlobalVars.dumpKeys_EAR: continue
                                            headings.append(i[1][_HEADING])

                                        myPrint("DB", _THIS_EXTRACT_NAME + "Now pre-processing the file to convert integer dates and strip non-ASCII if requested....")
                                        for _theRow in GlobalVars.transactionTable:
                                            dateasdate = datetime.datetime.strptime(str(_theRow[GlobalVars.dataKeys["_DATE"][_COLUMN]]), "%Y%m%d")  # Convert to Date field
                                            _dateoutput = dateasdate.strftime(GlobalVars.excelExtractDateFormat)
                                            _theRow[GlobalVars.dataKeys["_DATE"][_COLUMN]] = _dateoutput

                                            if _theRow[GlobalVars.dataKeys["_TAXDATE"][_COLUMN]]:
                                                dateasdate = datetime.datetime.strptime(str(_theRow[GlobalVars.dataKeys["_TAXDATE"][_COLUMN]]), "%Y%m%d")  # Convert to Date field
                                                _dateoutput = dateasdate.strftime(GlobalVars.excelExtractDateFormat)
                                                _theRow[GlobalVars.dataKeys["_TAXDATE"][_COLUMN]] = _dateoutput

                                            for col in range(0, GlobalVars.dataKeys["_ATTACHMENTLINK"][_COLUMN]):  # DO NOT MESS WITH ATTACHMENT LINK NAMES!!
                                                _theRow[col] = fixFormatsStr(_theRow[col])

                                        myPrint("B", _THIS_EXTRACT_NAME + "Opening file and writing %s records"  %(len(GlobalVars.transactionTable)))


                                        try:
                                            # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                                            with open(GlobalVars.csvfilename, "wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary just use "w" and newline='' in PY3.0

                                                if GlobalVars.lWriteBOMToExtractFile:
                                                    csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                                                writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(GlobalVars.csvDelimiter))

                                                if GlobalVars.csvDelimiter != ",":
                                                    writer.writerow(["sep=", ""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                                                iFindEndHeadingCol = headings.index(GlobalVars.dataKeys["_KEY"][_HEADING])
                                                writer.writerow(headings[:iFindEndHeadingCol])  # Write the header, but not the extra _field headings

                                                try:
                                                    for i in range(0, len(GlobalVars.transactionTable)):
                                                        if GlobalVars.ENABLE_BESPOKE_CODING:                            # PATCH: client_mark_extract_data
                                                            tmpRow = []
                                                            for tmpCol in range(0, GlobalVars.dataKeys["_ATTACHMENTLINKREL"][_COLUMN]):
                                                                if tmpCol in GlobalVars.dumpKeys_EAR: continue
                                                                tmpRow.append(GlobalVars.transactionTable[i][tmpCol])
                                                            writer.writerow(tmpRow)
                                                            del tmpRow, tmpCol
                                                        else:
                                                            writer.writerow(GlobalVars.transactionTable[i][:GlobalVars.dataKeys["_ATTACHMENTLINKREL"][_COLUMN]])
                                                except:
                                                    _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR writing to CSV on row %s. Please review console" %(i)
                                                    GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                    myPrint("B", _msgTxt)
                                                    myPrint("B", GlobalVars.transactionTable[i])
                                                    raise

                                            _msgTxt = _THIS_EXTRACT_NAME + "CSV file: '%s' created (%s records)" %(GlobalVars.csvfilename, len(GlobalVars.transactionTable))
                                            myPrint("B", _msgTxt)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            GlobalVars.countFilesCreated += 1

                                        except:
                                            e_type, exc_value, exc_traceback = sys.exc_info()                           # noqa
                                            _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR '%s' detected writing file: '%s' - Extract ABORTED!" %(exc_value, GlobalVars.csvfilename)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            myPrint("B", _msgTxt)
                                            raise

                                    def fixFormatsStr(theString, lNumber=False, sFormat=""):
                                        if isinstance(theString, bool): return theString
                                        if isinstance(theString, tuple): return theString
                                        if isinstance(theString, dict): return theString
                                        if isinstance(theString, list): return theString

                                        if isinstance(theString, int) or isinstance(theString, float) or isinstance(theString, long):
                                            lNumber = True

                                        if lNumber is None: lNumber = False
                                        if theString is None: theString = ""

                                        if sFormat == "%" and theString != "":
                                            theString = "{:.1%}".format(theString)
                                            return theString

                                        if lNumber: return str(theString)

                                        theString = theString.strip()  # remove leading and trailing spaces

                                        theString = theString.replace("\n", "*")  # remove newlines within fields to keep csv format happy
                                        theString = theString.replace("\t", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace(";", "*")
                                        # theString = theString.replace(",", "*")
                                        # theString = theString.replace("|", "*")

                                        if GlobalVars.lStripASCII:
                                            all_ASCII = ''.join(char for char in theString if ord(char) < 128)  # Eliminate non ASCII printable Chars too....
                                        else:
                                            all_ASCII = theString
                                        return all_ASCII

                                    if iBal+iCount > 0:
                                        ExtractDataToFile()

                                        if not GlobalVars.lGlobalErrorDetected:
                                            sTxt = "Extract file CREATED:"
                                            mTxt = ("With %s rows\n" % (len(GlobalVars.transactionTable)))
                                            myPrint("B", _THIS_EXTRACT_NAME + "%s\n%s" %(sTxt, mTxt))
                                        else:
                                            _msgTextx = _THIS_EXTRACT_NAME + "ERROR Creating extract (review console for error messages)...."
                                            GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                    else:
                                        _msgTextx = _THIS_EXTRACT_NAME + "@@ No records selected and no extract file created @@"
                                        GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                        myPrint("B", _msgTextx)
                                        if not GlobalVars.AUTO_EXTRACT_MODE:
                                            DoExtractsSwingWorker.killPleaseWait()
                                            genericSwingEDTRunner(True, True, myPopupInformationBox, client_mark_extract_data_frame_, _msgTextx, GlobalVars.thisScriptName, JOptionPane.WARNING_MESSAGE)

                                    # delete references to large objects
                                    GlobalVars.transactionTable = None
                                    del accountBalances

                                try:
                                    do_extract_account_registers()
                                except:
                                    GlobalVars.lGlobalErrorDetected = True

                                if GlobalVars.lGlobalErrorDetected:
                                    GlobalVars.countErrorsDuringExtract += 1
                                    _txt = _THIS_EXTRACT_NAME + "@@ ERROR: do_extract_account_registers() has failed (review console)!"
                                    GlobalVars.AUTO_MESSAGES.append(_txt)
                                    myPrint("B", _txt)
                                    dump_sys_error_to_md_console_and_errorlog()
                                    if not GlobalVars.AUTO_EXTRACT_MODE:
                                        DoExtractsSwingWorker.killPleaseWait()
                                        genericSwingEDTRunner(True, True, myPopupInformationBox, client_mark_extract_data_frame_, _txt, "ERROR", JOptionPane.ERROR_MESSAGE)
                                        return False
                            #### ENDIF lExtractAccountTxns ####

                            if lExtractInvestmentTxns:
                                # ####################################################
                                # EXTRACT_INVESTMENT_TRANSACTIONS_CSV EXECUTION
                                # ####################################################

                                _THIS_EXTRACT_NAME = pad("EXTRACT: Investment Transactions:", 34)
                                GlobalVars.lGlobalErrorDetected = False

                                if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                    self.super__publish([_THIS_EXTRACT_NAME.strip()])                                   # noqa

                                GlobalVars.csvfilename = getExtractFullPath("EIT")

                                def do_extract_investment_transactions():

                                    # noinspection PyArgumentList
                                    class MyTxnSearchCostBasisEIT(TxnSearch):

                                        def __init__(self,
                                                     _hideInactiveAccounts=False,
                                                     _lAllAccounts=True,
                                                     _filterForAccounts="ALL",
                                                     _hideHiddenAccounts=False,
                                                     _hideHiddenSecurities=False,
                                                     _lAllCurrency=True,
                                                     _filterForCurrency="ALL",
                                                     _lAllSecurity=True,
                                                     _filterForSecurity="ALL",
                                                     _findUUID=None):

                                            self._hideInactiveAccounts = _hideInactiveAccounts
                                            self._lAllAccounts = _lAllAccounts
                                            self._filterForAccounts = _filterForAccounts
                                            self._hideHiddenAccounts = _hideHiddenAccounts
                                            self._hideHiddenSecurities = _hideHiddenSecurities
                                            self._lAllCurrency = _lAllCurrency
                                            self._filterForCurrency = _filterForCurrency
                                            self._lAllSecurity = _lAllSecurity
                                            self._filterForSecurity = _filterForSecurity
                                            self._findUUID = _findUUID

                                        # noinspection PyMethodMayBeStatic
                                        def matchesAll(self):
                                            return False


                                        def matches(self, _txn):
                                            # NOTE: If not using the parameter selectAccountType=.SECURITY then the security filters won't work (without
                                            # special extra coding!)

                                            _txnAcct = _txn.getAccount()

                                            if self._findUUID is not None:  # If UUID supplied, override all other parameters...
                                                if _txnAcct.getUUID() == self._findUUID:
                                                    return True
                                                else:
                                                    return False

                                            # Investment Accounts only
                                            # noinspection PyUnresolvedReferences
                                            if _txnAcct.getAccountType() != Account.AccountType.INVESTMENT:
                                                return False

                                            if self._hideInactiveAccounts:
                                                # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
                                                if _txnAcct.getAccountOrParentIsInactive(): return False
                                                if _txnAcct.getHideOnHomePage() and _txnAcct.getBalance() == 0: return False
                                                # Don't repeat the above check on the security sub accounts as probably needed for cost basis reporting

                                            if self._lAllAccounts:
                                                pass
                                            elif (self._filterForAccounts.upper().strip() in _txnAcct.getFullAccountName().upper().strip()):
                                                pass
                                            else:
                                                return False

                                            if (not self._hideHiddenAccounts) or (self._hideHiddenAccounts and not _txnAcct.getHideOnHomePage()):
                                                pass
                                            else:
                                                return False

                                            # Check that we are on a parent. If we are on a split, in an Investment Account, then it must be a cash txfr only
                                            _lParent = isinstance(_txn, ParentTxn)
                                            txnCurr = _txnAcct.getCurrencyType()

                                            if self._lAllSecurity:
                                                _securityCurr = None                                                    # noqa
                                                _securityTxn = None                                                     # noqa
                                                _securityAcct = None                                                    # noqa
                                            else:

                                                if not _lParent: return False

                                                # If we don't have a security record, then we are not interested!
                                                _securityTxn = TxnUtil.getSecurityPart(_txn)
                                                if _securityTxn is None:
                                                    return False

                                                _securityAcct = _securityTxn.getAccount()
                                                _securityCurr = _securityAcct.getCurrencyType()

                                                if not self._hideHiddenSecurities or (self._hideHiddenSecurities and not _securityCurr.getHideInUI()):
                                                    pass
                                                else:
                                                    return False

                                                # noinspection PyUnresolvedReferences
                                                if self._lAllSecurity:
                                                    pass
                                                elif self._filterForSecurity.upper().strip() in _securityCurr.getTickerSymbol().upper().strip():
                                                    pass
                                                elif self._filterForSecurity.upper().strip() in _securityCurr.getName().upper().strip():
                                                    pass
                                                else:
                                                    return False

                                            if self._lAllCurrency:
                                                pass
                                            else:
                                                if _securityCurr:
                                                    # noinspection PyUnresolvedReferences
                                                    if txnCurr.getIDString().upper().strip() != _securityCurr.getRelativeCurrency().getIDString().upper().strip():
                                                        _msgTxt = _THIS_EXTRACT_NAME + "LOGIC ERROR: I can't see how the Security's currency is different to the Account's currency?"
                                                        myPrint("B", _msgTxt)
                                                        # noinspection PyUnresolvedReferences
                                                        myPrint("B", _THIS_EXTRACT_NAME, txnCurr.getIDString().upper().strip(), _securityCurr.getRelativeCurrency().getIDString().upper().strip())
                                                        myPrint("B", _THIS_EXTRACT_NAME, repr(_txn))
                                                        myPrint("B", _THIS_EXTRACT_NAME, repr(txnCurr))
                                                        myPrint("B", _THIS_EXTRACT_NAME, repr(_securityCurr))
                                                        # noinspection PyUnresolvedReferences
                                                        if not GlobalVars.AUTO_EXTRACT_MODE:
                                                            DoExtractsSwingWorker.killPleaseWait()
                                                            genericSwingEDTRunner(True, True, myPopupInformationBox, client_mark_extract_data_frame_, _msgTxt, "LOGIC ERROR", JOptionPane.ERROR_MESSAGE)
                                                        # noinspection PyUnresolvedReferences
                                                        raise Exception(_THIS_EXTRACT_NAME + "LOGIC Error - Security's currency: "
                                                                        + _securityCurr.getRelativeCurrency().getIDString().upper().strip()
                                                                        + " is different to txn currency: "
                                                                        + txnCurr.getIDString().upper().strip()
                                                                        + " Aborting")

                                                    # All accounts and security records can have currencies
                                                    # noinspection PyUnresolvedReferences
                                                    if self._lAllCurrency:
                                                        pass
                                                    elif (self._filterForCurrency.upper().strip() in txnCurr.getIDString().upper().strip()) \
                                                            and (
                                                            self._filterForCurrency.upper().strip() in _securityCurr.getRelativeCurrency().getIDString().upper().strip()):
                                                        pass
                                                    elif (self._filterForCurrency.upper().strip() in txnCurr.getName().upper().strip()) \
                                                            and (
                                                            self._filterForCurrency.upper().strip() in _securityCurr.getRelativeCurrency().getName().upper().strip()):
                                                        pass
                                                    else:
                                                        return False

                                                else:
                                                    # All accounts and security records can have currencies
                                                    if self._lAllCurrency:
                                                        pass
                                                    elif (self._filterForCurrency.upper().strip() in txnCurr.getIDString().upper().strip()):
                                                        pass
                                                    elif (self._filterForCurrency.upper().strip() in txnCurr.getName().upper().strip()):
                                                        pass
                                                    else:
                                                        return False

                                            # Phew! We made it....
                                            return True
                                        # enddef

                                    # noinspection PyArgumentList
                                    class MyAcctFilterEIT(AcctFilter):

                                        def __init__(self,
                                                     _hideInactiveAccounts=False,
                                                     _lAllAccounts=True,
                                                     _filterForAccounts="ALL",
                                                     _hideHiddenAccounts=False,
                                                     _hideHiddenSecurities=False,
                                                     _lAllCurrency=True,
                                                     _filterForCurrency="ALL",
                                                     _lAllSecurity=True,
                                                     _filterForSecurity="ALL",
                                                     _findUUID=None):

                                            self._hideInactiveAccounts = _hideInactiveAccounts
                                            self._lAllAccounts = _lAllAccounts
                                            self._filterForAccounts = _filterForAccounts
                                            self._hideHiddenAccounts = _hideHiddenAccounts
                                            self._hideHiddenSecurities = _hideHiddenSecurities
                                            self._lAllCurrency = _lAllCurrency
                                            self._filterForCurrency = _filterForCurrency
                                            self._lAllSecurity = _lAllSecurity
                                            self._filterForSecurity = _filterForSecurity
                                            self._findUUID = _findUUID

                                        def matches(self, acct):

                                            if self._findUUID is not None:  # If UUID supplied, override all other parameters...
                                                if acct.getUUID() == self._findUUID:
                                                    return True
                                                else:
                                                    return False

                                            # Investment Accounts only
                                            # noinspection PyUnresolvedReferences
                                            if acct.getAccountType() != Account.AccountType.INVESTMENT:
                                                return False

                                            if self._hideInactiveAccounts:
                                                # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
                                                if acct.getAccountOrParentIsInactive(): return False
                                                if acct.getHideOnHomePage() and acct.getBalance() == 0: return False

                                            if self._lAllAccounts:
                                                pass
                                            elif (self._filterForAccounts.upper().strip() in acct.getFullAccountName().upper().strip()):
                                                pass
                                            else:
                                                return False

                                            if (not self._hideHiddenAccounts) or (self._hideHiddenAccounts and not acct.getHideOnHomePage()):
                                                pass
                                            else:
                                                return False

                                            if self._lAllSecurity:
                                                pass
                                            else:
                                                return False

                                            if self._lAllCurrency:
                                                pass
                                            else:
                                                _acctCurr = acct.getCurrencyType()
                                                if (self._filterForCurrency.upper().strip() in _acctCurr.getIDString().upper().strip()):
                                                    pass
                                                elif (self._filterForCurrency.upper().strip() in _acctCurr.getName().upper().strip()):
                                                    pass
                                                else:
                                                    return False

                                            return True


                                    _COLUMN = 0
                                    _HEADING = 1

                                    dki = 0
                                    GlobalVars.dataKeys = {}                                                            # noqa
                                    GlobalVars.dataKeys["_ACCOUNT"]             = [dki, "Account"];                   dki += 1
                                    GlobalVars.dataKeys["_DATE"]                = [dki, "Date"];                      dki += 1
                                    GlobalVars.dataKeys["_TAXDATE"]             = [dki, "TaxDate"];                   dki += 1
                                    GlobalVars.dataKeys["_CURR"]                = [dki, "Currency"];                  dki += 1
                                    GlobalVars.dataKeys["_SECURITY"]            = [dki, "Security"];                  dki += 1
                                    GlobalVars.dataKeys["_SECURITYID"]          = [dki, "SecurityID"];                dki += 1
                                    GlobalVars.dataKeys["_TICKER"]              = [dki, "SecurityTicker"];            dki += 1
                                    GlobalVars.dataKeys["_SECCURR"]             = [dki, "SecurityCurrency"];          dki += 1
                                    GlobalVars.dataKeys["_AVGCOST"]             = [dki, "AverageCostControl"];        dki += 1

                                    if GlobalVars.lExtractExtraSecurityAcctInfo_EIT:
                                        GlobalVars.dataKeys["_SECINFO_TYPE"]              = [dki, "Sec_Type"];                     dki += 1
                                        GlobalVars.dataKeys["_SECINFO_SUBTYPE"]           = [dki, "Sec_SubType"];                  dki += 1
                                        GlobalVars.dataKeys["_SECINFO_STK_DIV"]           = [dki, "Sec_Stock_Div"];                dki += 1
                                        GlobalVars.dataKeys["_SECINFO_CD_APR"]            = [dki, "Sec_CD_APR"];                   dki += 1
                                        GlobalVars.dataKeys["_SECINFO_CD_COMPOUNDING"]    = [dki, "Sec_CD_Compounding"];           dki += 1
                                        GlobalVars.dataKeys["_SECINFO_CD_YEARS"]          = [dki, "Sec_CD_Years"];                 dki += 1
                                        GlobalVars.dataKeys["_SECINFO_BOND_TYPE"]         = [dki, "Sec_Bond_Type"];                dki += 1
                                        GlobalVars.dataKeys["_SECINFO_BOND_FACEVALUE"]    = [dki, "Sec_Bond_FaceValue"];           dki += 1
                                        GlobalVars.dataKeys["_SECINFO_BOND_MATURITYDATE"] = [dki, "Sec_Bond_MaturityDate"];        dki += 1
                                        GlobalVars.dataKeys["_SECINFO_BOND_APR"]          = [dki, "Sec_Bond_APR"];                 dki += 1
                                        GlobalVars.dataKeys["_SECINFO_STKOPT_CALLPUT"]    = [dki, "Sec_StockOpt_CallPut"];         dki += 1
                                        GlobalVars.dataKeys["_SECINFO_STKOPT_STKPRICE"]   = [dki, "Sec_StockOpt_StockPrice"];      dki += 1
                                        GlobalVars.dataKeys["_SECINFO_STKOPT_EXPRICE"]    = [dki, "Sec_StockOpt_ExercisePrice"];   dki += 1
                                        GlobalVars.dataKeys["_SECINFO_STKOPT_EXMONTH"]    = [dki, "Sec_StockOpt_ExerciseMonth"];   dki += 1

                                    GlobalVars.dataKeys["_ACTION"]              = [dki, "Action"];                    dki += 1
                                    GlobalVars.dataKeys["_TT"]                  = [dki, "ActionType"];                dki += 1
                                    GlobalVars.dataKeys["_CHEQUE"]              = [dki, "Cheque"];                    dki += 1
                                    GlobalVars.dataKeys["_DESC"]                = [dki, "Description"];               dki += 1
                                    GlobalVars.dataKeys["_MEMO"]                = [dki, "Memo"];                      dki += 1
                                    GlobalVars.dataKeys["_CLEARED"]             = [dki, "Cleared"];                   dki += 1
                                    GlobalVars.dataKeys["_TRANSFER"]            = [dki, "Transfer"];                  dki += 1
                                    GlobalVars.dataKeys["_CAT"]                 = [dki, "Category"];                  dki += 1
                                    GlobalVars.dataKeys["_SHARES"]              = [dki, "Shares"];                    dki += 1
                                    GlobalVars.dataKeys["_PRICE"]               = [dki, "Price"];                     dki += 1
                                    GlobalVars.dataKeys["_AMOUNT"]              = [dki, "Amount"];                    dki += 1
                                    GlobalVars.dataKeys["_FEE"]                 = [dki, "Fee"];                       dki += 1
                                    GlobalVars.dataKeys["_FEECAT"]              = [dki, "FeeCategory"];               dki += 1
                                    GlobalVars.dataKeys["_TXNNETAMOUNT"]        = [dki, "TransactionNetAmount"];      dki += 1
                                    GlobalVars.dataKeys["_CASHIMPACT"]          = [dki, "CashImpact"];                dki += 1
                                    GlobalVars.dataKeys["_SHRSAFTERSPLIT"]      = [dki, "CalculateSharesAfterSplit"]; dki += 1
                                    GlobalVars.dataKeys["_PRICEAFTERSPLIT"]     = [dki, "CalculatePriceAfterSplit"];  dki += 1
                                    GlobalVars.dataKeys["_HASATTACHMENTS"]      = [dki, "HasAttachments"];            dki += 1
                                    GlobalVars.dataKeys["_LOTS"]                = [dki, "Lot Data"];                  dki += 1
                                    GlobalVars.dataKeys["_ACCTCASHBAL"]         = [dki, "AccountCashBalance"];        dki += 1
                                    GlobalVars.dataKeys["_SECSHRHOLDING"]       = [dki, "SecurityShareHolding"];      dki += 1
                                    GlobalVars.dataKeys["_ATTACHMENTLINK"]      = [dki, "AttachmentLink"];            dki += 1
                                    GlobalVars.dataKeys["_ATTACHMENTLINKREL"]   = [dki, "AttachmentLinkRelative"];    dki += 1
                                    GlobalVars.dataKeys["_KEY"]                 = [dki, "Key"];                       dki += 1
                                    GlobalVars.dataKeys["_END"]                 = [dki, "_END"];                      dki += 1

                                    GlobalVars.dumpKeys_EIT = []
                                    if GlobalVars.ENABLE_BESPOKE_CODING:                                                # PATCH: client_mark_extract_data
                                        GlobalVars.dumpKeys_EIT.append(GlobalVars.dataKeys["_TAXDATE"][_COLUMN])
                                        GlobalVars.dumpKeys_EIT.append(GlobalVars.dataKeys["_HASATTACHMENTS"][_COLUMN])
                                        GlobalVars.dumpKeys_EIT.append(GlobalVars.dataKeys["_ATTACHMENTLINK"][_COLUMN])
                                        GlobalVars.dumpKeys_EIT.append(GlobalVars.dataKeys["_ATTACHMENTLINKREL"][_COLUMN])

                                    GlobalVars.transactionTable = []

                                    myPrint("DB", _THIS_EXTRACT_NAME, GlobalVars.dataKeys)

                                    book = MD_REF.getCurrentAccountBook()

                                    txns = book.getTransactionSet().getTransactions(MyTxnSearchCostBasisEIT(GlobalVars.hideInactiveAccounts_EIT,
                                                                                                            GlobalVars.lAllAccounts_EIT,
                                                                                                            GlobalVars.filterForAccounts_EIT,
                                                                                                            GlobalVars.hideHiddenAccounts_EIT,
                                                                                                            GlobalVars.hideHiddenSecurities_EIT,
                                                                                                            GlobalVars.lAllCurrency_EIT,
                                                                                                            GlobalVars.filterForCurrency_EIT,
                                                                                                            GlobalVars.lAllSecurity_EIT,
                                                                                                            GlobalVars.filterForSecurity_EIT,
                                                                                                            None))

                                    validAccountList = AccountUtil.allMatchesForSearch(book, MyAcctFilterEIT(GlobalVars.hideInactiveAccounts_EIT,
                                                                                                             GlobalVars.lAllAccounts_EIT,
                                                                                                             GlobalVars.filterForAccounts_EIT,
                                                                                                             GlobalVars.hideHiddenAccounts_EIT,
                                                                                                             GlobalVars.hideHiddenSecurities_EIT,
                                                                                                             GlobalVars.lAllCurrency_EIT,
                                                                                                             GlobalVars.filterForCurrency_EIT,
                                                                                                             GlobalVars.lAllSecurity_EIT,
                                                                                                             GlobalVars.filterForSecurity_EIT,
                                                                                                             None))

                                    iCount = 0
                                    _local_storage = MD_REF.getCurrentAccountBook().getLocalStorage()

                                    iBal = 0
                                    accountBalances = {}

                                    copyValidAccountList = ArrayList()
                                    if GlobalVars.lIncludeOpeningBalances_EIT:
                                        for acctBal in validAccountList:
                                            if getUnadjustedStartBalance(acctBal) != 0:
                                                if (not GlobalVars.lFilterDateRange_EIT or
                                                        (GlobalVars.lFilterDateRange_EIT and acctBal.getCreationDateInt() >= GlobalVars.startDateInt_EIT and acctBal.getCreationDateInt() <= GlobalVars.endDateInt_EIT)):
                                                    copyValidAccountList.add(acctBal)

                                    if GlobalVars.lIncludeBalanceAdjustments_EIT:
                                        for acctBal in validAccountList:
                                            if getBalanceAdjustment(acctBal) != 0:
                                                if acctBal not in copyValidAccountList:
                                                    copyValidAccountList.add(acctBal)

                                    for txn in txns:

                                        txnAcct = txn.getAccount()
                                        acctCurr = txnAcct.getCurrencyType()  # Currency of the Investment Account

                                        if (GlobalVars.lIncludeOpeningBalances_EIT or GlobalVars.lIncludeBalanceAdjustments_EIT):

                                            if txnAcct in copyValidAccountList:
                                                copyValidAccountList.remove(txnAcct)

                                            if accountBalances.get(txnAcct):
                                                pass

                                            else:
                                                accountBalances[txnAcct] = True

                                                if (not GlobalVars.lFilterDateRange_EIT
                                                        or (txnAcct.getCreationDateInt() >= GlobalVars.startDateInt_EIT and txnAcct.getCreationDateInt() <= GlobalVars.endDateInt_EIT)):

                                                    if (GlobalVars.lIncludeOpeningBalances_EIT):
                                                        openBal = acctCurr.getDoubleValue(getUnadjustedStartBalance(txnAcct))
                                                        if openBal != 0:
                                                            iBal += 1
                                                            _row = ([None] * GlobalVars.dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                            _row[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                                                            _row[GlobalVars.dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                                            _row[GlobalVars.dataKeys["_DESC"][_COLUMN]] = "MANUAL (UNADJUSTED) OPENING BALANCE"
                                                            _row[GlobalVars.dataKeys["_ACTION"][_COLUMN]] = "OpenBal"
                                                            _row[GlobalVars.dataKeys["_TT"][_COLUMN]] = "MANUAL"
                                                            _row[GlobalVars.dataKeys["_DATE"][_COLUMN]] = txnAcct.getCreationDateInt()
                                                            _row[GlobalVars.dataKeys["_AMOUNT"][_COLUMN]] = openBal
                                                            _row[GlobalVars.dataKeys["_CASHIMPACT"][_COLUMN]] = openBal
                                                            _row[GlobalVars.dataKeys["_ACCTCASHBAL"][_COLUMN]] = acctCurr.getDoubleValue(txnAcct.getBalance())

                                                            myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                            GlobalVars.transactionTable.append(_row)
                                                            del openBal

                                                if (GlobalVars.lIncludeBalanceAdjustments_EIT):
                                                    adjBal = acctCurr.getDoubleValue(getBalanceAdjustment(txnAcct))
                                                    if adjBal != 0:
                                                        iBal += 1
                                                        _row = ([None] * GlobalVars.dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                        _row[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                                                        _row[GlobalVars.dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                                        _row[GlobalVars.dataKeys["_DESC"][_COLUMN]] = "MANUAL BALANCE ADJUSTMENT (MD2023 onwards)"
                                                        _row[GlobalVars.dataKeys["_ACTION"][_COLUMN]] = "BalAdj"
                                                        _row[GlobalVars.dataKeys["_TT"][_COLUMN]] = "MANUAL"
                                                        _row[GlobalVars.dataKeys["_DATE"][_COLUMN]] = DateUtil.getStrippedDateInt()
                                                        _row[GlobalVars.dataKeys["_AMOUNT"][_COLUMN]] = adjBal
                                                        _row[GlobalVars.dataKeys["_CASHIMPACT"][_COLUMN]] = adjBal
                                                        _row[GlobalVars.dataKeys["_ACCTCASHBAL"][_COLUMN]] = acctCurr.getDoubleValue(txnAcct.getBalance())

                                                        myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                        GlobalVars.transactionTable.append(_row)
                                                        del adjBal

                                        if GlobalVars.lFilterDateRange_EIT and (txn.getDateInt() < GlobalVars.startDateInt_EIT or txn.getDateInt() > GlobalVars.endDateInt_EIT):
                                            continue

                                        # Check that we are on a parent. If we are on a split, in an Investment Account, then it must be a cash txfr only
                                        parent = txn.getParentTxn()
                                        if txn == parent:
                                            lParent = True
                                        else:
                                            lParent = False

                                        securityCurr = None
                                        securityTxn = feeTxn = xfrTxn = incTxn = expTxn = None
                                        feeAcct = incAcct = expAcct = xfrAcct = securityAcct = None

                                        cbTags = None
                                        if lParent:
                                            securityTxn = TxnUtil.getSecurityPart(txn)
                                            if securityTxn:
                                                securityAcct = securityTxn.getAccount()
                                                securityCurr = securityAcct.getCurrencyType()  # the Security master record
                                                cbTags = TxnUtil.parseCostBasisTag(securityTxn)

                                            xfrTxn = TxnUtil.getXfrPart(txn)
                                            if xfrTxn: xfrAcct = xfrTxn.getAccount()

                                            feeTxn = TxnUtil.getCommissionPart(txn)
                                            if feeTxn: feeAcct = feeTxn.getAccount()

                                            incTxn = TxnUtil.getIncomePart(txn)
                                            if incTxn: incAcct = incTxn.getAccount()

                                            expTxn = TxnUtil.getExpensePart(txn)
                                            if expTxn:expAcct = expTxn.getAccount()

                                        keyIndex = 0
                                        _row = ([None] * GlobalVars.dataKeys["_END"][0])  # Create a blank row to be populated below...

                                        txnKey = txn.getUUID()
                                        _row[GlobalVars.dataKeys["_KEY"][_COLUMN]] = txnKey + "-" + str(keyIndex).zfill(3)


                                        if lParent and str(txn.getTransferType()).lower() == "xfrtp_bank" and str(txn.getInvestTxnType()).lower() == "bank" \
                                                and not xfrTxn and feeTxn and not securityTxn:
                                            # This seems to be an error! It's an XFR (fixing MD data bug)
                                            xfrTxn = feeTxn
                                            feeTxn = None
                                            xfrAcct = feeAcct
                                            feeAcct = None

                                        _row[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                                        _row[GlobalVars.dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()

                                        _row[GlobalVars.dataKeys["_DATE"][_COLUMN]] = txn.getDateInt()
                                        if txn.getTaxDateInt() != txn.getDateInt():
                                            _row[GlobalVars.dataKeys["_TAXDATE"][_COLUMN]] = txn.getTaxDateInt()

                                        if GlobalVars.lExtractExtraSecurityAcctInfo_EIT:
                                            _row[GlobalVars.dataKeys["_SECINFO_TYPE"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SECINFO_SUBTYPE"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SECINFO_STK_DIV"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SECINFO_CD_APR"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SECINFO_CD_COMPOUNDING"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SECINFO_CD_YEARS"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SECINFO_BOND_TYPE"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SECINFO_BOND_FACEVALUE"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SECINFO_BOND_MATURITYDATE"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SECINFO_BOND_APR"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SECINFO_STKOPT_CALLPUT"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SECINFO_STKOPT_STKPRICE"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SECINFO_STKOPT_EXPRICE"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SECINFO_STKOPT_EXMONTH"][_COLUMN]] = ""

                                        if securityTxn:
                                            _row[GlobalVars.dataKeys["_SECURITY"][_COLUMN]] = safeStr(securityCurr.getName())
                                            _row[GlobalVars.dataKeys["_SECURITYID"][_COLUMN]] = safeStr(securityCurr.getIDString())
                                            _row[GlobalVars.dataKeys["_SECCURR"][_COLUMN]] = safeStr(securityCurr.getRelativeCurrency().getIDString())
                                            _row[GlobalVars.dataKeys["_TICKER"][_COLUMN]] = safeStr(securityCurr.getTickerSymbol())
                                            _row[GlobalVars.dataKeys["_SHARES"][_COLUMN]] = securityCurr.getDoubleValue(securityTxn.getValue())
                                            _row[GlobalVars.dataKeys["_PRICE"][_COLUMN]] = acctCurr.getDoubleValue(securityTxn.getAmount())
                                            _row[GlobalVars.dataKeys["_AVGCOST"][_COLUMN]] = securityAcct.getUsesAverageCost()
                                            _row[GlobalVars.dataKeys["_SECSHRHOLDING"][_COLUMN]] = securityCurr.formatSemiFancy(securityAcct.getBalance(),GlobalVars.decimalCharSep)

                                            if GlobalVars.lExtractExtraSecurityAcctInfo_EIT:
                                                try:
                                                    _row[GlobalVars.dataKeys["_SECINFO_TYPE"][_COLUMN]] = unicode(securityAcct.getSecurityType())
                                                    _row[GlobalVars.dataKeys["_SECINFO_SUBTYPE"][_COLUMN]] = securityAcct.getSecuritySubType()

                                                    if securityAcct.getSecurityType() == SecurityType.STOCK:
                                                        _row[GlobalVars.dataKeys["_SECINFO_STK_DIV"][_COLUMN]] = "" if (securityAcct.getDividend() == 0) else acctCurr.format(securityAcct.getDividend(), GlobalVars.decimalCharSep)

                                                    if securityAcct.getSecurityType() == SecurityType.MUTUAL: pass

                                                    if securityAcct.getSecurityType() == SecurityType.CD:
                                                        _row[GlobalVars.dataKeys["_SECINFO_CD_APR"][_COLUMN]] = "" if (securityAcct.getAPR() == 0.0) else securityAcct.getAPR()
                                                        _row[GlobalVars.dataKeys["_SECINFO_CD_COMPOUNDING"][_COLUMN]] = unicode(securityAcct.getCompounding())

                                                        numYearsChoice = ["0.5"]
                                                        for iYears in range(1, 51): numYearsChoice.append(str(iYears))
                                                        _row[GlobalVars.dataKeys["_SECINFO_CD_YEARS"][_COLUMN]] = numYearsChoice[-1] if (len(numYearsChoice) < securityAcct.getNumYears()) else numYearsChoice[securityAcct.getNumYears()]

                                                    if securityAcct.getSecurityType() == SecurityType.BOND:
                                                        bondTypes = [MD_REF.getUI().getStr("gov_bond"), MD_REF.getUI().getStr("mun_bond"), MD_REF.getUI().getStr("corp_bond"), MD_REF.getUI().getStr("zero_bond")]

                                                        _row[GlobalVars.dataKeys["_SECINFO_BOND_TYPE"][_COLUMN]] = "ERROR" if (securityAcct.getBondType() > len(bondTypes)) else bondTypes[securityAcct.getBondType()]
                                                        _row[GlobalVars.dataKeys["_SECINFO_BOND_FACEVALUE"][_COLUMN]] = "" if (securityAcct.getFaceValue() == 0) else acctCurr.format(securityAcct.getFaceValue(), GlobalVars.decimalCharSep)
                                                        _row[GlobalVars.dataKeys["_SECINFO_BOND_APR"][_COLUMN]] = "" if (securityAcct.getAPR() == 0.0) else securityAcct.getAPR()

                                                        if (securityAcct.getMaturity() != 0 and securityAcct.getMaturity() != 39600000):
                                                            _row[GlobalVars.dataKeys["_SECINFO_BOND_MATURITYDATE"][_COLUMN]] = DateUtil.convertLongDateToInt(securityAcct.getMaturity())

                                                    if securityAcct.getSecurityType() == SecurityType.OPTION:
                                                        _row[GlobalVars.dataKeys["_SECINFO_STKOPT_CALLPUT"][_COLUMN]] = "Put" if securityAcct.getPut() else "Call"
                                                        _row[GlobalVars.dataKeys["_SECINFO_STKOPT_STKPRICE"][_COLUMN]] = "" if (securityAcct.getOptionPrice() == 0.0) else securityAcct.getOptionPrice()
                                                        _row[GlobalVars.dataKeys["_SECINFO_STKOPT_EXPRICE"][_COLUMN]] = "" if (securityAcct.getStrikePrice()) == 0 else acctCurr.format(securityAcct.getStrikePrice(), GlobalVars.decimalCharSep)

                                                        monthOptions = [MD_REF.getUI().getStr("january"), MD_REF.getUI().getStr("february"), MD_REF.getUI().getStr("march"), MD_REF.getUI().getStr("april"), MD_REF.getUI().getStr("may"), MD_REF.getUI().getStr("june"), MD_REF.getUI().getStr("july"), MD_REF.getUI().getStr("august"), MD_REF.getUI().getStr("september"), MD_REF.getUI().getStr("october"), MD_REF.getUI().getStr("november"), MD_REF.getUI().getStr("december")]
                                                        _row[GlobalVars.dataKeys["_SECINFO_STKOPT_EXMONTH"][_COLUMN]] = "ERROR" if (securityAcct.getMonth() > len(monthOptions)) else monthOptions[securityAcct.getMonth()]

                                                    if securityAcct.getSecurityType() == SecurityType.OTHER: pass

                                                except: pass

                                        else:
                                            _row[GlobalVars.dataKeys["_SECURITY"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SECURITYID"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SECCURR"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_TICKER"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SHARES"][_COLUMN]] = 0
                                            _row[GlobalVars.dataKeys["_PRICE"][_COLUMN]] = 0
                                            _row[GlobalVars.dataKeys["_AVGCOST"][_COLUMN]] = ""
                                            _row[GlobalVars.dataKeys["_SECSHRHOLDING"][_COLUMN]] = 0

                                        if GlobalVars.lAdjustForSplits_EIT and securityTxn and _row[GlobalVars.dataKeys["_SHARES"][_COLUMN]] != 0:
                                            # Here we go.....
                                            _row[GlobalVars.dataKeys["_SHRSAFTERSPLIT"][_COLUMN]] = _row[GlobalVars.dataKeys["_SHARES"][_COLUMN]]
                                            stockSplits = securityCurr.getSplits()
                                            if stockSplits and len(stockSplits)>0:
                                                # Here we really go....1

                                                myPrint("D", _THIS_EXTRACT_NAME, securityCurr, " - Found share splits...")
                                                myPrint("D", _THIS_EXTRACT_NAME, securityTxn)

                                                stockSplits = sorted(stockSplits, key=lambda x: x.getDateInt(), reverse=True)   # Sort date newest first...
                                                for theSplit in stockSplits:
                                                    if _row[GlobalVars.dataKeys["_DATE"][_COLUMN]] >= theSplit.getDateInt():
                                                        continue
                                                    myPrint("D", _THIS_EXTRACT_NAME, securityCurr, " -  ShareSplits()... Applying ratio.... *", theSplit.getSplitRatio(), "Shares before:",  _row[GlobalVars.dataKeys["_SHRSAFTERSPLIT"][_COLUMN]])
                                                    # noinspection PyUnresolvedReferences
                                                    _row[GlobalVars.dataKeys["_SHRSAFTERSPLIT"][_COLUMN]] = _row[GlobalVars.dataKeys["_SHRSAFTERSPLIT"][_COLUMN]] * theSplit.getSplitRatio()
                                                    myPrint("D", _THIS_EXTRACT_NAME, securityCurr, " - Shares after:",  _row[GlobalVars.dataKeys["_SHRSAFTERSPLIT"][_COLUMN]])
                                                    # Keep going if more splits....
                                                    continue


                                        _row[GlobalVars.dataKeys["_DESC"][_COLUMN]] = safeStr(txn.getDescription())
                                        _row[GlobalVars.dataKeys["_ACTION"][_COLUMN]] = safeStr(txn.getTransferType())
                                        if lParent:
                                            _row[GlobalVars.dataKeys["_TT"][_COLUMN]] = safeStr(txn.getInvestTxnType())
                                        else:
                                            _row[GlobalVars.dataKeys["_TT"][_COLUMN]] = safeStr(txn.getParentTxn().getInvestTxnType())

                                        _row[GlobalVars.dataKeys["_CLEARED"][_COLUMN]] = getStatusCharRevised(txn)

                                        if lParent:
                                            if xfrTxn:
                                                _row[GlobalVars.dataKeys["_TRANSFER"][_COLUMN]] = xfrAcct.getFullAccountName()
                                        else:
                                            _row[GlobalVars.dataKeys["_TRANSFER"][_COLUMN]] = txn.getParentTxn().getAccount().getFullAccountName()

                                        if lParent:
                                            if securityTxn:
                                                _row[GlobalVars.dataKeys["_AMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(securityTxn.getAmount())
                                            else:
                                                _row[GlobalVars.dataKeys["_AMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue()) * -1
                                        else:
                                            _row[GlobalVars.dataKeys["_AMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())

                                        if xfrTxn:  # Override the value set above. Why? It's the amount TXF'd out of the account....
                                            _row[GlobalVars.dataKeys["_AMOUNT"][_COLUMN]] = (acctCurr.getDoubleValue(xfrTxn.getAmount())) * -1
                                        elif incTxn:
                                            _row[GlobalVars.dataKeys["_AMOUNT"][_COLUMN]] = (acctCurr.getDoubleValue(incTxn.getAmount())) * -1
                                        elif expTxn:
                                            _row[GlobalVars.dataKeys["_AMOUNT"][_COLUMN]] = (acctCurr.getDoubleValue(expTxn.getAmount())) * -1

                                        _row[GlobalVars.dataKeys["_CHEQUE"][_COLUMN]] = safeStr(txn.getCheckNumber())
                                        if lParent:
                                            _row[GlobalVars.dataKeys["_MEMO"][_COLUMN]] = safeStr(txn.getMemo())
                                        else:
                                            _row[GlobalVars.dataKeys["_MEMO"][_COLUMN]] = safeStr(txn.getParentTxn().getMemo())

                                        if expTxn:
                                            _row[GlobalVars.dataKeys["_CAT"][_COLUMN]] = expAcct.getFullAccountName()

                                        if incTxn:
                                            _row[GlobalVars.dataKeys["_CAT"][_COLUMN]] = incAcct.getFullAccountName()

                                        if feeTxn:
                                            _row[GlobalVars.dataKeys["_FEECAT"][_COLUMN]] = feeAcct.getFullAccountName()

                                        if incTxn:
                                            if feeTxn:
                                                _row[GlobalVars.dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                                _row[GlobalVars.dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(incTxn.getAmount()*-1 + feeTxn.getAmount()*-1)

                                                # # Match Moneydance bug - until MD is fixed
                                                # if lParent and str(txn.getTransferType()) == "xfrtp_miscincexp" and str(txn.getInvestTxnType()) == "MISCINC" \
                                                #         and not xfrTxn and feeTxn:
                                                #     row[GlobalVars.dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                                #     row[GlobalVars.dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue() + feeTxn.getAmount()*-1)

                                            else:
                                                _row[GlobalVars.dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(incTxn.getAmount()*-1)

                                        elif expTxn:
                                            if feeTxn:
                                                _row[GlobalVars.dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                                _row[GlobalVars.dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(expTxn.getAmount()*-1 + feeTxn.getAmount())

                                                # Match Moneydance bug - until MD is fixed
                                                if lParent and str(txn.getTransferType()) == "xfrtp_miscincexp" and str(txn.getInvestTxnType()) == "MISCEXP" \
                                                        and not xfrTxn and feeTxn:
                                                    _row[GlobalVars.dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                                    _row[GlobalVars.dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())

                                            else:
                                                _row[GlobalVars.dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(expTxn.getAmount()*-1)
                                        elif securityTxn:
                                            if feeTxn:
                                                _row[GlobalVars.dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                                _row[GlobalVars.dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(securityTxn.getAmount() + feeTxn.getAmount())
                                            else:
                                                _row[GlobalVars.dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(securityTxn.getAmount())
                                        else:
                                            if feeTxn:
                                                _row[GlobalVars.dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                                _row[GlobalVars.dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue() + feeTxn.getAmount())
                                            else:
                                                _row[GlobalVars.dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())

                                        if _row[GlobalVars.dataKeys["_SHARES"][_COLUMN]] != 0:
                                            # roundPrice = securityCurr.getDecimalPlaces()
                                            # noinspection PyUnresolvedReferences
                                            price = ((_row[GlobalVars.dataKeys["_AMOUNT"][_COLUMN]] / (_row[GlobalVars.dataKeys["_SHARES"][_COLUMN]])))
                                            _row[GlobalVars.dataKeys["_PRICE"][_COLUMN]] = price
                                            # price = None

                                            if GlobalVars.lAdjustForSplits_EIT:
                                                # noinspection PyUnresolvedReferences
                                                price = ((_row[GlobalVars.dataKeys["_AMOUNT"][_COLUMN]] / (_row[GlobalVars.dataKeys["_SHRSAFTERSPLIT"][_COLUMN]])))
                                                _row[GlobalVars.dataKeys["_PRICEAFTERSPLIT"][_COLUMN]] = price
                                                # price = None

                                        if lParent and (str(txn.getInvestTxnType()) == "SELL_XFER" or str(txn.getInvestTxnType()) == "BUY_XFER"
                                                        or str(txn.getInvestTxnType()) == "DIVIDEND_REINVEST" or str(txn.getInvestTxnType()) == "DIVIDENDXFR"):
                                            _row[GlobalVars.dataKeys["_CASHIMPACT"][_COLUMN]] = 0.0
                                        elif incTxn or expTxn:
                                            _row[GlobalVars.dataKeys["_CASHIMPACT"][_COLUMN]] = _row[GlobalVars.dataKeys["_TXNNETAMOUNT"][_COLUMN]]
                                        elif securityTxn:
                                            _row[GlobalVars.dataKeys["_CASHIMPACT"][_COLUMN]] = _row[GlobalVars.dataKeys["_TXNNETAMOUNT"][_COLUMN]]*-1
                                        else:
                                            _row[GlobalVars.dataKeys["_CASHIMPACT"][_COLUMN]] = _row[GlobalVars.dataKeys["_TXNNETAMOUNT"][_COLUMN]]

                                        _row[GlobalVars.dataKeys["_HASATTACHMENTS"][_COLUMN]] = txn.hasAttachments()

                                        _row[GlobalVars.dataKeys["_ACCTCASHBAL"][_COLUMN]] = acctCurr.getDoubleValue(txnAcct.getBalance())

                                        # row[GlobalVars.dataKeys["_CURRDPC"][_COLUMN]] = acctCurr.getDecimalPlaces()
                                        # row[GlobalVars.dataKeys["_SECDPC"][_COLUMN]] = securityCurr.getDecimalPlaces()

                                        if securityTxn:
                                            _row[GlobalVars.dataKeys["_AVGCOST"][_COLUMN]] = securityAcct.getUsesAverageCost()

                                        if securityTxn and cbTags:
                                            if not GlobalVars.lOmitLOTDataFromExtract_EIT:
                                                lots = []
                                                for cbKey in cbTags.keys():
                                                    relatedCBTxn = book.getTransactionSet().getTxnByID(cbKey)
                                                    if relatedCBTxn is not None:
                                                        lots.append([cbKey,
                                                                     relatedCBTxn.getTransferType(),
                                                                     relatedCBTxn.getOtherTxn(0).getInvestTxnType(),
                                                                     relatedCBTxn.getDateInt(),
                                                                     acctCurr.formatSemiFancy(relatedCBTxn.getValue(), GlobalVars.decimalCharSep),
                                                                     acctCurr.getDoubleValue(relatedCBTxn.getAmount()),
                                                                     ])
                                                # endfor
                                                if len(lots) > 0:
                                                    _row[GlobalVars.dataKeys["_LOTS"][_COLUMN]] = lots

                                        myPrint("D", _THIS_EXTRACT_NAME, _row)
                                        GlobalVars.transactionTable.append(_row)
                                        iCount += 1

                                    if (GlobalVars.lIncludeOpeningBalances_EIT or GlobalVars.lIncludeBalanceAdjustments_EIT) and len(copyValidAccountList) > 0:
                                        myPrint("DB", _THIS_EXTRACT_NAME + "Now iterating remaining %s Accounts with no txns for opening balances / manual adjustments (MD2023 onwards)...." %(len(copyValidAccountList)))

                                        # Yes I should just move this section from above so the code is not inefficient....
                                        for acctBal in copyValidAccountList:
                                            acctCurr = acctBal.getCurrencyType()  # Currency of the Investment Account
                                            openBal = acctCurr.getDoubleValue(getUnadjustedStartBalance(acctBal))
                                            if (GlobalVars.lIncludeOpeningBalances_EIT):
                                                if openBal != 0:
                                                    iBal+=1
                                                    _row = ([None] * GlobalVars.dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                    _row[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]] = acctBal.getFullAccountName()
                                                    _row[GlobalVars.dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                                    _row[GlobalVars.dataKeys["_DESC"][_COLUMN]] = "MANUAL (UNADJUSTED) OPENING BALANCE"
                                                    _row[GlobalVars.dataKeys["_ACTION"][_COLUMN]] = "OpenBal"
                                                    _row[GlobalVars.dataKeys["_TT"][_COLUMN]] = "MANUAL"
                                                    _row[GlobalVars.dataKeys["_DATE"][_COLUMN]] = acctBal.getCreationDateInt()
                                                    _row[GlobalVars.dataKeys["_AMOUNT"][_COLUMN]] = openBal
                                                    _row[GlobalVars.dataKeys["_CASHIMPACT"][_COLUMN]] = openBal
                                                    _row[GlobalVars.dataKeys["_ACCTCASHBAL"][_COLUMN]] = acctCurr.getDoubleValue(acctBal.getBalance())

                                                    myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                    GlobalVars.transactionTable.append(_row)
                                                    del openBal

                                            if (GlobalVars.lIncludeBalanceAdjustments_EIT):
                                                adjBal = acctCurr.getDoubleValue(getBalanceAdjustment(acctBal))
                                                if adjBal != 0:
                                                    iBal += 1
                                                    _row = ([None] * GlobalVars.dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                    _row[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]] = acctBal.getFullAccountName()
                                                    _row[GlobalVars.dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                                    _row[GlobalVars.dataKeys["_DESC"][_COLUMN]] = "MANUAL BALANCE ADJUSTMENT (MD2023 onwards)"
                                                    _row[GlobalVars.dataKeys["_ACTION"][_COLUMN]] = "BalAdj"
                                                    _row[GlobalVars.dataKeys["_TT"][_COLUMN]] = "MANUAL"
                                                    _row[GlobalVars.dataKeys["_DATE"][_COLUMN]] = DateUtil.getStrippedDateInt()
                                                    _row[GlobalVars.dataKeys["_AMOUNT"][_COLUMN]] = adjBal
                                                    _row[GlobalVars.dataKeys["_CASHIMPACT"][_COLUMN]] = adjBal
                                                    _row[GlobalVars.dataKeys["_ACCTCASHBAL"][_COLUMN]] = acctCurr.getDoubleValue(acctBal.getBalance())

                                                    myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                    GlobalVars.transactionTable.append(_row)
                                                    del adjBal

                                    myPrint("B", _THIS_EXTRACT_NAME + "Investment Transaction Records selected:", len(GlobalVars.transactionTable) )

                                    if iBal: myPrint("B", _THIS_EXTRACT_NAME + "...and %s Manual Opening Balance / Adjustment (MD2023 onwards) entries created too..." %iBal)

                                    ###########################################################################################################


                                    # sort the file: Account>Security>Date
                                    GlobalVars.transactionTable = sorted(GlobalVars.transactionTable, key=lambda x: (x[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]],
                                                                                                   x[GlobalVars.dataKeys["_DATE"][_COLUMN]]))
                                    ###########################################################################################################


                                    def ExtractDataToFile():
                                        myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                        headings = []
                                        sortDataFields = sorted(GlobalVars.dataKeys.items(), key=lambda x: x[1][_COLUMN])
                                        for i in sortDataFields:
                                            if GlobalVars.ENABLE_BESPOKE_CODING:                                        # PATCH: client_mark_extract_data
                                                if i[1][_COLUMN] in GlobalVars.dumpKeys_EIT: continue
                                            headings.append(i[1][_HEADING])
                                        print

                                        myPrint("DB", _THIS_EXTRACT_NAME + "Now pre-processing the file to convert integer dates and strip non-ASCII if requested....")
                                        for _theRow in GlobalVars.transactionTable:
                                            dateasdate = datetime.datetime.strptime(str(_theRow[GlobalVars.dataKeys["_DATE"][_COLUMN]]), "%Y%m%d")  # Convert to Date field
                                            _dateoutput = dateasdate.strftime(GlobalVars.excelExtractDateFormat)
                                            _theRow[GlobalVars.dataKeys["_DATE"][_COLUMN]] = _dateoutput

                                            if _theRow[GlobalVars.dataKeys["_TAXDATE"][_COLUMN]]:
                                                dateasdate = datetime.datetime.strptime(str(_theRow[GlobalVars.dataKeys["_TAXDATE"][_COLUMN]]), "%Y%m%d")  # Convert to Date field
                                                _dateoutput = dateasdate.strftime(GlobalVars.excelExtractDateFormat)
                                                _theRow[GlobalVars.dataKeys["_TAXDATE"][_COLUMN]] = _dateoutput

                                            for col in range(0, GlobalVars.dataKeys["_SECSHRHOLDING"][_COLUMN]):
                                                _theRow[col] = fixFormatsStr(_theRow[col])

                                        myPrint("B", _THIS_EXTRACT_NAME + "Opening file and writing %s records" %(len(GlobalVars.transactionTable)))


                                        try:
                                            # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                                            with open(GlobalVars.csvfilename, "wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; juse "w" and newline='' in PY3.0

                                                if GlobalVars.lWriteBOMToExtractFile:
                                                    csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                                                writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(GlobalVars.csvDelimiter))

                                                if GlobalVars.csvDelimiter != ",":
                                                    writer.writerow(["sep=", ""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                                                iFindEndHeadingCol = headings.index(GlobalVars.dataKeys["_KEY"][_HEADING])
                                                writer.writerow(headings[:iFindEndHeadingCol])  # Write the header, but not the extra _field headings

                                                try:
                                                    for i in range(0, len(GlobalVars.transactionTable)):
                                                        if GlobalVars.ENABLE_BESPOKE_CODING:                            # PATCH: client_mark_extract_data
                                                            tmpRow = []
                                                            for tmpCol in range(0, GlobalVars.dataKeys["_ATTACHMENTLINKREL"][_COLUMN]):
                                                                if tmpCol in GlobalVars.dumpKeys_EIT: continue
                                                                tmpRow.append(GlobalVars.transactionTable[i][tmpCol])
                                                            writer.writerow(tmpRow)
                                                            del tmpRow, tmpCol
                                                        else:
                                                            writer.writerow(GlobalVars.transactionTable[i][:GlobalVars.dataKeys["_ATTACHMENTLINKREL"][_COLUMN]])
                                                except:
                                                    _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR writing to CSV on row %s. Please review console" %(i)
                                                    GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                    myPrint("B", _msgTxt)
                                                    myPrint("B", _THIS_EXTRACT_NAME, GlobalVars.transactionTable[i])
                                                    raise

                                            _msgTxt = _THIS_EXTRACT_NAME + "CSV file: '%s' created (%s records)" %(GlobalVars.csvfilename, len(GlobalVars.transactionTable))
                                            myPrint("B", _msgTxt)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            GlobalVars.countFilesCreated += 1

                                        except:
                                            e_type, exc_value, exc_traceback = sys.exc_info()                           # noqa
                                            _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR '%s' detected writing file: '%s' - Extract ABORTED!" %(exc_value, GlobalVars.csvfilename)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            myPrint("B", _msgTxt)
                                            raise

                                    def fixFormatsStr(theString, lNumber=False, sFormat=""):
                                        if isinstance(theString, bool): return theString
                                        if isinstance(theString, tuple): return theString
                                        if isinstance(theString, dict): return theString
                                        if isinstance(theString, list): return theString

                                        if isinstance(theString, int) or isinstance(theString, float) or isinstance(theString, long):
                                            lNumber = True

                                        if lNumber is None: lNumber = False
                                        if theString is None: theString = ""

                                        if sFormat == "%" and theString != "":
                                            theString = "{:.1%}".format(theString)
                                            return theString

                                        if lNumber: return str(theString)

                                        theString = theString.strip()  # remove leading and trailing spaces

                                        theString = theString.replace("\n", "*")  # remove newlines within fields to keep csv format happy
                                        theString = theString.replace("\t", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace(";", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace(",", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace("|", "*")  # remove tabs within fields to keep csv format happy

                                        if GlobalVars.lStripASCII:
                                            all_ASCII = ''.join(char for char in theString if ord(char) < 128)  # Eliminate non ASCII printable Chars too....
                                        else:
                                            all_ASCII = theString
                                        return all_ASCII

                                    if len(GlobalVars.transactionTable) > 0:

                                        ExtractDataToFile()

                                        if not GlobalVars.lGlobalErrorDetected:
                                            sTxt = "Extract file CREATED:"
                                            mTxt = ("With %s rows\n" %(len(GlobalVars.transactionTable)))
                                            myPrint("B", _THIS_EXTRACT_NAME + "%s\n%s" %(sTxt, mTxt))
                                        else:
                                            _msgTextx = _THIS_EXTRACT_NAME + "ERROR Creating extract (review console for error messages)...."
                                            GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                    else:
                                        _msgTextx = _THIS_EXTRACT_NAME + "@@ No records selected and no extract file created @@"
                                        GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                        myPrint("B", _msgTextx)
                                        if not GlobalVars.AUTO_EXTRACT_MODE:
                                            DoExtractsSwingWorker.killPleaseWait()
                                            genericSwingEDTRunner(True, True, myPopupInformationBox, client_mark_extract_data_frame_, _msgTextx, GlobalVars.thisScriptName, JOptionPane.WARNING_MESSAGE)

                                    # delete references to large objects
                                    GlobalVars.transactionTable = None
                                    del accountBalances


                                try:
                                    do_extract_investment_transactions()
                                except:
                                    GlobalVars.lGlobalErrorDetected = True

                                if GlobalVars.lGlobalErrorDetected:
                                    GlobalVars.countErrorsDuringExtract += 1
                                    _txt = _THIS_EXTRACT_NAME + "@@ ERROR: do_extract_investment_transactions() has failed (review console)!"
                                    GlobalVars.AUTO_MESSAGES.append(_txt)
                                    myPrint("B", _txt)
                                    dump_sys_error_to_md_console_and_errorlog()
                                    if not GlobalVars.AUTO_EXTRACT_MODE:
                                        DoExtractsSwingWorker.killPleaseWait()
                                        genericSwingEDTRunner(True, True, myPopupInformationBox, client_mark_extract_data_frame_, _txt, "ERROR", JOptionPane.ERROR_MESSAGE)
                                        return False
                            #### ENDIF lExtractInvestmentTxns ####

                            if lExtractSecurityBalances:
                                # ####################################################
                                # EXTRACT_SECURITY_BALANCES_CSV EXECUTION
                                # ####################################################

                                _THIS_EXTRACT_NAME = pad("EXTRACT: Security Balances:", 34)
                                GlobalVars.lGlobalErrorDetected = False

                                if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                    self.super__publish([_THIS_EXTRACT_NAME.strip()])                                   # noqa

                                GlobalVars.csvfilename = getExtractFullPath("ESB")

                                def do_extract_security_balances():
                                    # noinspection PyArgumentList
                                    class MyAcctFilterESB(AcctFilter):

                                        def __init__(self,
                                                     _hideInactiveAccounts=True,
                                                     _lAllAccounts=True,
                                                     _filterForAccounts="ALL",
                                                     _hideHiddenAccounts=True,
                                                     _hideHiddenSecurities=True,
                                                     _lAllCurrency=True,
                                                     _filterForCurrency="ALL",
                                                     _lAllSecurity=True,
                                                     _filterForSecurity="ALL",
                                                     _findUUID=None):

                                            self._hideInactiveAccounts = _hideInactiveAccounts
                                            self._lAllAccounts = _lAllAccounts
                                            self._filterForAccounts = _filterForAccounts
                                            self._hideHiddenAccounts = _hideHiddenAccounts
                                            self._hideHiddenSecurities = _hideHiddenSecurities
                                            self._lAllCurrency = _lAllCurrency
                                            self._filterForCurrency = _filterForCurrency
                                            self._lAllSecurity = _lAllSecurity
                                            self._filterForSecurity = _filterForSecurity
                                            self._findUUID = _findUUID

                                        def matches(self, acct):
                                            if self._findUUID is not None:  # If UUID supplied, override all other parameters...
                                                if acct.getUUID() == self._findUUID: return True
                                                else: return False

                                            if acct.getAccountType() is not Account.AccountType.SECURITY:               # noqa
                                                return False

                                            if self._hideInactiveAccounts:
                                                # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
                                                if (acct.getAccountOrParentIsInactive()): return False
                                                if (acct.getHideOnHomePage() and acct.getBalance() == 0): return False

                                            theAcct = acct.getParentAccount()

                                            if (self._lAllAccounts
                                                    or (self._filterForAccounts.upper().strip() in theAcct.getFullAccountName().upper().strip())):
                                                pass
                                            else: return False

                                            if ((not self._hideHiddenAccounts)
                                                    or (self._hideHiddenAccounts and not theAcct.getHideOnHomePage())):
                                                pass
                                            else: return False

                                            curr = acct.getCurrencyType()
                                            currID = curr.getIDString()
                                            currName = curr.getName()

                                            # noinspection PyUnresolvedReferences
                                            if acct.getAccountType() == Account.AccountType.SECURITY:  # on Security Accounts, get the Currency from the Security master - else from the account)
                                                if self._lAllSecurity:
                                                    pass
                                                elif (self._filterForSecurity.upper().strip() in curr.getTickerSymbol().upper().strip()):
                                                    pass
                                                elif (self._filterForSecurity.upper().strip() in curr.getName().upper().strip()):
                                                    pass
                                                else: return False

                                                if ((self._hideHiddenSecurities and not curr.getHideInUI()) or (not self._hideHiddenSecurities)):
                                                    pass
                                                else:
                                                    return False

                                                currID = curr.getRelativeCurrency().getIDString()
                                                currName = curr.getRelativeCurrency().getName()

                                            else:
                                                pass

                                            # All accounts and security records can have currencies
                                            if self._lAllCurrency:
                                                pass
                                            elif (self._filterForCurrency.upper().strip() in currID.upper().strip()):
                                                pass
                                            elif (self._filterForCurrency.upper().strip() in currName.upper().strip()):
                                                pass

                                            else: return False

                                            return True


                                    # Override date to today if settings require this...
                                    if GlobalVars.saved_autoSelectCurrentAsOfDate_ESB:
                                        GlobalVars.saved_securityBalancesDate_ESB = DateUtil.getStrippedDateInt()

                                    _COLUMN = 0
                                    _HEADING = 1

                                    usedSecurityMasters = {}

                                    dki = 0
                                    GlobalVars.dataKeys = {}                                                            # noqa
                                    GlobalVars.dataKeys["_ACCOUNT"]                   = [dki, "Account"];                      dki += 1
                                    GlobalVars.dataKeys["_ACCTCURR"]                  = [dki, "AcctCurrency"];                 dki += 1
                                    GlobalVars.dataKeys["_BASECURR"]                  = [dki, "BaseCurrency"];                 dki += 1
                                    GlobalVars.dataKeys["_SECURITY"]                  = [dki, "Security"];                     dki += 1
                                    GlobalVars.dataKeys["_SECURITYID"]                = [dki, "SecurityID"];                   dki += 1
                                    GlobalVars.dataKeys["_TICKER"]                    = [dki, "SecurityTicker"];               dki += 1
                                    GlobalVars.dataKeys["_SECMSTRUUID"]               = [dki, "SecurityMasterUUID"];           dki += 1
                                    GlobalVars.dataKeys["_AVGCOST"]                   = [dki, "AverageCostControl"];           dki += 1

                                    GlobalVars.dataKeys["_SECINFO_TYPE"]              = [dki, "Sec_Type"];                     dki += 1
                                    GlobalVars.dataKeys["_SECINFO_SUBTYPE"]           = [dki, "Sec_SubType"];                  dki += 1
                                    GlobalVars.dataKeys["_SECINFO_STK_DIV"]           = [dki, "Sec_Stock_Div"];                dki += 1
                                    GlobalVars.dataKeys["_SECINFO_CD_APR"]            = [dki, "Sec_CD_APR"];                   dki += 1
                                    GlobalVars.dataKeys["_SECINFO_CD_COMPOUNDING"]    = [dki, "Sec_CD_Compounding"];           dki += 1
                                    GlobalVars.dataKeys["_SECINFO_CD_YEARS"]          = [dki, "Sec_CD_Years"];                 dki += 1
                                    GlobalVars.dataKeys["_SECINFO_BOND_TYPE"]         = [dki, "Sec_Bond_Type"];                dki += 1
                                    GlobalVars.dataKeys["_SECINFO_BOND_FACEVALUE"]    = [dki, "Sec_Bond_FaceValue"];           dki += 1
                                    GlobalVars.dataKeys["_SECINFO_BOND_MATURITYDATE"] = [dki, "Sec_Bond_MaturityDate"];        dki += 1
                                    GlobalVars.dataKeys["_SECINFO_BOND_APR"]          = [dki, "Sec_Bond_APR"];                 dki += 1
                                    GlobalVars.dataKeys["_SECINFO_STKOPT_CALLPUT"]    = [dki, "Sec_StockOpt_CallPut"];         dki += 1
                                    GlobalVars.dataKeys["_SECINFO_STKOPT_STKPRICE"]   = [dki, "Sec_StockOpt_StockPrice"];      dki += 1
                                    GlobalVars.dataKeys["_SECINFO_STKOPT_EXPRICE"]    = [dki, "Sec_StockOpt_ExercisePrice"];   dki += 1
                                    GlobalVars.dataKeys["_SECINFO_STKOPT_EXMONTH"]    = [dki, "Sec_StockOpt_ExerciseMonth"];   dki += 1

                                    GlobalVars.dataKeys["_SECSHRHOLDING"]             = [dki, "SecurityShareHolding"];         dki += 1
                                    GlobalVars.dataKeys["_ACCTCOSTBASIS"]             = [dki, "AcctCostBasis"];                dki += 1
                                    GlobalVars.dataKeys["_BASECOSTBASIS"]             = [dki, "BaseCostBasis"];                dki += 1
                                    GlobalVars.dataKeys["_CURRENTPRICE"]              = [dki, "CurrentPrice"];                 dki += 1
                                    GlobalVars.dataKeys["_SECRELCURR"]                = [dki, "SecurityRelCurrency"];          dki += 1
                                    GlobalVars.dataKeys["_CURRENTPRICETOBASE"]        = [dki, "CurrentPriceToBase"];           dki += 1
                                    GlobalVars.dataKeys["_CURRENTPRICEINVESTCURR"]    = [dki, "CurrentPriceInvestCurr"];       dki += 1

                                    GlobalVars.dataKeys["_CURRENTVALUETOBASE"]        = [dki, "CurrentValueToBase"];           dki += 1
                                    GlobalVars.dataKeys["_CURRENTVALUEINVESTCURR"]    = [dki, "CurrentValueInvestCurr"];       dki += 1

                                    GlobalVars.dataKeys["_KEY"]                       = [dki, "Key"];                          dki += 1
                                    GlobalVars.dataKeys["_END"]                       = [dki, "_END"];                         dki += 1

                                    GlobalVars.keepKeys_ESB = []
                                    if GlobalVars.ENABLE_BESPOKE_CODING:                                                # PATCH: client_mark_extract_data
                                        GlobalVars.keepKeys_ESB.append(GlobalVars.dataKeys["_ACCOUNT"][_COLUMN])
                                        GlobalVars.keepKeys_ESB.append(GlobalVars.dataKeys["_SECURITY"][_COLUMN])
                                        GlobalVars.keepKeys_ESB.append(GlobalVars.dataKeys["_TICKER"][_COLUMN])
                                        GlobalVars.keepKeys_ESB.append(GlobalVars.dataKeys["_SECSHRHOLDING"][_COLUMN])
                                        GlobalVars.keepKeys_ESB.append(GlobalVars.dataKeys["_CURRENTPRICEINVESTCURR"][_COLUMN])
                                        GlobalVars.keepKeys_ESB.append(GlobalVars.dataKeys["_CURRENTVALUEINVESTCURR"][_COLUMN])

                                    GlobalVars.transactionTable = []

                                    myPrint("DB", _THIS_EXTRACT_NAME, GlobalVars.dataKeys)

                                    book = MD_REF.getCurrentAccountBook()

                                    usedInvestmentCashAccts = []

                                    for sAcct in AccountUtil.allMatchesForSearch(book, MyAcctFilterESB(GlobalVars.hideInactiveAccounts_ESB,
                                                                                                       GlobalVars.lAllAccounts_ESB,
                                                                                                       GlobalVars.filterForAccounts_ESB,
                                                                                                       GlobalVars.hideHiddenAccounts_ESB,
                                                                                                       GlobalVars.hideHiddenSecurities_ESB,
                                                                                                       GlobalVars.lAllCurrency_ESB,
                                                                                                       GlobalVars.filterForCurrency_ESB,
                                                                                                       GlobalVars.lAllSecurity_ESB,
                                                                                                       GlobalVars.filterForSecurity_ESB,
                                                                                                       None)):

                                        if sAcct.getAccountType() is not Account.AccountType.SECURITY: raise Exception("LOGIC ERROR")   # noqa

                                        investAcct = sAcct.getParentAccount()
                                        investAcctCurr = investAcct.getCurrencyType()

                                        securityAcct = sAcct
                                        securityCurr = securityAcct.getCurrencyType()  # the Security master record
                                        del sAcct

                                        _row = ([None] * GlobalVars.dataKeys["_END"][0])  # Create a blank row to be populated below...

                                        usedSecurityMasters[securityCurr] = True

                                        # NOTE: When using the new bespoke asof date option, cost basis cannot be retrieved by date...

                                        _row[GlobalVars.dataKeys["_KEY"][_COLUMN]] = ""

                                        _row[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]] = investAcct.getFullAccountName()
                                        _row[GlobalVars.dataKeys["_ACCTCURR"][_COLUMN]] = investAcctCurr.getIDString()
                                        _row[GlobalVars.dataKeys["_BASECURR"][_COLUMN]] = GlobalVars.baseCurrency.getIDString()

                                        if GlobalVars.ENABLE_BESPOKE_CODING:
                                            _row[GlobalVars.dataKeys["_ACCTCOSTBASIS"][_COLUMN]] = 0.0
                                            _row[GlobalVars.dataKeys["_BASECOSTBASIS"][_COLUMN]] = 0.0
                                        else:
                                            costBasis = InvestUtil.getCostBasis(securityAcct)
                                            costBasisBase = CurrencyUtil.convertValue(costBasis, investAcctCurr, GlobalVars.baseCurrency)
                                            _row[GlobalVars.dataKeys["_ACCTCOSTBASIS"][_COLUMN]] = investAcctCurr.getDoubleValue(costBasis)
                                            _row[GlobalVars.dataKeys["_BASECOSTBASIS"][_COLUMN]] = GlobalVars.baseCurrency.getDoubleValue(costBasisBase)

                                        _row[GlobalVars.dataKeys["_SECURITY"][_COLUMN]] = unicode(securityCurr.getName())
                                        _row[GlobalVars.dataKeys["_SECURITYID"][_COLUMN]] = unicode(securityCurr.getIDString())
                                        _row[GlobalVars.dataKeys["_SECMSTRUUID"][_COLUMN]] = securityCurr.getUUID()
                                        _row[GlobalVars.dataKeys["_TICKER"][_COLUMN]] = unicode(securityCurr.getTickerSymbol())
                                        _row[GlobalVars.dataKeys["_AVGCOST"][_COLUMN]] = securityAcct.getUsesAverageCost()

                                        secShrHoldingLong = None
                                        if GlobalVars.ENABLE_BESPOKE_CODING:
                                            secShrHoldingLong = AccountUtil.getBalanceAsOfDate(book, securityAcct, GlobalVars.saved_securityBalancesDate_ESB, True)
                                            secShrHolding = securityCurr.getDoubleValue(secShrHoldingLong)
                                        else:
                                            secShrHolding = securityCurr.getDoubleValue(securityAcct.getBalance())
                                        _row[GlobalVars.dataKeys["_SECSHRHOLDING"][_COLUMN]] = secShrHolding

                                        _row[GlobalVars.dataKeys["_SECRELCURR"][_COLUMN]] = unicode(securityCurr.getRelativeCurrency().getIDString())

                                        if GlobalVars.ENABLE_BESPOKE_CODING:
                                            secBalInvestCurrLong = CurrencyUtil.convertValue(secShrHoldingLong, securityCurr, investAcctCurr, GlobalVars.saved_securityBalancesDate_ESB)
                                            secBalInvestCurrDbl = investAcctCurr.getDoubleValue(secBalInvestCurrLong)
                                            secBalBaseCurrLong = CurrencyUtil.convertValue(secShrHoldingLong, securityCurr, GlobalVars.baseCurrency, GlobalVars.saved_securityBalancesDate_ESB)
                                            secBalBaseCurrDbl = GlobalVars.baseCurrency.getDoubleValue(secBalBaseCurrLong)

                                            cPriceToBase = 0.0 if secShrHolding == 0.0 else (secBalBaseCurrDbl / secShrHolding)
                                            cPriceInvestCurr = 0.0 if secShrHolding == 0.0 else (secBalInvestCurrDbl / secShrHolding)

                                            _row[GlobalVars.dataKeys["_CURRENTPRICE"][_COLUMN]] = (1.0 / securityCurr.getRelativeRate(GlobalVars.saved_securityBalancesDate_ESB))
                                            _row[GlobalVars.dataKeys["_CURRENTPRICETOBASE"][_COLUMN]] = round(cPriceToBase, 2)
                                            _row[GlobalVars.dataKeys["_CURRENTPRICEINVESTCURR"][_COLUMN]] = round(cPriceInvestCurr, 2)
                                            _row[GlobalVars.dataKeys["_CURRENTVALUETOBASE"][_COLUMN]] = secBalBaseCurrDbl
                                            _row[GlobalVars.dataKeys["_CURRENTVALUEINVESTCURR"][_COLUMN]] = secBalInvestCurrDbl

                                        else:

                                            cPriceToBase = (1.0 / securityCurr.getBaseRate())                           # same as .getRate(None)
                                            cPriceInvestCurr = (1.0 / securityCurr.getRate(investAcctCurr))

                                            _row[GlobalVars.dataKeys["_CURRENTPRICE"][_COLUMN]] = (1.0 / securityCurr.getRelativeRate())
                                            _row[GlobalVars.dataKeys["_CURRENTPRICETOBASE"][_COLUMN]] = cPriceToBase
                                            _row[GlobalVars.dataKeys["_CURRENTPRICEINVESTCURR"][_COLUMN]] = cPriceInvestCurr
                                            _row[GlobalVars.dataKeys["_CURRENTVALUETOBASE"][_COLUMN]] = cPriceToBase * secShrHolding
                                            _row[GlobalVars.dataKeys["_CURRENTVALUEINVESTCURR"][_COLUMN]] = cPriceInvestCurr * secShrHolding

                                        _row[GlobalVars.dataKeys["_SECINFO_TYPE"][_COLUMN]] = ""
                                        _row[GlobalVars.dataKeys["_SECINFO_SUBTYPE"][_COLUMN]] = ""
                                        _row[GlobalVars.dataKeys["_SECINFO_STK_DIV"][_COLUMN]] = ""
                                        _row[GlobalVars.dataKeys["_SECINFO_CD_APR"][_COLUMN]] = ""
                                        _row[GlobalVars.dataKeys["_SECINFO_CD_COMPOUNDING"][_COLUMN]] = ""
                                        _row[GlobalVars.dataKeys["_SECINFO_CD_YEARS"][_COLUMN]] = ""
                                        _row[GlobalVars.dataKeys["_SECINFO_BOND_TYPE"][_COLUMN]] = ""
                                        _row[GlobalVars.dataKeys["_SECINFO_BOND_FACEVALUE"][_COLUMN]] = ""
                                        _row[GlobalVars.dataKeys["_SECINFO_BOND_MATURITYDATE"][_COLUMN]] = ""
                                        _row[GlobalVars.dataKeys["_SECINFO_BOND_APR"][_COLUMN]] = ""
                                        _row[GlobalVars.dataKeys["_SECINFO_STKOPT_CALLPUT"][_COLUMN]] = ""
                                        _row[GlobalVars.dataKeys["_SECINFO_STKOPT_STKPRICE"][_COLUMN]] = ""
                                        _row[GlobalVars.dataKeys["_SECINFO_STKOPT_EXPRICE"][_COLUMN]] = ""
                                        _row[GlobalVars.dataKeys["_SECINFO_STKOPT_EXMONTH"][_COLUMN]] = ""

                                        _row[GlobalVars.dataKeys["_SECINFO_TYPE"][_COLUMN]] = unicode(securityAcct.getSecurityType())
                                        _row[GlobalVars.dataKeys["_SECINFO_SUBTYPE"][_COLUMN]] = securityAcct.getSecuritySubType()

                                        if securityAcct.getSecurityType() == SecurityType.STOCK:
                                            _row[GlobalVars.dataKeys["_SECINFO_STK_DIV"][_COLUMN]] = "" if (securityAcct.getDividend() == 0) else investAcctCurr.format(securityAcct.getDividend(), GlobalVars.decimalCharSep)

                                        if securityAcct.getSecurityType() == SecurityType.MUTUAL: pass

                                        if securityAcct.getSecurityType() == SecurityType.CD:
                                            _row[GlobalVars.dataKeys["_SECINFO_CD_APR"][_COLUMN]] = "" if (securityAcct.getAPR() == 0.0) else securityAcct.getAPR()
                                            _row[GlobalVars.dataKeys["_SECINFO_CD_COMPOUNDING"][_COLUMN]] = unicode(securityAcct.getCompounding())

                                            numYearsChoice = ["0.5"]
                                            for iYears in range(1, 51): numYearsChoice.append(str(iYears))
                                            _row[GlobalVars.dataKeys["_SECINFO_CD_YEARS"][_COLUMN]] = numYearsChoice[-1] if (len(numYearsChoice) < securityAcct.getNumYears()) else numYearsChoice[securityAcct.getNumYears()]

                                        if securityAcct.getSecurityType() == SecurityType.BOND:
                                            bondTypes = [MD_REF.getUI().getStr("gov_bond"), MD_REF.getUI().getStr("mun_bond"), MD_REF.getUI().getStr("corp_bond"), MD_REF.getUI().getStr("zero_bond")]

                                            _row[GlobalVars.dataKeys["_SECINFO_BOND_TYPE"][_COLUMN]] = "ERROR" if (securityAcct.getBondType() > len(bondTypes)) else bondTypes[securityAcct.getBondType()]
                                            _row[GlobalVars.dataKeys["_SECINFO_BOND_FACEVALUE"][_COLUMN]] = "" if (securityAcct.getFaceValue() == 0) else investAcctCurr.format(securityAcct.getFaceValue(), GlobalVars.decimalCharSep)
                                            _row[GlobalVars.dataKeys["_SECINFO_BOND_APR"][_COLUMN]] = "" if (securityAcct.getAPR() == 0.0) else securityAcct.getAPR()

                                            if (securityAcct.getMaturity() != 0 and securityAcct.getMaturity() != 39600000):
                                                _row[GlobalVars.dataKeys["_SECINFO_BOND_MATURITYDATE"][_COLUMN]] = DateUtil.convertLongDateToInt(securityAcct.getMaturity())

                                        if securityAcct.getSecurityType() == SecurityType.OPTION:
                                            _row[GlobalVars.dataKeys["_SECINFO_STKOPT_CALLPUT"][_COLUMN]] = "Put" if securityAcct.getPut() else "Call"
                                            _row[GlobalVars.dataKeys["_SECINFO_STKOPT_STKPRICE"][_COLUMN]] = "" if (securityAcct.getOptionPrice() == 0.0) else securityAcct.getOptionPrice()
                                            _row[GlobalVars.dataKeys["_SECINFO_STKOPT_EXPRICE"][_COLUMN]] = "" if (securityAcct.getStrikePrice()) == 0 else investAcctCurr.format(securityAcct.getStrikePrice(), GlobalVars.decimalCharSep)

                                            monthOptions = [MD_REF.getUI().getStr("january"), MD_REF.getUI().getStr("february"), MD_REF.getUI().getStr("march"), MD_REF.getUI().getStr("april"), MD_REF.getUI().getStr("may"), MD_REF.getUI().getStr("june"), MD_REF.getUI().getStr("july"), MD_REF.getUI().getStr("august"), MD_REF.getUI().getStr("september"), MD_REF.getUI().getStr("october"), MD_REF.getUI().getStr("november"), MD_REF.getUI().getStr("december")]
                                            _row[GlobalVars.dataKeys["_SECINFO_STKOPT_EXMONTH"][_COLUMN]] = "ERROR" if (securityAcct.getMonth() > len(monthOptions)) else monthOptions[securityAcct.getMonth()]

                                        if securityAcct.getSecurityType() == SecurityType.OTHER: pass

                                        myPrint("D", _THIS_EXTRACT_NAME, _row)
                                        GlobalVars.transactionTable.append(_row)

                                    if GlobalVars.ENABLE_BESPOKE_CODING:                                                # PATCH: client_mark_extract_data
                                        # get the cash balance...
                                        allInvestAccounts = [_acct for _acct in AccountUtil.allMatchesForSearch(book, AcctFilter.ALL_ACCOUNTS_FILTER)
                                                             if _acct.getAccountType() == Account.AccountType.INVESTMENT]   # noqa
                                        for investAcct in allInvestAccounts:
                                            if investAcct not in usedInvestmentCashAccts:
                                                investAcctCurr = investAcct.getCurrencyType()
                                                usedInvestmentCashAccts.append(investAcct)
                                                cashBalCurrLong = AccountUtil.getBalanceAsOfDate(book, investAcct, GlobalVars.saved_securityBalancesDate_ESB, True)
                                                cashBalBaseLong = CurrencyUtil.convertValue(cashBalCurrLong, investAcctCurr, GlobalVars.baseCurrency, GlobalVars.saved_securityBalancesDate_ESB)
                                                cashBalBaseDbl = GlobalVars.baseCurrency.getDoubleValue(cashBalBaseLong)

                                                if cashBalBaseDbl != 0.0:
                                                    _row = ([None] * GlobalVars.dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                    _row[GlobalVars.dataKeys["_KEY"][_COLUMN]] = ""
                                                    _row[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]] = investAcct.getFullAccountName()
                                                    _row[GlobalVars.dataKeys["_BASECURR"][_COLUMN]] = GlobalVars.baseCurrency.getIDString()

                                                    _row[GlobalVars.dataKeys["_SECURITY"][_COLUMN]] = "Cash Balance"
                                                    _row[GlobalVars.dataKeys["_SECURITYID"][_COLUMN]] = "CASH"
                                                    _row[GlobalVars.dataKeys["_SECRELCURR"][_COLUMN]] = GlobalVars.baseCurrency.getIDString()
                                                    _row[GlobalVars.dataKeys["_SECMSTRUUID"][_COLUMN]] = ""
                                                    _row[GlobalVars.dataKeys["_TICKER"][_COLUMN]] = "__CASH BALANCE__"
                                                    _row[GlobalVars.dataKeys["_SECSHRHOLDING"][_COLUMN]] = 0.0
                                                    _row[GlobalVars.dataKeys["_CURRENTPRICE"][_COLUMN]] = 1.0
                                                    _row[GlobalVars.dataKeys["_CURRENTVALUEINVESTCURR"][_COLUMN]] = cashBalBaseDbl

                                                    myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                    GlobalVars.transactionTable.append(_row)
                                    else:
                                        # noinspection PyUnresolvedReferences
                                        unusedSecurityMasters = [secCurr for secCurr in MD_REF.getCurrentAccountBook().getCurrencies().getAllCurrencies()
                                                                 if (secCurr.getCurrencyType() is CurrencyType.Type.SECURITY and secCurr not in usedSecurityMasters)]

                                        if len(unusedSecurityMasters) > 0:
                                            myPrint("B", _THIS_EXTRACT_NAME + "Adding %s unused security master records...." %(len(unusedSecurityMasters)))
                                            for secCurr in unusedSecurityMasters:

                                                _row = ([None] * GlobalVars.dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                _row[GlobalVars.dataKeys["_KEY"][_COLUMN]] = ""
                                                _row[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]] = "__SecurityMaster__"
                                                _row[GlobalVars.dataKeys["_BASECURR"][_COLUMN]] = GlobalVars.baseCurrency.getIDString()

                                                _row[GlobalVars.dataKeys["_SECURITY"][_COLUMN]] = unicode(secCurr.getName())
                                                _row[GlobalVars.dataKeys["_SECURITYID"][_COLUMN]] = unicode(secCurr.getIDString())
                                                _row[GlobalVars.dataKeys["_SECRELCURR"][_COLUMN]] = unicode(secCurr.getRelativeCurrency().getIDString())
                                                _row[GlobalVars.dataKeys["_SECMSTRUUID"][_COLUMN]] = secCurr.getUUID()
                                                _row[GlobalVars.dataKeys["_TICKER"][_COLUMN]] = unicode(secCurr.getTickerSymbol())
                                                _row[GlobalVars.dataKeys["_SECSHRHOLDING"][_COLUMN]] = 0.0
                                                _row[GlobalVars.dataKeys["_CURRENTPRICE"][_COLUMN]] = (1.0 / secCurr.getRelativeRate())
                                                _row[GlobalVars.dataKeys["_CURRENTPRICETOBASE"][_COLUMN]] = (1.0 / secCurr.getBaseRate())          # same as .getRate(None)

                                                myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                GlobalVars.transactionTable.append(_row)

                                    myPrint("B", _THIS_EXTRACT_NAME + "Security Balance(s) Records selected:", len(GlobalVars.transactionTable))
                                    ###########################################################################################################

                                    GlobalVars.transactionTable = sorted(GlobalVars.transactionTable, key=lambda x: (x[GlobalVars.dataKeys["_SECURITY"][_COLUMN]].lower(),
                                                                                               x[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]].lower()))

                                    ###########################################################################################################


                                    def ExtractDataToFile():
                                        myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                        headings = []
                                        sortDataFields = sorted(GlobalVars.dataKeys.items(), key=lambda x: x[1][_COLUMN])
                                        for i in sortDataFields:
                                            if GlobalVars.ENABLE_BESPOKE_CODING:                                        # PATCH: client_mark_extract_data
                                                if i[1][_COLUMN] not in GlobalVars.keepKeys_ESB: continue
                                            headings.append(i[1][_HEADING])
                                        print

                                        myPrint("DB", _THIS_EXTRACT_NAME + "Now pre-processing the file to convert integer dates and strip non-ASCII if requested....")
                                        for _theRow in GlobalVars.transactionTable:

                                            mDate = _theRow[GlobalVars.dataKeys["_SECINFO_BOND_MATURITYDATE"][_COLUMN]]
                                            if mDate is not None and mDate != "":
                                                dateasdate = datetime.datetime.strptime(str(mDate), "%Y%m%d")           # Convert to Date field
                                                _dateoutput = dateasdate.strftime(GlobalVars.excelExtractDateFormat)
                                                _theRow[GlobalVars.dataKeys["_SECINFO_BOND_MATURITYDATE"][_COLUMN]] = _dateoutput

                                            for col in range(0, GlobalVars.dataKeys["_SECINFO_STK_DIV"][_COLUMN]):
                                                _theRow[col] = fixFormatsStr(_theRow[col])

                                        myPrint("B", _THIS_EXTRACT_NAME + "Opening file and writing %s records" %(len(GlobalVars.transactionTable)))

                                        try:
                                            # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                                            with open(GlobalVars.csvfilename, "wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; juse "w" and newline='' in PY3.0

                                                if GlobalVars.lWriteBOMToExtractFile:
                                                    csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                                                writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(GlobalVars.csvDelimiter))

                                                if GlobalVars.csvDelimiter != ",":
                                                    writer.writerow(["sep=", ""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                                                writer.writerow(headings[:GlobalVars.dataKeys["_KEY"][_COLUMN]])  # Print the header, but not the extra _field headings

                                                try:
                                                    for i in range(0, len(GlobalVars.transactionTable)):
                                                        if GlobalVars.ENABLE_BESPOKE_CODING:                            # PATCH: client_mark_extract_data
                                                            tmpRow = []
                                                            for tmpCol in range(0, GlobalVars.dataKeys["_KEY"][_COLUMN]):
                                                                if tmpCol not in GlobalVars.keepKeys_ESB: continue
                                                                tmpRow.append(GlobalVars.transactionTable[i][tmpCol])
                                                            writer.writerow(tmpRow)
                                                            del tmpRow, tmpCol
                                                        else:
                                                            writer.writerow(GlobalVars.transactionTable[i][:GlobalVars.dataKeys["_KEY"][_COLUMN]])
                                                    del GlobalVars.keepKeys_ESB
                                                except:
                                                    _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR writing to CSV on row %s. Please review console" %(i)
                                                    GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                    myPrint("B", _msgTxt)
                                                    myPrint("B", _THIS_EXTRACT_NAME, GlobalVars.transactionTable[i])
                                                    raise

                                            _msgTxt = _THIS_EXTRACT_NAME + "CSV file: '%s' created (%s records)" %(GlobalVars.csvfilename, len(GlobalVars.transactionTable))
                                            myPrint("B", _msgTxt)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            GlobalVars.countFilesCreated += 1

                                        except:
                                            e_type, exc_value, exc_traceback = sys.exc_info()                           # noqa
                                            _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR '%s' detected writing file: '%s' - Extract ABORTED!" %(exc_value, GlobalVars.csvfilename)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            myPrint("B", _msgTxt)
                                            raise

                                    def fixFormatsStr(theString, lNumber=False, sFormat=""):
                                        if isinstance(theString, bool): return theString
                                        if isinstance(theString, tuple): return theString
                                        if isinstance(theString, dict): return theString
                                        if isinstance(theString, list): return theString

                                        if isinstance(theString, int) or isinstance(theString, float) or isinstance(theString, long):
                                            lNumber = True

                                        if lNumber is None: lNumber = False
                                        if theString is None: theString = ""

                                        if sFormat == "%" and theString != "":
                                            theString = "{:.1%}".format(theString)
                                            return theString

                                        if lNumber: return str(theString)

                                        theString = theString.strip()  # remove leading and trailing spaces

                                        theString = theString.replace("\n", "*")  # remove newlines within fields to keep csv format happy
                                        theString = theString.replace("\t", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace(";", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace(",", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace("|", "*")  # remove tabs within fields to keep csv format happy

                                        if GlobalVars.lStripASCII:
                                            all_ASCII = ''.join(char for char in theString if ord(char) < 128)  # Eliminate non ASCII printable Chars too....
                                        else:
                                            all_ASCII = theString
                                        return all_ASCII

                                    if len(GlobalVars.transactionTable) > 0:

                                        ExtractDataToFile()

                                        if not GlobalVars.lGlobalErrorDetected:
                                            sTxt = "Extract file CREATED:"
                                            mTxt = "With %s rows\n" % (len(GlobalVars.transactionTable))
                                            myPrint("B", _THIS_EXTRACT_NAME + "%s\n%s" %(sTxt, mTxt))
                                        else:
                                            _msgTextx = _THIS_EXTRACT_NAME + "ERROR Creating extract (review console for error messages)...."
                                            GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                    else:
                                        _msgTextx = _THIS_EXTRACT_NAME + "@@ No records selected and no extract file created @@"
                                        GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                        myPrint("B", _msgTextx)
                                        if not GlobalVars.AUTO_EXTRACT_MODE:
                                            DoExtractsSwingWorker.killPleaseWait()
                                            genericSwingEDTRunner(True, True, myPopupInformationBox, client_mark_extract_data_frame_, _msgTextx, GlobalVars.thisScriptName, JOptionPane.WARNING_MESSAGE)

                                    # delete references to large objects
                                    GlobalVars.transactionTable = None

                                try:
                                    do_extract_security_balances()
                                except:
                                    GlobalVars.lGlobalErrorDetected = True

                                if GlobalVars.lGlobalErrorDetected:
                                    GlobalVars.countErrorsDuringExtract += 1
                                    _txt = _THIS_EXTRACT_NAME + "@@ ERROR: do_extract_security_balances() has failed (review console)!"
                                    GlobalVars.AUTO_MESSAGES.append(_txt)
                                    myPrint("B", _txt)
                                    dump_sys_error_to_md_console_and_errorlog()
                                    if not GlobalVars.AUTO_EXTRACT_MODE:
                                        DoExtractsSwingWorker.killPleaseWait()
                                        genericSwingEDTRunner(True, True, myPopupInformationBox, client_mark_extract_data_frame_, _txt, "ERROR", JOptionPane.ERROR_MESSAGE)
                                        return False
                            #### ENDIF lExtractSecurityBalances ####

                            if lExtractAccountBalances:
                                # ####################################################
                                # EXTRACT_ACCOUNT_BALANCES_CSV EXECUTION
                                # ####################################################

                                _THIS_EXTRACT_NAME = pad("EXTRACT: Account Balances:", 34)
                                GlobalVars.lGlobalErrorDetected = False

                                if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                    self.super__publish([_THIS_EXTRACT_NAME.strip()])                                   # noqa

                                GlobalVars.csvfilename = getExtractFullPath("EAB")

                                def do_extract_account_balances():

                                    _YEAR = 0; _MONTH = 1; _DAY = 2

                                    todayInt = DateUtil.getStrippedDateInt()

                                    # 0=this year and last year, 1=just this year, 2=just last year
                                    whichYears = GlobalVars.saved_whichYearOption_EAB

                                    lIncludeLastYear = (WhichYearChooser.BOTH_YEARS_KEY in whichYears or WhichYearChooser.LAST_YEAR_KEY in whichYears)
                                    lIncludeThisYear = (WhichYearChooser.BOTH_YEARS_KEY in whichYears or WhichYearChooser.THIS_YEAR_KEY in whichYears)

                                    yearInc = -1 if lIncludeLastYear else 0
                                    firstMonthEndDateInt = DateUtil.lastDayInMonth(DateUtil.firstDayInYear(DateUtil.incrementDate(todayInt, yearInc, 0, 0)))
                                    del yearInc

                                    if firstMonthEndDateInt > todayInt:
                                        eabTxt = ("The first calculated month-end date of: %s is after today's date of: %s - NOTHING TO DO - Quitting..."
                                                %(convertStrippedIntDateFormattedText(firstMonthEndDateInt), convertStrippedIntDateFormattedText(todayInt)))
                                        myPrint("B", eabTxt)
                                        GlobalVars.AUTO_MESSAGES.append(eabTxt)
                                        return

                                    if lIncludeThisYear:
                                        lastMonthEndInt = DateUtil.lastDayInMonth(todayInt)
                                        if todayInt != lastMonthEndInt:
                                            lastMonthEndInt = DateUtil.lastDayInMonth(DateUtil.incrementDate(lastMonthEndInt, 0, -1, 0))
                                    else:
                                        lastMonthEndInt = DateUtil.lastDayInYear(firstMonthEndDateInt)

                                    myPrint("DB", "@@ Calculate month-end dates: saved_whichYearOption_EAB: %s, today: %s, include last year: %s, include this year: %s, first monthend: %s, last monthend: %s"
                                                   %(whichYears, convertStrippedIntDateFormattedText(todayInt), lIncludeLastYear, lIncludeThisYear, convertStrippedIntDateFormattedText(firstMonthEndDateInt), convertStrippedIntDateFormattedText(lastMonthEndInt)))

                                    # Now calculate month-end 'buckets' - or 'intervals' - Seems to return beginning of months (I want month-ends)
                                    # interval = TimeInterval.MONTH
                                    # intervalUtil = TimeIntervalUtil()
                                    # firstInterval = intervalUtil.getIntervalStart(firstMonthEndDateInt, interval)
                                    # lastInterval = intervalUtil.getIntervalEnd(lastMonthEndInt, interval)
                                    # numIntervals = intervalUtil.getNumIntervals(firstInterval, lastInterval, interval)
                                    # monthEndDatesInt = intervalUtil.getIntervalPoints(numIntervals, firstInterval, interval)
                                    # if True or debug:
                                    #     myPrint("B", "interval: %s, firstInterval: %s, lastInterval: %s, numIntervals: %s" %(interval, firstInterval, lastInterval, numIntervals))
                                    #     myPrint("B", "intervals: %s" %(monthEndDatesInt));

                                    # Now calculate month-end 'buckets' - or 'intervals'
                                    monthEndDatesInt = []
                                    interval = TimeInterval.MONTH
                                    onDateInt = firstMonthEndDateInt
                                    while onDateInt <= lastMonthEndInt:
                                        monthEndDatesInt.append(onDateInt)
                                        onDateInt = DateUtil.lastDayInMonth(DateUtil.incrementDate(onDateInt, 0, 1, 0))

                                    if debug:
                                        myPrint("B", "intervals: %s, firstInterval: %s, lastInterval: %s, numIntervals: %s"
                                                %(interval, convertStrippedIntDateFormattedText(monthEndDatesInt[0]), convertStrippedIntDateFormattedText(monthEndDatesInt[-1]), len(monthEndDatesInt)))
                                        myPrint("B", "intervals: %s" %(monthEndDatesInt))

                                    if len(monthEndDatesInt) < 1:
                                        eabTxt = "@@ No monthend 'buckets' / 'intervals' found to report! @@"
                                        myPrint("B", eabTxt)
                                        GlobalVars.AUTO_MESSAGES.append(eabTxt)
                                        return

                                    # noinspection PyArgumentList
                                    class MyAcctFilterEAB(AcctFilter):

                                        def __init__(self,
                                                     _hideInactiveAccounts=True,
                                                     _hideHiddenAccounts=True,
                                                     _lAllAccounts=True,
                                                     _filterForAccounts="ALL",
                                                     _lAllCurrency=True,
                                                     _filterForCurrency="ALL"):

                                            self._hideHiddenAccounts = _hideHiddenAccounts
                                            self._hideInactiveAccounts = _hideInactiveAccounts
                                            self._lAllAccounts = _lAllAccounts
                                            self._filterForAccounts = _filterForAccounts
                                            self._lAllCurrency = _lAllCurrency
                                            self._filterForCurrency = _filterForCurrency

                                        def matches(self, acct):

                                            # noinspection PyUnresolvedReferences
                                            if not (acct.getAccountType() == Account.AccountType.BANK
                                                    or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                                                    or acct.getAccountType() == Account.AccountType.LOAN
                                                    or acct.getAccountType() == Account.AccountType.LIABILITY
                                                    or acct.getAccountType() == Account.AccountType.ASSET
                                                    or acct.getAccountType() == Account.AccountType.INVESTMENT):
                                                return False

                                            if self._hideInactiveAccounts:
                                                # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
                                                if (acct.getAccountOrParentIsInactive()): return False
                                                if (acct.getHideOnHomePage() and acct.getBalance() == 0): return False

                                            if self._lAllAccounts or (self._filterForAccounts.upper().strip() in acct.getFullAccountName().upper().strip()):
                                                pass
                                            else:
                                                return False

                                            curr = acct.getCurrencyType()
                                            currID = curr.getIDString()
                                            currName = curr.getName()

                                            # All accounts and security records can have currencies
                                            if self._lAllCurrency:
                                                pass
                                            elif (self._filterForCurrency.upper().strip() in currID.upper().strip()):
                                                pass
                                            elif (self._filterForCurrency.upper().strip() in currName.upper().strip()):
                                                pass
                                            else:
                                                return False

                                            return True


                                    validAccountList = AccountUtil.allMatchesForSearch(MD_REF.getCurrentAccountBook(),
                                                                                       MyAcctFilterEAB(_hideInactiveAccounts=GlobalVars.hideInactiveAccounts_EAB,
                                                                                                       _hideHiddenAccounts=GlobalVars.hideHiddenAccounts_EAB,
                                                                                                       _lAllAccounts=GlobalVars.lAllAccounts_EAB,
                                                                                                       _filterForAccounts=GlobalVars.filterForAccounts_EAB,
                                                                                                       _lAllCurrency=GlobalVars.lAllCurrency_EAB,
                                                                                                       _filterForCurrency=GlobalVars.filterForCurrency_EAB))

                                    _COLUMN = 0
                                    _HEADING = 1

                                    dki = 0
                                    GlobalVars.dataKeys = {}                                                            # noqa
                                    GlobalVars.dataKeys["_ACCOUNTTYPE"]         = [dki, "AccountType"]; dki += 1
                                    GlobalVars.dataKeys["_ACCOUNT"]             = [dki, "Account"];     dki += 1
                                    GlobalVars.dataKeys["_STATUS"]              = [dki, "Status"];      dki += 1

                                    for monthIdx in range(0, len(monthEndDatesInt)):
                                        dateInt = monthEndDatesInt[monthIdx]
                                        year, month, day = separateYearMonthDayFromDateInt(dateInt)
                                        GlobalVars.dataKeys[dateInt]            = [dki, "%s-%s" %(year, rpad(month, 2, "0"))]; dki += 1
                                        del year, month, day

                                    GlobalVars.dataKeys["_KEY"]                 = [dki, "Key"];         dki += 1
                                    GlobalVars.dataKeys["_END"]                 = [dki, "_END"];        dki += 1

                                    GlobalVars.transactionTable = []

                                    myPrint("DB", _THIS_EXTRACT_NAME, GlobalVars.dataKeys)

                                    book = MD_REF.getCurrentAccountBook()

                                    acctBalancesForDatesPerAccount = {}
                                    acctBalancesForDatesGrandTotals = [0.0 for _x in range(0, len(monthEndDatesInt))]   # noqa

                                    for acctEAB in validAccountList:
                                        if isinstance(acctEAB, Account): pass
                                        acctCurr = acctEAB.getCurrencyType()

                                        acctBalancesForDatesPerAccount[acctEAB] = AccountUtil.getBalancesAsOfDates(book, acctEAB, monthEndDatesInt, True)

                                        # Add security values into investment account total
                                        if acctEAB.getAccountType() == Account.AccountType.INVESTMENT:                  # noqa
                                            secSubAccts = ArrayList(acctEAB.getSubAccounts())
                                            for secAcct in secSubAccts:
                                                acctBalancesForDatesForSecAcct = AccountUtil.getBalancesAsOfDates(book, secAcct, monthEndDatesInt, True)
                                                for monthIdx in range(0, len(monthEndDatesInt)):
                                                    dateInt = monthEndDatesInt[monthIdx]
                                                    secBalLong = acctBalancesForDatesForSecAcct[monthIdx]
                                                    secBalInvestCurrLong = CurrencyUtil.convertValue(secBalLong, secAcct.getCurrencyType(), acctCurr, dateInt)
                                                    acctBalancesForDatesPerAccount[acctEAB][monthIdx] += secBalInvestCurrLong

                                        _row = ([None] * GlobalVars.dataKeys["_END"][0])  # Create a blank row to be populated below...
                                        _row[GlobalVars.dataKeys["_KEY"][_COLUMN]] = ""
                                        _row[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]] = acctEAB.getFullAccountName()
                                        _row[GlobalVars.dataKeys["_ACCOUNTTYPE"][_COLUMN]] = acctEAB.getAccountType().toString()
                                        _row[GlobalVars.dataKeys["_STATUS"][_COLUMN]] = "I" if acctEAB.getAccountIsInactive() else "A"
                                        _row[GlobalVars.dataKeys["_KEY"][_COLUMN]] = 0

                                        for monthIdx in range(0, len(monthEndDatesInt)):
                                            dateInt = monthEndDatesInt[monthIdx]
                                            valCurrLong = acctBalancesForDatesPerAccount[acctEAB][monthIdx]
                                            valCurrDbl = acctCurr.getDoubleValue(valCurrLong)                           # noqa

                                            valBaseLong = CurrencyUtil.convertValue(valCurrLong, acctCurr, GlobalVars.baseCurrency, dateInt)
                                            valBaseDbl = GlobalVars.baseCurrency.getDoubleValue(valBaseLong)

                                            _row[GlobalVars.dataKeys[dateInt][_COLUMN]] = round(valBaseDbl, 2)

                                            # Add value into totals row
                                            acctBalancesForDatesGrandTotals[monthIdx] += valBaseDbl

                                        myPrint("D", _THIS_EXTRACT_NAME, _row)
                                        GlobalVars.transactionTable.append(_row)

                                    if len(GlobalVars.transactionTable) < 1:
                                        eabTxt = "@@ No data found to report! @@"
                                        myPrint("B", eabTxt)
                                        GlobalVars.AUTO_MESSAGES.append(eabTxt)
                                        return
                                    else:
                                        # Add totals row....
                                        _row = ([None] * GlobalVars.dataKeys["_END"][0])  # Create a blank row to be populated below...
                                        _row[GlobalVars.dataKeys["_KEY"][_COLUMN]] = ""
                                        _row[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]] = "Grand Total"
                                        _row[GlobalVars.dataKeys["_ACCOUNTTYPE"][_COLUMN]] = "Grand Total"
                                        _row[GlobalVars.dataKeys["_KEY"][_COLUMN]] = 999

                                        for monthIdx in range(0, len(monthEndDatesInt)):
                                            dateInt = monthEndDatesInt[monthIdx]
                                            valueDbl = round(acctBalancesForDatesGrandTotals[monthIdx], 2)
                                            _row[GlobalVars.dataKeys[dateInt][_COLUMN]] = valueDbl

                                        myPrint("D", _THIS_EXTRACT_NAME, _row)
                                        GlobalVars.transactionTable.append(_row)


                                    myPrint("B", _THIS_EXTRACT_NAME + "Account Balance(s) Records selected:", len(GlobalVars.transactionTable))
                                    ###########################################################################################################

                                    GlobalVars.transactionTable = sorted(GlobalVars.transactionTable, key=lambda x: (x[GlobalVars.dataKeys["_KEY"][_COLUMN]],
                                                                                                                     x[GlobalVars.dataKeys["_ACCOUNTTYPE"][_COLUMN]].lower(),
                                                                                                                     x[GlobalVars.dataKeys["_ACCOUNT"][_COLUMN]].lower()))

                                    ###########################################################################################################


                                    def ExtractDataToFile():
                                        myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                        headings = []
                                        sortDataFields = sorted(GlobalVars.dataKeys.items(), key=lambda x: x[1][_COLUMN])
                                        for i in sortDataFields:
                                            headings.append(i[1][_HEADING])

                                        myPrint("DB", _THIS_EXTRACT_NAME + "Now pre-processing the file to convert integer dates and strip non-ASCII if requested....")
                                        for _theRow in GlobalVars.transactionTable:

                                            for col in range(0, GlobalVars.dataKeys["_STATUS"][_COLUMN]):
                                                _theRow[col] = fixFormatsStr(_theRow[col])

                                        myPrint("B", _THIS_EXTRACT_NAME + "Opening file and writing %s records" %(len(GlobalVars.transactionTable)))

                                        try:
                                            # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                                            with open(GlobalVars.csvfilename, "wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; juse "w" and newline='' in PY3.0

                                                if GlobalVars.lWriteBOMToExtractFile:
                                                    csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                                                writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(GlobalVars.csvDelimiter))

                                                if GlobalVars.csvDelimiter != ",":
                                                    writer.writerow(["sep=", ""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                                                writer.writerow(headings[:GlobalVars.dataKeys["_KEY"][_COLUMN]])  # Print the header, but not the extra _field headings

                                                try:
                                                    for i in range(0, len(GlobalVars.transactionTable)):
                                                        writer.writerow(GlobalVars.transactionTable[i][:GlobalVars.dataKeys["_KEY"][_COLUMN]])
                                                except:
                                                    _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR writing to CSV on row %s. Please review console" %(i)
                                                    GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                    myPrint("B", _msgTxt)
                                                    myPrint("B", _THIS_EXTRACT_NAME, GlobalVars.transactionTable[i])
                                                    raise

                                            _msgTxt = _THIS_EXTRACT_NAME + "CSV file: '%s' created (%s records)" %(GlobalVars.csvfilename, len(GlobalVars.transactionTable))
                                            myPrint("B", _msgTxt)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            GlobalVars.countFilesCreated += 1

                                        except:
                                            e_type, exc_value, exc_traceback = sys.exc_info()                           # noqa
                                            _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR '%s' detected writing file: '%s' - Extract ABORTED!" %(exc_value, GlobalVars.csvfilename)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            myPrint("B", _msgTxt)
                                            raise

                                    def fixFormatsStr(theString, lNumber=False, sFormat=""):
                                        if isinstance(theString, bool): return theString
                                        if isinstance(theString, tuple): return theString
                                        if isinstance(theString, dict): return theString
                                        if isinstance(theString, list): return theString

                                        if isinstance(theString, int) or isinstance(theString, float) or isinstance(theString, long):
                                            lNumber = True

                                        if lNumber is None: lNumber = False
                                        if theString is None: theString = ""

                                        if sFormat == "%" and theString != "":
                                            theString = "{:.1%}".format(theString)
                                            return theString

                                        if lNumber: return str(theString)

                                        theString = theString.strip()  # remove leading and trailing spaces

                                        theString = theString.replace("\n", "*")  # remove newlines within fields to keep csv format happy
                                        theString = theString.replace("\t", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace(";", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace(",", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace("|", "*")  # remove tabs within fields to keep csv format happy

                                        if GlobalVars.lStripASCII:
                                            all_ASCII = ''.join(char for char in theString if ord(char) < 128)  # Eliminate non ASCII printable Chars too....
                                        else:
                                            all_ASCII = theString
                                        return all_ASCII

                                    if len(GlobalVars.transactionTable) > 0:

                                        ExtractDataToFile()

                                        if not GlobalVars.lGlobalErrorDetected:
                                            sTxt = "Extract file CREATED:"
                                            mTxt = "With %s rows\n" % (len(GlobalVars.transactionTable))
                                            myPrint("B", _THIS_EXTRACT_NAME + "%s\n%s" %(sTxt, mTxt))
                                        else:
                                            _msgTextx = _THIS_EXTRACT_NAME + "ERROR Creating extract (review console for error messages)...."
                                            GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                    else:
                                        _msgTextx = _THIS_EXTRACT_NAME + "@@ No records selected and no extract file created @@"
                                        GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                        myPrint("B", _msgTextx)
                                        if not GlobalVars.AUTO_EXTRACT_MODE:
                                            DoExtractsSwingWorker.killPleaseWait()
                                            genericSwingEDTRunner(True, True, myPopupInformationBox, client_mark_extract_data_frame_, _msgTextx, GlobalVars.thisScriptName, JOptionPane.WARNING_MESSAGE)

                                    # delete references to large objects
                                    GlobalVars.transactionTable = None

                                try:
                                    do_extract_account_balances()
                                except:
                                    GlobalVars.lGlobalErrorDetected = True

                                if GlobalVars.lGlobalErrorDetected:
                                    GlobalVars.countErrorsDuringExtract += 1
                                    _txt = _THIS_EXTRACT_NAME + "@@ ERROR: do_extract_account_balances() has failed (review console)!"
                                    GlobalVars.AUTO_MESSAGES.append(_txt)
                                    myPrint("B", _txt)
                                    dump_sys_error_to_md_console_and_errorlog()
                                    if not GlobalVars.AUTO_EXTRACT_MODE:
                                        DoExtractsSwingWorker.killPleaseWait()
                                        genericSwingEDTRunner(True, True, myPopupInformationBox, client_mark_extract_data_frame_, _txt, "ERROR", JOptionPane.ERROR_MESSAGE)
                                        return False
                            #### ENDIF lExtractAccountBalances ####

                            GlobalVars.lGlobalErrorDetected = False

                        except:
                            e_type, exc_value, exc_traceback = sys.exc_info()                                           # noqa
                            GlobalVars.lGlobalErrorDetected = True
                            myPrint("B", "@@ ERROR '%s' Detected within DoExtractsSwingWorker()" %(exc_value))
                            dump_sys_error_to_md_console_and_errorlog()
                            return False

                        myPrint("DB", "DoExtractsSwingWorker.doInBackground() completed...")
                        return True

                    # noinspection PyMethodMayBeStatic
                    def done(self):
                        myPrint("DB", "In DoExtractsSwingWorker()", inspect.currentframe().f_code.co_name, "()")
                        myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                        if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                            myPrint("DB", "... calling done:get()")
                            self.get()     # wait for task to complete
                            myPrint("DB", "... after done:get()")

                        DoExtractsSwingWorker.killPleaseWait()

                        # EXTRACT(s) COMPLETED
                        msgs = []
                        msgs.append(">>>")
                        msgs.append("--------------------------------")
                        msgs.append("EXTRACT DATA: MESSAGES & SUMMARY")
                        msgs.append("")
                        if GlobalVars.AUTO_EXTRACT_MODE:
                            msgs.append("AUTO EXTRACT MODE ENABLED")
                        else:
                            msgs.append("SINGLE DATA FILE EXTRACT MODE ENABLED")
                        msgs.append("")

                        if GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                            msgs.append("EXTRACT TRIGGERED BY FILE CLOSING EVENT")
                            msgs.append("")

                        if GlobalVars.AUTO_INVOKE_CALLED:
                            if GlobalVars.AUTO_INVOKE_THEN_QUIT:
                                msgs.append("AUTO INVOKE CALLED >> WILL TRIGGER SHUTDOWN...")
                            else:
                                msgs.append("AUTO INVOKE CALLED >> Moneydance will remain running after extract(s)...")
                            msgs.append("")

                        if lExtractAccountTxns:         msgs.append("Extract Account Registers          REQUESTED")
                        if lExtractInvestmentTxns:      msgs.append("Extract Investment Transactions    REQUESTED")
                        if lExtractSecurityBalances:    msgs.append("Extract Security Balances          REQUESTED")
                        if lExtractAccountBalances:     msgs.append("Extract Account Balances           REQUESTED")

                        msgs.append("")
                        msgs.extend(GlobalVars.AUTO_MESSAGES)
                        msgs.append("")

                        msgs.append("Extract csv files / folders created..: %s" %(GlobalVars.countFilesCreated))
                        msgs.append("Extract errors during extract........: %s" %(GlobalVars.countErrorsDuringExtract))

                        if GlobalVars.lGlobalErrorDetected or GlobalVars.countErrorsDuringExtract > 0:
                            msgs.append("")
                            msgs.append("*** EXTRACT FAILED WITH ERROR >> REVIEW CONSOLE FOR DETAILS ***")
                            msgs.append("")

                        msgs.append("--------------------------------")
                        msgs.append("")

                        willShowConsoleAgain = (GlobalVars.saved_relaunchGUIAfterRun_SWSS and not GlobalVars.AUTO_EXTRACT_MODE)

                        GlobalVars.LAST_END_EXTRACT_MESSAGE = "\n".join(msgs)
                        myPrint("B", GlobalVars.LAST_END_EXTRACT_MESSAGE)

                        if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                            if not willShowConsoleAgain:
                                MyPopUpDialogBox(None, theStatus="EXTRACT PROCESS COMPLETED >> review status below:)",
                                                 theMessage=GlobalVars.LAST_END_EXTRACT_MESSAGE,
                                                 theTitle="EXTRACT_DATA: %s" %("AUTO MODE" if GlobalVars.AUTO_EXTRACT_MODE else "MANUAL MODE"),
                                                 lModal=False).go()
                                GlobalVars.LAST_END_EXTRACT_MESSAGE = None

                            if not GlobalVars.AUTO_EXTRACT_MODE and GlobalVars.countFilesCreated > 0:
                                if GlobalVars.saved_showFolderAfterExtract_SWSS:
                                    try: MD_REF.getPlatformHelper().openDirectory(File(GlobalVars.saved_defaultSavePath_SWSS))
                                    except: pass

                        cleanup_actions(client_mark_extract_data_frame_)

                        if GlobalVars.AUTO_INVOKE_CALLED:
                            if GlobalVars.AUTO_INVOKE_THEN_QUIT:
                                myPrint("B", "@@ COMPLETED - Triggering shutdown @@")
                                MD_REF.saveCurrentAccount()
                                try:
                                    MD_REF.SUPPRESS_BACKUPS = True
                                    myPrint("B", "@@ Successfully set SUPPRESS_BACKUPS for post extract auto-shutdown...")
                                except:
                                    myPrint("B", "@@ Failed to set SUPPRESS_BACKUPS for post extract auto-shutdown - ignoring...")
                                genericThreadRunner(True, MD_REF.getUI().shutdownApp, False)
                            else:
                                myPrint("B", "@@ COMPLETED (Moneydance will remain running) @@")

                        if willShowConsoleAgain:
                            myPrint("B", "@@ Execution complete, non-auto mode, re-launching config screen....")
                            invokeCmd = "moneydance:fmodule:%s:%s:%s" %(myModuleID, "showconsole", "noquit")
                            genericSwingEDTRunner(False, False, MD_REF.showURL, invokeCmd)

                _msgPad = 100
                _msg = pad("PLEASE WAIT: Extracting Data", _msgPad, padChar=".")
                if GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                    pleaseWait = None
                else:
                    pleaseWait = MyPopUpDialogBox(client_mark_extract_data_frame_, theStatus=_msg, theTitle=_msg, lModal=False, OKButtonText="WAIT")
                    pleaseWait.go()

                if GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                    # Run / block calling MD thread...
                    sw = DoExtractsSwingWorker(pleaseWait)
                    sw.doInBackground()
                    sw.done()
                else:
                    sw = DoExtractsSwingWorker(pleaseWait)
                    sw.execute()

            except QuickAbortThisScriptException:
                myPrint("DB", "Caught Exception: QuickAbortThisScriptException... Doing nothing (assume exit requested)...")

            except:
                crash_txt = "ERROR - Extract_Data has crashed. Please review MD Menu>Help>Console Window for details".upper()
                myPrint("B", crash_txt)
                crash_output = dump_sys_error_to_md_console_and_errorlog(True)
                if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                    jif = QuickJFrame("ERROR - Extract_Data:", crash_output).show_the_frame()
                    MyPopUpDialogBox(jif, theStatus="ERROR: Extract_Data has crashed", theMessage=crash_txt, theTitle="ERROR", lAlertLevel=2, lModal=False).go()
                raise


    if GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
        # Keep / block the same calling Moneydance event thread....
        myPrint("DB", "Executing code on the same Moneydance handle_event thread to block Moneydance whilst auto extract runs....")
        MainAppRunnable().run()
    else:
        SwingUtilities.invokeLater(MainAppRunnable())
