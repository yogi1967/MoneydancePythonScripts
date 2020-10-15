# extract_reminders_to_csv.py (version 2)

###############################################################################
# MIT License
#
# Copyright (c) 2020 Stuart Beesley - StuWareSoftSystems
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

# Harvested from allangdavies adgetreminderstocsv.py as base
# Upgraded by Stuart Beesley 2020-06-17 tested on MacOS - MD2019.4 - StuWareSoftSystems....
#  v2 recognise when reminder has expired

#   Extracts all Moneydance reminders to a csv file compatible with Excel
# 
# Use in MoneyDance Menu Window->Show Moneybot Console

# Before you run this script you must
# 
# 1. Change the 'myfolder' variable below to the output folder for the output CSV file
# 2. Set the date format output you require: 1=dd/mm/yyyy, 2=mm/dd/yyyy, 3=yyyy/mm/dd
#
# To run the script start the Python Interface Extension in the Extensions Menu,
# click *Read from File* button and locate script and click the *Open* button.
# The script will read and extract the reminders to the folder location
# you set in the *myfolder* variable in the script.

# This script accesses Moneydance reminders and write the details to a csv file

from com.infinitekind.moneydance.model import *

import sys
#reload(sys)                    # Was being used with setdefaultencoding below... But seems to work without
import os
import datetime
from javax.swing import JButton, JFrame, JScrollPane, JTextArea, BoxLayout, BorderFactory

#sys.setdefaultencoding('utf8') # Was being used with reload(sys) above... But seems to work without

# function to output the amount (held as integer in cents) to 2 dec place amount field
def formatasnumberforExcel(amountInt):
    wholeportion=str(amountInt)[0:-2]
    placesportion=str(amountInt)[-2:]
    outputfield=wholeportion+'.'+placesportion
    return outputfield

# Moneydance dates  are int yyyymmddd - convert to locale date string for CSV format
def dateoutput(dateinput,theformat):
	if 		dateinput == "EXPIRED": dateoutput=dateinput
	elif 		dateinput == "": dateoutput="" 	
	elif		dateinput == 0: dateoutput=""
	elif		dateinput == "0": dateoutput=""
	else:
			dateasdate=datetime.datetime.strptime(str(dateinput),"%Y%m%d") # Convert to Date field
			dateoutput=dateasdate.strftime(theformat)
	
	#print "Input: ",dateinput,"  Format: ",theformat,' Output: ',dateoutput
	return dateoutput



# ========= MAIN PROGRAM =============
def main():
	print "StuWareSoftSystems..."
	print "Export reminders to csv file"

	# vvvvvvvvvvvvvv SET THIS BELOW vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	myfolder="/Users/stu/Documents/MoneyDance/Extracts/"	######### CHANGE THIS TO YOUR FOLDER LOCATION
	#  for example myfolder="/Users/Fred/Desktop/" for Mac
	#              myfolder="c:/Users/Fred/Desktop/ for Windows

	csvfilename=myfolder+"mdreminders.csv"

	# vvvvvvvvvvvvvv SET THIS BELOW vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	userdateformat=3												######### CHANGE THIS TO 1 or 2 or 3 - as per instruction above

	if	userdateformat==1:	userdateformat="%d/%m/%Y"
	elif	userdateformat==2: 	userdateformat="%m/%d/%Y"
	elif	userdateformat==3: 	userdateformat="%Y/%m/%d"
	else:
		#PROBLEM /  default
		userdateformat="%Y%m%d"

	print 'Reading Reminders and extracting to file: ', csvfilename
	print 'NOTE: Will drop non utf8 characters...'

	root=moneydance.getCurrentAccountBook()

	rems = root.getReminders().getAllReminders()
	print 'Success: read ',rems.size(),'reminders'
	print

	csvheaderline="NextDue,Number#,ReminderType,Frequency,AutoCommitDays,LastAcknowledged,FirstDate,EndDate,ReminderDecription,NetAmount,TxfrType,Account,MainDescription,Split#,SplitAmount,Category,Description,Memo\n"

	# Read each reminder and create a csv line for each in the csvlines array
	csvlines=[]		# Set up an ampty array
	csvlines.append(csvheaderline)
	
	for index in range(0,int(rems.size())):

	    rem=rems[index]									# Get the reminder

	    remtype=rem.getReminderType()                     #NOTE or TRANSACTION
	    desc=rem.getDescription().replace(","," ")        	#remove commas to keep csv format happy
	    memo=str(rem.getMemo()).replace(","," ").strip() #remove commas to keep csv format happy
	    memo=str(memo).replace("\n","*").strip()  		#remove newlines to keep csv format happy

	    print index+1,rem.getDescription() 			# Name of Reminder

	    #determine the frequency of the transaction
	    daily=rem.getRepeatDaily()
	    weekly=rem.getRepeatWeeklyModifier()
	    monthly=rem.getRepeatMonthlyModifier()
	    yearly=rem.getRepeatYearly()
	    numperiods=0
	    countfreqs=0

	    remfreq=''

	    if daily>0:
        		remfreq+='DAILY'
        		remfreq+='(every '+str(daily)+' days)'
        		countfreqs+=1

	    if len( rem.getRepeatWeeklyDays())>0 and rem.getRepeatWeeklyDays()[0] > 0:
        		for freq in range(0,len(rem.getRepeatWeeklyDays())):
					if len(remfreq)>0: remfreq += " & "
					if weekly  == Reminder.WEEKLY_EVERY:					remfreq += 'WEEKLY_EVERY'
					if weekly  == Reminder.WEEKLY_EVERY_FIFTH:			remfreq += 'WEEKLY_EVERY_FIFTH'
					if weekly  == Reminder.WEEKLY_EVERY_FIRST:			remfreq += 'WEEKLY_EVERY_FIRST'
					if weekly  == Reminder.WEEKLY_EVERY_FOURTH:		remfreq += 'WEEKLY_EVERY_FOURTH'
					if weekly  == Reminder.WEEKLY_EVERY_LAST:			remfreq += 'WEEKLY_EVERY_LAST'
					if weekly  == Reminder.WEEKLY_EVERY_SECOND:		remfreq += 'WEEKLY_EVERY_SECOND'
					if weekly  == Reminder.WEEKLY_EVERY_THIRD:			remfreq += 'WEEKLY_EVERY_THIRD'

					if rem.getRepeatWeeklyDays()[freq] == 1: remfreq+='(on Sunday)'
					if rem.getRepeatWeeklyDays()[freq] == 2: remfreq+='(on Monday)'
					if rem.getRepeatWeeklyDays()[freq] == 3: remfreq+='(on Tuesday)'
					if rem.getRepeatWeeklyDays()[freq] == 4: remfreq+='(on Wednesday)'
					if rem.getRepeatWeeklyDays()[freq] == 5: remfreq+='(on Thursday)'
					if rem.getRepeatWeeklyDays()[freq] == 6: remfreq+='(on Friday)'
					if rem.getRepeatWeeklyDays()[freq] == 7: remfreq+='(on Saturday)'
					if rem.getRepeatWeeklyDays()[freq] <1 or rem.getRepeatWeeklyDays()[freq] > 7: remfreq+='(*ERROR*)'
					countfreqs+=1

	    if len(rem.getRepeatMonthly())>0 and rem.getRepeatMonthly()[0] > 0 :
        		for freq in range(0,len(rem.getRepeatMonthly())):
					if len(remfreq)>0: remfreq += " & "
					if monthly  == Reminder.MONTHLY_EVERY:				remfreq += 'MONTHLY_EVERY' 
					if monthly  == Reminder.MONTHLY_EVERY_FOURTH:	remfreq += 'MONTHLY_EVERY_FOURTH'
					if monthly  == Reminder.MONTHLY_EVERY_OTHER: 	remfreq += 'MONTHLY_EVERY_OTHER'
					if monthly  == Reminder.MONTHLY_EVERY_SIXTH: 		remfreq += 'MONTHLY_EVERY_SIXTH' 
					if monthly  == Reminder.MONTHLY_EVERY_THIRD: 		remfreq += 'MONTHLY_EVERY_THIRD' 

					theday = rem.getRepeatMonthly()[freq]
					if theday == Reminder.LAST_DAY_OF_MONTH:
						remfreq+='(on LAST_DAY_OF_MONTH)'
					else:

						if 4 <= theday <= 20 or 24 <= theday <= 30: 		suffix = "th"
						else:    													suffix = ["st", "nd", "rd"][theday % 10 - 1]

						remfreq+='(on '+str(theday)+suffix+')'

					countfreqs+=1

	    if yearly:
			   if len(remfreq)>0: remfreq += " & "
 	  		   remfreq+='YEARLY'
 	  		   countfreqs+=1

	    if len(remfreq) < 1 or countfreqs==0:         remfreq='!ERROR! NO ACTUAL FREQUENCY OPTIONS SET PROPERLY '+remfreq
	    if countfreqs>1: remfreq = "**MULTI** "+remfreq

	    lastdate=rem.getLastDateInt()		
	    if lastdate < 1:   															# Detect if an enddate is set
				remdate=str(rem.getNextOccurance( 20991231 ))				# Use cutoff  far into the future
	    else:		remdate=str(rem.getNextOccurance( rem.getLastDateInt() ))	# Stop at enddate

	    if lastdate <1: lastdate=''

	    if remdate =='0': remdate="EXPIRED"

	    lastack = rem.getDateAcknowledgedInt()
	    if lastack == 0 or lastack == 19700101: lastack=''
				
	    auto = rem.getAutoCommitDays()
	    if auto>= 0: 	auto='YES: ('+str(auto)+' days before scheduled)'
	    else:				auto='NO'

	    if str(remtype)=='NOTE':
			csvline='%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' %(
					dateoutput(remdate,userdateformat),
					index+1,
					rem.getReminderType(),
					remfreq,
					auto,
					dateoutput(lastack,userdateformat),
					dateoutput(rem.getInitialDateInt(),userdateformat),
					dateoutput(lastdate,userdateformat),
					desc,
					'',					# NetAmount
					'',					# TxfrType
					'',					# Account
					'',					# MainDescription
					str(index+1)+'.0',	# Split#
					'',					# SplitAmount
					'',					# Category
					'',					# Description
					'"'+memo+'"'		# Memo
			)
			csvlines.append(csvline)



	    elif str(remtype)=='TRANSACTION':
      
    			txnparent=rem.getTransaction()
    			amount=formatasnumberforExcel(int(txnparent.getValue()))
        
 			for index2 in range(0,int(txnparent.getOtherTxnCount())): 
				splitdesc=txnparent.getOtherTxn(index2).getDescription().replace(","," ")        		#remove commas to keep csv format happy
				splitmemo=txnparent.getMemo().replace(","," ")        									#remove commas to keep csv format happy
 				maindesc=txnparent.getDescription().replace(","," ").strip()

				if index2>0: amount='' 																	# Don't repeat the new amount on subsequent split lines (so you can total column). The split amount will be correct

				stripacct = str(txnparent.getAccount()).replace(","," ").strip() 							#remove commas to keep csv format happy
				stripcat = str(txnparent.getOtherTxn(index2).getAccount()).replace(","," ").strip() 	#remove commas to keep csv format happy

		
				csvline='%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' %(
					dateoutput(remdate,userdateformat),
					index+1,
					rem.getReminderType(),
					remfreq,
					auto,
					dateoutput(lastack,userdateformat),
					dateoutput(rem.getInitialDateInt(),userdateformat),
					dateoutput(lastdate,userdateformat),
					desc,
					amount,
					txnparent.getTransferType(),
					stripacct,
					maindesc,
					str(index+1)+'.'+str(index2+1),
					formatasnumberforExcel(int(txnparent.getOtherTxn(index2).getValue())*-1),
					stripcat,
					splitdesc,
					splitmemo 
				)
				csvlines.append(csvline)

	index+=1

	# Write the csvlines to a file
	f=open(csvfilename,"w")
	for csvline in csvlines: f.write(csvline)
	print 'CSV file '+csvfilename+' created'
	print 'Done'
	f.close()


	return( csvlines )
# END OF FUNCTION

main()
