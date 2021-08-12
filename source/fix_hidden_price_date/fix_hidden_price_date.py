#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# fix_hidden_price_date.py (build: 1000)

###############################################################################
# MIT License
#
# Copyright (c) 2021 Stuart Beesley - StuWareSoftSystems
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

# Build: 1000 - Initial release
# Build: 1001 - Common code tweaks

# Sweeps and fixes the Currency/Security hidden price_date field (and updates the current price too):
# Extension, detects Quote Loader extension, then reads the QL Parameter file.
# Then for each Currency/Security found in the parameter file it scans the MD CurrencyType object
# and resets the hidden price_date field to the latest dated price history date (snapshot)

# Note: QL ignores currencies that are hidden from the summary screen - thus, so does this extension.
# This extension also obeys the QL parameters to include/exclude currencies and include zero accounts
# Thus, even if a security is in the parameter file, the above override the inclusion...


# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################

# SET THESE LINES
myModuleID = u"fix_hidden_price_date"
version_build = "1001"
MIN_BUILD_REQD = 1904                                               # Check for builds less than 1904 / version < 2019.4
_I_CAN_RUN_AS_MONEYBOT_SCRIPT = True

if u"debug" in globals():
	global debug
else:
	debug = False
global fix_hidden_price_date_frame_
# SET LINES ABOVE ^^^^

# COPY >> START
global moneydance, moneydance_ui, moneydance_extension_loader, moneydance_extension_parameter
MD_REF = moneydance             # Make my own copy of reference as MD removes it once main thread ends.. Don't use/hold on to _data variable
MD_REF_UI = moneydance_ui       # Necessary as calls to .getUI() will try to load UI if None - we don't want this....
if MD_REF is None: raise Exception("CRITICAL ERROR - moneydance object/variable is None?")
if u"moneydance_extension_loader" in globals():
	MD_EXTENSION_LOADER = moneydance_extension_loader
else:
	MD_EXTENSION_LOADER = None

from java.lang import System, Runnable
from javax.swing import JFrame, SwingUtilities, SwingWorker
from java.awt.event import WindowEvent

class MyJFrame(JFrame):

	def __init__(self, frameTitle=None):
		super(JFrame, self).__init__(frameTitle)
		self.myJFrameVersion = 2
		self.isActiveInMoneydance = False
		self.isRunTimeExtension = False
		self.MoneydanceAppListener = None
		self.HomePageViewObj = None

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

def getMyJFrame( moduleName ):
	try:
		frames = JFrame.getFrames()
		for fr in frames:
			if (fr.getName().lower().startswith(u"%s_main" %moduleName)
					and type(fr).__name__ == MyJFrame.__name__                         # isinstance() won't work across namespaces
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
			and isinstance(fix_hidden_price_date_frame_, MyJFrame)        # EDIT THIS
			and fix_hidden_price_date_frame_.isActiveInMoneydance):       # EDIT THIS
		frameToResurrect = fix_hidden_price_date_frame_                   # EDIT THIS
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

elif not _I_CAN_RUN_AS_MONEYBOT_SCRIPT and u"moneydance_extension_loader" not in globals():
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
	import sys
	reload(sys)  # Dirty hack to eliminate UTF-8 coding errors
	sys.setdefaultencoding('utf8')  # Dirty hack to eliminate UTF-8 coding errors. Without this str() fails on unicode strings...

	import os
	import os.path
	import codecs
	import inspect
	import pickle
	import platform
	import csv
	import datetime

	from org.python.core.util import FileUtil

	from java.lang import Thread

	from com.moneydance.util import Platform
	from com.moneydance.awt import JTextPanel, GridC, JDateField
	from com.moneydance.apps.md.view.gui import MDImages

	from com.infinitekind.util import DateUtil, CustomDateFormat
	from com.infinitekind.moneydance.model import *
	from com.infinitekind.moneydance.model import AccountUtil, AcctFilter, CurrencyType, CurrencyUtil
	from com.infinitekind.moneydance.model import Account, Reminder, ParentTxn, SplitTxn, TxnSearch, InvestUtil, TxnUtil

	from javax.swing import JButton, JScrollPane, WindowConstants, JLabel, JPanel, JComponent, KeyStroke, JDialog, JComboBox
	from javax.swing import JOptionPane, JTextArea, JMenuBar, JMenu, JMenuItem, AbstractAction, JCheckBoxMenuItem, JFileChooser
	from javax.swing import JTextField, JPasswordField, Box, UIManager, JTable, JCheckBox, JRadioButton, ButtonGroup
	from javax.swing.text import PlainDocument
	from javax.swing.border import EmptyBorder

	exec("from javax.print import attribute")   # IntelliJ doesnt like the use of 'print' (as it's a keyword). Messy, but hey!

	from java.awt.datatransfer import StringSelection
	from javax.swing.text import DefaultHighlighter

	from java.awt import Color, Dimension, FileDialog, FlowLayout, Toolkit, Font, GridBagLayout, GridLayout
	from java.awt import BorderLayout, Dialog, Insets
	from java.awt.event import KeyEvent, WindowAdapter, InputEvent
	from java.util import Date

	from java.text import DecimalFormat, SimpleDateFormat, MessageFormat
	from java.util import Calendar, ArrayList
	from java.lang import Double, Math, Character
	from java.io import FileNotFoundException, FilenameFilter, File, FileInputStream, FileOutputStream, IOException, StringReader
	from java.io import BufferedReader, InputStreamReader
	from java.nio.charset import Charset
	if isinstance(None, (JDateField,CurrencyUtil,Reminder,ParentTxn,SplitTxn,TxnSearch, JComboBox, JCheckBox,
						JTextArea, JMenuBar, JMenu, JMenuItem, JCheckBoxMenuItem, JFileChooser, JDialog,
						JButton, FlowLayout, InputEvent, ArrayList, File, IOException, StringReader, BufferedReader,
						InputStreamReader, Dialog, JTable, BorderLayout, Double, InvestUtil, JRadioButton, ButtonGroup,
						AccountUtil, AcctFilter, CurrencyType, Account, TxnUtil, JScrollPane, WindowConstants, JFrame,
						JComponent, KeyStroke, AbstractAction, UIManager, Color, Dimension, Toolkit, KeyEvent,
						WindowAdapter, CustomDateFormat, SimpleDateFormat, Insets, FileDialog, Thread, SwingWorker)): pass
	if codecs.BOM_UTF8 is not None: pass
	if csv.QUOTE_ALL is not None: pass
	if datetime.MINYEAR is not None: pass
	if Math.max(1,1): pass
	# END COMMON IMPORTS ###################################################################################################

	# COMMON GLOBALS #######################################################################################################
	global myParameters, myScriptName, _resetParameters, i_am_an_extension_so_run_headless, moneydanceIcon
	global lPickle_version_warning, decimalCharSep, groupingCharSep, lIamAMac, lGlobalErrorDetected
	global MYPYTHON_DOWNLOAD_URL
	# END COMMON GLOBALS ###################################################################################################
	# COPY >> END

	# SET THESE VARIABLES FOR ALL SCRIPTS ##################################################################################
	myScriptName = u"%s.py(Extension)" %myModuleID                                                                      # noqa
	myParameters = {}                                                                                                   # noqa
	_resetParameters = False                                                                                            # noqa
	lPickle_version_warning = False                                                                                     # noqa
	lIamAMac = False                                                                                                    # noqa
	lGlobalErrorDetected = False																						# noqa
	MYPYTHON_DOWNLOAD_URL = "https://yogi1967.github.io/MoneydancePythonScripts/"                                       # noqa
	# END SET THESE VARIABLES FOR ALL SCRIPTS ##############################################################################

	# >>> THIS SCRIPT'S IMPORTS ############################################################################################
	import json
	from com.moneydance.apps.md.controller import Util
	# >>> END THIS SCRIPT'S IMPORTS ########################################################################################

	# >>> THIS SCRIPT'S GLOBALS ############################################################################################

	# Saved to parameters file
	global __fix_hidden_price_date
	global userdateformat, lStripASCII, csvDelimiter, _column_widths_LFR, scriptpath, daysToLookForward_LFR
	global lWriteBOMToExportFile_SWSS

	# Other used by this program
	global csvfilename, lDisplayOnly
	global baseCurrency, sdf, csvlines, csvheaderline, headerFormats
	global table, focus, row, scrollpane, EditedReminderCheck, ReminderTable_Count, ExtractDetails_Count
	global saveStatusLabel
	# >>> END THIS SCRIPT'S GLOBALS ############################################################################################

	# Set programmatic defaults/parameters for filters HERE.... Saved Parameters will override these now
	# NOTE: You  can override in the pop-up screen
	userdateformat = "%Y/%m/%d"																							# noqa
	lStripASCII = False																									# noqa
	csvDelimiter = ","																									# noqa
	scriptpath = ""																										# noqa
	_column_widths_LFR = []                                                                                          	# noqa
	daysToLookForward_LFR = 365                                                                                         # noqa
	lWriteBOMToExportFile_SWSS = True                                                                                   # noqa
	extract_filename="%s.csv" %(myModuleID)
	# >>> END THIS SCRIPT'S GLOBALS ############################################################################################

	# COPY >> START
	# COMMON CODE ##########################################################################################################
	# COMMON CODE ##########################################################################################################
	# COMMON CODE ##########################################################################################################
	i_am_an_extension_so_run_headless = False                                                                           # noqa
	try:
		myScriptName = os.path.basename(__file__)
	except:
		i_am_an_extension_so_run_headless = True                                                                        # noqa

	scriptExit = """
----------------------------------------------------------------------------------------------------------------------
Thank you for using %s!
The author has other useful Extensions / Moneybot Python scripts available...:

Extension (.mxt) format only:
toolbox                                 View Moneydance settings, diagnostics, fix issues, change settings and much more
net_account_balances:                   Homepage / summary screen widget. Display the total of selected Account Balances
total_selected_transactions:            One-click. Shows a popup total of the register txn amounts selected on screen

Extension (.mxt) and Script (.py) Versions available:
extract_data                            Extract various data to screen and/or csv.. Consolidation of:
- stockglance2020                       View summary of Securities/Stocks on screen, total by Security, export to csv 
- extract_reminders_csv                 View reminders on screen, edit if required, extract all to csv
- extract_currency_history_csv          Extract currency history to csv
- extract_investment_transactions_csv   Extract investment transactions to csv
- extract_account_registers_csv         Extract Account Register(s) to csv along with any attachments

list_future_reminders:                  View future reminders on screen. Allows you to set the days to look forward

A collection of useful ad-hoc scripts (zip file)
useful_scripts:                         Just unzip and select the script you want for the task at hand...

Visit: %s (Author's site)
----------------------------------------------------------------------------------------------------------------------
""" %(myScriptName, MYPYTHON_DOWNLOAD_URL)

	def cleanup_references():
		global MD_REF, MD_REF_UI, MD_EXTENSION_LOADER
		myPrint("DB","About to delete reference to MD_REF, MD_REF_UI and MD_EXTENSION_LOADER....!")
		del MD_REF, MD_REF_UI, MD_EXTENSION_LOADER

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
					line += "\n"
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
		global myScriptName, debug, i_am_an_extension_so_run_headless

		if where[0] == "D" and not debug: return

		printString = ""
		for what in args:
			printString += "%s " %what
		printString = printString.strip()

		if where == "P" or where == "B" or where[0] == "D":
			if not i_am_an_extension_so_run_headless:
				try:
					print(printString)
				except:
					print("Error writing to screen...")
					dump_sys_error_to_md_console_and_errorlog()

		if where == "J" or where == "B" or where == "DB":
			dt = datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
			try:
				System.err.write(myScriptName + ":" + dt + ": ")
				System.err.write(printString)
				System.err.write("\n")
			except:
				System.err.write(myScriptName + ":" + dt + ": "+"Error writing to console")
				dump_sys_error_to_md_console_and_errorlog()
		return

	def dump_sys_error_to_md_console_and_errorlog( lReturnText=False ):

		theText = ""
		myPrint("B","Unexpected error caught: %s" %(sys.exc_info()[0]))
		myPrint("B","Unexpected error caught: %s" %(sys.exc_info()[1]))
		myPrint("B","Error on Script Line Number: %s" %(sys.exc_info()[2].tb_lineno))

		if lReturnText:
			theText += "\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
			theText += "Unexpected error caught: %s\n" %(sys.exc_info()[0])
			theText += "Unexpected error caught: %s\n" %(sys.exc_info()[1])
			theText += "Error on Script Line Number: %s\n" %(sys.exc_info()[2].tb_lineno)
			theText += "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
			return theText

		return

	def pad(theText, theLength):
		theText = theText[:theLength].ljust(theLength, u" ")
		return theText

	def rpad(theText, theLength):
		if not (isinstance(theText, unicode) or isinstance(theText, str)):
			theText = str(theText)

		theText = theText[:theLength].rjust(theLength, u" ")
		return theText

	def cpad(theText, theLength):
		if not (isinstance(theText, unicode) or isinstance(theText, str)):
			theText = str(theText)

		if len(theText)>=theLength: return theText[:theLength]

		padLength = int((theLength - len(theText)) / 2)
		theText = theText[:theLength]
		theText = ((" "*padLength)+theText+(" "*padLength))[:theLength]

		return theText


	myPrint("B", myScriptName, ": Python Script Initialising.......", "Build:", version_build)

	def getMonoFont():
		global debug

		try:
			theFont = MD_REF.getUI().getFonts().code
			# if debug: myPrint("B","Success setting Font set to Moneydance code: %s" %theFont)
		except:
			theFont = Font("monospaced", Font.PLAIN, 15)
			if debug: myPrint("B","Failed to Font set to Moneydance code - So using: %s" %theFont)

		return theFont

	def getTheSetting(what):
		x = MD_REF.getPreferences().getSetting(what, None)
		if not x or x == u"": return None
		return what + u": %s" %(x)

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

		if not homeDir: homeDir = u"?"
		return homeDir

	def getDecimalPoint(lGetPoint=False, lGetGrouping=False):
		global debug

		decimalFormat = DecimalFormat.getInstance()
		# noinspection PyUnresolvedReferences
		decimalSymbols = decimalFormat.getDecimalFormatSymbols()

		if not lGetGrouping: lGetPoint = True
		if lGetGrouping and lGetPoint: return u"error"

		try:
			if lGetPoint:
				_decimalCharSep = decimalSymbols.getDecimalSeparator()
				myPrint(u"D",u"Decimal Point Character: %s" %(_decimalCharSep))
				return _decimalCharSep

			if lGetGrouping:
				_groupingCharSep = decimalSymbols.getGroupingSeparator()
				if _groupingCharSep is None or _groupingCharSep == u"":
					myPrint(u"B", u"Caught empty Grouping Separator")
					return u""
				if ord(_groupingCharSep) >= 128:    # Probably a nbsp (160) = e.g. South Africa for example..!
					myPrint(u"B", u"Caught special character in Grouping Separator. Ord(%s)" %(ord(_groupingCharSep)))
					if ord(_groupingCharSep) == 160:
						return u" (non breaking space character)"
					return u" (non printable character)"
				myPrint(u"D",u"Grouping Separator Character:", _groupingCharSep)
				return _groupingCharSep
		except:
			myPrint(u"B",u"Error in getDecimalPoint() routine....?")
			dump_sys_error_to_md_console_and_errorlog()

		return u"error"


	decimalCharSep = getDecimalPoint(lGetPoint=True)
	groupingCharSep = getDecimalPoint(lGetGrouping=True)

	# JOptionPane.DEFAULT_OPTION, JOptionPane.YES_NO_OPTION, JOptionPane.YES_NO_CANCEL_OPTION, JOptionPane.OK_CANCEL_OPTION
	# JOptionPane.ERROR_MESSAGE, JOptionPane.INFORMATION_MESSAGE, JOptionPane.WARNING_MESSAGE, JOptionPane.QUESTION_MESSAGE, JOptionPane.PLAIN_MESSAGE

	# Copies MD_REF.getUI().showInfoMessage
	def myPopupInformationBox(theParent=None, theMessage="What no message?!", theTitle="Info", theMessageType=JOptionPane.INFORMATION_MESSAGE):

		if theParent is None:
			if theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE:
				icon_to_use=MD_REF.getUI().getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")
				JOptionPane.showMessageDialog(theParent, JTextPanel(theMessage), theTitle, theMessageType, icon_to_use)
				return
		JOptionPane.showMessageDialog(theParent, JTextPanel(theMessage), theTitle, theMessageType)
		return

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
												None,
												_options,
												_options[0])

		if response == 2:
			myPrint("B", "User requested to perform Export Backup before update/fix - calling moneydance export backup routine...")
			MD_REF.getUI().setStatus("%s performing an Export Backup...." %(myScriptName),-1.0)
			MD_REF.getUI().saveToBackup(None)
			MD_REF.getUI().setStatus("%s Export Backup completed...." %(myScriptName),0)
			return True

		elif response == 1:
			myPrint("B", "User DECLINED to perform Export Backup before update/fix...!")
			if not lReturnTheTruth:
				return True

		return False

	# Copied MD_REF.getUI().askQuestion
	def myPopupAskQuestion(theParent=None,
							theTitle="Question",
							theQuestion="What?",
							theOptionType=JOptionPane.YES_NO_OPTION,
							theMessageType=JOptionPane.QUESTION_MESSAGE):

		icon_to_use = None
		if theParent is None:
			if theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE:
				icon_to_use=MD_REF.getUI().getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")

		# question = wrapLines(theQuestion)
		question = theQuestion
		result = JOptionPane.showConfirmDialog(theParent,
												question,
												theTitle,
												theOptionType,
												theMessageType,
												icon_to_use)  # getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"))

		return result == 0

	# Copies Moneydance .askForQuestion
	def myPopupAskForInput(theParent,
							theTitle,
							theFieldLabel,
							theFieldDescription="",
							defaultValue=None,
							isPassword=False,
							theMessageType=JOptionPane.INFORMATION_MESSAGE):

		icon_to_use = None
		if theParent is None:
			if theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE:
				icon_to_use=MD_REF.getUI().getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")

		p = JPanel(GridBagLayout())
		defaultText = None
		if defaultValue: defaultText = defaultValue
		if isPassword:
			field = JPasswordField(defaultText)
		else:
			field = JTextField(defaultText)

		x = 0
		if theFieldLabel:
			p.add(JLabel(theFieldLabel), GridC.getc(x, 0).east())
			x+=1

		p.add(field, GridC.getc(x, 0).field())
		p.add(Box.createHorizontalStrut(244), GridC.getc(x, 0))
		if theFieldDescription:
			p.add(JTextPanel(theFieldDescription), GridC.getc(x, 1).field().colspan(x + 1))
		if (JOptionPane.showConfirmDialog(theParent,
											p,
											theTitle,
											JOptionPane.OK_CANCEL_OPTION,
											theMessageType,
											icon_to_use) == 0):
			return field.getText()
		return None

	# APPLICATION_MODAL, DOCUMENT_MODAL, MODELESS, TOOLKIT_MODAL
	class MyPopUpDialogBox():

		def __init__(self, theParent=None, theStatus="", theMessage="", theWidth=200, theTitle="Info", lModal=True, lCancelButton=False, OKButtonText="OK", lAlertLevel=0):
			self.theParent = theParent
			self.theStatus = theStatus
			self.theMessage = theMessage
			self.theWidth = max(80,theWidth)
			self.theTitle = theTitle
			self.lModal = lModal
			self.lCancelButton = lCancelButton
			self.OKButtonText = OKButtonText
			self.lAlertLevel = lAlertLevel
			self.fakeJFrame = None
			self._popup_d = None
			self.lResult = [None]
			if not self.theMessage.endswith("\n"): self.theMessage+="\n"
			if self.OKButtonText == "": self.OKButtonText="OK"

		class WindowListener(WindowAdapter):

			def __init__(self, theDialog, theFakeFrame, lResult):
				self.theDialog = theDialog
				self.theFakeFrame = theFakeFrame
				self.lResult = lResult

			def windowClosing(self, WindowEvent):                                                                       # noqa
				global debug
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
			# noinspection PyMethodMayBeStatic

			def __init__(self, theDialog, theFakeFrame, lResult):
				self.theDialog = theDialog
				self.theFakeFrame = theFakeFrame
				self.lResult = lResult

			def actionPerformed(self, event):
				global debug
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
			# noinspection PyMethodMayBeStatic

			def __init__(self, theDialog, theFakeFrame, lResult):
				self.theDialog = theDialog
				self.theFakeFrame = theFakeFrame
				self.lResult = lResult

			def actionPerformed(self, event):
				global debug
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

			global debug
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
			return

		def result(self):
			global debug
			return self.lResult[0]

		def go(self):
			global debug

			myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
			myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

			class MyPopUpDialogBoxRunnable(Runnable):
				def __init__(self, callingClass):
					self.callingClass = callingClass

				def run(self):                                                                                                      # noqa

					myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
					myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

					# Create a fake JFrame so we can set the Icons...
					if self.callingClass.theParent is None:
						self.callingClass.fakeJFrame = MyJFrame()
						self.callingClass.fakeJFrame.setName(u"%s_fake_dialog" %(myModuleID))
						self.callingClass.fakeJFrame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)
						self.callingClass.fakeJFrame.setUndecorated(True)
						self.callingClass.fakeJFrame.setVisible( False )
						if not Platform.isOSX():
							self.callingClass.fakeJFrame.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))

					if self.callingClass.lModal:
						# noinspection PyUnresolvedReferences
						self.callingClass._popup_d = JDialog(self.callingClass.theParent, self.callingClass.theTitle, Dialog.ModalityType.APPLICATION_MODAL)
					else:
						# noinspection PyUnresolvedReferences
						self.callingClass._popup_d = JDialog(self.callingClass.theParent, self.callingClass.theTitle, Dialog.ModalityType.MODELESS)

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

					displayJText = JTextArea(self.callingClass.theMessage)
					displayJText.setFont( getMonoFont() )
					displayJText.setEditable(False)
					displayJText.setLineWrap(False)
					displayJText.setWrapStyleWord(False)

					_popupPanel=JPanel()

					# maxHeight = 500
					_popupPanel.setLayout(GridLayout(0,1))
					_popupPanel.setBorder(EmptyBorder(8, 8, 8, 8))

					if self.callingClass.theStatus:
						_label1 = JLabel(pad(self.callingClass.theStatus,self.callingClass.theWidth-20))
						_label1.setForeground(Color.BLUE)
						_popupPanel.add(_label1)

					myScrollPane = JScrollPane(displayJText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
					if displayJText.getLineCount()>5:
						myScrollPane.setWheelScrollingEnabled(True)
						_popupPanel.add(myScrollPane)
					else:
						_popupPanel.add(displayJText)

					buttonPanel = JPanel()
					if self.callingClass.lModal or self.callingClass.lCancelButton:
						buttonPanel.setLayout(FlowLayout(FlowLayout.CENTER))

						if self.callingClass.lCancelButton:
							cancel_button = JButton("CANCEL")
							cancel_button.setPreferredSize(Dimension(100,40))
							cancel_button.setBackground(Color.LIGHT_GRAY)
							cancel_button.setBorderPainted(False)
							cancel_button.setOpaque(True)
							cancel_button.addActionListener( self.callingClass.CancelButtonAction(self.callingClass._popup_d, self.callingClass.fakeJFrame,self.callingClass.lResult) )
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
							ok_button.addActionListener( self.callingClass.OKButtonAction(self.callingClass._popup_d, self.callingClass.fakeJFrame, self.callingClass.lResult) )
							buttonPanel.add(ok_button)

						_popupPanel.add(buttonPanel)

					if self.callingClass.lAlertLevel>=2:
						# internalScrollPane.setBackground(Color.RED)
						# theJText.setBackground(Color.RED)
						# theJText.setForeground(Color.BLACK)
						displayJText.setBackground(Color.RED)
						displayJText.setForeground(Color.BLACK)
						_popupPanel.setBackground(Color.RED)
						_popupPanel.setForeground(Color.BLACK)
						buttonPanel.setBackground(Color.RED)
						myScrollPane.setBackground(Color.RED)

					elif self.callingClass.lAlertLevel>=1:
						# internalScrollPane.setBackground(Color.YELLOW)
						# theJText.setBackground(Color.YELLOW)
						# theJText.setForeground(Color.BLACK)
						displayJText.setBackground(Color.YELLOW)
						displayJText.setForeground(Color.BLACK)
						_popupPanel.setBackground(Color.YELLOW)
						_popupPanel.setForeground(Color.BLACK)
						buttonPanel.setBackground(Color.YELLOW)
						myScrollPane.setBackground(Color.RED)

					self.callingClass._popup_d.add(_popupPanel)
					self.callingClass._popup_d.pack()
					self.callingClass._popup_d.setLocationRelativeTo(None)
					self.callingClass._popup_d.setVisible(True)  # Keeping this modal....

			if not SwingUtilities.isEventDispatchThread():
				myPrint("DB",".. Not running within the EDT so calling via MyPopUpDialogBoxRunnable()...")
				SwingUtilities.invokeAndWait(MyPopUpDialogBoxRunnable(self))
			else:
				myPrint("DB",".. Already within the EDT so calling naked...")
				MyPopUpDialogBoxRunnable(self).run()

			myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

			return self.lResult[0]

	def play_the_money_sound():

		# Seems to cause a crash on Virtual Machine with no Audio - so just in case....
		try:
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
		ext = ""

		def __init__(self, ext):
			self.ext = "." + ext.upper()

		def accept(self, thedir, filename):                                                                             # noqa
			if filename is not None and filename.upper().endswith(self.ext):
				return True
			return False

	try:
		moneydanceIcon = MDImages.getImage(MD_REF.getSourceInformation().getIconResource())
	except:
		moneydanceIcon = None

	def MDDiag():
		global debug
		myPrint("D", "Moneydance Build:", MD_REF.getVersion(), "Build:", MD_REF.getBuild())


	MDDiag()

	myPrint("DB","System file encoding is:", sys.getfilesystemencoding() )   # Not used, but interesting. Perhaps useful when switching between Windows/Macs and writing files...

	def checkVersions():
		global debug

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

		myFont = MD_REF.getUI().getFonts().defaultText

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

	if MD_REF_UI is not None:
		setDefaultFonts()

	def who_am_i():
		try:
			username = System.getProperty("user.name")
		except:
			username = "???"

		return username

	def getHomeDir():
		# Yup - this can be all over the place...
		myPrint("D", 'System.getProperty("user.dir")', System.getProperty("user.dir"))
		myPrint("D", 'System.getProperty("UserHome")', System.getProperty("UserHome"))
		myPrint("D", 'System.getProperty("user.home")', System.getProperty("user.home"))
		myPrint("D", 'os.path.expanduser("~")', os.path.expanduser("~"))
		myPrint("D", 'os.environ.get("HOMEPATH")', os.environ.get("HOMEPATH"))
		return

	def amIaMac():
		return Platform.isOSX()

	myPrint("D", "I am user:", who_am_i())
	if debug: getHomeDir()
	lIamAMac = amIaMac()

	def myDir():
		global lIamAMac
		homeDir = None

		try:
			if lIamAMac:
				homeDir = System.getProperty("UserHome")  # On a Mac in a Java VM, the homedir is hidden
			else:
				# homeDir = System.getProperty("user.home")
				homeDir = os.path.expanduser("~")  # Should work on Unix and Windows
				if homeDir is None or homeDir == "":
					homeDir = System.getProperty("user.home")
				if homeDir is None or homeDir == "":
					homeDir = os.environ.get("HOMEPATH")
		except:
			pass

		if homeDir is None or homeDir == "":
			homeDir = MD_REF.getCurrentAccountBook().getRootFolder().getParent()  # Better than nothing!

		myPrint("DB", "Home Directory selected...:", homeDir)
		if homeDir is None: return ""
		return homeDir

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
					super(JTextFieldLimitYN, self).insertString(myOffset, myString, myAttr)                         # noqa

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
		global debug, myParameters, lPickle_version_warning, version_build, _resetParameters                            # noqa

		myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

		if _resetParameters:
			myPrint("B", "User has specified to reset parameters... keeping defaults and skipping pickle()")
			myParameters = {}
			return

		old_dict_filename = os.path.join("..", myFile)

		# Pickle was originally encrypted, no need, migrating to unencrypted
		migratedFilename = os.path.join(MD_REF.getCurrentAccountBook().getRootFolder().getAbsolutePath(),myFile)

		myPrint("DB", "Now checking for parameter file:", migratedFilename)

		if os.path.exists( migratedFilename ):

			myPrint("DB", "loading parameters from non-encrypted Pickle file:", migratedFilename)
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

				myParameters = pickle.loads(load_string)
				load_file.close()
			except FileNotFoundException:
				myPrint("B", "Error: failed to find parameter file...")
				myParameters = None
			except EOFError:
				myPrint("B", "Error: reached EOF on parameter file....")
				myParameters = None
			except:
				myPrint("B","Error opening Pickle File (will try encrypted version) - Unexpected error ", sys.exc_info()[0])
				myPrint("B","Error opening Pickle File (will try encrypted version) - Unexpected error ", sys.exc_info()[1])
				myPrint("B","Error opening Pickle File (will try encrypted version) - Line Number: ", sys.exc_info()[2].tb_lineno)

				# OK, so perhaps from older version - encrypted, try to read
				try:
					local_storage = MD_REF.getCurrentAccountBook().getLocalStorage()
					istr = local_storage.openFileForReading(old_dict_filename)
					load_file = FileUtil.wrap(istr)
					# noinspection PyTypeChecker
					myParameters = pickle.load(load_file)
					load_file.close()
					myPrint("B","Success loading Encrypted Pickle file - will migrate to non encrypted")
					lPickle_version_warning = True
				except:
					myPrint("B","Opening Encrypted Pickle File - Unexpected error ", sys.exc_info()[0])
					myPrint("B","Opening Encrypted Pickle File - Unexpected error ", sys.exc_info()[1])
					myPrint("B","Error opening Pickle File - Line Number: ", sys.exc_info()[2].tb_lineno)
					myPrint("B", "Error: Pickle.load() failed.... Is this a restored dataset? Will ignore saved parameters, and create a new file...")
					myParameters = None

			if myParameters is None:
				myParameters = {}
				myPrint("DB","Parameters did not load, will keep defaults..")
			else:
				myPrint("DB","Parameters successfully loaded from file...")
		else:
			myPrint("J", "Parameter Pickle file does not exist - will use default and create new file..")
			myPrint("D", "Parameter Pickle file does not exist - will use default and create new file..")
			myParameters = {}

		if not myParameters: return

		myPrint("DB","myParameters read from file contains...:")
		for key in sorted(myParameters.keys()):
			myPrint("DB","...variable:", key, myParameters[key])

		if myParameters.get("debug") is not None: debug = myParameters.get("debug")
		if myParameters.get("lUseMacFileChooser") is not None:
			myPrint("B", "Detected old lUseMacFileChooser parameter/variable... Will delete it...")
			myParameters.pop("lUseMacFileChooser", None)  # Old variable - not used - delete from parameter file

		myPrint("DB","Parameter file loaded if present and myParameters{} dictionary set.....")

		# Now load into memory!
		load_StuWareSoftSystems_parameters_into_memory()

		return

	def save_StuWareSoftSystems_parameters_to_file(myFile="StuWareSoftSystems.dict"):
		global debug, myParameters, lPickle_version_warning, version_build

		myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

		if myParameters is None: myParameters = {}

		# Don't forget, any parameters loaded earlier will be preserved; just add changed variables....
		myParameters["__Author"] = "Stuart Beesley - (c) StuWareSoftSystems"
		myParameters["debug"] = debug

		dump_StuWareSoftSystems_parameters_from_memory()

		# Pickle was originally encrypted, no need, migrating to unencrypted
		migratedFilename = os.path.join(MD_REF.getCurrentAccountBook().getRootFolder().getAbsolutePath(),myFile)

		myPrint("DB","Will try to save parameter file:", migratedFilename)

		ostr = FileOutputStream(migratedFilename)

		myPrint("DB", "about to Pickle.dump and save parameters to unencrypted file:", migratedFilename)

		try:
			save_file = FileUtil.wrap(ostr)
			pickle.dump(myParameters, save_file, protocol=0)
			save_file.close()

			myPrint("DB","myParameters now contains...:")
			for key in sorted(myParameters.keys()):
				myPrint("DB","...variable:", key, myParameters[key])

		except:
			myPrint("B", "Error - failed to create/write parameter file.. Ignoring and continuing.....")
			dump_sys_error_to_md_console_and_errorlog()

			return

		myPrint("DB","Parameter file written and parameters saved to disk.....")

		return

	def get_time_stamp_as_nice_text( timeStamp ):

		prettyDate = ""
		try:
			c = Calendar.getInstance()
			c.setTime(Date(timeStamp))
			dateFormatter = SimpleDateFormat("yyyy/MM/dd HH:mm:ss(.SSS) Z z zzzz")
			prettyDate = dateFormatter.format(c.getTime())
		except:
			pass

		return prettyDate

	def currentDateTimeMarker():
		c = Calendar.getInstance()
		dateformat = SimpleDateFormat("_yyyyMMdd_HHmmss")
		_datetime = dateformat.format(c.getTime())
		return _datetime

	def destroyOldFrames(moduleName):
		myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", WindowEvent)
		myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))
		frames = JFrame.getFrames()
		for fr in frames:
			if fr.getName().lower().startswith(moduleName):
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

			_search_options = [ "Next", "Previous", "Cancel" ]

			defaultDirection = _search_options[self.lastDirection]

			response = JOptionPane.showOptionDialog(self.theFrame,
													p,
													"Search for text",
													JOptionPane.OK_CANCEL_OPTION,
													JOptionPane.QUESTION_MESSAGE,
													None,
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

	def computeFontSize(_theComponent, _maxPaperWidth):

		# Auto shrink font so that text fits on one line when printing
		# Note: Java seems to operate it's maths at 72DPI....

		try:
			_DEFAULT_MIN_WIDTH = 100

			_minFontSize = 5
			theString = _theComponent.getText()
			_startingComponentFont = _theComponent.getFont()

			if not theString or len(theString) < 1: return -1

			fm = _theComponent.getFontMetrics(_startingComponentFont)
			_maxFontSize = curFontSize = _startingComponentFont.getSize()

			maxLineWidthInFile = _DEFAULT_MIN_WIDTH
			longestLine = ""
			for line in theString.split("\n"):
				_w = fm.stringWidth(line)
				if _w > maxLineWidthInFile:
					longestLine = line
					maxLineWidthInFile = _w

			while (fm.stringWidth(longestLine) + 5 > _maxPaperWidth):
				curFontSize -= 1
				fm = _theComponent.getFontMetrics(Font(_startingComponentFont.getName(), _startingComponentFont.getStyle(), curFontSize))

			# Code to increase width....
			# while (fm.stringWidth(theString) + 5 < _maxPaperWidth):
			#     curSize += 1
			#     fm = _theComponent.getFontMetrics(Font(_startingComponentFont.getName(), _startingComponentFont.getStyle(), curSize))

			curFontSize = max(_minFontSize, curFontSize)
			curFontSize = min(_maxFontSize, curFontSize)

		except:
			myPrint("B", "ERROR: computeFontSize() crashed?")
			dump_sys_error_to_md_console_and_errorlog()
			return -1

		return curFontSize

	def saveOutputFile(_theFrame, _theTitle, _fileName, _theText, _statusLabel=None):

		if Platform.isOSX():
			System.setProperty("com.apple.macos.use-file-dialog-packages", "true")
			System.setProperty("apple.awt.fileDialogForDirectories", "false")

		filename = FileDialog(_theFrame, "Select location to save the current displayed output... (CANCEL=ABORT)")
		filename.setDirectory(get_home_dir())
		filename.setMultipleMode(False)
		filename.setMode(FileDialog.SAVE)
		filename.setFile(_fileName)

		if (not Platform.isOSX() or not Platform.isOSXVersionAtLeast("10.13")):
			extFilter = ExtFilenameFilter("txt")
			filename.setFilenameFilter(extFilter)

		filename.setVisible(True)
		copyToFile = filename.getFile()

		if Platform.isOSX():
			System.setProperty("com.apple.macos.use-file-dialog-packages","true")
			System.setProperty("apple.awt.fileDialogForDirectories", "false")

		if (copyToFile is None) or copyToFile == "":
			filename.dispose(); del filename
			return
		elif not str(copyToFile).endswith(".txt"):
			myPopupInformationBox(_theFrame, "Sorry - please use a .txt file extension when saving output txt")
			filename.dispose(); del filename
			return
		elif ".moneydance" in filename.getDirectory():
			myPopupInformationBox(_theFrame, "Sorry, please choose a location outside of the Moneydance location")
			filename.dispose();del filename
			return

		copyToFile = os.path.join(filename.getDirectory(), filename.getFile())

		if not check_file_writable(copyToFile):
			myPopupInformationBox(_theFrame, "Sorry, that file/location does not appear allowed by the operating system!?")

		toFile = None
		try:
			toFile = os.path.join(filename.getDirectory(), filename.getFile())
			with open(toFile, 'w') as f: f.write(_theText)
			myPrint("B", "%s: text output copied to: %s" %(_theTitle, toFile))

			# noinspection PyTypeChecker
			if os.path.exists(toFile):
				play_the_money_sound()
				txt = "%s: Output text saved as requested to: %s" %(_theTitle, toFile)
				if _statusLabel:
					_statusLabel.setText((txt).ljust(800, " ")); _statusLabel.setForeground(Color.BLUE)
				myPopupInformationBox(_theFrame, txt)
			else:
				txt = "ERROR - failed to write output text to file: %s" %(toFile)
				myPrint("B", txt)
				myPopupInformationBox(_theFrame, txt)
		except:
			txt = "ERROR - failed to write output text to file: %s" %(toFile)
			dump_sys_error_to_md_console_and_errorlog()
			myPopupInformationBox(_theFrame, txt)

		filename.dispose(); del filename

	rememberPrintSize = eval("MD_REF.getUI().getFonts().print.getSize()")   # Do this here as MD_REF disappears after script ends...

	# noinspection PyUnresolvedReferences, PyUnusedLocal
	def printOutputFile(_callingClass=None, _theTitle=None, _theJText=None, _theString=None):

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
			# if _callingClass is not None:
			#     printJTextArea.setLineWrap(_callingClass.lWrapText)  # Mirror the word wrap set by user
			# else:
			#     printJTextArea.setLineWrap(False)
			printJTextArea.setLineWrap(True)

			printJTextArea.setWrapStyleWord(False)

			# IntelliJ doesnt like the use of 'print' (as it's a keyword)
			if "MD_REF" in globals():
				defaultPrintFontSize = eval("MD_REF.getUI().getFonts().print.getSize()")
			elif "moneydance" in globals():
				defaultPrintFontSize = eval("moneydance.getUI().getFonts().print.getSize()")
			else:
				defaultPrintFontSize = rememberPrintSize

			theFontToUse = getMonoFont()       # Need Monospaced font, but with the font set in MD preferences for print
			theFontToUse = theFontToUse.deriveFont(float(defaultPrintFontSize))
			printJTextArea.setFont(theFontToUse)

			_IN2MM = 25.4                                                                                               # noqa
			_IN2CM = 2.54                                                                                               # noqa
			_IN2PT = 72                                                                                                 # noqa
			def mm2pt(_mm):                 return _mm * _IN2PT / _IN2MM                                                # noqa
			def mm2mpt(_mm):                return _mm * 1000 * _IN2PT / _IN2MM                                         # noqa
			def pt2mm(_pt):                 return _pt * _IN2MM / _IN2PT                                                # noqa
			def mm2in(_mm):                 return _mm / _IN2MM                                                         # noqa
			def in2mm(_in):                 return _in * _IN2MM                                                         # noqa
			def in2mpt(_in):                return _in * _IN2PT * 1000                                                  # noqa
			def in2pt(_in):                 return _in * _IN2PT                                                         # noqa
			def mpt2in(_mpt):               return _mpt / _IN2PT / 1000                                                 # noqa
			def mm2px(_mm, _resolution):    return mm2in(_mm) * _resolution                                             # noqa
			def mpt2px(_mpt, _resolution):  return mpt2in(_mpt) * _resolution                                           # noqa

			_DPI = 72
			_MARGINS = 5
			_BUFFER_PCT = 0.95

			# Refer: https://docs.oracle.com/javase/7/docs/api/javax/print/attribute/standard/package-summary.html
			thePaper = attribute.standard.MediaPrintableArea(_MARGINS, _MARGINS, 210 - _MARGINS, 297 - _MARGINS, attribute.standard.MediaPrintableArea.MM)
			maxPaperWidth = mm2px(thePaper.getPrintableArea(attribute.standard.MediaPrintableArea.MM)[3] - thePaper.getPrintableArea(attribute.standard.MediaPrintableArea.MM)[1],_DPI)
			maxPaperWidth *= _BUFFER_PCT

			if _callingClass is None or not _callingClass.lWrapText:
				newFontSize = computeFontSize(printJTextArea, int(maxPaperWidth))

				if newFontSize > 0:
					theFontToUse = theFontToUse.deriveFont(float(newFontSize))
					printJTextArea.setFont(theFontToUse)

			pAttrs = attribute.HashPrintRequestAttributeSet()
			pAttrs.add(attribute.standard.OrientationRequested.LANDSCAPE)
			pAttrs.add(attribute.standard.Chromaticity.MONOCHROME)
			pAttrs.add(attribute.standard.MediaSizeName.ISO_A4)
			pAttrs.add(thePaper)
			pAttrs.add(attribute.standard.Copies(1))
			pAttrs.add(attribute.standard.PrintQuality.NORMAL)
			pAttrs.add(attribute.standard.PrinterResolution(_DPI, _DPI, attribute.standard.PrinterResolution.DPI))
			pAttrs.add(attribute.standard.JobName("%s: %s" %(myModuleID.capitalize(), _theTitle), None))
			header = MessageFormat(_theTitle)
			footer = MessageFormat("- page {0} -")

			# avoiding Intellij errors
			eval("printJTextArea.print(header, footer, True, None, pAttrs, True)")
			del printJTextArea
		except:
			myPrint("B", "ERROR in printing routines.....:")
			dump_sys_error_to_md_console_and_errorlog()
		return

	class QuickJFrame():

		def __init__(self, title, output, lAlertLevel=0, copyToClipboard=False, lJumpToEnd=False):
			self.title = title
			self.output = output
			self.lAlertLevel = lAlertLevel
			self.returnFrame = None
			self.copyToClipboard = copyToClipboard
			self.lJumpToEnd = lJumpToEnd
			self.lWrapText = True

		class CloseAction(AbstractAction):

			def __init__(self, theFrame):
				self.theFrame = theFrame

			def actionPerformed(self, event):
				global debug
				myPrint("D","in CloseAction(), Event: ", event)
				myPrint("DB", "QuickJFrame() Frame shutting down....")

				# Already within the EDT
				self.theFrame.dispose()
				return

		class ToggleWrap(AbstractAction):

			def __init__(self, theCallingClass, theJText):
				self.theCallingClass = theCallingClass
				self.theJText = theJText

			def actionPerformed(self, event):
				myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

				self.theCallingClass.lWrapText = not self.theCallingClass.lWrapText
				self.theJText.setLineWrap(self.theCallingClass.lWrapText)

				return

		class QuickJFrameNavigate(AbstractAction):

			def __init__(self, theJText, lTop=False, lBottom=False):
				self.theJText = theJText
				self.lTop = lTop
				self.lBottom = lBottom

			def actionPerformed(self, event):
				myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

				if self.lBottom: self.theJText.setCaretPosition(self.theJText.getDocument().getLength())
				if self.lTop:    self.theJText.setCaretPosition(0)

				return

		class QuickJFramePrint(AbstractAction):

			def __init__(self, theCallingClass, theJText, theTitle=""):
				self.theCallingClass = theCallingClass
				self.theJText = theJText
				self.theTitle = theTitle

			def actionPerformed(self, event):
				myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

				printOutputFile(_callingClass=self.theCallingClass, _theTitle=self.theTitle, _theJText=self.theJText)

				return

		class QuickJFrameSaveTextToFile(AbstractAction):

			def __init__(self, theText, callingFrame):
				self.theText = theText
				self.callingFrame = callingFrame

			def actionPerformed(self, event):
				myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

				saveOutputFile(self.callingFrame, "QUICKJFRAME", "toolbox_output.txt", self.theText)

				return

		def show_the_frame(self):
			global debug

			class MyQuickJFrameRunnable(Runnable):

				def __init__(self, callingClass):
					self.callingClass = callingClass

				def run(self):                                                                                                      # noqa
					screenSize = Toolkit.getDefaultToolkit().getScreenSize()

					frame_width = min(screenSize.width-20, max(1024,int(round(MD_REF.getUI().firstMainFrame.getSize().width *.9,0))))
					frame_height = min(screenSize.height-20, max(768, int(round(MD_REF.getUI().firstMainFrame.getSize().height *.9,0))))

					JFrame.setDefaultLookAndFeelDecorated(True)

					jInternalFrame = MyJFrame(self.callingClass.title + " (%s+F to find/search for text)" %(MD_REF.getUI().ACCELERATOR_MASK_STR))
					jInternalFrame.setName(u"%s_quickjframe" %myModuleID)

					if not Platform.isOSX():
						jInternalFrame.setIconImage(MDImages.getImage(MD_REF.getUI().getMain().getSourceInformation().getIconResource()))

					jInternalFrame.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
					jInternalFrame.setResizable(True)

					shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
					jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W,  shortcut), "close-window")
					jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
					jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F,  shortcut), "search-window")
					jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")
					jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_P, shortcut), "print-me")

					theJText = JTextArea(self.callingClass.output)
					theJText.setEditable(False)
					theJText.setLineWrap(self.callingClass.lWrapText)
					theJText.setWrapStyleWord(False)
					theJText.setFont( getMonoFont() )

					jInternalFrame.getRootPane().getActionMap().put("close-window", self.callingClass.CloseAction(jInternalFrame))
					jInternalFrame.getRootPane().getActionMap().put("search-window", SearchAction(jInternalFrame,theJText))
					jInternalFrame.getRootPane().getActionMap().put("print-me", self.callingClass.QuickJFramePrint(self.callingClass, theJText, self.callingClass.title))

					internalScrollPane = JScrollPane(theJText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)

					if self.callingClass.lAlertLevel>=2:
						internalScrollPane.setBackground(Color.RED)
						theJText.setBackground(Color.RED)
						theJText.setForeground(Color.BLACK)
					elif self.callingClass.lAlertLevel>=1:
						internalScrollPane.setBackground(Color.YELLOW)
						theJText.setBackground(Color.YELLOW)
						theJText.setForeground(Color.BLACK)

					jInternalFrame.setPreferredSize(Dimension(frame_width, frame_height))

					printButton = JButton("Print")
					printButton.setToolTipText("Prints the output displayed in this window to your printer")
					printButton.setOpaque(True)
					printButton.setBackground(Color.WHITE); printButton.setForeground(Color.BLACK)
					printButton.addActionListener(self.callingClass.QuickJFramePrint(self.callingClass, theJText, self.callingClass.title))

					saveButton = JButton("Save to file")
					saveButton.setToolTipText("Saves the output displayed in this window to a file")
					saveButton.setOpaque(True)
					saveButton.setBackground(Color.WHITE); saveButton.setForeground(Color.BLACK)
					saveButton.addActionListener(self.callingClass.QuickJFrameSaveTextToFile(self.callingClass.output, jInternalFrame))

					wrapOption = JCheckBox("Wrap Contents (Screen & Print)", self.callingClass.lWrapText)
					wrapOption.addActionListener(self.callingClass.ToggleWrap(self.callingClass, theJText))

					topButton = JButton("Top")
					topButton.setOpaque(True)
					topButton.setBackground(Color.WHITE); topButton.setForeground(Color.BLACK)
					topButton.addActionListener(self.callingClass.QuickJFrameNavigate(theJText, lTop=True))

					botButton = JButton("Bottom")
					botButton.setOpaque(True)
					botButton.setBackground(Color.WHITE); botButton.setForeground(Color.BLACK)
					botButton.addActionListener(self.callingClass.QuickJFrameNavigate(theJText, lBottom=True))

					closeButton = JButton("Close")
					closeButton.setOpaque(True)
					closeButton.setBackground(Color.WHITE); botButton.setForeground(Color.BLACK)
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

	class AboutThisScript():

		class CloseAboutAction(AbstractAction):

			def __init__(self, theFrame):
				self.theFrame = theFrame

			def actionPerformed(self, event):
				global debug
				myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event:", event)

				# Listener is already on the Swing EDT...
				self.theFrame.dispose()

		def __init__(self, theFrame):
			global debug, scriptExit
			self.theFrame = theFrame

		def go(self):
			myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")

			class MyAboutRunnable(Runnable):
				def __init__(self, callingClass):
					self.callingClass = callingClass

				def run(self):                                                                                                      # noqa

					myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
					myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

					# noinspection PyUnresolvedReferences
					about_d = JDialog(self.callingClass.theFrame, "About", Dialog.ModalityType.MODELESS)

					shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
					about_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
					about_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
					about_d.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")

					about_d.getRootPane().getActionMap().put("close-window", self.callingClass.CloseAboutAction(about_d))

					about_d.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)  # The CloseAction() and WindowListener() will handle dispose() - else change back to DISPOSE_ON_CLOSE

					if (not Platform.isMac()):
						# MD_REF.getUI().getImages()
						about_d.setIconImage(MDImages.getImage(MD_REF.getUI().getMain().getSourceInformation().getIconResource()))

					aboutPanel=JPanel()
					aboutPanel.setLayout(FlowLayout(FlowLayout.LEFT))
					aboutPanel.setPreferredSize(Dimension(1120, 525))

					_label1 = JLabel(pad("Author: Stuart Beesley", 800))
					_label1.setForeground(Color.BLUE)
					aboutPanel.add(_label1)

					_label2 = JLabel(pad("StuWareSoftSystems (2020-2021)", 800))
					_label2.setForeground(Color.BLUE)
					aboutPanel.add(_label2)

					_label3 = JLabel(pad("Script/Extension: %s (build: %s)" %(myScriptName, version_build), 800))
					_label3.setForeground(Color.BLUE)
					aboutPanel.add(_label3)

					displayString=scriptExit
					displayJText = JTextArea(displayString)
					displayJText.setFont( getMonoFont() )
					displayJText.setEditable(False)
					displayJText.setLineWrap(False)
					displayJText.setWrapStyleWord(False)
					displayJText.setMargin(Insets(8, 8, 8, 8))
					# displayJText.setBackground((mdGUI.getColors()).defaultBackground)
					# displayJText.setForeground((mdGUI.getColors()).defaultTextForeground)

					aboutPanel.add(displayJText)

					about_d.add(aboutPanel)

					about_d.pack()
					about_d.setLocationRelativeTo(None)
					about_d.setVisible(True)

			if not SwingUtilities.isEventDispatchThread():
				myPrint("DB",".. Not running within the EDT so calling via MyAboutRunnable()...")
				SwingUtilities.invokeAndWait(MyAboutRunnable(self))
			else:
				myPrint("DB",".. Already within the EDT so calling naked...")
				MyAboutRunnable(self).run()

			myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

	def isGoodRate(theRate):

		if Double.isNaN(theRate) or Double.isInfinite(theRate) or theRate == 0:
			return False

		return True

	def safeInvertRate(theRate):

		if not isGoodRate(theRate):
			return theRate

		return (1.0 / theRate)

	def checkCurrencyRawRatesOK(theCurr):

		checkRate = theCurr.getParameter("rate", None)
		checkRateDouble = theCurr.getDoubleParameter("rate", 0.0)
		checkRRate = theCurr.getParameter("rrate", None)
		checkRRateDouble = theCurr.getDoubleParameter("rrate", 0.0)

		if checkRate is None or not isGoodRate(checkRateDouble):
			myPrint("DB", "WARNING: checkCurrencyRawRatesOK() 'rate' check failed on %s - checking stopped here" %(theCurr))
			return False

		if checkRRate is None or not isGoodRate(checkRRateDouble):
			myPrint("DB", "WARNING: checkCurrencyRawRatesOK() 'rrate' check failed on %s - checking stopped here" %(theCurr))
			return False

		return True

	def check_all_currency_raw_rates_ok(filterType=None):

		_currs = MD_REF.getCurrentAccount().getBook().getCurrencies().getAllCurrencies()
		for _curr in _currs:
			if filterType and _curr.getCurrencyType() != filterType: continue
			if not checkCurrencyRawRatesOK(_curr):
				return False

		return True

	# END COMMON DEFINITIONS ###############################################################################################
	# END COMMON DEFINITIONS ###############################################################################################
	# END COMMON DEFINITIONS ###############################################################################################
	# COPY >> END

	# >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
	# >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
	# >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
	def load_StuWareSoftSystems_parameters_into_memory():
		pass
		return

		# >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
	def dump_StuWareSoftSystems_parameters_from_memory():
		pass
		return

	get_StuWareSoftSystems_parameters_from_file()

	# clear up any old left-overs....
	destroyOldFrames(myModuleID)

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
			MD_REF.getUI().setStatus(">> StuWareSoftSystems - thanks for using >> %s......." %(myScriptName),0)
		except:
			pass  # If this fails, then MD is probably shutting down.......

		if not i_am_an_extension_so_run_headless: print(scriptExit)

		cleanup_references()

	# END ALL CODE COPY HERE ###############################################################################################
	# END ALL CODE COPY HERE ###############################################################################################
	# END ALL CODE COPY HERE ###############################################################################################

	MD_REF.getUI().setStatus(">> StuWareSoftSystems - %s launching......." %(myScriptName),-1)

	QLID = "securityquoteload"
	QLFILE = "securityquoteload.bpam2"
	MBFILE = "MRBPreferences.dict2"
	MB_KEY = "mapData"
	QL_STOCKS_KEY = "listAccounts"
	QL_INCL_CURR_KEY = "includeCurrency"
	QL_INCL_ZERO_KEY = "includeZero"
	QL_STOCK_NAME = "name"
	QL_CURRENCY_FLAG = "currency"
	QLCURRMARKER = "???"  # as of build 3040 this is 3 invisible 7f high byte ascii characters (previously other high byte chars)
	QL_MIN_BUILD = 3039   # This build defaults to 'us-ascii' character set parameter file and eliminates the 3 preceding high byte characters
	QL_MIN_BUILD2 = 3040
	QL_MAX_BUILD = 9999

	MD_decimal = MD_REF.getPreferences().getDecimalChar()

	MD_REF.getUI().setStatus("%s: Detecting & reading Quote Loader extension/parameters...." %(myModuleID),-1)

	# Having to do this myself as QL does not store trailing spaces and thus lookups fail.... :-<
	def my_getCurrencyByID(_ct, _theID, isCurrency=False):

		for c in _ct:
			if isCurrency:
				if c.getIDString() == _theID:
					return c
			else:
				if c.getTickerSymbol() == _theID:
					return c

		for c in _ct:
			if isCurrency:
				if c.getIDString().lower() == _theID.lower():
					return c
			else:
				if c.getTickerSymbol().lower() == _theID.lower():
					return c

		for c in _ct:
			if isCurrency:
				if c.getIDString().lower().strip() == _theID.lower().strip():
					return c
			else:
				if c.getTickerSymbol().lower().strip() == _theID.lower().strip():
					return c

		return None

	def convertStrippedIntDateFormattedText( strippedDateInt ):

		prettyDate = ""
		try:
			c = Calendar.getInstance()
			dateFromInt = DateUtil.convertIntDateToLong(strippedDateInt)
			c.setTime(dateFromInt)
			dateFormatter = SimpleDateFormat("yyyy/MM/dd")
			prettyDate = dateFormatter.format(c.getTime())
		except:
			pass

		return prettyDate

	class MyAcctFilter(AcctFilter):

		def __init__(self, selectType=0):
			self.selectType = selectType

		def matches(self, acct):

			# Security sub accounts for stock holdings
			if self.selectType == 22:
				# noinspection PyUnresolvedReferences
				if not (acct.getAccountType() == Account.AccountType.SECURITY):
					return False
				return True

			if (acct.getAccountOrParentIsInactive()): return False
			if (acct.getHideOnHomePage() and acct.getBalance() == 0): return False

			return True

	# noinspection PyUnresolvedReferences
	def get_security_holdings(security):
		if security.getCurrencyType() != CurrencyType.Type.SECURITY:
			return 0

		acctHoldings = AccountUtil.allMatchesForSearch(MD_REF.getCurrentAccount().getBook(), MyAcctFilter(22))
		balance = 0
		for acct in acctHoldings:
			if acct.getCurrencyType() == security:
				balance += acct.getBalance()

		return balance

	fmods = MD_REF.getLoadedModules()
	foundBuild = 0
	foundQL = False
	for fmod in fmods:
		if fmod.getIDStr().lower() == QLID:
			foundBuild = fmod.getBuild()
			if foundBuild >= QL_MIN_BUILD and foundBuild <= QL_MAX_BUILD:
				foundQL = True
				break
			else:
				myPrint("B","Found QL extension build %s but min/max builds are %s-to-%s.." %(foundBuild,QL_MIN_BUILD,QL_MAX_BUILD))
				break
	if foundQL:
		myPrint("DB","Quote Loader (QL) extension (valid build %s) is loaded..." %(foundBuild))
	else:
		myPrint("B","Sorry, did not find Quote Loader extension (meeting build requirements) running... ABORTING")

	f_file = os.path.join(MD_REF.getCurrentAccountBook().getRootFolder().getAbsolutePath(),MBFILE)
	if foundQL:
		if os.path.exists(f_file):
			myPrint("DB","MB Master parameter file found: %s" %(f_file))
		else:
			myPrint("B", "Sorry, did not find MB Master parameter file: %s. ABORTING" %(f_file))
			foundQL = False

	if foundQL:
		try:
			with open(f_file,'rb') as json_file:
				contents = json_file.read()
				data = json.loads(contents)
				myPrint("DB","Successfully read MB Master parameter file")
		except:
			dump_sys_error_to_md_console_and_errorlog()
			myPrint("B", "Sorry, error reading MB Master parameter file... ABORTING")
			foundQL = False

	if foundQL:
		if not data.get(MB_KEY):
			myPrint("B","Error: The MB Master Parameter file does not contain the key: '%s'. ABORTING" %(MB_KEY))
			foundQL = False
		else:
			for ql_key in sorted(data[MB_KEY]):
				if ql_key.lower().strip().startswith(QLID.lower().strip()):
					myPrint("DB","MB Master parameter for QL: '%s': %s" %(ql_key,data[MB_KEY][ql_key]))

	f_file = os.path.join(MD_REF.getCurrentAccountBook().getRootFolder().getAbsolutePath(),QLFILE)
	if foundQL:
		if os.path.exists(f_file):
			myPrint("DB","QL parameter file found: %s" %(f_file))
		else:
			myPrint("B", "Sorry, did not find QL parameter file: %s. ABORTING" %(f_file))
			foundQL = False

	if foundQL:

		try:
			with open(f_file,'rb') as json_file:

				# It seems that QL extension just uses that machine's platform's default charset.. We have to try both....
				try_charsets = ['utf-8','iso-8859-1']
				if Platform.isWindows(): try_charsets = ['iso-8859-1','utf-8']
				if foundBuild >= QL_MIN_BUILD2: try_charsets.insert(0,'us-ascii')

				myPrint("DB","QL parameter file open format order....: %s" %(try_charsets))

				for tryCharacterSet in try_charsets:
					try:
						myPrint("DB","Attempting to read QL parameter file using '%s' charset" %(tryCharacterSet))
						contents = json_file.read().decode(tryCharacterSet)
						break
					except:
						myPrint("B","Could not read QL parameter file using '%s'..." %(tryCharacterSet))
						if try_charsets.index(tryCharacterSet)+1 >= len(try_charsets):
							raise

						json_file.seek(0)  # rewind... try again... ;->
						continue

				data = json.loads(contents)
				myPrint("DB","Successfully read QL parameter file (using %s character set)" %(tryCharacterSet))
		except:
			dump_sys_error_to_md_console_and_errorlog()
			myPrint("B", "Sorry, error reading QL parameter file... ABORTING")
			foundQL = False

	if foundQL:
		# for ql_key in [QL_STOCKS_KEY]:
		for ql_key in [QL_STOCKS_KEY,QL_INCL_ZERO_KEY,QL_INCL_CURR_KEY]:
			if ql_key not in data:
				myPrint("B","Error: The QL Parameter file does not contain the key: '%s'. ABORTING" %(ql_key))
				foundQL = False
				break

	if foundQL:
		for ql_key in sorted(data):
			if ql_key.lower().strip() == QL_STOCKS_KEY.lower().strip(): continue
			myPrint("DB","QL parameter: '%s': %s" %(ql_key,data[ql_key]))

	stocksList = []
	QL_stocks = None
	QL_includeZero = None
	QL_includeCurrency = None

	if foundQL:
		MD_REF.getUI().setStatus("%s: Analysing Quote Loader parameters/stocks...." %(myModuleID),-1)
		myPrint("DB","Parameters read: %s" %(data))
		QL_stocks = data[QL_STOCKS_KEY]
		QL_includeZero = data[QL_INCL_ZERO_KEY]
		QL_includeCurrency = data[QL_INCL_CURR_KEY]
		myPrint("DB","QL includeZero: %s" %(QL_includeZero))
		myPrint("DB","QL includeCurrency: %s" %(QL_includeCurrency))

		for stock in sorted(QL_stocks, key=lambda x: (x[QL_STOCK_NAME])):
			if stock[QL_CURRENCY_FLAG]:
				myPrint("DB","Currency ID: %s" %(stock[QL_STOCK_NAME][3:]))		# Currency IDs now has preceding 3 high-byte 7f characters
				stocksList.append([stock[QL_STOCK_NAME][3:],True])
				# myPrint("DB","Currency ID: %s" %(stock[QL_STOCK_NAME]))
				# stocksList.append([stock[QL_STOCK_NAME],True])
			else:
				myPrint("DB","Stock Ticker: %s" %(stock[QL_STOCK_NAME]))
				stocksList.append([stock[QL_STOCK_NAME],False])
		if len(stocksList) < 1:
			myPrint("B","Error: QL stock list is empty..")
			foundQL = False

	stocksDict = {}
	iCountUnfixedWarnings = 0
	if foundQL:
		MD_REF.getUI().setStatus("%s: Linking Quote Loader stocks to Moneydance Objects...." %(myModuleID),-1)
		ct = moneydance.getCurrentAccount().getBook().getCurrencies()
		allXCurrs = ct.getAllCurrencies()

		base = ct.getBaseType()
		allCurrs = []
		for cr in allXCurrs:
			if cr != base:
				allCurrs.append(cr)

		_ID = 0
		_CURR = 1

		for stock_curr in sorted(stocksList, key=lambda x: (x[_CURR], x[_ID].upper())):
			if stock_curr[_CURR]:
				curr = my_getCurrencyByID(allCurrs, stock_curr[_ID], True)
				if curr is not None:
					if curr.getHideInUI():
						myPrint("DB","Ignoring hidden (from summary screen) MD Currency: %s (%s)" %(curr,stock_curr[_ID]))
					elif not QL_includeCurrency:
						myPrint("DB","includeCurrency=NO >> Thus, ignoring MD Currency: %s (%s)" %(curr,stock_curr[_ID]))
					else:
						myPrint("DB","Found MD Currency: %s (%s)" %(curr,stock_curr[_ID]))
						stocksDict[curr] = stock_curr[_ID]
				else:
					myPrint("B","@@ Warning: Did not find MD Currency: %s (will continue)" %(stock_curr[_ID]))
					# iCountUnfixedWarnings += 1
			else:
				sec = my_getCurrencyByID(allCurrs, stock_curr[_ID], False)
				if sec is not None:
					if False and sec.getHideInUI():
						myPrint("DB","Ignoring hidden (from summary screen) MD Security: %s (%s)" %(sec,stock_curr[_ID]))
					elif not QL_includeZero and get_security_holdings(sec) == 0:
						myPrint("DB","Ignoring MD Security: %s (%s) with zero shares/units balance " %(sec,stock_curr[_ID]))
					else:
						myPrint("DB","Found MD Security: %s (%s)" %(sec,stock_curr[_ID]))
						stocksDict[sec] = stock_curr[_ID]
				else:
					myPrint("B","@@ Warning: Did not find MD Security: %s (will continue)" %(stock_curr[_ID]))
					# iCountUnfixedWarnings += 1

		if len(stocksDict) < 1:
			myPrint("B","Error: Did not find any MD Securities / Currencies that match the QL Parameters... ABORTING")
			foundQL = False
		else:
			myPrint("DB","Successfully linked %s MD Securities / Currencies to QL Parameters...." %(len(stocksDict)))

	iCountUpdated = 0

	if foundQL:
		stocksDict = sorted(stocksDict, key=lambda x: (x.getCurrencyType(), x.getName().upper()))
		nowTimeMS = System.currentTimeMillis()
		intNowTime = DateUtil.convertLongDateToInt(nowTimeMS)
		MD_REF.getUI().setStatus("%s: Diagnosing hidden price_date fields & updating where necessary...." %(myModuleID),-1)
		myPrint("B","Diagnosing all matched Securities/Objects....")
		for ctObj in stocksDict:
			currPriceDate = ctObj.getLongParameter("price_date", 0L)												# noqa
			myPrint("B","")
			myPrint("B","%s: %s" %(ctObj.getCurrencyType(),ctObj.getName()))										# noqa

			if currPriceDate < 1:
				myPrint("B","Hidden 'price_date' NOT SET, so skipping....")
				continue

			intCurrPriceDate = DateUtil.convertLongDateToInt(currPriceDate)
			myPrint("B","Hidden 'price_date' (%s): %s" %(currPriceDate,get_time_stamp_as_nice_text(currPriceDate)))

			snaps = ctObj.getSnapshots()																			# noqa
			if len(snaps) < 1:
				myPrint("B","No snapshots exist, so skipping....")
				continue
			s=snaps[-1]
			intLatestSnapDate = s.getDateInt()
			newestRate = s.getRate()
			myPrint("B","Latest dated snapshot date: %s - current rate: %s latest history rate: %s"
					%(convertStrippedIntDateFormattedText(intLatestSnapDate), safeInvertRate(ctObj.getRelativeRate()), safeInvertRate(newestRate)))

			lUpdateRequired = False
			if intCurrPriceDate > intNowTime:
				myPrint("B", "@@ WARNING: Your price_date field is future dated! FIXED @@")
				lUpdateRequired = True

			if intCurrPriceDate < intLatestSnapDate:
				if intCurrPriceDate < intNowTime:
					myPrint("B", "@@ WARNING: Your price_date field is older than latest price history: %s FIXED @@" %(convertStrippedIntDateFormattedText(intLatestSnapDate)))
					lUpdateRequired = True
				else:
					myPrint("B", "@@ WARNING: Your price_date field is older than latest price history: %s NOTFIXED @@" %(convertStrippedIntDateFormattedText(intLatestSnapDate)))
					iCountUnfixedWarnings += 1

			if intLatestSnapDate > intNowTime:
				myPrint("B", "@@ WARNING: Your latest price history date (snapshot) is future dated! %s - SNAPSHOT NOTFIXED @@" %(convertStrippedIntDateFormattedText(intLatestSnapDate)))
				iCountUnfixedWarnings += 1

			if intCurrPriceDate > intLatestSnapDate:
				myPrint("B", "@@ WARNING: price_date field is newer than your latest price history: %s - FIXED @@" %(convertStrippedIntDateFormattedText(intLatestSnapDate)))
				lUpdateRequired = True

			if lUpdateRequired and not checkCurrencyRawRatesOK(ctObj):
				myPrint("B", "@@ ERROR: Security/Currency's underlying fields are an old format. Please manually edit this record to address (this will update the record). NOTFIXED @@")
				iCountUnfixedWarnings += 1
				lUpdateRequired = False

			if lUpdateRequired and not isGoodRate(newestRate):
				myPrint("B", "@@ ERROR: Object's latest dated history price/rate is not valid. SKIPPED/NOTFIXED @@")
				iCountUnfixedWarnings += 1
				lUpdateRequired = False

			if not lUpdateRequired:
				myPrint("B","No update required/possible, skipping.....")
				continue

			rCurr = ctObj.getRelativeCurrency()
			newDate = DateUtil.convertIntDateToLong(min(intNowTime,intLatestSnapDate)).getTime()
			myPrint("B","@@@ UPDATE REQUIRED..... Updating %s hidden 'price_date' field to %s..... "
						"Relative Currency: %s - old current price: %s >> UPDATING current price to: %s @@@"
					%(ctObj,get_time_stamp_as_nice_text(newDate), rCurr, safeInvertRate(ctObj.getRelativeRate()), safeInvertRate(newestRate)))

			ctObj.setEditingMode()
			ctObj.setParameter("price_date", newDate)
			ctObj.setRate(Util.safeRate(newestRate),rCurr)
			ctObj.syncItem()
			iCountUpdated += 1


	MD_REF.getUI().setStatus("%s: FINISHED (review console output)" %(myModuleID),0)
	myPrint("B","")

	msgType = JOptionPane.INFORMATION_MESSAGE
	if foundQL:
		if iCountUpdated > 0:
			msg = "FINISHED. Updated %s hidden 'price_date' fields" %(iCountUpdated)
			msgType = JOptionPane.WARNING_MESSAGE
		else:
			msg = "FINISHED. No hidden 'price_date' fields needed updating"

		if iCountUnfixedWarnings > 0:
			msgType = JOptionPane.WARNING_MESSAGE
			msg += " (with %s unfixed warnings)" %(iCountUnfixedWarnings)
	else:
		msg = "FINISHED WITH WARNINGS! Please review console log. No updates made"
		msgType = JOptionPane.ERROR_MESSAGE

	myPrint("B",msg)
	myPopupInformationBox(None,msg,theMessageType=msgType)

	cleanup_actions()
