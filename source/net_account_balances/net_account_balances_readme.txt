Author: Stuart Beesley - StuWareSoftSystems (March 2021 - a lockdown project) - Last updated December 2023
Credit: (slack: @dtd) aka Dan T Davis for his input, testing and suggestions to make a better product......

Custom Balances works with 2021.1(3056) and newer.
DISCLAIMER: THIS EXTENSION IS READONLY (IT DOES NOT CHANGE DATA) >> BUT YOU USE AT YOUR OWN RISK!

DEFINITIONS:
- CB means this extension / Custom Balances
- Dates are typically mentioned in this guide in the format yyyymmdd (e.g. 15th January 2025 = 20250115)

INSTALLATION:
- Double-click the .mxt file (this may not work if you do not have .mxt extensions associated with Moneydance)
  ... or Drag & drop .mxt onto left side bar, or Extensions, Manage Extensions, add from file to install.
- Once installed, visit Preferences > Summary Page, and then move the new widget to the desired Summary Page location


*******Make this the normal versus trying to explain the change (it won't be a change in future versions***************
** auto simulate row when you make GUI config changes has been turned off. Now you need to click the SIMULATE button **
***********************************************************************************************************************

PURPOSE:
This extension creates a 'widget' that calculates / displays totals on the Moneydance Summary Page (Home Page)

- This widget allows you to select multiple accounts / categories / Securities and filter Active/Inactive items
- The balances are totalled and displayed on the Summary Page widget, converted to the Currency you select to display

- You could create a Net Worth Balance for example; or total particular securities, or total certain accounts...
- Or total expenses by date - e.g. 'how much did I spend on fuel last month?'

- You can use it for anything really. Warning >> you can create 'nonsense' totals if you like too....

- To configure the widget, select an existing row on the Summary Page, or use the Extensions Menu

- You can add/delete/move as many rows as you require, and then configure the selected items per row
- You can select to total together Accounts / Categories (by date range) / Securities....

- You can change the name of each row, the balance type, and the currency to display. Also Active/Inactive items.

LET'S GET STARTED:

Let's start with a row that is <NOT CONFIGURED>. Give it a name - like Credit Card Debt.
Now select all your credit cards from the picklist. Click each one. Hit Save All Settings.
See the result on the summary page.You did note the installation bit, right? Putting the widget in place?
You should now have a row which says "Credit Card Debt.    £(not too much hopefully)"
That's the basics of CB (to create custom calculations)... "Custom Balances"... But you can do so many things now!

How about an account which has a minimum balance? New row - "Checking Account I keep too low" (minimum balance 100)
Click that account to pick it, select "Hide Row" if >=X and set X to 100
If it goes below 100, it will appear, and you can even make it blink.

You can also monitor your spending. E.g. Groceries spend this month? So, create a row, and find your groceries category.
Select "Month to date" in Inc/Exp Date Range. If you have multiple groceries categories, you can select them all.
Save and look.

Now that you have an inkling of the custom balance power potential here, go explore.


WARNINGS:

  - You can create (very) illogical totals (e.g. by adding Securities to Income). CB tries to detect these issues.
  - It will alert you if any are found. Help>Console Window will show you the details of any warnings
  - A red warning icon will appear on the title bar of the widget, and in the GUI, if you have warnings.
        - Click the warning icon to see a popup window displaying the detail(s) of the warnings.
        - NOTE: The symbol will not be triggered for warnings on rows where Show Warnings has been un-ticked
                ... unless debug mode is enabled, in which case the icon will always appear.

EXAMINING THE CHOICES/CONFIGURATION:

- Balance option: Choose from 'Balance', 'Current Balance', 'Cleared Balance'
    - These are the same definitions used by Moneydance:
        - Balance:             Includes all transactions - even future
        - Current Balance:     The same as Balance but excluding future transactions
        - Cleared Balance:     Includes all 'cleared' (i.e. reconciled) transactions - even future

- AutoSum:
  - You can turn AutoSum ON/OFF: When on,  AutoSum recursively totals the selected account and all its sub-accounts
                                           it auto summarises the whole account(s) including Investments/Cash/Securities
                                           ('recursively' means iterate through all an account's children accounts...)
                                 When off, it just adds the value held at that account level (ignoring its children)
                                           you can manually select individual accounts/cats/securities/cash (by row)

  - AutoSum ON  will always auto-include all a selected account's child/sub accounts at runtime.
            OFF will only include the accounts you have selected. You will have to select/add any new accounts created

  - Investment accounts hold Cash at the investment account level. AutoSum affects your ability to select just cash
                        - When AutoSum is on, all securities get totalled into the Investment account

  - You set the AutoSum setting by row. Thus some rows can be on, and others can be off.

- Override Balance asof Date:  Allows you to obtain the balance asof a specified date.
        - Includes all transactions / balances up to, and including, the selected balance asof date
          When selected, the balance asof date options are enabled. Here you select the automatic asof end date,
          or specify a fixed custom asof date. Auto-dates will auto-adjust every time the calculations are executed.

        - Calculation methodology for Balance/Current/Cleared Balance when using asof date:
             - Balance always uses the calculated asof-dated Balance
             - Past asof-dated Current Balance uses the calculated asof-dated Balance
             - Today/future asof-dated Current Balance uses the real account's Current Balance
             - Past asof-dated Cleared Balance is ILLOGICAL, so uses the calculated asof-dated Balance     ** WARNING **
             - Today/future asof-dated Cleared Balance uses the real account's Cleared Balance

        The following points should be noted:
             - Income / Expense categories: Not affected by this option - refer separate 'I/E Date Range' section
             - Include Reminders:           Not affected by this option - refer separate 'Include Reminders' section
             - Security accounts when the 'Securities return Cost Basis / Unrealised Gains' option is selected
                 ... or Investment accounts when 'include cash' option is selected in conjunction with return cost basis
                 - refer separate 'Securities: Return Cost Basis / Unrealised Gains options' section...

        - WARNING: tax dates when using 'asof' cannot be derived. The 'normal' txn date will be applied.

        - WARNING: When using asof dates, consider that inactive accounts might have had balances in the past!
                   I.E. It might be best to Include Inactive and select all accounts (including currently inactive).

        - WARNING: REFER 'PARALLEL BALANCES' BELOW CONCERNING CALCULATION SPEED

- Include Reminders: When selected, Reminders (up to the specified reminder asof date) will be included in the balances.
        - The 'balance asof date' setting has no bearing on Reminders.
        - Only uncommitted (ie. non-recorded) Reminders will be selected. Then...
        - Reminder date(s) will be forward calculated up to the Reminder's asof date setting. Then...
        - The normal rules will apply when calculating Balance, Current Balance, Cleared Balance balances

        - NOTE: It would be unusual to find any reminders with a Cleared Status - so expect ZERO.
        - NOTE: Ignored when returning cost basis / unrealised gains

        - WARNING: tax dates on reminders cannot be calculated. The 'normal' date will be applied.
        - WARNING: REFER 'PARALLEL BALANCES' BELOW CONCERNING CALCULATION SPEED

- Securities: Return Cost Basis / Unrealised Gains options:
    - N/A (default):         Cost Basis is never used
    - Rtn Cost Basis:        When selected, then the cost basis (**as of the balance / asof date) for selected Security
                             accounts will be returned (instead of the normal shareholding).
    - Rtn Unrealised Gains:  When selected, then the calculated unrealised gains (**asof the balance / asof date) for the
                             selected Security accounts will be returned. This is calculated as value less cost basis.
    - Include Cash Balances: When selected then cash balances on (selected) investment accounts will be included too.

    >> NOTES:
        - When selected then calculated cost basis / unrealised gains values will overwrite normal calculated balances
          ... this is a MUTUALLY EXCLUSIVE option. When enabled, no other calculation type(s) will be included!
          ...... (no reminders, no other non-security/investment(cash), no income / expense transactions)
        - There can in theory be future-dated cost basis / ur-gains. Let me know how this works out for you?!
        - Current Balance will derive the cost basis asof today.
        - asof-dated Cleared Balance is ILLOGICAL, so uses the calculated asof-dated Balance               ** WARNING **

        - WARNING: REFER 'PARALLEL BALANCES' BELOW CONCERNING CALCULATION SPEED

INC/EXP Date Range: Simple Explanation - Refer to Detail at USING Categories

Display Currency: Simple Explanation


CALCULATIONS TO BALANCES:

- Average by options:
    - Changes the final calculated balance into an average. Specify the number to divide by (DEFAULT 1.0)
      ...or...
    - Use the predefined: 'Inc/Exp Date Range' - calculate calendar units between XXX option:
      ... Only enabled/allowed when Income/Expense categories are selected AND when NOT using 'All dates'
      ... XXX: select one of: NOTSET, DAYS, WEEKS, MONTHS, YEARS (prefixed with "-" will reverse the sign of avg/result)
      ... Tick/un-tick 'Fractional' as required - see below:
          - ticked will return the exact result (including decimals) - (E.g. 1.45 months in the date range)
          - un-ticked will chop off the decimals with no rounding to return an integer / whole number
      ... WARNING - this can return zero which will mean your calculated result will also be zero or 'n/a'
      ... When allowed/enabled and used, then this overrides the first avg/by field.

      *** NOTE: DO NOT select to use a date range if no Inc/Exp categories are selected. It will automatically revert
                back to All dates at a later point when it validates the settings.

- Adj/by: Allows you to adjust the final calculated balance by a +/- amount (DEFAULT 0.0)

- Maths using another row: If set, you can retrieve the result from another row and then apply maths
                           to the result of the current row.. E.g. take this row and divide it by the result from row x
                           and treat the result as a percent. For example, this could calculate the value of investments
                           as a percentage of total networth...
                           UORs can be chained together. E.G. row 3 can use row 2 and row 2 can use row 1

- Hide row when options: Never, Always(Disable), balance = X, balance >= X, balance <= X. DEFAULT FOR X is ZERO
... You can set X to any value (positive or negative)
    NOTE: If you select row option 'Hide Decimal Places', AND auto-hide row when balance=X,
          AND set X to a value with no decimals, then the calculated balance will be rounded when comparing to X.
          Rounding will be towards X... This means that X=0 would include -0.99 to +0.99 (example)

- Hide Decimal places: Will hide decimal places on the selected row's calculated balance (e.g. 1.99 will show as 1)
                       This option impacts auto-hide logic in some situations - refer: Hide row when options....
                       NOTE: Rounding towards X will be triggered for display formatting when this option selected:
                       ... This means if X=1 for example, then 0.1 thru 1.9 would show as 1 (not zero)

- Row separator: You can put horizontal lines above / below rows to separate sections
- Blink: Enables the blinking of the selected rows (when displayed / visible)

- Show Warnings: This enables / disables the alerts flagging whether warnings have been detected in your parameters
                 These are primarily where you have created 'illogical' calculations - e.g. Expense: Gas plus a Security
                 You can enable/disable warnings per row. The widget doesn't care. It will total up anything...!

                 NOTE: For 'Multi-Warnings Detected' review Help>Console Window for details
                       .. The search for warnings stops after the first occurrence of each type of error it finds....

- Active / Inactive Accounts:
  - MD ALWAYS includes the total balance(s) of all child accounts in an account's total. Irrespective of Active/Inactive
  - Thus if you select Active only and select an account containing inactive children, it will include inactive balances
  - When using AutoSum in this situation you will get a warning on screen
  - You will also see a small (3 vertical bars) icon to the right of account totals in the list window when this occurs.

- Inactive Securities: You can flag a security as inactive by unticking the 'Show on summary page' box on a security
                       in the MD/Tools/Securities menu. This will then treat this security in ALL investment accounts
                       as INACTIVE.

** NOTE: When rows can be hidden, they may not display on the Summary screen widget. Click on the widget to config:
         - In the row selector:
           ... rows coloured red are currently filtered out / hidden by a groupid filter or AutoHide option
           ... row numbers are suffixed with codes:
               <always hide>    Always hide row option is set (red = NOT active and hidden)
               <auto hide>      An auto hide row rule is active. (red = ACTIVE, but hidden)
               <groupid: xxx>   A groupid value has been set on this row
               <FILTERED OUT>   This row is currently NOT showing on the Summary Screen widget due to the active filter.
                                NOTE: Filtered rows (red) are NOT active and hidden.

>> CALCULATION ORDER: The calculations are performed is this sequence:
    - Skip any 'always hide' rows - these are never calculated / used anywhere
    - Skip any rows filtered out by GroupID
    - Calculate raw balances for selected rows/accounts, including recursive sub accounts for autosum rows
    - Convert calculated balances to target currency
    - Iterate over each row/calculation, apply any average/by calculations
    - Iterate over each row/calculation, apply any Use Other Row (UOR) calculations.. Iterate the whole UOR chain
    - Lastly, iterate over each row/calculation, apply any final calculation adjustment amounts specified



USING CATEGORIES:

- Income / Expense Categories:
  - WARNING: REFER 'PARALLEL BALANCES' BELOW CONCERNING CALCULATION SPEED

  - You can change the date range selection from the default of "All Dates" to any of the options in the list

  - NOTE: You can select to use a date range at any time. BUT if you have not selected any Inc/Exp categories, then
          the date range will later revert back automatically to 'All dates'.

  - NOTE: The 'Balance asof Date' has no bearing on this setting which is used exclusively for Income / Expense txns.

  - I/E Date Range options:
    Example: Given a today's date of 4th November 2023 (20231104), the I/E Date Range filters will return the following:
    DR_YEAR_TO_DATE                20230101 - 20231104
    DR_FISCAL_YEAR_TO_DATE         20230406 - 20231104  (assuming a UK tax year starting 6th April 2023)
    DR_LAST_FISCAL_QUARTER         20230706 - 20231005
    DR_QUARTER_TO_DATE             20231001 - 20231104
    DR_MONTH_TO_DATE               20231101 - 20231104
    DR_THIS_YEAR                   20230101 - 20231231 **future**
    DR_THIS_FISCAL_YEAR            20230406 - 20240405 **future**
    DR_THIS_QUARTER                20231001 - 20231231 **future**
    DR_THIS_MONTH                  20231101 - 20231130 **future**
    DR_THIS_WEEK                   20231029 - 20231104
    DR_LAST_YEAR                   20220101 - 20221231
    DR_LAST_FISCAL_YEAR            20220406 - 20230405
    DR_LAST_QUARTER                20230701 - 20230930
    DR_LAST_MONTH                  20231001 - 20231031
    DR_LAST_WEEK                   20231022 - 20231028
    DR_LAST_12_MONTHS              20221101 - 20231031
    DR_LAST_365_DAYS               20221105 - 20231104
    DR_LAST_30_DAYS                20231006 - 20231104
    DR_LAST_1_DAY                  20231103 - 20231104  (known as yesterday and today, which is actually 2 days)
    DR_ALL_DATES                   (returns all dates)  (from 1970 thru 2100)

    NOTE: The above will interact with your Balance/Current Balance/Cleared setting for that row:
          E.G.  Current Balance will always cutoff to today's date
                Balance will just include everything it finds within the above date ranges
                Cleared Balance will just include all cleared items within the above date ranges

    >> If you choose 'Custom Date' you can manually edit the date range. Once you have selected 'Custom Date',
       .. if you then select one of the preconfigured date options, it simply pre-populates the start/end dates for you
       .. this pre-selection name is irrelevant and is not saved. All that is saved is the date range you enter.

    NOTE: All the date options are dynamic and will auto adjust, except 'Custom' dates which remain as you set them

PARALLEL BALANCES:
    - Selecting any of the following options will trigger parallel balance operations for that row, for all accounts
      ... used by that row: Balance asof date; Income/Expense date range; Cost Basis / Unrealised Gains; incl. Reminders

    - The sequence of harvesting data / calculating balances for rows using parallel balances is as follows:
        # 1. per row, gather all selected accounts along with all child/sub accounts...
        # 2. if Income/Expense dates requested, then harvest related I/E txns...
        # 3. convert the harvested I/E txn table into account balances...
        # 4. for all accounts / balances not derived by steps 2 & 3, calculate balance asof dates (where requested)...
        # 5. for all accounts / balances not derived by steps 2, 3 & 4, harvest remaining Account's real balance(s)...
        # 6. replace balance(s) with cost basis / unrealised gains on security accounts (where requested)...
        # 7. for all accounts selected, add reminder txn/balances upto the reminder's asof date (where requested).

    - NOTE: When cost basis / unrealised gains is enabled, all other steps are skipped >> MUTUALLY EXCLUSIVE option!
            (i.e. no reminders, income / expense transactions, no non-security/investment(cash) accounts

    - NOTE: For the Summary Screen (Home Page), only selected accounts use parallel balances...
            But when using the configuration GUI, then all Accounts for the viewed row will use parallel balances...

    - WARNING: Parallel operations calculate by sweeping through transactions and calculating balances from scratch
               Balance asof dates & I/E date ranges harvest transactions...
               Future reminders are forward calculated...
               Cost Basis / Unrealised Gains sweep Buy/Sell txns... (possibly twice for Balance vs Current Balance)
               Remaining real balances, sweep accounts and uses the Account's real stored balance(s)
               ALL THIS CAN POTENTIALLY BE CPU CONSUMING. Do not use the widget for heavy reporting purposes!
               No harm will be caused, but these rows may take a few seconds to calculate / appear....

ACCOUNT PICKLIST:
    - You select accounts one-by-one to include in the row calculation.
    - You can use the dropdown select box to quickly view certain accounts - e.g. "All Investment AND Security accts"
      ... using the dropdown does not actually select any accounts. You have to click each one.
      ... or use the 'Select All Visible' button
    - 'Select All Visbible'     selects all accounts in the current view filtered list, and adds the selection to the
                                existing selection. E.g. If you view INVESTMENT, select all visible, then view SECURITY,
                                then select all, then you will end up with all investment and all security.
    - 'Clear Visible Selection' deselects all accounts in the currently viewable list (but does not deselect any
                                selected accounts in non-viewable filtered list). E.g. view SECURITY,
                                clear visible selection, then view INVESTMENT, and you will see your investment
                                selections are still there.
    - 'Clear Entire Selection'  deselects all accounts - whether they are in the viewable/filtered list or not.
    - 'Undo List Changes'       undo any selection changes since your last 'Store List Changes'
    - 'Store List Changes'      stores the current account list selection into memory (this does NOT save selections)

    >> You must click 'STORE LIST CHANGES' before you click simulate or exit the config screen. If you do not do this
       then your selection changes will be lost!

>> DON'T FORGET TO SAVE CHANGES! (for convenience, this also stores your current account selection list too) <<


OPTIONS MENU

  - Debug: Generates program debug messages in Help>Console Window. DO NOT LEAVE THIS PERMANENTLY ON (setting not saved)
                     NOTE: Enabling this will show [row number] against each widget row on the home screen
  - Show Print Icon: Enables/shows the print icon on the Home / Summary screen widget.. Will print the current view
                     NOTE: Even when icon not visible, clicking the white-space before the title will activate print...
  - Page Setup: Allows you to predefine certain page attributes for printing - e.g. Landscape etc...
  - Backup Config: Creates a backup of your current config file (then opens a window showing location of backup)
  - Restore Config: Allows you to restore (or import) config file from previous back up
  - You can disable the Widget's Display Name Title. This prevents the title appearing on the Summary Page widget
  - You can change the default setting AutoSum for new rows that you insert/create. It does not affect existing rows
  - Show Dashes instead of Zeros: Changes the display so that you get '-' instead of '£ 0.0'
  - Treat Securities with Zero Balance as Inactive: If a Security holds zero units, it will be treated as Inactive
  - Use Indian numbering format: On numbers greater than 10,000 group in powers of 100 (e.g. 10,00,000 not 1,000,000)
  - Use Tax Dates: When selected then all calculations based on Income/Expense categories will use the Tax Date.
                   WARNING: tax dates cannot be derived when including:
                            - reminders,  cost basis / ur-gains, or when using 'balance asof dates'.
                            ... as such, the 'normal' transaction date will be used.
  - Display underline dots: Display 'underline' dots that fill the blank space between row names and values


BACKUP/RESTORE

- When in the config GUI, the keystroke combination:
          CMD-SHIFT-B will create a backup of your config...
          CMD-SHIFT-R will restore the last backup of your config...
          CMD-I       will display this readme/help guide...
          CMD-SHIFT-I will display some debugging information about the rows...
          CMD-SHIFT-L will display debugging information about the internal lastResultsTable (not for 'normal' users)...
          CMD-SHIFT-W will display current warnings (same as clicking the warnings icon)...
          CMD-SHIFT-G allows you to edit the pre-defined/used GroupID Filter(s)... Click +/- cell (on right) to add/del


ROW NAME FORMATTING

- ROW NAME Configuration Options:
  - You can embed the following text (lowercase) in the Row Name field to configure the row / total (value) as follows:
    <#brn>  = Forces row name to be blank/empty
    <#jr>   = Row name justify: right
    <#jc>   = Row name justify: center
    <#cre>  = Row name colour:  red
    <#cbl>  = Row name colour:  blue
    <#cgr>  = Row name colour:  light grey
    <#fbo>  = Row name font:    bold
    <#fun>  = Row name font:    underline
    <#fit>  = Row name font:    italics
    <#bzv>  = Forces any total (value) to appear blank when zero
    <#cvre>  = Value colour:  red
    <#cvbl>  = Value colour:  blue
    <#cvgr>  = Value colour:  light grey
    <#fvbo>  = Value font:    bold
    <#fvun>  = Value font:    underline
    <#fvit>  = Value font:    italics
    <#nud>  = No special underline dots...
    <#fud>  = Force special underline dots...

    NOTE: Underline dots will always be turned off if you justify center the text...

    <#html> = EXPERIMENTAL - USE WITH CARE: Takes your row name as html encoded text (do NOT wrap with <html> </html>)..
              Common html tags are: for bold: <b>text</b>   italics: <i>text</i>   small text: <small>small text</small>
                                        colors(hex) red: <font color=#bb0000>red text</font>
                                                    blue: #0000ff
                                                    default MD foreground color(black-ish): #4a4a4a
                                        Refer: https://www.rapidtables.com/web/color/RGB_Color.html

   HTML EXAMPLE:
   <#html><b><font color=#0000ff>Expenses </font></b>Last month <small><u><font color=#bb0000>OVERDUE</font></u></small>


FILTERS [Using GroupID]

- You can enter a 'GroupID' per row. This is free format text (digits 0-9, Aa-Zz, '_', '-', '.', ':', '%')
   NOTE: You can also enter the ';' character to separate groups. But you cannot filter for ';' as
         this is the separator between filter search elements...

   When you enter 'Group ID' filter text (next to the row selector), then this will filter rows from
   appearing on the Summary / Home page widget.. For example, set a row with "123" and then filter "2", then
   only the row(s) containing "2" will appear on the widget (this would include groups with id "123")
   NOTE: You can filter multiple 'Group IDs' by separating with ';'
         Enter '!' (not) to make the filter include rows that do NOT have the requested filters
         Enter '&' (and) to make the filter include rows where all the requested filters match
                        NOTE: |(or) is default - will be the default anyway unless '!' or '&' used
         Group ID Filters are cAsE InSeNsItIve...
         Each filter you use will be remembered and stored for later quick selection.. The most recent will always be
              top of the list. Click the little up/down selector on the widget title bar, or in the GUI to select one
              Use CMD-SHIFT-G to edit the list and provide names to the filters
              Only the most recent 20 will be saved...

   WARNING: Only enter one of '!|&' characters as only one search type can be used within a single filter.
         NOTE:    !(not) is always implicitly also &(and) - i.e. !1;2 (means not '1' and not '2')

   EXAMPLES:
          - Filter: '1'      - only include rows where the groupid includes a '1'
          - Filter: '1;2;3'  - only include rows where the groupid includes a '1' or '2' or '3'
          - Filter: '!1;2;3' - only include rows where the groupid does NOT include a '1' or '2' or '3'
          - Filter: '&1;2;3' - only include rows where the groupid includes one '1' and '2' and '3'


NOTE: This is free text, so the numbers are examples. A groupid of "Debt;CCList;Whatever" totally works.


TECHNICAL/HISTORICAL NOTES:
- My original concept was to add balances to target zero. Thus a positive number is 'good', a negative is 'bad'
- The idea was that you net cash and debt to get back to zero every month (but you can do so much more than this now)!

>> Display Name changed to 'Custom Balances' (from 'Net Account Balances') Dec 2021.

Extension format only >> Minimum Moneydance version 2021.1 (build: 3056, ideally 3069 onwards)
(If you have installed the extension, but nothing happens, then check your Moneydance version)

This is a Python(Jython 2.7) Extension that runs inside of Moneydance via the Python Interpreter
It's a prototype to demonstrate the capabilities of Python. Yes - if you can do it in Java, you can do it in Python too!

DEVELOPERS: >> You can actually grab the results of the calculations from other extensions.. Contact me for details...

Thanks for reading..... ;->
Get more Scripts/Extensions from: https://yogi1967.github.io/MoneydancePythonScripts/

<END>
