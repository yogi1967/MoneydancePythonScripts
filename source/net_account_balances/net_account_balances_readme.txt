Author: Stuart Beesley - StuWareSoftSystems (March 2021 - a lockdown project) - Last updated Dec 2021

Extension format only >> Minimum Moneydance version 2021.1 (build: 3056, ideally 3069 onwards)
(If you have installed the extension, but nothing happens, then check your Moneydance version)

This is a Python(Jython 2.7) Extension that runs inside of Moneydance via the Moneybot Python Interpreter
It's a prototype to demonstrate the capabilities of Python. Yes - if you can do it in Java, you can do it in Python too!

DISCLAIMER: THIS EXTENSION IS READONLY (IT DOES NOT CHANGE DATA) >> BUT YOU USE AT YOUR OWN RISK!

PURPOSE:
This extension creates a 'widget' that displays Totals for items you select on the Moneydance Summary Page (Home Page)

- Double-click .mxt, or Drag & drop .mxt onto left side bar, or Extensions, Manage Extensions, add from file to install.
- Once installed, visit Preferences > Summary Page, and then move the new widget to the desired Summary Page location

- This widget allows you to select multiple accounts / categories / Securities and filter Active/Inactive items
- The balances are totalled and displayed on the Summary Page widget, converted to the Currency you select to display

- My original concept was to add balances to target zero. Thus a positive number is 'good', a negative is 'bad'
- The idea was that you net cash and debt to get back to zero every month

- You could create a Net Worth Balance for example; or total particular securities, or total certain accounts...
- You can use it for anything really. Warning >> you can create 'nonsense' totals if you like too....

- To configure the widget, select an existing row on the Summary Page, or use the Extensions Menu

- You can add/delete/move as many rows as you require, and then configure the accounts for each row
- You can select to show / list Accounts / Categories / Securities....

- You can change the name of each row, the balance type, and the currency to display. Also Active/Inactive items.

- AutoSum:
  - You can turn AutoSum ON/OFF: When on,  AutoSum recursively totals the selected account and all its sub-accounts
                                           it auto summarises the whole account(s) including Investments/Cash/Securities
                                 When off, it just adds the value held at that account level (ignoring its children)
                                           you can manually select individual accounts/securities/cash (by row)

  - AutoSum ON  will always auto-include all a selected account's child/sub accounts at runtime.
            OFF will only include the accounts you have selected. You will have to select/add any new accounts created

  - Investment accounts hold Cash at the investment account level. AutoSum affects your ability to select just cash
                        - When AutoSum is on, all securities get totalled into the Investment account

  - You set the AutoSum setting by row. Thus some rows can be on, and others can be off.

- Active / Inactive Accounts:
  - MD always includes the total balance(s) of all child accounts in an account's total.. Irrespective of Active/Inactive
  - Thus if you select Active only and select an account which contains inactive children, it will include inactive balances
  - When using AutoSum in this situation you will get a warning in Help>Console
  - You will also see a small icon to the right of account totals in the list window in this situation too.

- Income / Expense Categories:
  - You can change the date range selection from the default of "All Dates" to any of the options in the list
  - WARNING: This switches the widget to build and maintain a parallel table of balances.
             Calculated by sweeping through all transactions and calculating balances
             THIS CAN POTENTIALLY BE CPU CONSUMING. Do not use the widget for heavy reporting purposes!
             Any row that uses a NON "All Dates" will trigger this parallel balances sweep

  - I/E Date Range options:
    Example: Given a today's date of 11th December 2021, the I/E Date Range filters will return the following:
    DR_YEAR_TO_DATE                20210101 - 20211211
    DR_FISCAL_YEAR_TO_DATE         20210406 - 20211211
    DR_LAST_FISCAL_QUARTER         20210706 - 20211005
    DR_QUARTER_TO_DATE             20211001 - 20211211
    DR_MONTH_TO_DATE               20211201 - 20211211
    DR_THIS_YEAR                   20210101 - 20211231 **future**
    DR_THIS_FISCAL_YEAR            20210406 - 20220405 **future**
    DR_THIS_QUARTER                20211001 - 20211231 **future**
    DR_THIS_MONTH                  20211201 - 20211231 **future**
    DR_THIS_WEEK                   20211205 - 20211211
    DR_LAST_YEAR                   20200101 - 20201231
    DR_LAST_FISCAL_YEAR            20200406 - 20210405
    DR_LAST_QUARTER                20210701 - 20210930
    DR_LAST_MONTH                  20211101 - 20211130
    DR_LAST_WEEK                   20211128 - 20211204
    DR_LAST_12_MONTHS              20201201 - 20211130
    DR_LAST_365_DAYS               20201211 - 20211211
    DR_LAST_30_DAYS                20211111 - 20211211
    DR_LAST_1_DAY                  20211210 - 20211211
    DR_ALL_DATES                   (returns all dates)

    NOTE: The above will interact with your Balance/Current Balance/Cleared setting for that row:
          E.G.  Current Balance will always cutoff to today's date
                Balance will just include everything it finds within the above date ranges
                Cleared Balance will just include all cleared items within the above date ranges

- Warnings:
  - You can create illogical totals (e.g. by adding Securities to Income). NAB tries to detect these issues.
  - It will alert you if any are found. Help>Console will show you the details of any warnings

- Options Menu:
  - You can change the default setting AutoSum for new rows that you insert/create. It does not affect existing rows
  - Show Warnings: This enables / disables the alerts flagging whether warnings have been detected in your parameters
                   It's either on or off for all rows and affects the whole program.

>> DON'T FORGET TO SAVE CHANGES <<

Thanks for reading..... ;->
Get more Scripts/Extensions from: https://yogi1967.github.io/MoneydancePythonScripts/