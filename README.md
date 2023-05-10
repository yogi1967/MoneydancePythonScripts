# Moneydance Python Scripts

Visit: https://yogi1967.github.io/MoneydancePythonScripts/ for downloads...

My collection of Python(Jython 2.7) scripts and extensions for Moneydance (MoneyBot console)

NOTE: My script (*.py) and extension (*.mxt) programs are exactly the same. Just the method to run changes.....
If you downloaded a zip file (extension *.zip) then unzip first in a directory of your choice to get at the file(s)

To build them yourself, fork this repo, use ant (and therefore the build.xml file). E.g.
- ant               (for all)
- ant toolbox       (for just toolbox etc)
NOTE: You may need python2.7 installed for the build to work properly on my extensions (not your own)...

Extensions will only run on Moneydance version 2021.1 build 3056 onwards (ideally 3069+)...
The standalone script versions require a minimum of 2019.4 (build 1904 onwards)...
_(If you have installed the extension, but nothing happens when you click the menu, then check your Moneydance version)_

The <module_name>.zip files in this directory contain both the Extension version (and the Script version if available).
Unzip this file, and then install the Extension, or run the Script, as required - see below:

NOTE: *.pyc files are CPython byte code files generated from the .py script. These are "helpers" to the Jython
interpreter. Within the .mxt file you may also find a *$py.class file. This is a compiled version of the script
for faster launch times. Some of my scripts are large and these "helpers" prevent a "method too large" RuntimeException.
You don't normally need to worry about all this, but if you want to run the .py script manually (e.g. in Moneybot),
then please ensure the .pyc file is placed in the same location as the .py script you are running.

**!! From June 2021 on, most extensions available via the Moneydance menu >> Manage Extensions - Check there first !!**

To use extension (*.mxt):
- Launch Moneydance
- Double-click the .mxt file
- .. or drag and drop the .mxt file onto the Moneydance left side bar
- .. or Menu>Extensions>Manage Extensions>add from file>Select the mxt>Open/Install.
- Then exit and restart Moneydance 
- To run, Menu>Extensions> and choose the Extension to run

To use script (*.py):
- Run Moneydance
- Window>Show Moneybot Console
- Open Script>Choose the script
- RUN

Good luck - contact me with any issues.....

_Stuart Beesley_
**StuWareSoftSystems** 2020-2023
