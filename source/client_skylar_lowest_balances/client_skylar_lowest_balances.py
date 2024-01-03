#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# client_skylar_lowest_balances.py build: 1001 - November 2023 - Stuart Beesley - StuWareSoftSystems
#
# "Bespoke for 'Skylar De'Font. Shows lowest future balances on Summary / Home page widget"
########################################################################################################################
# MIT License
#
# Copyright (c) 2020-2024 Stuart Beesley - StuWareSoftSystems
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

# Built to operate on Moneydance 2021.1 build 3056 onwards (as this is when the Py Extensions became fully functional)

# Build: 1 - Initial beta release. Based code copied from net_account_balances.
# Build: 1000 - Initial release...
# Build: 1001 - Exclude inactive accounts from AccountSelectList()...


# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################

# SET THESE LINES
myModuleID = u"client_skylar_lowest_balances"
version_build = "1001"
MIN_BUILD_REQD = 3056  # 2021.1 Build 3056 is when Python extensions became fully functional (with .unload() method for example)
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

global client_skylar_lowest_balances_frame_
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
            and (isinstance(client_skylar_lowest_balances_frame_, MyJFrame)                 # EDIT THIS
                 or type(client_skylar_lowest_balances_frame_).__name__ == u"MyCOAWindow")  # EDIT THIS
            and client_skylar_lowest_balances_frame_.isActiveInMoneydance):                 # EDIT THIS
        frameToResurrect = client_skylar_lowest_balances_frame_                             # EDIT THIS
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
    from javax.swing import ImageIcon
    from java.awt import Image
    from javax.imageio import ImageIO
    from java.awt.image import BufferedImage
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
    # All common globals have now been eliminated :->
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
    GlobalVars.thisScriptName = u"%s.py(Extension)" %(myModuleID)

    # END SET THESE VARIABLES FOR ALL SCRIPTS ##############################################################################

    # >>> THIS SCRIPT'S IMPORTS ############################################################################################
    import threading

    from com.moneydance.apps.md.view.gui import MDAction
    from com.moneydance.apps.md.view.gui.select import AccountSelectList
    from com.moneydance.apps.md.view.gui.reporttool import GraphReportUtil
    from com.moneydance.awt import GridC, JLinkListener, JLinkLabel, AwtUtil
    from com.moneydance.apps.md.view import HomePageView
    from com.moneydance.apps.md.view.gui import MoneydanceGUI
    from com.moneydance.apps.md.view.gui import MoneydanceLAF, MainFrame
    from com.moneydance.apps.md.controller import FeatureModule, PreferencesListener, AccountFilter, FullAccountList
    from com.infinitekind.moneydance.model import AccountListener, AbstractTxn, CurrencyListener
    from com.infinitekind.util import StringUtils, StreamVector

    from org.apache.commons.lang3 import StringEscapeUtils

    from java.io import BufferedInputStream
    from javax.swing import JSeparator, BorderFactory, Timer as SwingTimer
    from java.awt import BasicStroke, Graphics2D, Rectangle
    from java.awt.font import TextAttribute
    from java.awt.event import MouseListener, ActionListener
    from java.awt.geom import Path2D
    from java.lang import Integer, InterruptedException, Character
    from java.lang.ref import WeakReference
    from java.util import  UUID
    from java.util.concurrent import CancellationException
    # >>> END THIS SCRIPT'S IMPORTS ########################################################################################

    # >>> THIS SCRIPT'S GLOBALS ############################################################################################
    GlobalVars.specialDebug = False

    GlobalVars.MD_KOTLIN_COMPILED_BUILD_ALL = 5008                          # 2023.2 (Entire codebase compiled in Kotlin)

    GlobalVars.Strings.MD_GLYPH_APPICON_64 = "/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"
    GlobalVars.Strings.MD_GLYPH_REFRESH = "/com/moneydance/apps/md/view/gui/glyphs/glyph_refresh.png"
    GlobalVars.Strings.MD_GLYPH_TRIANGLE_RIGHT = "/com/moneydance/apps/md/view/gui/glyphs/glyph_triangle_right.png"
    GlobalVars.Strings.MD_GLYPH_TRIANGLE_DOWN = "/com/moneydance/apps/md/view/gui/glyphs/glyph_triangle_down.png"
    GlobalVars.Strings.MD_GLYPH_REMINDERS = "/com/moneydance/apps/md/view/gui/glyphs/glyph_reminders.png"
    GlobalVars.Strings.MD_ICON_ALERT_16 = "/com/moneydance/apps/md/view/gui/icons/alert16.png"
    GlobalVars.Strings.MD_GLYPH_SELECTOR_7_9 = "/com/moneydance/apps/md/view/gui/glyphs/selector_sm.png"
    GlobalVars.Strings.MD_GLYPH_DELETE_32_32 = "/com/moneydance/apps/md/view/gui/glyphs/glyph_delete.png"
    GlobalVars.Strings.MD_GLYPH_ADD_28_28 = "/com/moneydance/apps/md/view/gui/glyphs/glyph_income_icon@2x.png"

    GlobalVars.Strings.PARAMETER_FILEUUID = "__last_saved_file_uuid"
    GlobalVars.Strings.MD_STORAGE_KEY_FILEUUID = "netsync.dropbox.fileid"

    GlobalVars.Strings.UNICODE_CROSS = u"\u2716"
    GlobalVars.Strings.UNICODE_UP_ARROW = u"\u2191"
    GlobalVars.Strings.UNICODE_DOWN_ARROW = u"\u2193"
    GlobalVars.Strings.UNICODE_THIN_SPACE = u"\u2009"

    GlobalVars.EXTENSION_LOCK = threading.Lock()

    # Saved parameters loaded from file
    GlobalVars.extn_param_listAccountUUIDs_LBE = None
    GlobalVars.extn_param_expandedView_LBE = None

    GlobalVars.extn_newParams = [paramKey for paramKey in dir(GlobalVars) if (paramKey.lower().startswith("extn_param_".lower()))]

    GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME          = "Lowest Balances"
    GlobalVars.DEFAULT_WIDGET_EXTENSION_NAME        = GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME + " (Bespoke)"
    GlobalVars.DEFAULT_WIDGET_ROW_NOT_CONFIGURED    = "<NOT CONFIGURED>"

    GlobalVars.BALTYPE_BALANCE = 0
    GlobalVars.BALTYPE_CURRENTBALANCE = 1
    GlobalVars.BALTYPE_CLEAREDBALANCE = 2

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

        myPrint("DB", "... destroying own reference to frame('client_skylar_lowest_balances_frame_')...")
        global client_skylar_lowest_balances_frame_
        client_skylar_lowest_balances_frame_ = None
        del client_skylar_lowest_balances_frame_

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

        if not Platform.isOSX() and lForceFD and not fileChooser_selectFiles:
            myPrint("DB", "@@ Overriding lForceFD to False - as it won't work for selecting Folders on Windows/Linux!")
            lForceFD = False

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

            _label2 = JLabel(pad("StuWareSoftSystems (2020-2024)", 800))
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

    def selectAllHomeScreens():

        try:
            firstMF = GlobalVars.CONTEXT.getUI().firstMainFrame
            secWindows = [secWin for secWin in GlobalVars.CONTEXT.getUI().getSecondaryWindows() if (isinstance(secWin, MainFrame) and secWin is not firstMF)]
            secWindows.append(firstMF)
            for secWin in secWindows:
                currentViewAccount = secWin.getSelectedAccount()
                if currentViewAccount != GlobalVars.CONTEXT.getRootAccount():
                    myPrint("DB","Switched to Home Page Summary Page (from: %s) - on main frame: %s" %(currentViewAccount, secWin))
                    secWin.selectAccount(GlobalVars.CONTEXT.getRootAccount())
        except:
            myPrint("B","@@ Error switching to Summary Page (Home Page)")


    class NoneLock:
        """Used as a 'do-nothing' alternative to a real 'with:' lock"""
        def __init__(self): pass
        def __enter__(self): pass
        def __exit__(self, *args): pass

    def getSwingObjectProxyName(swComponent):
        if swComponent is None: return "None"
        try: rtnStr = unicode(swComponent.__class__.__bases__[0])
        except: rtnStr = "Error"
        return rtnStr

    def load_StuWareSoftSystems_parameters_into_memory():
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()" )
        myPrint("DB", "Loading variables into memory...")

        if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}

        allParams = []
        allParams.extend(GlobalVars.extn_newParams)
        for _paramKey in allParams:
            paramValue = GlobalVars.parametersLoadedFromFile.get(_paramKey, None)
            if paramValue is not None:
                setattr(GlobalVars, _paramKey, paramValue)

        myPrint("DB", "parametersLoadedFromFile{} set into memory (as variables).....:",                        GlobalVars.parametersLoadedFromFile)

        return

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def dump_StuWareSoftSystems_parameters_from_memory():
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()" )

        # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
        # (i.e. other StuWareSoftSystems programs might be sharing the same file)

        if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}

        # save current parameters
        for _paramKey in GlobalVars.extn_newParams:
            GlobalVars.parametersLoadedFromFile[_paramKey] = getattr(GlobalVars, _paramKey)

        GlobalVars.parametersLoadedFromFile["__%s_extension" %(myModuleID)] = version_build

        myPrint("DB", "variables dumped from memory back into parametersLoadedFromFile{}.....:", GlobalVars.parametersLoadedFromFile)

    # clear up any old left-overs....
    destroyOldFrames(myModuleID)

    myPrint("DB", "DEBUG IS ON..")

    if SwingUtilities.isEventDispatchThread():
        myPrint("DB", "FYI - This script/extension is currently running within the Swing Event Dispatch Thread (EDT)")
    else:
        myPrint("DB", "FYI - This script/extension is NOT currently running within the Swing Event Dispatch Thread (EDT)")

    def cleanup_actions(theFrame, md_reference):
        myPrint("DB", "In", inspect.currentframe().f_code.co_name, "()")
        myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

        if theFrame: pass
        # if not theFrame.isActiveInMoneydance:
        #     destroyOldFrames(myModuleID)  # This was killing frames just launched/reinstalled... not needed (I think)
        #
        try:
            md_reference.getUI().setStatus(">> StuWareSoftSystems - thanks for using >> %s......." %(GlobalVars.thisScriptName),0)
        except:
            pass  # If this fails, then MD is probably shutting down.......

        if not GlobalVars.i_am_an_extension_so_run_headless: print(scriptExit)

        cleanup_references()

    # .moneydance_invoke_called() is used via the _invoke.py script as defined in script_info.dict. Not used for runtime extensions
    def moneydance_invoke_called(theCommand):
        # ... modify as required to handle .showURL() events sent to this extension/script...
        myPrint("B", "INVOKE - Received extension command: '%s'" %(theCommand))

    GlobalVars.defaultPrintLandscape = False
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################

    def isSyncTaskSyncing(checkMainTask=False, checkAttachmentsTask=False):
        if ((not checkMainTask and not checkAttachmentsTask) or (checkMainTask and checkAttachmentsTask)):
            raise Exception("LOGIC ERROR: Must provide either checkMainTask or checkAttachmentsTask True parameter...!")
        _b = MD_REF.getCurrentAccountBook()
        if _b is not None:
            _s = _b.getSyncer()
            if _s is not None:
                try:      # This method only works from MD2023.2(5008) onwards...
                    checkTasks = []
                    if checkMainTask: checkTasks.append("getMainSyncTask")
                    if checkAttachmentsTask: checkTasks.append("getAttachmentsSyncTask")
                    for checkTask in checkTasks:
                        _st = invokeMethodByReflection(_s, checkTask, [])
                        _isSyncing = invokeMethodByReflection(_st, "isSyncing", [])
                        myPrint("DB", "isSyncTaskSyncing(): Task: .%s(), Thread: '%s', .isSyncing(): %s" %(checkTask, _st, _isSyncing))
                        if _isSyncing:
                            return True
                except:
                    # There is only one big sync thread for versions prior to build 5008...
                    myPrint("DB", "isSyncTaskSyncing(): Ignoring parameters (main: %s, attachments: %s) >> Simply checking the single Syncer status. .isSyncing(): %s"
                            %(checkMainTask, checkAttachmentsTask, _s.isSyncing()))
                    return _s.isSyncing()
        return False

    def padTruncateWithDots(theText, theLength, padChar=u" ", stripSpaces=True, padString=True):
        if not isinstance(theText, basestring): theText = safeStr(theText)
        if theLength < 1: return ""
        if stripSpaces: theText = theText.strip()
        dotChop = min(3, theLength) if (len(theText) > theLength) else 0
        if padString:
            theText = (theText[:theLength-dotChop] + ("." * dotChop)).ljust(theLength, padChar)
        else:
            theText = (theText[:theLength-dotChop] + ("." * dotChop))
        return theText

    def roundTowards(value, target):
        assert (isinstance(value, float)), "ERROR - roundTowards() must be supplied a double/float value! >> received: %s(%s)" %(value, type(value))
        roundedValue = value
        if value < target:
            roundedValue = Math.ceil(value)
        elif value > target:
            roundedValue = Math.floor(value)
        return roundedValue

    # com.infinitekind.moneydance.model.CurrencyType.formatSemiFancy(long, char) : String
    def formatSemiFancy(ct, amt, decimalChar, indianFormat=False):
        # type: (CurrencyType, long, basestring, bool) -> basestring
        """Replicates MD API .formatSemiFancy(), but can override for Indian Number format"""
        if not indianFormat: return ct.formatSemiFancy(amt, decimalChar)                # Just call the MD original for efficiency
        return formatFancy(ct, amt, decimalChar, True, False, indianFormat=indianFormat)

    # com.infinitekind.moneydance.model.CurrencyType.formatFancy(long, char, boolean) : String
    def formatFancy(ct, amt, decimalChar, includeDecimals=True, fancy=True, indianFormat=False, roundingTarget=0.0):
        # type: (CurrencyType, long, basestring, bool, bool, bool, float) -> basestring
        """Replicates MD API .formatFancy() / .formatSemiFancy(), but can override for Indian Number format"""

        # Disabled the standard as .formatSemiFancy() has no option to deselect decimal places!! :-(
        # if not indianFormat:
        #     if not fancy: return ct.formatSemiFancy(amt, decimalChar)                   # Just call the MD original for efficiency
        #     return ct.formatFancy(amt, decimalChar, includeDecimals)                    # Just call the MD original for efficiency

        # decStr = "."; comma = GlobalVars.Strings.UNICODE_THIN_SPACE
        decStr = "." if (decimalChar == ".") else ","
        comma = "," if (decimalChar == ".") else "."

        # Do something special for round towards target (not zero)....
        if not includeDecimals and roundingTarget != 0.0:
            origAmt = ct.getDoubleValue(amt)
            roundedAmt = roundTowards(origAmt, roundingTarget)
            amt = ct.getLongValue(roundedAmt)
            # myPrint("B", "@@ Special formatting rounding towards zero triggered.... Original: %s, Target: %s, Rounded: %s" %(origAmt, roundingTarget, roundedAmt));

        sb = invokeMethodByReflection(ct, "formatBasic", [Long.TYPE, Character.TYPE, Boolean.TYPE], [Long(amt), Character(decimalChar), includeDecimals])
        decPlace = sb.lastIndexOf(decStr)
        if decPlace < 0: decPlace = sb.length()
        minPlace = 1 if (amt < 0) else 0

        commaDividingPos = 3
        while (decPlace - commaDividingPos > minPlace):
            decPlace -= commaDividingPos
            sb.insert(decPlace, comma)
            if indianFormat: commaDividingPos = 2   # In the Indian Number system, numbers > 1000 have commas every 2 places (not 3)....

        if not fancy: return sb.toString()

        sb.insert(0, " ")
        sb.insert(0, ct.getPrefix())
        sb.append(" ")
        sb.append(ct.getSuffix())
        return sb.toString().strip()

    def html_strip_chars(_textToStrip):
        _textToStrip = StringEscapeUtils.escapeHtml4(_textToStrip)
        _textToStrip = _textToStrip.replace("  ","&nbsp;&nbsp;")
        return _textToStrip

    def wrap_HTML_wrapper(wrapperCharacter, _textToWrap, stripChars=True, addHTML=True):
        newText = "<%s>%s</%s>" %(wrapperCharacter, _textToWrap if not stripChars else html_strip_chars(_textToWrap), wrapperCharacter)
        if addHTML: newText = wrap_HTML(newText, stripChars=False)
        return newText

    def wrap_HTML_fontColor(_fontColorHexOrColor, _textToWrap, stripChars=True, addHTML=True):
        wrapperCharacter = "font"
        if isinstance(_fontColorHexOrColor, Color):
            _fontColorHexOrColor = AwtUtil.hexStringForColor(_fontColorHexOrColor)
        elif (isinstance(_fontColorHexOrColor, basestring)
                and (_fontColorHexOrColor.startswith("#") and len(_fontColorHexOrColor) == 7)):
            pass
        else: raise Exception("Invalid hex color specified!", _fontColorHexOrColor)

        newText = "<%s color=#%s>%s</%s>" %(wrapperCharacter, _fontColorHexOrColor, _textToWrap if not stripChars else html_strip_chars(_textToWrap), wrapperCharacter)
        if addHTML: newText = wrap_HTML(newText, stripChars=False)
        return newText

    def wrap_HTML(_textToWrap, stripChars=True):
        return wrap_HTML_wrapper("html", _textToWrap, stripChars, addHTML=False)

    def wrap_HTML_bold(_textToWrap, stripChars=True, addHTML=True):
        return wrap_HTML_wrapper("b", _textToWrap, stripChars, addHTML)

    def wrap_HTML_underline(_textToWrap, stripChars=True, addHTML=True):
        return wrap_HTML_wrapper("u", _textToWrap, stripChars, addHTML)

    def wrap_HTML_small(_textToWrap, stripChars=True, addHTML=True):
        return wrap_HTML_wrapper("small", _textToWrap, stripChars, addHTML)

    def wrap_HTML_italics(_textToWrap, stripChars=True, addHTML=True):
        return wrap_HTML_wrapper("i", _textToWrap, stripChars, addHTML)

    def wrap_HTML_BIG_small(_bigText, _smallText, _smallColor=None, stripBigChars=True, stripSmallChars=True, _bigColor=None, _italics=False, _bold=False, _underline=False, _html=False, _smallItalics=False, _smallBold=False, _smallUnderline=False):
        if _html:
            htmlBigText = _bigText
        else:
            strippedBigText = html_strip_chars(_bigText) if stripBigChars else _bigText
            if _bigColor is not None:
                htmlBigText = wrap_HTML_fontColor(_bigColor, strippedBigText, stripChars=False, addHTML=False)
            else:
                htmlBigText = strippedBigText

            if (_bold): htmlBigText = wrap_HTML_bold(htmlBigText, stripChars=False, addHTML=False)
            if (_italics): htmlBigText = wrap_HTML_italics(htmlBigText, stripChars=False, addHTML=False)
            if (_underline): htmlBigText = wrap_HTML_underline(htmlBigText, stripChars=False, addHTML=False)

        if _smallColor is None: _smallColor = GlobalVars.CONTEXT.getUI().getColors().tertiaryTextFG
        _htmlSmallText = html_strip_chars(_smallText) if stripSmallChars else _smallText
        convertedSmallText = wrap_HTML_fontColor(_smallColor, _htmlSmallText, stripChars=False, addHTML=False)
        convertedSmallText = wrap_HTML_small(convertedSmallText, stripChars=False, addHTML=False)
        if (_smallBold): convertedSmallText = wrap_HTML_bold(convertedSmallText, stripChars=False, addHTML=False)
        if (_smallItalics): convertedSmallText = wrap_HTML_italics(convertedSmallText, stripChars=False, addHTML=False)
        if (_smallUnderline): convertedSmallText = wrap_HTML_underline(convertedSmallText, stripChars=False, addHTML=False)
        return wrap_HTML("%s%s" %(htmlBigText, convertedSmallText), stripChars=False)

    def sendMessage(extensionID, theMessage):
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
        # replicating moneydance.showURL("moneydance:fmodule:net_account_balances:myCommand_here?thisIsMyParameter")

        frs = getMyJFrame(extensionID)
        if frs:
            myPrint("DB", "... found frame: %s - requesting .invoke(%s)" %(frs, theMessage))
            return frs.MoneydanceAppListener.invoke("%s:customevent:%s" %(extensionID, theMessage))
        else:
            myPrint("DB", ".. Sorry - did not find my application (JFrame) to send message....")
        return


    # My attempts below to switch my GUI's LaF to match MD after a Theme switch
    # Basically doesn't work... As MD doesn't set all properties up properly after a switch
    # So user just needs to restart MD.....
    # All properties: https://thebadprogrammer.com/swing-uimanager-keys/


    def setJComponentStandardUIDefaults(component, opaque=False, border=False, background=True, foreground=True, font=True):

        if isinstance(component,    JPanel):            key = "Panel"
        elif isinstance(component,  JLabel):            key = "Label"
        elif isinstance(component,  JComboBox):         key = "ComboBox"
        elif isinstance(component,  JButton):           key = "Button"
        elif isinstance(component,  JRadioButton):      key = "RadioButton"
        elif isinstance(component,  JTextField):        key = "TextField"
        elif isinstance(component,  JCheckBox):         key = "CheckBox"
        elif isinstance(component,  JScrollPane):       key = "ScrollPane"
        elif isinstance(component,  JMenu):             key = "Menu"
        elif isinstance(component,  JMenuBar):          key = "MenuBar"
        elif isinstance(component,  JCheckBoxMenuItem): key = "CheckBoxMenuItem"
        elif isinstance(component,  JMenuItem):         key = "MenuItem"
        elif isinstance(component,  JSeparator):        key = "Separator"
        else: raise Exception("Error in setJComponentStandardUIDefaults() - unknown Component instance: %s" %(component))

        if opaque: component.setOpaque(UIManager.getBoolean("%s.opaque" %(key)))

        if isinstance(component, (JMenu)) or component.getClientProperty("%s.id.reversed" %(myModuleID)):
            SetupMDColors.updateUI()
            component.setForeground(SetupMDColors.FOREGROUND_REVERSED)
            component.setBackground(SetupMDColors.BACKGROUND_REVERSED)
        else:
            if foreground: component.setForeground(UIManager.getColor("%s.foreground" %(key)))
            if background and (component.isOpaque() or isinstance(component, (JComboBox, JTextField, JMenuBar))):
                component.setBackground(UIManager.getColor("%s.background" %(key)))

        if border: component.setBorder(UIManager.getBorder("%s.border" %(key)))
        if font:   component.setFont(UIManager.getFont("%s.font" %(key)))

    class MyJPanel(JPanel):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            setJComponentStandardUIDefaults(self)

    class MyJLabel(JLabel):

        def __init__(self, *args, **kwargs):
            self.maxWidth = -1
            self.hasMDHeaderBorder = False
            super(self.__class__, self).__init__(*args, **kwargs)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            setJComponentStandardUIDefaults(self)

            if self.hasMDHeaderBorder: self.setMDHeaderBorder()

        def setMDHeaderBorder(self):
            self.hasMDHeaderBorder = True
            self.setBorder(BorderFactory.createLineBorder(GlobalVars.CONTEXT.getUI().getColors().headerBorder))

        # Avoid the dreaded issue when Blinking changes the width...
        def getPreferredSize(self):
            dim = super(self.__class__, self).getPreferredSize()
            self.maxWidth = Math.max(self.maxWidth, dim.width)
            dim.width = self.maxWidth
            return dim

    class MyJCheckBox(JCheckBox):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)
            self.setFocusable(True)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            # setJComponentStandardUIDefaults(self, border=True)
            setJComponentStandardUIDefaults(self)


    def detectMDClosingError(e):
        if "'NoneType' object has no attribute".lower() in e.message.lower():
            myPrint("B", "Detected that MD is probably closing... Aborting whatever I was doing...")
            return True
        return False

    class MyCollapsibleRefresher:
        """"com.moneydance.awt.CollapsibleRefresher
        Class that enables easy collapsible refreshing.  That is, if you expect to receive a lot of updates
        to a data model that the UI can't keep up with, you can use this to enqueue a Runnable that will
        refresh your UI that won't queue up more than one Runnable on the swing event dispatch thread.

        Multiple .enqueue()s will get ignored.... The first gets pushed to the EDT via .invokeLater()
        EXCEPT: Where an enqueued job has started on the EDT, then the next enqueued will get pushed onto the Queue

        NOTE: HomePageView.ViewPanel gets created as a new instance each time the summary page is requested
              Hence, a new ViewPanel instance will get created with it's own CollapsibleRefresher
              So new .enqueue()s to this Refresher will load whilst the old one might be dead/dying as de-referenced."""

        @staticmethod
        class MyQueueableRefresher(Runnable):
            def __init__(self, collapsibleRefresherClass):
                # type: (Runnable) -> None
                self.collapsibleRefresherClass = collapsibleRefresherClass

            # noinspection PyMethodMayBeStatic
            def run(self):
                if debug: myPrint("DB", "Inside MyQueueableRefresher.... Calling MyCollapsibleRefresher.refreshable.run() Calling Instance:", self.collapsibleRefresherClass)
                self.collapsibleRefresherClass.isPendingRefresh = False
                self.collapsibleRefresherClass.refreshable.run()

        def __init__(self, refreshable):
            # type: (Runnable, bool) -> None
            if debug: myPrint("DB", "Initialising MyCollapsibleRefresher.... Instance: %s. Refreshable: %s" %(self, refreshable))
            self.isPendingRefresh = False
            self.refreshable = refreshable
            self.queueableRefresher = MyCollapsibleRefresher.MyQueueableRefresher(self)

        def enqueueRefresh(self):
            if debug: myPrint("DB", "Inside MyCollapsibleRefresher (instance: %s).... invokeLater(%s) .." %(self, self.queueableRefresher))
            if self.isPendingRefresh:
                if debug: myPrint("DB", "... DISCARDING enqueueRefresh request as one is already pending... Discarded:", self.queueableRefresher)
                return
            if debug: myPrint("DB", "... REQUESTING .invokeLater() on:", self.queueableRefresher)
            self.isPendingRefresh = True
            SwingUtilities.invokeLater(self.queueableRefresher)


    def isSwingComponentValid(swComponent): return not isSwingComponentInvalid(swComponent)

    def isSwingComponentInvalid(swComponent):

        # if debug:
        #     myPrint("B", "isSwingComponentInvalid(), swComponent is None: %s, !isVisible(): %s, !isValid(): %s, !isDisplayable(): %s, getWindowAncestor() is None: %s"
        #             % (swComponent is None, not swComponent.isVisible(), not swComponent.isValid(), not swComponent.isDisplayable(), SwingUtilities.getWindowAncestor(swComponent) is None))

        return (swComponent is None
                or not swComponent.isVisible() or not swComponent.isDisplayable() or SwingUtilities.getWindowAncestor(swComponent) is None)

    class BlinkSwingTimer(SwingTimer, ActionListener):
        ALL_BLINKERS = []
        blinker_LOCK = threading.Lock()

        @staticmethod
        def stopAllBlinkers():
            if debug: myPrint("DB", "BlinkSwingTimer.stopAllBlinkers() called....")
            with BlinkSwingTimer.blinker_LOCK:
                for i in range(0, len(BlinkSwingTimer.ALL_BLINKERS)):
                    blinker = BlinkSwingTimer.ALL_BLINKERS[i]
                    try:
                        blinker.stop()
                        if debug: myPrint("DB", "... stopped blinker: id: %s" %(blinker.uuid))
                    except:
                        if debug: myPrint("DB", ">> ERROR stopping blinker: id: %s" %(blinker.uuid))
                del BlinkSwingTimer.ALL_BLINKERS[:]

        def __init__(self, timeMS, swComponents, flipColor=None, flipBold=False):
            with BlinkSwingTimer.blinker_LOCK:
                self.uuid = UUID.randomUUID().toString()
                self.isForeground = True
                self.countBlinkLoops = 0

                if isinstance(swComponents, JComponent):
                    swComponents = [swComponents]
                elif not isinstance(swComponents, list) or len(swComponents) < 1:
                    return

                self.swComponents = []
                for swComponent in swComponents:
                    font = swComponent.getFont()
                    self.swComponents.append([swComponent,
                                              swComponent.getForeground(),
                                              swComponent.getBackground() if (flipColor is None) else flipColor,
                                              font.deriveFont(font.getStyle() | Font.BOLD) if (flipBold) else font,
                                              font.deriveFont(font.getStyle() & ~Font.BOLD) if (flipBold) else font
                                              ])
                super(self.__class__, self).__init__(max(timeMS, 1200), None)   # Less than 1000ms will prevent whole application from closing when requested...
                if self.getInitialDelay() > 0: self.setInitialDelay(int(self.getInitialDelay()/2))
                self.addActionListener(self)
                BlinkSwingTimer.ALL_BLINKERS.append(self)
                if debug: myPrint("DB", "Blinker initiated - id: %s; with %s components" %(self.uuid, len(swComponents)))

        def actionPerformed(self, event):                                                                               # noqa
            try:
                with BlinkSwingTimer.blinker_LOCK:
                    for i in range(0, len(self.swComponents)):
                        swComponent = self.swComponents[i][0]
                        if isSwingComponentInvalid(swComponent):
                            if debug: myPrint("DB", ">>> Shutting down blinker (id: %s) as component index: %s no longer available" %(self.uuid, i))
                            self.stop()
                            BlinkSwingTimer.ALL_BLINKERS.remove(self)
                            return

                    for i in range(0, len(self.swComponents)):
                        swComponent = self.swComponents[i][0]
                        fg = self.swComponents[i][1]
                        bg = self.swComponents[i][2]
                        boldON = self.swComponents[i][3]
                        boldOFF = self.swComponents[i][4]
                        swComponent.setForeground(fg if self.isForeground else bg)
                        swComponent.setFont(boldON if self.isForeground else boldOFF)

                    self.countBlinkLoops += 1
                    self.isForeground = not self.isForeground
                    if self.countBlinkLoops % 100 == 0:
                        if debug: myPrint("DB", "** Blinker (id: %s), has now iterated %s blink loops" %(self.uuid, self.countBlinkLoops))

            except: pass

    def hideUnideCollapsiblePanels(startingComponent, lSetVisible):
        # type: (JComponent, bool) -> None

        # if isinstance(startingComponent, JPanel) and startingComponent.getClientProperty("%s.collapsible" %(myModuleID)) is not None:
        if isinstance(startingComponent, JComponent) and startingComponent.getClientProperty("%s.collapsible" %(myModuleID)) == "true":
            startingComponent.setVisible(lSetVisible)

        for subComp in startingComponent.getComponents():
            hideUnideCollapsiblePanels(subComp, lSetVisible=lSetVisible)

    class MyFutureTxnsByAcctSearch(TxnSearch):
        def __init__(self, accts):
            # type: ([Account]) -> None
            self.accts = accts
            self.todayInt = DateUtil.getStrippedDateInt()

        def matchesAll(self):   return False

        def matches(self, _txn):
            if _txn.getDateInt() <= self.todayInt: return False
            if not _txn.getAccount() in self.accts: return False
            return True

    class CalculatedBalance:

        @staticmethod
        def getBalanceObjectForUUID(rowDict, uuid):
            for balObj in rowDict.values():
                if balObj.getUUID() == uuid:
                    return balObj
            return None

        @staticmethod
        def getBalanceObjectForRowNumber(rowDict, rowNumber):
            for balObj in rowDict.values():
                if balObj.getRowNumber() == rowNumber:
                    return balObj
            return None

        def __init__(self, rowName=None, currencyType=None, balance=None, extraRowTxt=None, uuid=None, rowNumber=-1, shouldBlink=False):
            self.lastUpdated = -1L                          # type: long
            self.uuid = uuid                                # type: unicode
            self.rowName = rowName                          # type: unicode
            self.currencyType = currencyType                # type: CurrencyType
            self.balance = balance                          # type: long
            self.extraRowTxt = extraRowTxt                  # type: unicode
            self.rowNumber = rowNumber                      # type: int            # Only set when needed - otherwise -1
            self.blink = shouldBlink                        # type: bool
            self.updateLastUpdated()

        def shouldBlink(self): return self.blink
        def setRowNumber(self, rowNumber): self.rowNumber = rowNumber
        def getRowNumber(self): return self.rowNumber
        def updateLastUpdated(self): self.lastUpdated = System.currentTimeMillis()
        def getLastUpdated(self): return self.lastUpdated
        def getUUID(self): return self.uuid
        def getRowName(self): return self.rowName
        def getBalance(self): return self.balance
        def setBalance(self, newBal): self.balance = newBal
        def getCurrencyType(self): return self.currencyType
        def getExtraRowTxt(self): return self.extraRowTxt
        def cloneBalanceObject(self):
            return CalculatedBalance(self.getRowName(), self.getCurrencyType(), self.getBalance(), self.getExtraRowTxt(), self.getUUID(), self.getRowNumber())
        def __str__(self):      return  "[uuid: '%s', row name: '%s', curr: '%s', balance: %s, extra row txt: '%s', rowNumber: %s]"\
                                        %(self.getUUID(), self.getRowName(), self.getCurrencyType(), self.getBalance(), self.getExtraRowTxt(), self.getRowNumber())
        def __repr__(self):     return self.__str__()
        def toString(self):     return self.__str__()

    class StoreAccountBalance:
        def __init__(self, _acct):
            # type: (Account) -> None
            self.acct = _acct                                                                               # type: Account
            self.curr = _acct.getCurrencyType()                                                             # type: CurrencyType
            self.currentBalance = _acct.getCurrentBalance()
            self.futureBalance = self.currentBalance
            self.futureBalances = []
            self.futureDateInts = []

        def getLowestFutureBalance(self):
            lowestBal = None
            for bal in self.futureBalances:
                if lowestBal is None or bal < lowestBal:
                    lowestBal = bal
            return lowestBal

        def getLowestFutureBalDate(self):
            lowestBal = self.getLowestFutureBalance()
            return None if lowestBal is None else self.futureDateInts[self.futureBalances.index(lowestBal)]

        def __repr__(self): return self.__str__()
        def toString(self): return self.__str__()
        def __str__(self):  return  "[Account: '%s', curr: '%s', c/balance: %s, cal f/balance: %s, lowest f/bal: %s, lowest f/date: %s, future balances: %s, future balance dates: %s"\
                                    %(self.acct.getFullAccountName(), self.curr,  self.currentBalance, self.futureBalance, self.getLowestFutureBalance(), self.getLowestFutureBalDate(), self.futureBalances, self.futureDateInts)

    def scaleIcon(_icon, scaleFactor):
        bufferedImage = BufferedImage(_icon.getIconWidth(), _icon.getIconHeight(), BufferedImage.TYPE_INT_ARGB)
        g = bufferedImage.createGraphics()
        _icon.paintIcon(None, g, 0, 0)
        g.dispose()
        return ImageIcon(bufferedImage.getScaledInstance(int(_icon.getIconWidth() * scaleFactor), int(_icon.getIconHeight() * scaleFactor), Image.SCALE_SMOOTH))

    def loadScaleColorImageToIcon(classLoader, iconPath, desiredSizeDim, finalIconColor):
        icon = None
        if classLoader is not None:
            try:
                stream = BufferedInputStream(classLoader.getResourceAsStream(iconPath))                                 # noqa
                if stream is not None:
                    image = ImageIO.read(stream)

                    if finalIconColor is not None:
                        image = invokeMethodByReflection(MDImages, "colorizedImage", [Image, Color], [image, finalIconColor])

                    if desiredSizeDim is not None:
                        scaledImage = BufferedImage(desiredSizeDim.width, desiredSizeDim.height, BufferedImage.TYPE_INT_ARGB)
                        g = scaledImage.createGraphics()
                        g.drawImage(image, 0, 0, desiredSizeDim.width, desiredSizeDim.height, None)
                        g.dispose()
                    else:
                        scaledImage = image

                    icon = ImageIcon(scaledImage)
                    stream.close()
                if debug: myPrint("DB", "Loaded image/icon: '%s' %s" %(iconPath, icon))
            except:
                myPrint("B", "@@ Failed to load image/icon: '%s'" %(iconPath))
                dump_sys_error_to_md_console_and_errorlog()
        return icon

    def loadDebugIcon(reloadDebugIcon=False):
        LBE = LowestBalancesExtension.getLBE()
        if LBE.debugIcon is None or reloadDebugIcon:
            # LBE.debugIcon = loadScaleColorImageToIcon(LBE.moneydanceExtensionLoader, "/debug16icon.png", None, LBE.moneydanceContext.getUI().getColors().secondaryTextFG)
            LBE.debugIcon = loadScaleColorImageToIcon(LBE.moneydanceExtensionLoader, "/debug16icon.png", None, getColorDarkGreen())

    ####################################################################################################################

    myPrint("B", "HomePageView widget / extension is now running...")

    class LowestBalancesExtension(FeatureModule, PreferencesListener):

        LBE = None

        @staticmethod
        def getLBE():
            if LowestBalancesExtension.LBE is not None: return LowestBalancesExtension.LBE
            with GlobalVars.EXTENSION_LOCK:
                if debug: myPrint("DB", "Creating and returning a new single instance of LowestBalancesExtension() using a lock....")
                LowestBalancesExtension.LBE = LowestBalancesExtension()
            return LowestBalancesExtension.LBE

        def __init__(self):  # This is the class' own initialise, just to set up variables
            self.myModuleID = myModuleID

            myPrint("B", "##########################################################################################")
            myPrint("B", "Extension: %s:%s (HomePageView widget) initialising...." %(self.myModuleID, GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME))
            myPrint("B", "##########################################################################################")

            if GlobalVars.specialDebug: myPrint("B", "@@ SPECIAL DEBUG enabled")

            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            self.NAB_LOCK = threading.Lock()
            self.NAB_TEMP_BALANCE_TABLE_LOCK = threading.Lock()

            self.moneydanceContext = MD_REF
            self.moneydanceExtensionObject = None

            self.decimal = None
            self.comma = None
            self.themeID = None

            if float(self.moneydanceContext.getBuild()) >= 3051:
                self.moneydanceExtensionLoader = moneydance_extension_loader  # This is the class loader for the whole extension
                myPrint("DB", "... Build is >= 3051 so using moneydance_extension_loader: %s" %(self.moneydanceExtensionLoader))
            else:
                self.moneydanceExtensionLoader = None

            self.alreadyClosed = False
            self.configSaved = True

            self.parametersLoaded = False
            self.listenersActive = False

            self.theFrame = None
            self.isUIavailable = False
            self.saveMyHomePageView = None

            self.saveActionListener = None

            self.saved_accountListUUIDs = None
            self.saved_expandedView = None

            self.accountList_ASL = None                                                                                 # type: AccountSelectList

            self.shouldDisableWidgetTitle = False
            self.shouldDisplayVisualUnderDots = True

            self.isPreview = None
            self.configPanelOpen = False

            self.swingWorkers_LOCK = threading.Lock()
            with self.swingWorkers_LOCK:
                self.swingWorkers = []

            self.debugIcon = None

            myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "##########################################################################################")

        def initialize(self, extension_context, extension_object):  # This is called by Moneydance after the run-time extension self installs itself
            myPrint("DB", "##########################################################################################")
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            # These extension_* variables are set by Moneydance before calling this script via the PY Interpreter
            self.moneydanceContext = extension_context  # This is the same as the moneydance variable and com.moneydance.apps.md.controller.Main
            self.moneydanceExtensionObject = extension_object  # This is com.moneydance.apps.md.controller.PythonExtension

            if debug:
                myPrint("DB", "meta_info.dict 'id' = %s" %(self.moneydanceExtensionObject.getIDStr()))
                myPrint("DB", "meta_info.dict 'module_build' = %s" %(self.moneydanceExtensionObject.getBuild()))
                myPrint("DB", "meta_info.dict 'desc' = %s" %(self.moneydanceExtensionObject.getDescription()))
                myPrint("DB", "script path: %s" %(self.moneydanceExtensionObject.getSourceFile()))

            self.preferencesUpdated()
            self.moneydanceContext.getPreferences().addListener(self)

            self.moneydanceContext.registerFeature(extension_object, "%s:customevent:showConfig" %(self.myModuleID), None, GlobalVars.DEFAULT_WIDGET_EXTENSION_NAME)
            myPrint("DB", "@@ Registered self as an Extension onto the Extension Menu @@")

            self.saveMyHomePageView = MyHomePageView.getHPV()

            if self.getMoneydanceUI():         # Only do this if the UI is loaded and dataset loaded...
                myPrint("B", "@@ Assuming an extension reinstall...")

                myPrint("B", "...Checking Home Screen Display Order Layout (lefties/righties/unused)")
                self.configureLeftiesRightiesAtInstall(self.saveMyHomePageView.getID())

                myPrint("B", "...Selecting Home Screen (on all main frames) in preparation to receive new widget....")
                selectAllHomeScreens()
                self.load_saved_parameters()

            else:
                # Runtime install... Let's just check we are visible.....
                self.configureLeftiesRightiesAtRuntime(self.saveMyHomePageView.getID())

            self.moneydanceContext.registerHomePageView(extension_object, self.saveMyHomePageView)
            myPrint("DB", "@@ Registered extension_object as containing a Home Page View (Summary Page / Dashboard object) @@")

            # If the UI is loaded, then probably a re-install... Refresh the UI with a new window....
            if self.getMoneydanceUI():         # Only do this if the UI is loaded and dataset loaded...
                myPrint("B", "@@ Assuming an extension reinstall. Reloading the Dashboard to refresh the view....")
                # moneydance_ui.selectAccountNewWindow(self.moneydanceContext.getCurrentAccountBook().getRootAccount())
                fireMDPreferencesUpdated()

            myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "##########################################################################################")

        ################################################################################################################
        def areSwingWorkersRunning(self):
            with self.swingWorkers_LOCK: return len(self.swingWorkers) > 0

        def listAllSwingWorkers(self):
            with self.swingWorkers_LOCK:
                if len(self.swingWorkers) < 1:
                    if debug: myPrint("DB", "No SwingWorkers found...")
                else:
                    for sw in self.swingWorkers:                                                                        # type: SwingWorker
                        if debug: myPrint("DB", "... Found SwingWorker:", sw)
                        if debug: myPrint("DB", "....... Status - isDone: %s, isCancelled: %s" %(sw.isDone(), sw.isCancelled()))
                    return

        def isWidgetRefreshRunning_NOLOCKFIRST(self):
            for sw in self.swingWorkers:                                                                                # type: SwingWorker
                if sw.isBuildHomePageWidgetSwingWorker():
                    # myPrint("DB", "isWidgetRefreshRunning() reports TRUE on SwingWorker:", sw)
                    return True
            # myPrint("DB", "isSimulateRunning() reports False")
            return False

        def isWidgetRefreshRunning_LOCKFIRST(self):
            with self.swingWorkers_LOCK: return self.isWidgetRefreshRunning_NOLOCKFIRST()

        def cancelSwingWorkers(self, lBuildHomePageWidgets=False):
            lCancelledAny = False
            for sw in self.swingWorkers:                                                                                # type: SwingWorker
                if (lBuildHomePageWidgets and sw.isBuildHomePageWidgetSwingWorker()):
                    if not sw.isCancelled() and not sw.isDone():
                        if debug: myPrint("DB", "cancelSwingWorkers() sending CANCEL COMMAND to running SwingWorker:", sw)
                        if not sw.cancel(True):
                            myPrint("DB", "@@ ALERT - SwingWorker.cancel(True) failed >> Moving on.....:", sw)
                        else:
                            lCancelledAny = True
                    else:
                        if debug: myPrint("DB", "cancelSwingWorkers() skipping cancellation of SwingWorker as isDone: %s isCancelled: %s ... SW:" %(sw.isDone(), sw.isCancelled()), sw)

            if not lCancelledAny: myPrint("DB", "cancelSwingWorkers() no SwingWorker(s) to cancel....")
            return lCancelledAny
        ################################################################################################################

        def preferencesUpdated(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            LBE = LowestBalancesExtension.getLBE()                                                                      # noqa
            prefs = self.moneydanceContext.getPreferences()

            self.decimal = prefs.getDecimalChar()
            self.comma = "." if self.decimal == "," else ","
            myPrint("DB", ".. Decimal set to '%s', Comma set to '%s'" %(self.decimal, self.comma))

            loadDebugIcon(reloadDebugIcon=True)
            myPrint("DB", ".. (Re)loaded Debug icon...")

            newThemeID = prefs.getSetting(GlobalVars.MD_PREFERENCE_KEY_CURRENT_THEME, ThemeInfo.DEFAULT_THEME_ID)
            if self.themeID and self.themeID != newThemeID:
                myPrint("DB", ".. >> Detected Preferences ThemeID change from '%s' to '%s'" %(self.themeID, newThemeID))
                myPrint("DB", ".. >> Moneydance has already called 'SwingUtilities.updateComponentTreeUI()' on all frames including mine....")

            else:
                myPrint("DB", ".. Preferences ThemeID is set to: '%s' (no change)" %(newThemeID))
            self.themeID = newThemeID

        class SaveSettingsRunnable(Runnable):
            def __init__(self): pass

            def run(self):
                LBE = LowestBalancesExtension.getLBE()
                LBE.saveSettings(lFromHomeScreen=True)

        def saveSettings(self, lFromHomeScreen=False):
            global debug        # Need this here as we set it below

            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            myPrint("B", "SAVING PARAMETERS HomePageView widget back to disk..")

            LBE = LowestBalancesExtension.getLBE()

            LBE.dumpSavedOptions()

            GlobalVars.extn_param_listAccountUUIDs_LBE = LBE.saved_accountListUUIDs
            GlobalVars.extn_param_expandedView_LBE = LBE.saved_expandedView

            if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}

            try:
                save_StuWareSoftSystems_parameters_to_file(myFile="%s_extension.dict" %(LBE.myModuleID))
            except:
                myPrint("B", "@@ Error saving parameters back to pickle file....?")
                dump_sys_error_to_md_console_and_errorlog()

            LBE.configSaved = True
            if lFromHomeScreen:
                MyHomePageView.getHPV().lastRefreshTriggerWasAccountModified = False
                LBE.executeRefresh()

        def configureLeftiesRightiesAtRuntime(self, widgetID):

            prefs = self.moneydanceContext.getPreferences()

            lefties = prefs.getVectorSetting(prefs.GUI_VIEW_LEFT, StreamVector())
            righties = prefs.getVectorSetting(prefs.GUI_VIEW_RIGHT, StreamVector())
            unused = prefs.getVectorSetting(prefs.GUI_VIEW_UNUSED, StreamVector())

            iCount = 0
            myPrint("DB", "Confirming WidgetID: %s exists in Summary Page layout (somewhere)" %(widgetID))
            for where_key, where in [[prefs.GUI_VIEW_LEFT, lefties], [prefs.GUI_VIEW_RIGHT, righties], [prefs.GUI_VIEW_UNUSED, unused]]:
                for iIndex in range(0, where.size()):
                    theID = where.get(iIndex)
                    if theID == widgetID:
                        myPrint("DB", ".. WidgetID: '%s' found in '%s' on row: %s" %(theID, where_key, iIndex+1))
                        iCount += 1

            if iCount > 0:
                myPrint("DB", "Found WidgetID: %s in Summary Page layout - so doing nothing..." %(widgetID))
                return

            myPrint("B", ".. Widget: '%s'... Adding to first position in '%s' (Summary Page top left)"  %(widgetID, prefs.GUI_VIEW_LEFT))

            if isinstance(lefties, StreamVector): pass

            lefties.add(0, widgetID)

            prefs.setSetting(prefs.GUI_VIEW_LEFT, lefties)

        def configureLeftiesRightiesAtInstall(self, widgetID):

            prefs = self.moneydanceContext.getPreferences()

            lefties = prefs.getVectorSetting(prefs.GUI_VIEW_LEFT, StreamVector())
            righties = prefs.getVectorSetting(prefs.GUI_VIEW_RIGHT, StreamVector())
            unused = prefs.getVectorSetting(prefs.GUI_VIEW_UNUSED, StreamVector())

            for where_key, where in [[prefs.GUI_VIEW_LEFT, lefties], [prefs.GUI_VIEW_RIGHT, righties], [prefs.GUI_VIEW_UNUSED, unused]]:
                myPrint("DB", "%s '%s': %s" %("Starting...", where_key, where))

            # Remove from unused as presumably user wants to install and use...
            for theID in [widgetID]:
                while theID in unused:
                    myPrint("DB", ".. Removing WidgetID: '%s' from '%s' layout area"  %(theID, prefs.GUI_VIEW_UNUSED))
                    unused.remove(theID)

            # Remove duplicates...
            for where_key, where in [[prefs.GUI_VIEW_LEFT, lefties], [prefs.GUI_VIEW_RIGHT, righties]]:
                for theID in [widgetID]:
                    while where.lastIndexOf(theID) > where.indexOf(theID):
                        myPrint("DB", ".. Removing duplicated WidgetID: '%s' from '%s' layout area (row: %s)"
                                %(theID, where_key, where.lastIndexOf(theID)+1))
                        where.remove(where.lastIndexOf(theID))

            # Make sure not in lefties and righties...
            if widgetID in lefties:

                while widgetID in righties:
                    myPrint("DB", ".. Removing WidgetID: '%s' from '%s' layout area as already in '%s'"  %(widgetID, prefs.GUI_VIEW_RIGHT, prefs.GUI_VIEW_LEFT))
                    righties.remove(widgetID)

                myPrint("DB", ".. Widget: '%s' configured in '%s'... Will not change Layout any further"  %(widgetID, prefs.GUI_VIEW_LEFT))

            if widgetID in righties:

                if righties[-1] != widgetID:
                    myPrint("DB", ".. Widget: '%s' already configured in '%s' (not last)... Will not change Layout further"  %(widgetID, prefs.GUI_VIEW_RIGHT))
                else:
                    myPrint("DB", ".. Widget: '%s'... Will remove from last position in '%s' (Summary Page bottom right)"  %(widgetID, prefs.GUI_VIEW_RIGHT))
                    righties.remove(widgetID)

            if widgetID not in lefties and widgetID not in righties:
                myPrint("B", ".. Widget: '%s'... Adding to first position in '%s' (Summary Page top left)"  %(widgetID, prefs.GUI_VIEW_LEFT))
                lefties.add(0, widgetID)

            prefs.setSetting(prefs.GUI_VIEW_LEFT,   lefties)
            prefs.setSetting(prefs.GUI_VIEW_RIGHT,  righties)
            prefs.setSetting(prefs.GUI_VIEW_UNUSED,    unused)

            for where_key, where in [[prefs.GUI_VIEW_LEFT, lefties], [prefs.GUI_VIEW_RIGHT, righties], [prefs.GUI_VIEW_UNUSED, unused]]:
                myPrint("DB", "%s '%s': %s" %("Ending...", where_key, where))


        class HideAction(AbstractAction):

            def __init__(self, theFrame):
                self.theFrame = theFrame

            def actionPerformed(self, event):                                                                           # noqa

                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, event))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                myPrint("DB", "Pushing Window Closing event....")
                self.theFrame.dispatchEvent(WindowEvent(self.theFrame, WindowEvent.WINDOW_CLOSING))

        def accountListDefault(self):  return ""
        def expandedViewDefault(self): return True

        # noinspection PyUnusedLocal
        def validateParameters(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            if not isinstance(self.saved_accountListUUIDs, basestring):
                myPrint("B", "@@ Invalid parameters 'saved_accountListUUIDs' - resetting....")
                self.saved_accountListUUIDs = ""

        def resetParameters(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            myPrint("B", "Initialising PARAMETERS....")

            self.saved_accountListUUIDs = self.accountListDefault()
            self.saved_expandedView = self.expandedViewDefault()

        def setDisableListeners(self, components, disabled):
            wasDisabled = None
            if not isinstance(components, list): components = [components]
            for comp in components:
                disableTxt = "DISABLING" if disabled else "ENABLING"
                # myPrint("DB", ".. %s Action & Focus listener(s) on: %s" %(disableTxt, comp.getName()))
                listeners = []
                try:
                    listeners.extend(comp.getActionListeners())
                    listeners.extend(comp.getFocusListeners())
                except: pass
                for compListener in listeners:
                    if hasattr(compListener, "disabled"):
                        myPrint("DB", ".... %s %s : %s..." %(disableTxt, comp.getName(), compListener))
                        if wasDisabled is None: wasDisabled = compListener.disabled
                        compListener.disabled = disabled
                    else:
                        # myPrint("DB", ".... 'disabled' field not found in %s : %s, skipping..." %(comp.getName(), compListener))
                        pass
            return False if wasDisabled is None else wasDisabled

        def resetAccountSelector(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            LBE = LowestBalancesExtension.getLBE()
            LBE.accountList_ASL = None              # This gets recreated again when the Frame next opens...
            myPrint("DB", "... wiped accountList_ASL...")

        def dumpSavedOptions(self):

            if not debug: return

            LBE = LowestBalancesExtension.getLBE()

            myPrint("B", "LBE: Analysis of saved options:")
            myPrint("B", "-------------------------------------------")
            myPrint("B", "saved_accountListUUIDs..:", LBE.saved_accountListUUIDs)
            myPrint("B", "saved_expandedView......:", LBE.saved_expandedView)

        class WindowListener(WindowAdapter):

            def __init__(self, theFrame, moduleID):
                self.theFrame = theFrame                                                                                # type: MyJFrame
                self.myModuleID = moduleID

            # noinspection PyMethodMayBeStatic
            def windowActivated(self, WindowEvent):                                                                     # noqa

                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                LBE = LowestBalancesExtension.getLBE()

                if LBE.configPanelOpen:
                    myPrint("DB", ".. Application's config panel is already open...")

                elif (LBE.moneydanceContext.getCurrentAccount() is not None
                      and LBE.moneydanceContext.getCurrentAccount().getBook() is not None):

                    myPrint("DB", ".. Application's config panel was not open already...")
                    LBE.configPanelOpen = True
                    LBE.build_main_frame(lRebuild=True)

                    LBE.saved_expandedView = LBE.expandedViewDefault()   # Force widget to be fully visible....

                else:
                    myPrint("B", "WARNING: getCurrentAccount() or 'Book' is None.. Perhaps MD is shutting down.. Will do nothing....")

                # The below is in case of a LaF/Theme change
                pnls = []
                subPnls = []
                for comp in LBE.theFrame.getContentPane().getComponents():
                    if isinstance(comp, JPanel) and comp.getClientProperty("%s.id" %(LBE.myModuleID)) == "controlPnl": pnls.append(comp)
                    for subComp in comp.getComponents():
                        if isinstance(subComp, JPanel) and subComp.getClientProperty("%s.id" %(LBE.myModuleID)) == "controlPnl": subPnls.append(comp)

                for comp in subPnls:
                    myPrint("DB", ".... invalidating: %s" %(comp))
                    comp.revalidate()
                    comp.repaint()

                for comp in pnls:
                    myPrint("DB", ".... invalidating: %s" %(comp))
                    comp.revalidate()
                    comp.repaint()

                myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")

            # noinspection PyMethodMayBeStatic
            def windowDeactivated(self, WindowEvent):                                                                   # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            # noinspection PyMethodMayBeStatic
            def windowDeiconified(self, WindowEvent):                                                                   # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            # noinspection PyMethodMayBeStatic
            def windowGainedFocus(self, WindowEvent):                                                                   # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            # noinspection PyMethodMayBeStatic
            def windowLostFocus(self, WindowEvent):                                                                     # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            # noinspection PyMethodMayBeStatic
            def windowIconified(self, WindowEvent):                                                                     # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            # noinspection PyMethodMayBeStatic
            def windowOpened(self, WindowEvent):                                                                        # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            # noinspection PyMethodMayBeStatic
            def windowStateChanged(self, WindowEvent):                                                                  # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            def terminate_script(self):
                myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                try:
                    # NOTE - .dispose() - The windowClosed event should set .isActiveInMoneydance False and .removeAppEventListener()
                    if not SwingUtilities.isEventDispatchThread():
                        SwingUtilities.invokeLater(GenericDisposeRunnable(self.theFrame))
                    else:
                        GenericDisposeRunnable(self.theFrame).run()
                except:
                    myPrint("B", "@@ Error. Final dispose of application failed....?")
                    dump_sys_error_to_md_console_and_errorlog()

            def windowClosing(self, WindowEvent):                                                                       # noqa

                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                LBE = LowestBalancesExtension.getLBE()
                HPV = MyHomePageView.getHPV()

                LBE.configPanelOpen = False

                if self.theFrame.isVisible():
                    myPrint("DB", ".. in windowClosing, but isVisible is True, let's trigger a widget refresh....")

                    LBE.cancelSwingWorkers(lBuildHomePageWidgets=True)

                    HPV.lastRefreshTriggerWasAccountModified = False

                    LBE.resetAccountSelector()
                    LBE.executeRefresh()
                else:
                    myPrint("DB", ".. in windowClosing, and isVisible is False, so will start termination....")
                    self.terminate_script()

            def windowClosed(self, WindowEvent):                                                                        # noqa

                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                LBE = LowestBalancesExtension.getLBE()

                LBE.configPanelOpen = False

                self.theFrame.isActiveInMoneydance = False

                if self.theFrame.MoneydanceAppListener is not None and not self.theFrame.MoneydanceAppListener.alreadyClosed:

                    try:
                        myPrint("DB", "\n@@@ Calling .unload() to deactivate extension and close the HomePageView... \n")
                        self.theFrame.MoneydanceAppListener.unload(True)
                    except:
                        myPrint("B", "@@@ FAILED to call .unload() to deactivate extension and close the HomePageView... \n")
                        dump_sys_error_to_md_console_and_errorlog()

                elif self.theFrame.MoneydanceAppListener is not None and self.theFrame.MoneydanceAppListener.alreadyClosed:
                    myPrint("DB", "Skipping .unload() as I'm assuming that's where I was called from (alreadyClosed was set)...")
                else:
                    myPrint("DB", "MoneydanceAppListener is None so Skipping .unload()..")

                self.theFrame.MoneydanceAppListener.alreadyClosed = True
                self.theFrame.MoneydanceAppListener = None

                cleanup_actions(self.theFrame, LBE.moneydanceContext)

        class MyRefreshRunnable(Runnable):

            def __init__(self): pass

            # noinspection PyMethodMayBeStatic
            def run(self):

                LBE = LowestBalancesExtension.getLBE()

                if debug: myPrint("DB", "Inside %s MyRefreshRunnable.... About call HomePageView .refresh()\n" %(LBE.myModuleID))
                if debug: myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                try:
                    LBE.saveMyHomePageView.refresh()
                    if debug: myPrint("DB", "Back from calling HomePageView .refresh() on %s...." %(LBE.myModuleID))
                except:
                    dump_sys_error_to_md_console_and_errorlog()
                    myPrint("B", "@@ ERROR calling .refresh() in HomePageView on %s....  :-< " %(LBE.myModuleID))
                return

        def executeRefresh(self):
            if debug: myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            if debug: myPrint("DB", "... About to call HomePageView .refresh() after updating accounts list via SwingUtilities.invokeLater(MyRefreshRunnable())")
            SwingUtilities.invokeLater(self.MyRefreshRunnable())

        class MyActionListener(AbstractAction):

            def __init__(self): self.disabled = False

            def actionPerformed(self, event):
                global debug    # Keep this here as we change debug further down

                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, event))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                myPrint("DB", "... Action Command:", event.getActionCommand(), "(event.source.name: %s)" %(event.getSource().getName()))

                if self.disabled:
                    myPrint("DB", "... disabled is set, skipping this.....")
                    return

                lShouldSaveParameters = False
                lShouldRefreshHomeScreenWidget = False

                LBE = LowestBalancesExtension.getLBE()

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("close_window".lower()):
                    myPrint("DB", "Close window requested - OK (doing nothing)")
                    lShouldRefreshHomeScreenWidget = True
                    lShouldSaveParameters = False
                    LBE.configPanelOpen = False
                    LBE.theFrame.setVisible(False)

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("debug".lower()):
                    debug = not debug
                    myPrint("B", "Debug setting changed to: %s" %(debug))

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("save_settings".lower()):
                    myPrint("DB", ".. saving settings...")
                    LBE.configSaved = False

                    # Save Selected Accounts
                    acctUUIDs = LBE.accountList_ASL.getSelectedAccountIds()
                    LBE.saved_accountListUUIDs = ",".join(acctUUIDs)
                    if debug: myPrint("DB", "Saved Account UUIDs: '%s'" %(LBE.saved_accountListUUIDs))
                    lShouldRefreshHomeScreenWidget = True
                    lShouldSaveParameters = True
                    LBE.configPanelOpen = False
                    LBE.theFrame.setVisible(False)

                # ######################################################################################################
                if lShouldRefreshHomeScreenWidget: LBE.executeRefresh()
                if lShouldSaveParameters: LBE.saveSettings()
                # ######################################################################################################

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        def load_saved_parameters(self, lForceReload=False):
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB", "... parametersLoaded: %s .getCurrentAccountBook(): %s" %(self.parametersLoaded, self.moneydanceContext.getCurrentAccountBook()))

            def load_all_defaults(LBE):
                # Loading will overwrite if saved, else pre-load defaults

                GlobalVars.extn_param_listAccountUUIDs_LBE = LBE.accountListDefault()
                GlobalVars.extn_param_expandedView_LBE = LBE.expandedViewDefault()

            with self.NAB_LOCK:
                if not self.parametersLoaded or lForceReload:
                    if self.moneydanceContext.getCurrentAccountBook() is None:
                        myPrint("DB", "... getCurrentAccountBook() reports None - skipping parameter load...")
                    else:
                        # self.configPanelOpen = False

                        self.resetParameters()

                        load_all_defaults(self)

                        get_StuWareSoftSystems_parameters_from_file(myFile="%s_extension.dict" %(self.myModuleID))

                        self.parametersLoaded = True

                        self.saved_accountListUUIDs = GlobalVars.extn_param_listAccountUUIDs_LBE
                        self.saved_expandedView = GlobalVars.extn_param_expandedView_LBE

                        self.validateParameters()
                        self.configSaved = True

                        self.dumpSavedOptions()

        # method getName() must exist as the interface demands it.....
        def getName(self): return GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME.title()

        # Not really used, but returns this value if print or repr is used on the class to retrieve its name....
        def __str__(self): return u"%s:%s (Extension)" %(self.myModuleID.capitalize(), GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME.title())
        def __repr__(self): return self.__str__()

        def isPreviewBuild(self):
            if self.moneydanceExtensionLoader is not None:
                try:
                    stream = self.moneydanceExtensionLoader.getResourceAsStream("/_PREVIEW_BUILD_")
                    if stream is not None:
                        myPrint("B", "@@ PREVIEW BUILD (%s) DETECTED @@" %(version_build))
                        stream.close()
                        return True
                except: pass
            return False

        def getSelectedAccountsFromStr(self, savedStr):
            # type: (str) -> [Account]
            LBE = self
            book = LBE.moneydanceContext.getCurrentAccountBook()
            if savedStr.strip() == "": return []
            newASL = LBE.getAccountSelectListComponent()
            GraphReportUtil.selectIndices(book, savedStr, newASL)
            selectedAccounts = LBE.getSelectedAccounts(newASL)
            if debug: myPrint("B", ".getSelectedAccountsFromStr: savedStr: '%s', returning selected accounts:" %(savedStr), selectedAccounts)
            return selectedAccounts

        def getSelectedAccounts(self, fromASL):
            # type: (AccountSelectList) -> [Account]
            LBE = self
            return AccountUtil.allMatchesForSearch(LBE.moneydanceContext.getCurrentAccountBook(), fromASL.getAccountFilter().getAcctSearch())

        def getAccountSelectListComponent(self):
            # type: () -> AccountSelectList
            LBE = self
            accountFilter = AccountFilter("all_accounts")
            accountFilter.addAllowedType(Account.AccountType.BANK)                                                      # noqa
            accountFilter.addAllowedType(Account.AccountType.CREDIT_CARD)                                               # noqa
            fullAccountList = FullAccountList(LBE.moneydanceContext.getCurrentAccountBook(), accountFilter, True)
            accountFilter.setFullList(fullAccountList)
            accountList_ASL = AccountSelectList(LBE.moneydanceContext.getUI())
            accountList_ASL.setAccountFilter(accountFilter)
            return accountList_ASL

        # def getAccountSelectListComponent(self):
        #     # type: () -> AccountSelectList
        #     LBE = self
        #     book = LBE.moneydanceContext.getCurrentAccountBook()
        #     accountFilter = AccountFilter("all_accounts")
        #     allowedTypes = [Account.AccountType.BANK, Account.AccountType.CREDIT_CARD]                                  # noqa
        #     for allowedType in allowedTypes: accountFilter.addAllowedType(allowedType)
        #     inactiveAccts = [acct for acct in AccountUtil.allMatchesForSearch(book, AcctFilter.ALL_ACCOUNTS_FILTER)
        #                      if (acct.getAccountType() in allowedTypes) and acct.getAccountOrParentIsInactive()]
        #     fullAccountList = FullAccountList(LBE.moneydanceContext.getCurrentAccountBook(), accountFilter, True)
        #     accountFilter.setFullList(fullAccountList)
        #     for acct in inactiveAccts: myPrint("B", "**", accountFilter.exclude(acct));
        #     accountList_ASL = AccountSelectList(LBE.moneydanceContext.getUI())
        #     accountList_ASL.setAccountFilter(accountFilter)
        #     return accountList_ASL

        def build_main_frame(self, lRebuild=False):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            if not lRebuild:
                if self.theFrame is not None:
                    myPrint("DB", ".. main JFrame is already built: %s - so exiting" %(self.theFrame))
                    return

            SetupMDColors.updateUI()

            class BuildMainFrameRunnable(Runnable):
                def __init__(self, _lRebuild):
                    self.lRebuild = _lRebuild

                def run(self):                                                                                          # noqa
                    global client_skylar_lowest_balances_frame_  # Keep this here as we set it below

                    LBE = LowestBalancesExtension.getLBE()
                    mdGUI = LBE.moneydanceContext.getUI()

                    ####################################################################################################
                    if LBE.theFrame is None:
                        myPrint("DB", "Creating main JFrame for application...")

                        # At startup, create dummy settings to build frame if nothing set.. Real settings will get loaded later
                        if LBE.saved_accountListUUIDs is None: LBE.resetParameters()

                        if LBE.isPreview is None:
                            myPrint("DB", "Checking for Preview build status...")
                            LBE.isPreview = LBE.isPreviewBuild()
                        titleExtraTxt = u"" if not LBE.isPreview else u"<PREVIEW BUILD: %s>" %(version_build)

                        # Called from getMoneydanceUI() so assume the Moneydance GUI is loaded...
                        # JFrame.setDefaultLookAndFeelDecorated(True)   # Note: Darcula Theme doesn't like this and seems to be OK without this statement...
                        client_skylar_lowest_balances_frame_ = MyJFrame(u"%s: Configure widget's settings   %s"
                                                               %(GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME.title(), titleExtraTxt))
                        LBE.theFrame = client_skylar_lowest_balances_frame_
                        LBE.theFrame.setName(u"%s_main" %(LBE.myModuleID))

                        LBE.theFrame.isActiveInMoneydance = True
                        LBE.theFrame.isRunTimeExtension = True

                        LBE.theFrame.MoneydanceAppListener = LBE
                        LBE.theFrame.HomePageViewObj = LBE.saveMyHomePageView

                        LBE.saveActionListener = LBE.MyActionListener()

                        if (not Platform.isOSX()):
                            LBE.moneydanceContext.getUI().getImages()
                            LBE.theFrame.setIconImage(MDImages.getImage(LBE.moneydanceContext.getUI().getMain().getSourceInformation().getIconResource()))

                        LBE.theFrame.setDefaultCloseOperation(WindowConstants.HIDE_ON_CLOSE)

                        # shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
                        shortcut = MoneydanceGUI.ACCELERATOR_MASK

                        LBE.theFrame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "hide-window")
                        LBE.theFrame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "hide-window")
                        LBE.theFrame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "hide-window")

                        LBE.theFrame.getRootPane().getActionMap().put("hide-window", LBE.HideAction(LBE.theFrame))

                        LBE.theFrame.addWindowListener(LBE.WindowListener(LBE.theFrame, LBE.myModuleID))

                        LBE.theFrame.setExtendedState(JFrame.NORMAL)
                        LBE.theFrame.setResizable(True)

                    elif not self.lRebuild:
                        myPrint("DB", "Frame was already set and not requesting rebuild.... So  will do nothing!")
                        return
                    ####################################################################################################

                    book = LowestBalancesExtension.getLBE().moneydanceContext.getCurrentAccountBook()

                    myPrint("DB", "Clearing and rebuilding frame contents....")
                    LBE.theFrame.getContentPane().removeAll()       # Wipe and rebuild the contents...

                    controlPnl = MyJPanel(GridBagLayout())
                    controlPnl.putClientProperty("%s.id" %(LBE.myModuleID), "controlPnl")

                    onRow = 1

                    LBE.accountList_ASL = LBE.getAccountSelectListComponent()
                    if isinstance(LBE.accountList_ASL, AccountSelectList): pass
                    GraphReportUtil.selectIndices(book, LBE.saved_accountListUUIDs, LBE.accountList_ASL)
                    LBE.accountList_ASL.layoutComponentUI()
                    controlPnl.add(LBE.accountList_ASL.getView(), GridC.getc(0, onRow).field().wxy(1.0, 1.0).fillboth())
                    myPrint("DB", "Created / loaded AccountListSelector...")

                    controlPnl.add(Box.createHorizontalStrut(750), GridC.getc(0, onRow))

                    onRow += 1

                    debug_JCB = MyJCheckBox(MDAction.makeNonKeyedAction(mdGUI, "Debug", "debug", LBE.saveActionListener))
                    debug_JCB.setSelected(debug)
                    myPrint("DB", "Set debug_JCB to: %s" %(debug))

                    saveParameters_JBTN = JButton(MDAction.makeNonKeyedAction(mdGUI, "Save Settings", "save_settings", LBE.saveActionListener))
                    abort_JBTN = JButton(MDAction.makeNonKeyedAction(mdGUI, "Close", "close_window", LBE.saveActionListener))

                    y = 0
                    saveAbort_JPNL = MyJPanel(GridBagLayout())
                    saveAbort_JPNL.add(debug_JCB, GridC.getc(y, 0));                                y+=1
                    saveAbort_JPNL.add(Box.createRigidArea(Dimension(50, 0)), GridC.getc(y, 0));    y+=1
                    saveAbort_JPNL.add(saveParameters_JBTN, GridC.getc(y, 0));                      y+=1
                    saveAbort_JPNL.add(abort_JBTN,          GridC.getc(y, 0));                      y+=1
                    controlPnl.add(saveAbort_JPNL, GridC.getc(0, onRow).east())
                    onRow += 1

                    # -----------------------------------------------------------------------------------
                    masterPnl = MyJPanel(BorderLayout())
                    masterPnl.putClientProperty("%s.id" %(LBE.myModuleID), "masterPnl")
                    masterPnl.setBorder(EmptyBorder(8, 8, 8, 8))
                    masterPnl.setBackground(mdGUI.getColors().defaultBackground)

                    masterPnl.add(controlPnl, BorderLayout.CENTER)

                    LBE.theFrame.getContentPane().setLayout(BorderLayout())
                    LBE.theFrame.getContentPane().add(masterPnl, BorderLayout.CENTER)

                    LBE.theFrame.pack()

                    if not lRebuild:
                        LBE.theFrame.setLocationRelativeTo(None)

                    LBE.theFrame.setVisible(self.lRebuild)
                    myPrint("DB", "Finished (re)building the main frame. lRebuild: %s" %(self.lRebuild))

            if not SwingUtilities.isEventDispatchThread():
                myPrint("DB", ".. build_main_frame() Not running within the EDT so calling via BuildMainFrameRunnable()...")
                SwingUtilities.invokeLater(BuildMainFrameRunnable(lRebuild))
            else:
                myPrint("DB", ".. build_main_frame() Already within the EDT so calling naked...")
                BuildMainFrameRunnable(lRebuild).run()


        # .invoke() is called when this extension is selected on the Extension Menu.
        # the eventString is set to the string set when the class self-installed itself via .registerFeature() - e.g. "showConfig"
        def invoke(self, eventString=""):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB", "Extension .invoke() received command: %s. Passing onto .handleEvent()" %(eventString))

            result = self.handle_event(eventString, True)

            myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return result

        def getMoneydanceUI(self):
            global debug    # global statement must be here as we can set debug here
            saveDebug = debug

            if GlobalVars.specialDebug:
                debug = True
                myPrint("B", "*** Switching on SPECIAL DEBUG here for .getMoneydanceUI() only......")

            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            if not self.isUIavailable:
                myPrint("DB", "Checking to see whether the Moneydance UI is loaded yet....")

                f_ui_result = getFieldByReflection(self.moneydanceContext, "ui")

                myPrint("DB", "** SPECIAL: f_ui_result:", f_ui_result)
                if f_ui_result is None or f_ui_result.firstMainFrame is None:
                    myPrint("DB", ".. Nope - the Moneydance UI is NOT yet loaded (fully)..... so exiting...")
                    debug = saveDebug
                    return False

                myPrint("DB", "** SPECIAL: book:", self.moneydanceContext.getCurrentAccountBook())
                if self.moneydanceContext.getCurrentAccountBook() is None:
                    myPrint("DB", ".. The UI is loaded, but the dataset is not yet loaded... so exiting ...")
                    debug = saveDebug
                    return False

                try:
                    # I'm calling this on firstMainFrame rather than just .getUI().setStatus() to confirm GUI is properly loaded.....
                    myPrint("DB", "SPECIAL: pre-calling .firstMainFrame.setStatus()")

                    # self.moneydanceContext.getUI().firstMainFrame.setStatus(">> StuWareSoftSystems - %s:%s runtime extension installing......." %(self.myModuleID.capitalize(),GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME.title()), -1.0)

                    genericSwingEDTRunner(False, False,
                                          self.moneydanceContext.getUI().firstMainFrame.setStatus,
                                          ">> StuWareSoftSystems - %s:%s runtime extension installing......." %(self.myModuleID.capitalize(), GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME.title()), -1.0)

                    myPrint("DB", "SPECIAL: post-calling .firstMainFrame.setStatus()")

                except:
                    dump_sys_error_to_md_console_and_errorlog()
                    myPrint("B", "@@ ERROR - failed using the UI..... will just exit for now...")
                    debug = saveDebug
                    return False

                myPrint("DB", "Success - the Moneydance UI is loaded.... Extension can execute properly now...!")

                # Have to do .getUI() etc stuff here (and not at startup) as UI not loaded then. As of 4069, is blocked by MD!
                myPrint("DB", "SPECIAL: pre-calling setDefaultFonts()")

                genericSwingEDTRunner(False, False, setDefaultFonts)

                myPrint("DB", "SPECIAL: post-calling setDefaultFonts()")

                try: GlobalVars.defaultPrintFontSize = eval("GlobalVars.CONTEXT.getUI().getFonts().print.getSize()")
                except: GlobalVars.defaultPrintFontSize = 12

                myPrint("DB", "SPECIAL: pre-calling build_main_frame()")
                self.build_main_frame()
                self.isUIavailable = True
                myPrint("DB", "SPECIAL: post-calling build_main_frame()")
            else:
                myPrint("DB", "..UI is available - returning True....")

            myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")

            debug = saveDebug
            return True


        def handle_event(self, appEvent, lPassedFromInvoke=False):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            if self.alreadyClosed:
                myPrint("DB", "....alreadyClosed (deactivated by user) but the listener is still here (MD EVENT %s CALLED).. - Ignoring and returning back to MD.... (restart to clear me out)..." %(appEvent))
                return

            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB", "Extension .handle_event() received command: %s (from .invoke() flag = %s)" %(appEvent, lPassedFromInvoke))

            if appEvent == AppEventManager.FILE_CLOSING or appEvent == AppEventManager.FILE_CLOSED:

                self.parametersLoaded = self.configPanelOpen = False

                if self.theFrame is not None and self.theFrame.isVisible():
                    myPrint("DB", "Requesting application JFrame to go invisible...")
                    SwingUtilities.invokeLater(GenericVisibleRunnable(self.theFrame, False))

                self.resetAccountSelector()

                if appEvent == AppEventManager.FILE_CLOSING:

                    with self.swingWorkers_LOCK:
                        myPrint("DB", "Cancelling any active SwingWorkers - all types....")
                        self.cancelSwingWorkers(lBuildHomePageWidgets=True)

                    myPrint("DB", "Closing all resources and listeners being used by View(s)")
                    MyHomePageView.getHPV().cleanupAsBookClosing()


            elif (appEvent == AppEventManager.FILE_OPENING):  # Precedes file opened
                myPrint("DB", "%s Dataset is opening... Internal list of SwingWorkers as follows...:" %(appEvent))
                self.listAllSwingWorkers()

            elif (appEvent == AppEventManager.FILE_OPENED):  # This is the key event when a file is opened

                if GlobalVars.specialDebug: myPrint("B", "'%s' >> SPECIAL DEBUG - Checking to see whether UI loaded and create application Frame" %(appEvent))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                class GetMoneydanceUIRunnable(Runnable):
                    def __init__(self, callingClass): self.callingClass = callingClass
                    def run(self):
                        cumulativeSleepTimeMS = 0
                        abortAfterSleepMS = (1000.0 * 15)     # Abort after 15 seconds of waiting..... Tough luck....!
                        sleepTimeMS = 500
                        if GlobalVars.specialDebug or debug: myPrint("B", "... GetMoneydanceUIRunnable sleeping for %sms..." %(sleepTimeMS))
                        Thread.sleep(sleepTimeMS)
                        if GlobalVars.specialDebug or debug: myPrint("B", "...... back from sleep....")
                        cumulativeSleepTimeMS += sleepTimeMS
                        while cumulativeSleepTimeMS < abortAfterSleepMS:
                            if self.callingClass.moneydanceContext.getCurrentAccountBook() is not None:
                                if isSyncTaskSyncing(checkMainTask=True, checkAttachmentsTask=False):
                                    if GlobalVars.specialDebug or debug:
                                        myPrint("B", "... Moneydance [main sync task] appears to be syncing... will wait %sms... (attachments sync task reports isSyncing: %s)"
                                                %(sleepTimeMS, isSyncTaskSyncing(checkMainTask=False, checkAttachmentsTask=True)))
                                    Thread.sleep(sleepTimeMS)
                                    cumulativeSleepTimeMS += sleepTimeMS
                                    continue
                                else:
                                    myPrint("B", "... Moneydance [main sync task] appears to be NOT syncing... so will continue to load UI... (attachments sync task reports isSyncing: %s)"
                                            %(isSyncTaskSyncing(checkMainTask=False, checkAttachmentsTask=True)))
                            break

                        if cumulativeSleepTimeMS >= abortAfterSleepMS: myPrint("B", "... WARNING: sleep/wait loop aborted (after %sms) waiting for MD sync to finish... Continuing anyway..." %(cumulativeSleepTimeMS))

                        if GlobalVars.specialDebug or debug: myPrint("B", "... GetMoneydanceUIRunnable calling getMoneydanceUI()...")
                        self.callingClass.getMoneydanceUI()  # Check to see if the UI & dataset are loaded.... If so, create the JFrame too...

                if GlobalVars.specialDebug or debug: myPrint("B", "... firing off call to getMoneydanceUI() via new thread (so-as not to hang MD)...")
                _t = Thread(GetMoneydanceUIRunnable(self), "NAB_GetMoneydanceUIRunnable".lower())
                _t.setDaemon(True)
                _t.start()

                # myPrint("DB", "%s Checking to see whether UI loaded and create application Frame" %(appEvent))
                # self.getMoneydanceUI()  # Check to see if the UI & dataset are loaded.... If so, create the JFrame too...

                myPrint("B", "... end of routines after receiving  '%s' command...." %(AppEventManager.FILE_OPENED))

            elif (appEvent.lower().startswith(("%s:customevent:showConfig" %(self.myModuleID)).lower())):
                myPrint("DB", "%s Config screen requested - I might show it if conditions are appropriate" %(appEvent))

                self.getMoneydanceUI()  # Check to see if the UI & dataset are loaded.... If so, create the JFrame too...

                if self.theFrame is not None and self.isUIavailable and self.theFrame.isActiveInMoneydance:
                    myPrint("DB", "... launching the config screen...")
                    SwingUtilities.invokeLater(GenericVisibleRunnable(self.theFrame, True, True))
                else:
                    myPrint("DB", "Sorry, conditions are not right to allow the GUI to load. Ignoring request....")
                    myPrint("DB", "self.theFrame: %s" %(self.theFrame))
                    myPrint("DB", "self.isUIavailable: %s" %(self.isUIavailable))
                    myPrint("DB", "self.theFrame.isActiveInMoneydance: %s" %(self.theFrame.isActiveInMoneydance))       # noqa

            elif (appEvent.lower().startswith(("%s:customevent:saveSettings" %(self.myModuleID)).lower())):
                myPrint("DB", "%s Save settings requested - I might trigger a save if conditions are appropriate" %(appEvent))

                self.getMoneydanceUI()  # Check to see if the UI & dataset are loaded.... If so, create the JFrame too...

                if self.theFrame is not None and self.theFrame.isActiveInMoneydance:
                    myPrint("DB", "Triggering saveSettings() via Runnable....")
                    SwingUtilities.invokeLater(self.SaveSettingsRunnable())

            else:
                myPrint("DB", "@@ Ignoring handle_event: %s (from .invoke() = %s) @@" %(appEvent,lPassedFromInvoke))

            if lPassedFromInvoke: return True

            return

        def cleanup(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            raise Exception("@@ ERROR: .cleanup() was called; but it was previously never called by anything!? (inform developer) **")

        def unload(self, lFromDispose=False):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            myPrint("B", "@@ Extension Unload called, either a uninstall or reinstall (or deactivate request)... Deactivate and unload...")

            LBE = LowestBalancesExtension.getLBE()

            self.theFrame.isActiveInMoneydance = False

            self.alreadyClosed = True

            if not lFromDispose:
                if not SwingUtilities.isEventDispatchThread():
                    SwingUtilities.invokeLater(GenericDisposeRunnable(self.theFrame))
                    myPrint("DB", "Pushed dispose() - via SwingUtilities.invokeLater() - Hopefully I will close to allow re-installation...\n")
                else:
                    GenericDisposeRunnable(self.theFrame).run()
                    myPrint("DB", "Called dispose() (direct as already on EDT) - Hopefully I will close to allow re-installation...\n")

            self.saveMyHomePageView.unload()
            myPrint("DB", "@@ Called HomePageView.unload()")

            try:
                myPrint("DB", "Removing myself from PreferenceListeners...")
                LBE.moneydanceContext.getPreferences().removeListener(self)
            except:
                myPrint("B", "@@ ERROR - failed to remove myself from PreferenceListeners?")

            self.moneydanceContext.getUI().setStatus(">> StuWareSoftSystems - thanks for using >> %s....... >> I am now unloaded...." %(GlobalVars.thisScriptName),0)

            myPrint("DB", "... Completed unload routines...")

    class SpecialJLinkLabel(JLinkLabel):
        def __init__(self, *args, **kwargs):
            tdfsc = kwargs.pop("tdfsc", None)                                                                           # type: TextDisplayForSwingConfig
            self.maxWidth = -1
            self.maxHeight = -1
            super(self.__class__, self).__init__(*args)
            self.LBE = LowestBalancesExtension.getLBE()
            self.md = self.LBE.moneydanceContext
            self.fonts = self.md.getUI().getFonts()
            self.fonts.updateMetricsIfNecessary(self.getGraphics())
            self.maxBaseline = self.fonts.defaultMetrics.getMaxDescent()
            self.underlineStroke = BasicStroke(1.0, BasicStroke.CAP_BUTT, BasicStroke.JOIN_BEVEL, 1.0, [1.0, 6.0], 1.0 if (self.getHorizontalAlignment() == JLabel.LEFT) else 0.0)
            self.underlineDots = self.LBE.shouldDisplayVisualUnderDots
            if tdfsc.isNoUnderlineDots(): self.underlineDots = False
            if tdfsc.isForceUnderlineDots(): self.underlineDots = True

        def setUnderlineDots(self, underlineDots): self.underlineDots = underlineDots

        def getPreferredSize(self):
            dim = super(self.__class__, self).getPreferredSize()
            self.maxWidth = Math.max(self.maxWidth, dim.width)
            dim.width = self.maxWidth
            self.maxHeight = Math.max(self.maxHeight, dim.height)
            dim.height = self.maxHeight
            return dim

        def paintComponent(self, g2d):
            if isinstance(self, JLabel): pass                                                                           # trick IDE into type checking
            if isinstance(g2d, Graphics2D): pass                                                                        # trick IDE into type checking

            super(self.__class__, self).paintComponent(g2d)
            if (not self.underlineDots or g2d is None): return

            # html_view = self.getClientProperty("html")
            # if html_view is None: return
            # if isinstance(html_view, View): pass

            isLeftAlign = (self.getHorizontalAlignment() == JLabel.LEFT)

            x = 0
            y = 0
            w = self.getWidth()
            h = self.getHeight()
            insets = self.getInsets()

            viewR = Rectangle(w, h)
            iconR = Rectangle()
            textR = Rectangle()

            clippedText = SwingUtilities.layoutCompoundLabel(
                self,
                g2d.getFontMetrics(),
                self.getText(),
                self.getIcon(),
                self.getVerticalAlignment(),
                self.getHorizontalAlignment(),
                self.getVerticalTextPosition(),
                self.getHorizontalTextPosition(),
                viewR,
                iconR,
                textR,
                self.getIconTextGap()
            )
            if clippedText is None: pass

            visibleTextWidth = int(textR.getWidth())

            baselineY = (y + self.getHeight() - self.maxBaseline - 1)

            if isLeftAlign:
                startDots = (visibleTextWidth + insets.left)
                lengthOfDots = (self.getWidth() - startDots)
            else:
                startDots = x
                lengthOfDots = (self.getWidth() - visibleTextWidth - insets.right)

            line = Path2D.Double()                                                                                      # noqa
            line.moveTo(w if isLeftAlign else 0.0, baselineY - insets.top)
            line.lineTo(0.0 if isLeftAlign else w, baselineY - insets.top)

            g2d.setColor(self.md.getUI().getColors().defaultTextForeground)
            g2d.clipRect(startDots, 0, lengthOfDots, h)
            g2d.setStroke(self.underlineStroke)
            g2d.draw(line)

    class TextDisplayForSwingConfig:
        WIDGET_ROW_BLANKROWNAME = "<#brn>"
        WIDGET_ROW_RIGHTROWNAME = "<#jr>"
        WIDGET_ROW_CENTERROWNAME = "<#jc>"
        WIDGET_ROW_REDROWNAME = "<#cre>"
        WIDGET_ROW_BLUEROWNAME = "<#cbl>"
        WIDGET_ROW_LIGHTGREYROWNAME = "<#cgr>"
        WIDGET_ROW_BOLDROWNAME = "<#fbo>"
        WIDGET_ROW_ITALICSROWNAME = "<#fit>"
        WIDGET_ROW_UNDERLINESROWNAME = "<#fun>"
        WIDGET_ROW_NO_UNDERLINE_DOTS = "<#nud>"
        WIDGET_ROW_FORCE_UNDERLINE_DOTS = "<#fud>"
        WIDGET_ROW_HTMLROWNAME = "<#html>"

        WIDGET_ROW_BLANKZEROVALUE = "<#bzv>"

        WIDGET_ROW_VALUE_RED = "<#cvre>"
        WIDGET_ROW_VALUE_BLUE = "<#cvbl>"
        WIDGET_ROW_VALUE_LIGHTGREY = "<#cvgr>"
        WIDGET_ROW_VALUE_BOLD = "<#fvbo>"
        WIDGET_ROW_VALUE_ITALICS = "<#fvit>"
        WIDGET_ROW_VALUE_UNDERLINE = "<#fvun>"

        def __init__(self, _rowText, _smallText, _smallColor=None, stripBigChars=True, stripSmallChars=True):
            self.ui = GlobalVars.CONTEXT.getUI()
            self.mono = self.ui.getFonts().mono
            self.originalRowText = _rowText
            self.originalSmallText = _smallText
            self.originalSmallColor = _smallColor
            self.originalStripBigChars = stripBigChars
            self.originalStripSmallChars = stripSmallChars
            self.swingComponentText = None
            self.color = None
            self.blankRow = False
            self.bold = False
            self.italics = False
            self.underline = False
            self.forceUnderlineDots = False
            self.noUnderlineDots = False
            self.html = False
            self.justification = JLabel.LEFT
            self.disableBlinkOnValue = False
            self.blankZero = False
            self.valueColor = None
            self.valueBold = False
            self.valueItalics = False
            self.valueUnderline = False

            if (self.__class__.WIDGET_ROW_BLUEROWNAME in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_BLUEROWNAME, "")
                self.color = getColorBlue()

            if (self.__class__.WIDGET_ROW_REDROWNAME in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_REDROWNAME, "")
                self.color = getColorRed()

            if (self.__class__.WIDGET_ROW_LIGHTGREYROWNAME in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_LIGHTGREYROWNAME, "")
                self.color = GlobalVars.CONTEXT.getUI().getColors().tertiaryTextFG

            if (self.__class__.WIDGET_ROW_BOLDROWNAME in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_BOLDROWNAME, "")
                self.bold = True

            if (self.__class__.WIDGET_ROW_ITALICSROWNAME in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_ITALICSROWNAME, "")
                self.italics = True

            if (self.__class__.WIDGET_ROW_UNDERLINESROWNAME in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_UNDERLINESROWNAME, "")
                self.underline = True

            if (self.__class__.WIDGET_ROW_HTMLROWNAME in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_HTMLROWNAME, "")
                self.html = True

            if (self.__class__.WIDGET_ROW_BLANKZEROVALUE in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_BLANKZEROVALUE, "")
                self.blankZero = True

            if (self.__class__.WIDGET_ROW_VALUE_BLUE in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_VALUE_BLUE, "")
                self.valueColor = getColorBlue()

            if (self.__class__.WIDGET_ROW_VALUE_RED in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_VALUE_RED, "")
                self.valueColor = getColorRed()

            if (self.__class__.WIDGET_ROW_VALUE_LIGHTGREY in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_VALUE_LIGHTGREY, "")
                self.valueColor = GlobalVars.CONTEXT.getUI().getColors().tertiaryTextFG

            if (self.__class__.WIDGET_ROW_VALUE_BOLD in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_VALUE_BOLD, "")
                self.valueBold = True

            if (self.__class__.WIDGET_ROW_VALUE_ITALICS in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_VALUE_ITALICS, "")
                self.valueItalics = True

            if (self.__class__.WIDGET_ROW_VALUE_UNDERLINE in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_VALUE_UNDERLINE, "")
                self.valueUnderline = True

            if (self.__class__.WIDGET_ROW_RIGHTROWNAME in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_RIGHTROWNAME, "")
                self.justification = JLabel.RIGHT

            if (self.__class__.WIDGET_ROW_CENTERROWNAME in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_CENTERROWNAME, "")
                self.justification = JLabel.CENTER

            if (self.__class__.WIDGET_ROW_BLANKROWNAME in _rowText):
                _rowText = ""
                self.blankRow = True

            if (self.__class__.WIDGET_ROW_NO_UNDERLINE_DOTS in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_NO_UNDERLINE_DOTS, "")
                self.noUnderlineDots = True
                self.forceUnderlineDots = False

            if (self.__class__.WIDGET_ROW_FORCE_UNDERLINE_DOTS in _rowText):
                _rowText = _rowText.replace(self.__class__.WIDGET_ROW_FORCE_UNDERLINE_DOTS, "")
                self.forceUnderlineDots = True
                self.noUnderlineDots = False

            if self.getJustification() == JLabel.CENTER:
                self.noUnderlineDots = True         # These don't work properly when centered....
                self.forceUnderlineDots = False

            if self.blankZero: self.disableBlinkOnValue = True

            self.swingComponentText = wrap_HTML_BIG_small(_rowText,
                                                          _smallText,
                                                          _smallColor=_smallColor,
                                                          stripBigChars=stripBigChars,
                                                          stripSmallChars=stripSmallChars,
                                                          _bigColor=self.color,
                                                          _italics=self.italics,
                                                          _bold=self.bold,
                                                          _underline=self.underline,
                                                          _html=self.html)

        def clone(self, tdfsc, prependBigText, appendBigText):
            newTDFSC = TextDisplayForSwingConfig(prependBigText + tdfsc.originalRowText + appendBigText,
                                                 tdfsc.originalSmallText,
                                                 _smallColor=tdfsc.originalSmallText,
                                                 stripBigChars=tdfsc.originalStripBigChars,
                                                 stripSmallChars=tdfsc.originalStripSmallChars)
            return newTDFSC

        def getSwingComponentText(self): return self.swingComponentText
        def getBlankZero(self): return self.blankZero
        def getJustification(self): return self.justification
        def isNoUnderlineDots(self): return self.noUnderlineDots
        def isForceUnderlineDots(self): return self.forceUnderlineDots
        def getDisableBlinkonValue(self): return self.disableBlinkOnValue
        def getValueBold(self): return self.valueBold
        def getValueItalics(self): return self.valueItalics
        def getValueUnderline(self): return self.valueUnderline

        def getValueColor(self, resultValue=-1):
            if self.valueColor is not None:
                return self.valueColor
            if resultValue < 0:
                return self.ui.getColors().negativeBalFG
            else:
                if "default" == ThemeInfo.themeForID(self.ui,
                        self.ui.getPreferences().getSetting(GlobalVars.MD_PREFERENCE_KEY_CURRENT_THEME, ThemeInfo.DEFAULT_THEME_ID)).getThemeID():
                    return self.ui.getColors().budgetHealthyColor
                else:
                    return self.ui.getColors().positiveBalFG

        def getValueFont(self, enhanceFormat=True):
            font = self.mono                                                                                            # type: Font
            if enhanceFormat:
                if self.getValueBold() or self.getValueItalics() or self.getValueUnderline():
                    fa = font.getAttributes()
                    if self.getValueBold(): fa.put(TextAttribute.WEIGHT, TextAttribute.WEIGHT_BOLD)
                    if self.getValueItalics(): fa.put(TextAttribute.POSTURE, TextAttribute.POSTURE_OBLIQUE)
                    if self.getValueUnderline(): fa.put(TextAttribute.UNDERLINE, TextAttribute.UNDERLINE_ON)
                    font = font.deriveFont(fa)
            return font

    class MyHomePageView(HomePageView, AccountListener, CurrencyListener):

        HPV = None

        @staticmethod
        def getHPV():
            if MyHomePageView.HPV is not None: return MyHomePageView.HPV
            with GlobalVars.EXTENSION_LOCK:
                if debug: myPrint("DB", "Creating and returning a new single instance of MyHomePageView() using extension lock....")
                MyHomePageView.HPV = MyHomePageView()
            return MyHomePageView.HPV

        def __init__(self):

            self.myModuleID = myModuleID

            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            self.generatedView = None       # Transitory object
            self.views = []                 # New for build 1020.. Enabling multi home screen views....
            self.viewPnlCounter = 0

            self.refresher = None
            self.lastRefreshTimeDelayMs = 2000      # was originally 10000
            self.lastRefreshTriggerWasAccountModified = False

            self.is_unloaded = False

            # my attempt to replicate Java's 'synchronized' statements
            self.HPV_LOCK = threading.Lock()

            # self.refresher = CollapsibleRefresher(self.GUIRunnable(self))
            self.refresher = MyCollapsibleRefresher(self.GUIRunnable())

        # noinspection PyMethodMayBeStatic
        def getID(self): return self.myModuleID

        # noinspection PyMethodMayBeStatic
        def __str__(self): return GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME.title()

        # noinspection PyMethodMayBeStatic
        def __repr__(self): return self.__str__()

        # noinspection PyMethodMayBeStatic
        def toString(self): return self.__str__()

        def currencyTableModified(self, currencyTable):                                                                 # noqa
            if debug: myPrint("DB", "In MyHomePageView.currencyTableModified()")
            self.listenerTriggeredAction()

        def accountModified(self, paramAccount):                                                                        # noqa
            if debug: myPrint("DB", "In MyHomePageView.accountModified()")
            self.listenerTriggeredAction(lFromAccountListener=True)

        def accountBalanceChanged(self, paramAccount):                                                                  # noqa
            if debug: myPrint("DB", "In MyHomePageView.accountBalanceChanged()")
            self.listenerTriggeredAction(lFromAccountListener=True)

        def accountDeleted(self, paramAccount):                                                                         # noqa
            if debug: myPrint("DB", "In MyHomePageView.accountDeleted()")
            if debug: myPrint("DB", "... ignoring....")

        def accountAdded(self, paramAccount):                                                                           # noqa
            if debug: myPrint("DB", "In MyHomePageView.accountAdded()")
            if debug: myPrint("DB", "... ignoring....")

        def listenerTriggeredAction(self, lFromAccountListener=False):
            if debug: myPrint("DB", ".listenerTriggeredAction(lFromAccountListener=%s) triggered" %(lFromAccountListener))
            if self.areAnyViewsActive(False):
                if debug: myPrint("DB", "... calling refresh(lFromAccountListener=%s)" %(lFromAccountListener))
                self.refresh(lFromAccountListener=lFromAccountListener)
            else:
                if debug: myPrint("DB", "... no views appear active... deactivating listeners...")
                # genericThreadRunner(True, self.deactivateListeners)
                self.deactivateListeners()

        def activateListeners(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            LBE = LowestBalancesExtension.getLBE()
            with LBE.NAB_LOCK:
                if not LBE.listenersActive:
                    myPrint("DB", ".. activateListeners().. Adding myself as (HomePageView) AccountBook & Currency listener(s)...")
                    book = LowestBalancesExtension.getLBE().moneydanceContext.getCurrentAccountBook()
                    myPrint("DB", "... activateListeners() detected book:", book)
                    book.addAccountListener(self)
                    book.getCurrencies().addCurrencyListener(self)
                else:
                    myPrint("DB", ".. activateListeners().. SKIPPING adding myself as (HomePageView) AccountBook & Currency listener(s) - as already active...")
                LBE.listenersActive = True

        def deactivateListeners(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            LBE = LowestBalancesExtension.getLBE()
            book = LBE.moneydanceContext.getCurrentAccountBook()
            with LBE.NAB_LOCK:
                if LBE.listenersActive:
                    myPrint("DB", ".. deactivateListeners().. Removing myself as (HomePageView) AccountBook & Currency listener(s)... Book:", book)
                    try:
                        book.removeAccountListener(self)
                    except:
                        e_type, exc_value, exc_traceback = sys.exc_info()                                               # noqa
                        myPrint("B", "@@ ERROR calling .removeAccountListener() on:", self)
                        myPrint("B", "Error:", exc_value)
                        myPrint("B", ".. will ignore and continue")

                    try:
                        book.getCurrencies().removeCurrencyListener(self)
                    except:
                        e_type, exc_value, exc_traceback = sys.exc_info()                                               # noqa
                        myPrint("B", "@@ ERROR calling .removeCurrencyListener() on:", self)
                        myPrint("B", "Error:", exc_value)
                        myPrint("B", ".. will ignore and continue")
                else:
                    myPrint("DB", ".. deactivateListeners().. SKIPPING removing myself as (HomePageView) AccountBook & Currency listener(s) - as already NOT active... Book:", book)

                LBE.listenersActive = False


        # The Runnable for CollapsibleRefresher() >> Doesn't really need to be a Runnable as .run() is called directly
        class GUIRunnable(Runnable):

            def __init__(self):
                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            # noinspection PyMethodMayBeStatic
            def run(self):
                myPrint("DB", "Inside GUIRunnable.... Calling .reallyRefresh()..")
                MyHomePageView.getHPV().reallyRefresh()

        def areAnyViewsActive(self, obtainLockFirst=True):
            with (self.HPV_LOCK if (obtainLockFirst) else NoneLock()):
                for _viewWR in self.views:
                    _view = _viewWR.get()
                    if isSwingComponentValid(_view): return True
                return False

        def cleanupDeadViews(self, obtainLockFirst=True):
            if debug: myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            with (self.HPV_LOCK if (obtainLockFirst) else NoneLock()):
                if debug: myPrint("DB", "... Pre-purge - Number of remembered Views(widgets): %s" %(len(self.views)))
                for i in reversed(range(0, len(self.views))):
                    _viewWR = self.views[i]
                    if isSwingComponentInvalid(_viewWR.get()):
                        if debug: myPrint("DB", "... Erasing (old) View(WIDGET) from my memory as seems to no longer exist (or is invalid):", _viewWR)
                        self.views.pop(i)
                if debug:
                    myPrint("B", "... Post-purge - Number of remembered Views(widgets): %s" %(len(self.views)))
                    for _viewWR in self.views:
                        _view = _viewWR.get()
                        if _view is not None:
                            myPrint("B", "...... keeping valid view: %s (valid: %s)" %(classPrinter(_view.getName(), _view), isSwingComponentValid(_view)))

        # Called by Moneydance. Must returns a (swing JComponent) GUI component that provides a view for the given data file.
        def getGUIView(self, book):
            if debug: myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            if debug: myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            if debug: myPrint("DB", "HomePageView: .getGUIView(%s)" %(book))

            LBE = LowestBalancesExtension.getLBE()

            if self.is_unloaded:
                if debug: myPrint("DB", "HomePageView is unloaded, so ignoring....")
                return None     # this hides the widget from the home screen

            if not LBE.parametersLoaded:
                if debug: myPrint("DB", "LOADING PARAMETERS..... (if not already set)....")
                LBE.load_saved_parameters()

            if debug: myPrint("DB", "... Setting up CreateViewPanelRunnable to create ViewPanel etc....")


            class CreateViewPanelRunnable(Runnable):

                def __init__(self): pass

                # noinspection PyMethodMayBeStatic
                def run(self):
                    HPV = MyHomePageView.getHPV()
                    if debug: myPrint("DB", "Inside CreateViewPanelRunnable().... Calling creating ViewPanel..")
                    HPV.generatedView = HPV.ViewPanel()

            with self.HPV_LOCK:
                if not SwingUtilities.isEventDispatchThread():
                    if debug: myPrint("DB", ".. Not running within the EDT so calling via CreateViewPanelRunnable()...")
                    SwingUtilities.invokeAndWait(CreateViewPanelRunnable())
                else:
                    if debug: myPrint("DB", ".. Already within the EDT so calling CreateViewPanelRunnable() naked...")
                    CreateViewPanelRunnable().run()

                self.viewPnlCounter += 1
                self.generatedView.setName("%s_ViewPanel_%s" %(self.myModuleID, str(self.viewPnlCounter)))
                if debug: myPrint("DB", "... Created ViewPanel: %s" %(classPrinter(self.generatedView.getName(), self.generatedView)))

                _returnView = self.generatedView
                self.generatedView = None
                self.views.append(WeakReference(_returnView))
                # self.refresh()    # Not sure this is needed as .setActive(True) should follow soon after...

                self.activateListeners()

                return _returnView

        def getLowestBalancesBuildView(self, swClass):
            if debug: myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            if debug: myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            HPV = self

            LBE = LowestBalancesExtension.getLBE()
            book = LBE.moneydanceContext.getCurrentAccountBook()

            lowestBalanceTable = []

            if HPV.is_unloaded:
                if debug: myPrint("DB", "HomePageView is unloaded, so ignoring & returning zero....")
                return lowestBalanceTable

            if book is None:
                if debug: myPrint("DB", "HomePageView: book is None - returning zero...")
                return lowestBalanceTable

            if debug: myPrint("DB", "HomePageView: (re)calculating lowest balances")

            if not swClass.isCancelled():
                lowestBalanceTable = MyHomePageView.calculateLowestBalances(book, swClass=swClass)

            return lowestBalanceTable

        @staticmethod
        def calculateLowestBalances(_book, swClass=None):                                                               # noqa
            if debug: myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")

            LBE = LowestBalancesExtension.getLBE()

            if _book is None or (swClass and swClass.isCancelled()): return []

            # baseCurr = _book.getCurrencies().getBaseType()

            _lowestBalanceTable = []                                                                                    # type: [CalculatedBalance]

            try:
                startTime = System.currentTimeMillis()

                accountsToShow = sorted(LBE.getSelectedAccountsFromStr(LBE.saved_accountListUUIDs), key=lambda sort_x: (sort_x.getAccountType(), sort_x.getFullAccountName().lower()))
                try: myPrint("DB", "accountsToShow table (length: %s): %s" %(len(accountsToShow), accountsToShow))
                except: pass

                if len(accountsToShow) < 1:
                    if debug: myPrint("DB", "...saved selected accounts is empty - creating dummy row...")

                    _lowestBalanceTable.append(CalculatedBalance(rowName=GlobalVars.DEFAULT_WIDGET_ROW_NOT_CONFIGURED,
                                                                 currencyType=None,
                                                                 balance=None,
                                                                 extraRowTxt="",
                                                                 uuid=None,
                                                                 rowNumber=1,
                                                                 shouldBlink=False))

                else:
                    ts = _book.getTransactionSet().getTransactions(MyFutureTxnsByAcctSearch(accountsToShow))
                    ts.sortWithComparator(TxnUtil.DATE_COMPARATOR)

                    accountBalances = {}
                    for acct in accountsToShow: accountBalances[acct] = StoreAccountBalance(acct)

                    if debug: myPrint("B", "Processing %s txns into Future Balances....." %(ts.getSize()))
                    todayInt = lastDateFoundInt = DateUtil.getStrippedDateInt()

                    for iTxn in range(0, ts.getSize()):
                        txn = ts.getTxnAt(iTxn)
                        if isinstance(txn, AbstractTxn): pass
                        txnDateInt = txn.getDateInt()
                        if  txnDateInt <= todayInt: raise Exception("LOGIC ERROR: txn date: %s is not future - today: %s ?!" %(txnDateInt, todayInt))
                        if  txnDateInt < lastDateFoundInt: raise Exception("LOGIC ERROR: txn date: %s is older than last date found: %s ?!" %(txnDateInt, lastDateFoundInt))
                        lastDateFoundInt = txnDateInt
                        txnAcct = txn.getAccount()
                        acctBal = accountBalances[txnAcct]
                        acctBal.futureBalance += txn.getValue()
                        acctBal.futureBalances.append(acctBal.futureBalance)
                        acctBal.futureDateInts.append(txnDateInt)

                    if debug:
                        myPrint("B", "------- Displaying future balances:")
                        for acct in accountBalances:
                            acctBal = accountBalances[acct]
                            myPrint("B", acctBal.toString())
                        myPrint("B", "-----------------------------------")

                    for iAccountLoop in range(len(accountsToShow)):
                        acct = accountsToShow[iAccountLoop]                                                                 # type: Account
                        acctBal = accountBalances[acct]

                        # cBal = acctBal.currentBalance
                        # fBal = acctBal.futureBalance
                        lowestFBal = acctBal.getLowestFutureBalance()
                        lowestBalDateInt = acctBal.getLowestFutureBalDate()
                        curr = acctBal.curr

                        if lowestBalDateInt is None:
                            lowestDateTxt = " <no future dated txns found>"
                        else:
                            lowestDateTxt = " <lowest date: %s>" %(convertStrippedIntDateFormattedText(lowestBalDateInt))

                        _lowestBalanceTable.append(CalculatedBalance(rowName=acct.getAccountName(),
                                                                     currencyType=curr,
                                                                     balance=(lowestFBal if lowestFBal is not None else acctBal.currentBalance),
                                                                     extraRowTxt=lowestDateTxt,
                                                                     uuid=None,
                                                                     rowNumber=iAccountLoop,
                                                                     shouldBlink=(lowestFBal is not None)))

                if debug:
                    if debug: myPrint("DB", "----------------")
                    for i in range(0, len(_lowestBalanceTable)):
                        balanceObj = _lowestBalanceTable[i]                                                             # type: CalculatedBalance
                        if balanceObj.getBalance() is None:
                            result = "<NONE>"
                        elif balanceObj.getBalance() == 0:
                            result = "<ZERO>"
                        else:
                            result = balanceObj.getBalance() / 100.0
                        if debug: myPrint("DB", ".. Row: %s - DEBUG >> Calculated a total (potentially mixed currency) total of %s (%s)" %(i+1, result, balanceObj.toString()))
                    if debug: myPrint("DB", "----------------")

                tookTime = System.currentTimeMillis() - startTime
                if debug or (tookTime >= 1000):
                    myPrint("B", ">> CALCULATE BALANCES TOOK: %s milliseconds (%s seconds)" %(tookTime, tookTime / 1000.0))

            except AttributeError as e:
                _lowestBalanceTable = []
                if not detectMDClosingError(e): raise

            except IllegalArgumentException:
                _lowestBalanceTable = []
                myPrint("B", "@@ ERROR - Probably on a multi-byte character.....")
                dump_sys_error_to_md_console_and_errorlog()
                raise

            return _lowestBalanceTable

        class BuildHomePageWidgetSwingWorker(SwingWorker):

            def __init__(self, pleaseWaitLabel, callingClass):
                self.pleaseWaitLabel = pleaseWaitLabel
                self.callingClass = callingClass
                self.lowestBalanceTable = None
                self.widgetOnPnlRow = 0
                self.widgetSeparatorsUsed = []

                LBE = LowestBalancesExtension.getLBE()
                with LBE.swingWorkers_LOCK:
                    LBE.swingWorkers.append(self)

            def isBuildHomePageWidgetSwingWorker(self):         return True

            def doInBackground(self):                                                                                   # Runs on a worker thread
                if debug: myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

                ct = Thread.currentThread()
                if "_extn_LBE" not in ct.getName(): ct.setName(u"%s_extn_LBE" %(ct.getName()))

                result = False

                try:
                    HPV = MyHomePageView.getHPV()

                    if HPV.lastRefreshTriggerWasAccountModified:
                        if debug: myPrint("DB", "** BuildHomePageWidgetSwingWorker.doInBackground() will now sleep for %s seconds as last trigger for .reallyRefresh() was an Account Listener... (unless I get superceded and cancelled)"
                                %(HPV.lastRefreshTimeDelayMs / 1000.0))
                        Thread.sleep(HPV.lastRefreshTimeDelayMs)
                        if debug: myPrint("DB", ".. >> Back from my sleep.... Now will reallyRefresh....!")

                    self.lowestBalanceTable = self.callingClass.getLowestBalancesBuildView(self)

                    if self.lowestBalanceTable is not None and len(self.lowestBalanceTable) > 0:
                        result = True

                except AttributeError as e:
                    if not detectMDClosingError(e): raise

                except InterruptedException:
                    if debug: myPrint("DB", "@@ BuildHomePageWidgetSwingWorker InterruptedException - aborting...")

                except CancellationException:
                    if debug: myPrint("DB", "@@ BuildHomePageWidgetSwingWorker CancellationException - aborting...")

                except:
                    myPrint("B", "@@ ERROR Detected in BuildHomePageWidgetSwingWorker running: getLowestBalancesBuildView() inside ViewPanel")
                    dump_sys_error_to_md_console_and_errorlog()

                return result

            def addRowSeparator(self, theView):
                countConsecutive = 0
                for i in [1, 2]:
                    if (self.widgetOnPnlRow - i) in self.widgetSeparatorsUsed:
                        countConsecutive += 1
                if countConsecutive >= 2: return
                theView.listPanel.add(JSeparator(), GridC.getc().xy(0, self.widgetOnPnlRow).wx(1.0).fillx().pady(2).leftInset(15).rightInset(15).colspan(2))
                self.widgetSeparatorsUsed.append(self.widgetOnPnlRow)
                self.widgetOnPnlRow += 1

            def done(self):  # Executes on the EDT
                if debug: myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

                LBE = LowestBalancesExtension.getLBE()
                HPV = MyHomePageView.getHPV()
                md = LBE.moneydanceContext

                with HPV.HPV_LOCK:
                    blinkers = []
                    thisViewsBlinkers = []                                                                              # noqa

                    try:
                        result = self.get()  # wait for process to finish
                        if debug: myPrint("DB", "..done() reports: %s" %(result))

                        for _viewWR in HPV.views:
                            _view = _viewWR.get()
                            if _view is None:
                                if debug: myPrint("DB", "... skipping View(WIDGET) as no longer exists (or is invalid):", _viewWR)
                                continue

                            self.widgetOnPnlRow = 0
                            self.widgetSeparatorsUsed = []
                            thisViewsBlinkers = []

                            if debug:
                                mfRef = SwingUtilities.getWindowAncestor(_view)
                                mfName = "None" if (mfRef is None) else classPrinter(getSwingObjectProxyName(mfRef), mfRef)
                                myPrint("B", ".. Rebuilding the widget view panel... view: %s, main frame: %s (valid: %s)"
                                        %(classPrinter(_view.getName(), _view), mfName, isSwingComponentValid(_view)))
                                del mfRef, mfName

                            _view.setVisible(False)
                            _view.listPanel.removeAll()

                            if LBE.shouldDisableWidgetTitle:
                                if _view.headerPanel in _view.getComponents():
                                    _view.remove(_view.headerPanel)
                            else:
                                if _view.headerPanel not in _view.getComponents():
                                    _view.add(_view.headerPanel, GridC.getc().xy(0, 0).wx(1.0).fillx())

                            altFG = md.getUI().getColors().tertiaryTextFG

                            if result and not LBE.saved_expandedView: pass
                            elif result:

                                baseCurr = md.getCurrentAccountBook().getCurrencies().getBaseType()

                                if not LBE.configSaved:
                                    rowText = " ** CLICK TO SAVE SETTINGS **"
                                    nameLabel = JLinkLabel(rowText, "saveSettings", JLabel.LEFT)
                                    nameLabel.setForeground(md.getUI().getColors().negativeBalFG)                       # noqa
                                    nameLabel.setDrawUnderline(False)
                                    nameLabel.setBorder(_view.nameBorder)                                               # noqa

                                    _view.listPanel.add(nameLabel, GridC.getc().xy(0, self.widgetOnPnlRow).wx(1.0).filly().west().pady(2))
                                    self.widgetOnPnlRow += 1

                                    nameLabel.addLinkListener(_view)
                                    thisViewsBlinkers.append(nameLabel)

                                    # self.addRowSeparator(_view)

                                for i in range(0, len(self.lowestBalanceTable)):

                                    onRow = i + 1
                                    balanceObj = self.lowestBalanceTable[i]                                             # type: CalculatedBalance

                                    lowestBalance = balanceObj.getBalance()

                                    # self.addRowSeparator(_view)

                                    showCurrText = ""
                                    if balanceObj.getCurrencyType() is not baseCurr:
                                        if balanceObj.getCurrencyType() is None:
                                            showCurrText = ""
                                        else:
                                            showCurrText = " (%s)" %(balanceObj.getCurrencyType().getIDString())

                                    # uuidTxt = "" if not debug else " (uuid: %s)" %(balanceObj.getUUID())
                                    uuidTxt = ""

                                    # tdfsc = TextDisplayForSwingConfig(balanceObj.getRowName(), balanceObj.getExtraRowTxt() + showCurrText + uuidTxt, altFG)
                                    tdfsc = TextDisplayForSwingConfig(balanceObj.getRowName(), balanceObj.getExtraRowTxt() + showCurrText + uuidTxt, GlobalVars.CONTEXT.getUI().getColors().defaultTextForeground)
                                    nameLabel = SpecialJLinkLabel(tdfsc.getSwingComponentText(), "showConfig?%s" %(str(onRow)), tdfsc.getJustification(), tdfsc=tdfsc)

                                    # NOTE: Leave "  " to avoid the row height collapsing.....
                                    if lowestBalance is None:
                                        netTotalLbl = SpecialJLinkLabel(" " if (tdfsc.getBlankZero()) else GlobalVars.DEFAULT_WIDGET_ROW_NOT_CONFIGURED.lower(),
                                                                        "showConfig?%s" %(str(onRow)),
                                                                        JLabel.RIGHT,
                                                                        tdfsc=tdfsc)
                                        netTotalLbl.setFont(tdfsc.getValueFont(False))

                                    else:

                                        # NOTE: Leave "  " to avoid the row height collapsing.....
                                        if (lowestBalance == 0 and tdfsc.getBlankZero()):
                                            theFormattedValue = "  "
                                        else:
                                            fancy = True
                                            theFormattedValue = formatFancy(balanceObj.getCurrencyType(),
                                                                            lowestBalance,
                                                                            LBE.decimal,
                                                                            fancy=fancy,
                                                                            indianFormat=False,
                                                                            includeDecimals=False,
                                                                            roundingTarget=0.0)

                                        netTotalLbl = SpecialJLinkLabel(theFormattedValue, "showConfig?%s" %(onRow), JLabel.RIGHT, tdfsc=tdfsc)
                                        netTotalLbl.setFont(tdfsc.getValueFont())
                                        netTotalLbl.setForeground(tdfsc.getValueColor(lowestBalance))

                                    nameLabel.setBorder(_view.nameBorder)                                               # noqa
                                    netTotalLbl.setBorder(_view.amountBorder)                                           # noqa

                                    nameLabel.setDrawUnderline(False)
                                    netTotalLbl.setDrawUnderline(False)

                                    # _view.listPanel.add(Box.createVerticalStrut(23), GridC.getc().xy(0, self.widgetOnPnlRow))
                                    _view.listPanel.add(nameLabel, GridC.getc().xy(0, self.widgetOnPnlRow).wx(1.0).fillboth().pady(2))
                                    _view.listPanel.add(netTotalLbl, GridC.getc().xy(1, self.widgetOnPnlRow).fillboth().pady(2))
                                    self.widgetOnPnlRow += 1

                                    nameLabel.addLinkListener(_view)
                                    netTotalLbl.addLinkListener(_view)

                                    if balanceObj.shouldBlink() and not tdfsc.getDisableBlinkonValue(): thisViewsBlinkers.append(netTotalLbl)

                                    # self.addRowSeparator(_view)

                                blinkers.extend(thisViewsBlinkers)

                                if LBE.isPreview is None:
                                    if debug: myPrint("DB", "Checking for Preview build status...")
                                    LBE.isPreview = LBE.isPreviewBuild()

                                if LBE.isPreview or debug:
                                    self.widgetOnPnlRow += 1
                                    previewText = "" if not LBE.isPreview else "*PREVIEW(%s)* " %(version_build)
                                    debugText = "" if not debug else "*DEBUG* "
                                    combinedTxt = ""
                                    _countTxtAdded = 0
                                    for _txt in [previewText, debugText]:
                                        combinedTxt += _txt
                                        if _txt != "": _countTxtAdded += 1
                                        if _countTxtAdded >= 3:
                                            combinedTxt += "<BR>"
                                            _countTxtAdded = 0
                                    rowText = wrap_HTML_BIG_small("", combinedTxt, altFG, stripSmallChars=False)
                                    nameLabel = MyJLabel(rowText, JLabel.LEFT)
                                    nameLabel.setBorder(_view.nameBorder)
                                    _view.listPanel.add(nameLabel, GridC.getc().xy(0, self.widgetOnPnlRow).wx(1.0).fillboth().west().pady(2))
                                    self.widgetOnPnlRow += 1

                            else:
                                myPrint("B", "@@ ERROR BuildHomePageWidgetSwingWorker:done().get() reported FALSE >> Either crashed or MD is closing (the 'book')...")

                                _view.setVisible(False)
                                _view.listPanel.removeAll()
                                self.widgetOnPnlRow = 0

                                rowText = "%s ERROR DETECTED? (review console)" %(GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME)
                                nameLabel = JLinkLabel(rowText, "showConsole", JLabel.LEFT)
                                nameLabel.setDrawUnderline(False)
                                nameLabel.setForeground(md.getUI().getColors().errorMessageForeground)                  # noqa
                                nameLabel.setBorder(_view.nameBorder)                                                   # noqa
                                nameLabel.addLinkListener(_view)
                                _view.listPanel.add(nameLabel, GridC.getc().xy(0, self.widgetOnPnlRow).wx(1.0).fillboth().west().pady(2))
                                blinkers.append(nameLabel)

                        self.lowestBalanceTable = None

                    except AttributeError as e:
                        if detectMDClosingError(e):
                            return
                        else:
                            raise

                    except InterruptedException:
                        if debug: myPrint("DB", "@@ BuildHomePageWidgetSwingWorker InterruptedException - aborting...")

                    except CancellationException:
                        if debug: myPrint("DB", "@@ BuildHomePageWidgetSwingWorker CancellationException - aborting...")

                    except:

                        myPrint("B", "@@ ERROR BuildHomePageWidgetSwingWorker ERROR Detected building the viewPanel(s)..")
                        dump_sys_error_to_md_console_and_errorlog()

                        for _viewWR in HPV.views:
                            _view = _viewWR.get()
                            if _view is None: continue

                            _view.setVisible(False)
                            _view.listPanel.removeAll()
                            self.widgetOnPnlRow = 0

                            rowText = "%s ERROR DETECTED! (review console)" %(GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME)
                            nameLabel = MyJLabel(rowText, JLabel.LEFT)
                            nameLabel.setForeground(md.getUI().getColors().errorMessageForeground)
                            nameLabel.setBorder(_view.nameBorder)
                            _view.listPanel.add(nameLabel, GridC.getc().xy(0, self.widgetOnPnlRow).wx(1.0).fillboth().west().pady(2))
                            blinkers.append(nameLabel)

                    finally:
                        LBE = LowestBalancesExtension.getLBE()
                        with LBE.swingWorkers_LOCK:
                            if self in LBE.swingWorkers:
                                LBE.swingWorkers.remove(self)
                            else:
                                if debug: myPrint("DB", "@@ ALERT: I did not find myself within swingworkers list, so doing nothing...:", self)

                    for _viewWR in HPV.views:
                        _view = _viewWR.get()
                        if _view is None: continue

                        _view.setVisible(True)  # Already on the Swing Event Dispatch Thread (EDT) so can just call directly....
                        _view.invalidate()
                        parent = _view.getParent()
                        while parent is not None:
                            parent.repaint()
                            parent.validate()
                            parent = parent.getParent()

                    if len(blinkers) > 0: BlinkSwingTimer(1200, blinkers, flipColor=(GlobalVars.CONTEXT.getUI().getColors().defaultTextForeground), flipBold=True).start()

        class ViewPanel(JPanel, JLinkListener, MouseListener):

            def linkActivated(self, link, event):                                                                       # noqa
                myPrint("DB", "In ViewPanel.linkActivated()")
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                myPrint("DB", "... link: %s" %(link))

                LBE = LowestBalancesExtension.getLBE()
                HPV = MyHomePageView.getHPV()

                if isinstance(link, basestring):
                    if (link.lower().startswith("showConfig".lower())):
                        myPrint("DB", ".. calling .showURL() to call up %s panel" %(link))
                        LBE.moneydanceContext.showURL("moneydance:fmodule:%s:%s:customevent:%s" %(HPV.myModuleID,HPV.myModuleID,link))

                    if (link.lower().startswith("saveSettings".lower())):
                        myPrint("DB", ".. calling .showURL() to trigger a save of settings ('%s')..." %(link))
                        LBE.moneydanceContext.showURL("moneydance:fmodule:%s:%s:customevent:%s" %(HPV.myModuleID,HPV.myModuleID,link))

                    if (link.lower().startswith("showConsole".lower())):
                        myPrint("DB", ".. calling .showURL() to trigger Help>Console Window ('%s')..." %(link))
                        LBE.moneydanceContext.showURL("moneydance:fmodule:%s:%s:customevent:%s" %(HPV.myModuleID,HPV.myModuleID,link))

            def mousePressed(self, evt):
                myPrint("DB", "In mousePressed. Event:", evt, evt.getSource())

                if evt.getSource() is self.collapsableIconLbl:
                    myPrint("DB", "mousePressed: detected collapsableIconLbl... going for toggle collapse....")
                    self.toggleExpandCollapse()

            def mouseClicked(self, evt): pass
            def mouseReleased(self, evt): pass
            def mouseExited(self, evt): pass
            def mouseEntered(self, evt): pass

            def toggleExpandCollapse(self):
                LBE = LowestBalancesExtension.getLBE()
                if not LBE.configSaved:
                    myPrint("B", "Alert - Blocking expand/collapse widget as (changed) parameters not yet saved...!")
                elif LBE.configPanelOpen:
                    myPrint("B", "Alert - Blocking expand/collapse widget as widget config gui is open...!")
                else:
                    LBE.saved_expandedView = not LBE.saved_expandedView

                    SwingUtilities.invokeLater(LBE.SaveSettingsRunnable())
                    MyHomePageView.getHPV().refresher.enqueueRefresh()

            def __init__(self):

                super(self.__class__, self).__init__()

                if debug: myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                if debug: myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                LBE = LowestBalancesExtension.getLBE()

                self.nameBorder = EmptyBorder(3, 14, 3, 0)
                self.amountBorder = EmptyBorder(3, 0, 3, 14)

                gridbag = GridBagLayout()
                self.setLayout(gridbag)

                self.setOpaque(False)
                self.setBorder(MoneydanceLAF.homePageBorder)

                self.headerPanel = JPanel(GridBagLayout())
                self.headerPanel.setOpaque(False)

                self.headerLabel = JLinkLabel(" ", "showConfig", JLabel.LEFT)
                self.headerLabel.setDrawUnderline(False)
                self.headerLabel.setFont(LBE.moneydanceContext.getUI().getFonts().header)                               # noqa
                # self.headerLabel.setBorder(self.nameBorder)                                                           # noqa

                self.balTypeLabel = JLinkLabel("", "showConfig", JLabel.RIGHT)
                self.balTypeLabel.setFont(LBE.moneydanceContext.getUI().getFonts().defaultText)                         # noqa
                self.balTypeLabel.setBorder(self.amountBorder)                                                          # noqa
                self.balTypeLabel.setDrawUnderline(False)

                self.headerLabel.addLinkListener(self)
                self.balTypeLabel.addLinkListener(self)

                self.titlePnl = JPanel(GridBagLayout())
                self.titlePnl.setOpaque(False)

                self.collapsableIconLbl = JLabel("")
                self.collapsableIconLbl.setFont(LBE.moneydanceContext.getUI().getFonts().header)
                self.collapsableIconLbl.setBorder(self.nameBorder)

                self.debugIconLbl = JLabel("")
                self.debugIconLbl.setBorder(EmptyBorder(0, 2, 0, 2))

                lblCol = 0
                self.titlePnl.add(self.collapsableIconLbl, GridC.getc().xy(lblCol, 0).wx(0.1).east());  lblCol += 1
                self.titlePnl.add(self.debugIconLbl, GridC.getc().xy(lblCol, 0).wx(0.1).center());      lblCol += 1
                self.titlePnl.add(self.headerLabel, GridC.getc().xy(lblCol, 0).wx(9.0).fillx().west()); lblCol += 1

                self.headerPanel.add(self.titlePnl, GridC.getc().xy(0, 0).wx(1.0).fillx().east())
                self.headerPanel.add(self.balTypeLabel, GridC.getc().xy(1, 0))

                if LBE.shouldDisableWidgetTitle:
                    if debug: myPrint("DB", "Skipping adding the Widget's title to the ViewPanel")
                else:
                    self.add(self.headerPanel, GridC.getc().xy(0, 0).wx(1.0).fillx())

                self.listPanel = JPanel(gridbag)        # Don't need to use MyJPanel as LaF / Theme change calls a refresh/rebuild of this anyway
                self.add(self.listPanel, GridC.getc(0, 1).wx(1.0).fillboth())
                self.add(Box.createVerticalStrut(2), GridC.getc(0, 2).wy(1.0))
                self.listPanel.setOpaque(False)

                self.collapsableIconLbl.addMouseListener(self)

            def updateUI(self):
                if debug: myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                super(self.__class__, self).updateUI()


        # Sets the view as active or inactive. When not active, a view should not have any registered listeners
        # with other parts of the program. This will be called when an view is added to the home page,
        # or the home page is refreshed after not being visible for a while.

        def setActive(self, active):
            if debug: myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            if debug: myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            if debug: myPrint("DB", "HomePageView: .setActive(%s)" %(active))

            if self.is_unloaded:
                if debug: myPrint("DB", "HomePageView is unloaded, so ignoring....")
                return

            if not active:
                if debug: myPrint("DB", "... setActive() (as of build 1020) doing nothing...")
            else:
                self.refresh()

        # Forces a refresh of the information in the view. For example, this is called after the preferences are updated.
        def refresh(self, lFromAccountListener=False):                                                                  # noqa
            if debug: myPrint("DB", "In MyHomePageView: %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            if debug: myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            if self.is_unloaded:
                if debug: myPrint("DB", "HomePageView is unloaded, so ignoring....")
                return

            HPV = self

            if debug: myPrint("DB", ".. lastRefreshTriggerWasAccountModified: %s" %(HPV.lastRefreshTriggerWasAccountModified))
            HPV.lastRefreshTriggerWasAccountModified = lFromAccountListener

            if LowestBalancesExtension.getLBE().moneydanceContext.getUI().getSuspendRefreshes():
                if debug: myPrint("DB", "... .getUI().getSuspendRefreshes() is True so ignoring...")
                return

            if self.refresher is not None:
                if debug: myPrint("DB", "... calling refresher.enqueueRefresh()")
                self.refresher.enqueueRefresh()
            else:
                if debug: myPrint("DB", "... refresher is None - just returning without refresh...")

        def reallyRefresh(self):
            if debug: myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            if debug: myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            if debug: myPrint("DB", "HomePageView .reallyRefresh().. rebuilding the panel(s) and contents...")

            LBE = LowestBalancesExtension.getLBE()
            md = LBE.moneydanceContext

            LBE.cancelSwingWorkers(lBuildHomePageWidgets=True)

            # launch -invoke[_and_quit] can cause program to fall over as it's shutting down.. Detect None condition
            if md.getCurrentAccountBook() is None:
                if debug: myPrint("DB", "@@ .reallyRefresh() detected .getCurrentAccountBook() is None... Perhaps -invoke[_and_quit].. Just ignore and exit this refresh..")
                return

            lShouldStartSwingWorker = False

            with self.HPV_LOCK:

                self.cleanupDeadViews(False)

                for _viewWR in self.views:
                    _view = _viewWR.get()
                    if isSwingComponentInvalid(_view):
                        if debug: myPrint("DB", "... skipping View(WIDGET) as no longer exists (or is invalid):", _viewWR)
                        continue

                    if debug:
                        mfRef = SwingUtilities.getWindowAncestor(_view)
                        mfName = "None" if (mfRef is None) else classPrinter(mfRef.getName(), mfRef)
                        myPrint("B", "... view: %s, main frame: %s (valid: %s)"
                                %(classPrinter(_view.getName(), _view), mfName, isSwingComponentValid(_view)))
                        del mfRef, mfName

                    _view.headerLabel.setText(GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME.title())                           # noqa
                    _view.headerLabel.setForeground(md.getUI().getColors().secondaryTextFG)                             # noqa

                    # Always set the debug icon (if running debug)...
                    _view.debugIconLbl.setIcon(LBE.debugIcon if debug else None)

                    if not LBE.saved_expandedView and LBE.configSaved:
                        if debug: myPrint("DB", "Widget is collapsed, so doing nothing....")
                        _view.collapsableIconLbl.setIcon(md.getUI().getImages().getIconWithColor(GlobalVars.Strings.MD_GLYPH_TRIANGLE_RIGHT, LBE.moneydanceContext.getUI().getColors().secondaryTextFG))
                        _view.listPanel.removeAll()
                        _view.listPanel.getParent().revalidate()
                        _view.listPanel.getParent().repaint()

                    else:

                        LBE.saved_expandedView = True        # Override as expanded in case it was collapsed but not saved....

                        if not LBE.configSaved:
                            _view.collapsableIconLbl.setIcon(md.getUI().getImages().getIconWithColor(GlobalVars.Strings.MD_GLYPH_REMINDERS, LBE.moneydanceContext.getUI().getColors().secondaryTextFG))
                        else:
                            _view.collapsableIconLbl.setIcon(md.getUI().getImages().getIconWithColor(GlobalVars.Strings.MD_GLYPH_TRIANGLE_DOWN, LBE.moneydanceContext.getUI().getColors().secondaryTextFG))

                        _view.balTypeLabel.setText("Lowest F/Balance")                                                  # noqa
                        _view.balTypeLabel.setForeground(md.getUI().getColors().secondaryTextFG)                        # noqa

                        if debug:
                            _view.listPanel.removeAll()
                            onPnlRow = 0

                            mdImages = LBE.moneydanceContext.getUI().getImages()
                            iconTintPleaseWait = LBE.moneydanceContext.getUI().getColors().errorMessageForeground
                            iconPleaseWait = mdImages.getIconWithColor(GlobalVars.Strings.MD_GLYPH_REFRESH, iconTintPleaseWait)

                            pleaseWaitLabel = JLabel("Please wait - widget is updating...")
                            pleaseWaitLabel.setIcon(iconPleaseWait)
                            pleaseWaitLabel.setHorizontalAlignment(JLabel.CENTER)
                            pleaseWaitLabel.setHorizontalTextPosition(JLabel.LEFT)
                            pleaseWaitLabel.setForeground(md.getUI().getColors().errorMessageForeground)
                            pleaseWaitLabel.setBorder(_view.nameBorder)

                            onCol = 0
                            _view.listPanel.add(pleaseWaitLabel, GridC.getc().xy(onCol, onPnlRow).wx(1.0).filly().colspan(2).pady(2))
                            _view.listPanel.getParent().revalidate()
                            _view.listPanel.getParent().repaint()

                        else:
                            pleaseWaitLabel = JLabel("")

                        lShouldStartSwingWorker = True

            if lShouldStartSwingWorker:
                if debug: myPrint("DB", "About to start swing worker to offload processing to non EDT thread....")
                sw = self.BuildHomePageWidgetSwingWorker(pleaseWaitLabel, self)
                sw.execute()

        # Called when the view should clean up everything. For example, this is called when a file is closed and the GUI
        #  is reset. The view should disconnect from any resources that are associated with the currently opened data file.
        def reset(self):
            if debug: myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            if debug: myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            if debug: myPrint("DB", ".... .reset() (as of build 1020) doing nothing")

        def unload(self):   # This is my own method (not overridden from HomePageView)
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("B", "HomePageView: .unload() extension called - so I will wipe all panels and deactivate myself....")

            self.cleanupAsBookClosing()

            with self.HPV_LOCK: self.is_unloaded = True

        def cleanupAsBookClosing(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            with self.HPV_LOCK:
                for _viewWR in self.views:
                    _view = _viewWR.get()
                    if _view is None:
                        myPrint("DB", "... skipping wiping of view as it no longer exists:", _viewWR)
                    else:
                        myPrint("DB", "... wiping view:", classPrinter(_view.getName(), _view))
                        _view.removeAll()       # Hopefully already within the EDT....
                del self.views[:]
                self.reset()
                self.deactivateListeners()

            myPrint("DB", "... Exiting %s.%s()" %(self, inspect.currentframe().f_code.co_name))


    # Don't worry about the Swing EDT for initialisation... The GUI won't be loaded on MD startup anyway....
    myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

    # Moneydance queries this variable after script exit and uses it to install the extension
    moneydance_extension = LowestBalancesExtension.getLBE()

    myPrint("B", "StuWareSoftSystems - ", GlobalVars.thisScriptName, " initialisation routines ending......")
