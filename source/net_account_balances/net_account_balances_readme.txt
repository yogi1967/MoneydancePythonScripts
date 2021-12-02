Author: Stuart Beesley - StuWareSoftSystems (March 2021 - a lockdown project)

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
- The idea is that you net cash and debt to get back to zero every month

- However, you could create a Net Worth Balance for example; you can use it for anything really
- Warning >> you can create 'nonsense' totals if you like too....

- To configure the widget, select an existing row on the Summary Page, or use the Extensions Menu

- You can add/delete/move as many rows as you require, and then configure the accounts for each row
- You can select to show / list Accounts / Categories / Securities....

- You can change the name of each row, the balance type, and the currency to display. Also Active/Inactive items.
  AutoSum Accounts: will auto summarise the whole account(s) including Investments/Cash/Securities
                               when OFF, you can manually select individual accounts/securities/cash (by row)

- NOTE: AutoSum uses recursive balance totalling. When OFF, it simply uses the selected accounts' balance...
-       With AutoSum OFF, this widget will only total selected sub accounts/sub securities.
                          If you later add Accounts/Securities, you will need to change the list too

>> DON'T FORGET TO SAVE CHANGES <<

Thanks for reading..... ;->
Get more Scripts/Extensions from: https://yogi1967.github.io/MoneydancePythonScripts/